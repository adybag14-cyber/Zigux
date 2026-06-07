const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectPadWritten(written: usize, expected_current: usize, expected_legacy: usize) !void {
    try std.testing.expect(written == expected_current or written == expected_legacy);
}

test "ring ferry preserves helper-owned windows across rewrites" {
    slab.kmalloc_nr_allocated = 0;

    const allocator = std.testing.allocator;
    var ferry_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 72);
    defer zalloc.zfreeBytes(allocator, &ferry_owner);
    const ferry = ferry_owner.?;

    const slab_window = slab.kmallocBytes(52, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_window);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(slab_window, 0xa5);

    const fallback = str_error_r.strErrorR(8193, slab_window[4..48]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(8193, [buf], 44)", fallback);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_window[3]);
    try std.testing.expectEqual(@as(u8, 0), slab_window[47]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_window[48]);

    const ferry_written = vsprintf.scnprintf(ferry[5..41], "ferry:{s}:{d}", .{ fallback[0..8], slab_window[47] });
    try std.testing.expectEqual(@as(usize, 16), ferry_written);
    try std.testing.expectEqualStrings("ferry:INTERNAL:0", ferry[5 .. 5 + ferry_written]);
    try std.testing.expectEqual(@as(u8, 0), ferry[5 + ferry_written]);
    try std.testing.expectEqual(@as(u8, 0), ferry[4]);

    const known = str_error_r.strErrorR(22, slab_window[14..32]);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0), slab_window[30]);
    try std.testing.expectEqual(@as(u8, '8'), slab_window[31]);

    const padded_written = vsprintf.scnprintfPad(ferry[41..58], 12, "ok:{s}", .{known[0..7]});
    try expectPadWritten(padded_written, 12, 11);
    try std.testing.expectEqualSlices(u8, "ok:Inva", ferry[41..48]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'l', 'i', 'd', ' ', ' ', 0 }, ferry[48..54]);
    for (ferry[54..58]) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    var packet_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    const packet = packet_owner.?;
    const packet_written = vsprintf.scnprintf(packet, "{s}|{s}", .{ ferry[5..10], ferry[41..48] });
    try std.testing.expectEqual(@as(usize, 13), packet_written);
    try std.testing.expectEqualStrings("ferry|ok:Inva", packet[0..packet_written]);

    zalloc.zfreeBytes(allocator, &packet_owner);
    try std.testing.expect(packet_owner == null);

    var reacquired_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &reacquired_owner);
    for (reacquired_owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const snapshot = slab.kmallocArray(3, 8, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(snapshot);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memcpy(snapshot[0..8], "ringferr");
    try std.testing.expectEqualStrings("ringferr", snapshot[0..8]);
}

test "ring ferry keeps failure paths and typed owners balanced" {
    slab.kmalloc_nr_allocated = 0;

    const live = slab.kmallocBytes(16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(live);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (live) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    try std.testing.expect(slab.kmallocBytes(16, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const allocator = std.testing.allocator;
    const FerryState = struct {
        copied: usize,
        failed_allocations: usize,
        had_known_error: bool,
    };

    var state: ?*FerryState = try zalloc.zallocValue(allocator, FerryState);
    defer zalloc.zfreeValue(allocator, FerryState, &state);
    try std.testing.expectEqual(@as(usize, 0), state.?.copied);
    try std.testing.expectEqual(@as(usize, 0), state.?.failed_allocations);
    try std.testing.expectEqual(false, state.?.had_known_error);

    var message: [40]u8 = @splat(0xcc);
    const rendered = str_error_r.strErrorR(12, message[3..30]);
    state.?.copied = rendered.len;
    state.?.failed_allocations = 2;
    state.?.had_known_error = true;

    var summary: [32]u8 = @splat(0xdd);
    const summary_written = vsprintf.scnprintf(&summary, "copy={d},fail={d},known={}", .{
        state.?.copied,
        state.?.failed_allocations,
        state.?.had_known_error,
    });
    try std.testing.expectEqual(@as(usize, 25), summary_written);
    try std.testing.expectEqualStrings("copy=22,fail=2,known=true", summary[0..summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary[summary_written]);

    zalloc.zfreeValue(allocator, FerryState, &state);
    try std.testing.expect(state == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
