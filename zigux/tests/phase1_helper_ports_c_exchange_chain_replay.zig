const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "exchange chain rewrites slab and zalloc caller windows" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    var slab_owner: ?[]u8 = slab.kmallocBytes(96, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer slab.kfree(slab_owner);
    const arena = slab_owner orelse return error.TestUnexpectedResult;

    const fallback_window = arena[5..42];
    const fallback = str_error_r.strErrorR(5151, fallback_window);
    try std.testing.expectEqual(fallback_window.len - 1, fallback.len);
    try std.testing.expect(std.mem.startsWith(u8, fallback, "INTERNAL ERROR: strerror_r(5151,"));
    try std.testing.expectEqual(@as(u8, 0), fallback_window[fallback.len]);

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 64);
    defer zalloc.zfreeBytes(allocator, &zbytes);
    const summary = zbytes.?;
    for (summary) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const padded_written = vsprintf.scnprintfPad(
        summary[0..32],
        20,
        "fb:{s}:n={d}",
        .{ fallback[0..8], fallback.len },
    );
    try std.testing.expect(padded_written == 20 or padded_written == 19);
    try std.testing.expectEqualStrings("fb:INTERNAL:n=36    ", summary[0..20]);
    try std.testing.expectEqual(@as(u8, 0), summary[20]);
    try std.testing.expectEqual(@as(u8, 0), summary[21]);

    const known_window = arena[48..66];
    const known = str_error_r.strErrorR(22, known_window);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0), known_window[known.len]);

    const SummaryState = struct {
        fallback_len: usize,
        known_len: usize,
        marker: [4]u8,
    };
    var state: ?*SummaryState = try zalloc.zallocValue(allocator, SummaryState);
    defer zalloc.zfreeValue(allocator, SummaryState, &state);
    try std.testing.expectEqual(@as(usize, 0), state.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 0), state.?.known_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &state.?.marker);

    state.?.fallback_len = fallback.len;
    state.?.known_len = known.len;
    @memcpy(&state.?.marker, summary[3..7]);

    const record_written = vsprintf.scnprintf(
        arena[70..88],
        "lens={d}/{d}:{s}",
        .{ state.?.fallback_len, state.?.known_len, state.?.marker[0..] },
    );
    try std.testing.expectEqual(@as(usize, 15), record_written);
    try std.testing.expectEqualStrings("lens=36/16:INTE", arena[70 .. 70 + record_written]);
    try std.testing.expectEqual(@as(u8, 0), arena[70 + record_written]);

    zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes == null);
    zbytes = try zalloc.zallocBytes(allocator, 8);
    for (zbytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    zalloc.zfreeValue(allocator, SummaryState, &state);
    try std.testing.expect(state == null);

    slab.kfree(slab_owner);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "failed slab allocation preserves live exchange buffers" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    var slab_owner: ?[]u8 = slab.kmallocArray(3, 16, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer slab.kfree(slab_owner);
    const slots = slab_owner orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const slot_written = vsprintf.scnprintf(slots[4..20], "slot={d}", .{7});
    try std.testing.expectEqual(@as(usize, 6), slot_written);
    try std.testing.expectEqualStrings("slot=7", slots[4 .. 4 + slot_written]);
    try std.testing.expectEqual(@as(u8, 0), slots[4 + slot_written]);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualStrings("slot=7", slots[4 .. 4 + slot_written]);

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &zbytes);
    const errbuf = zbytes.?;
    for (errbuf) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const known = str_error_r.strErrorR(12, errbuf[1..]);
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try std.testing.expectEqual(@as(u8, 0), errbuf[1 + known.len]);
    try std.testing.expectEqual(@as(u8, 0), errbuf[0]);

    const err_written = vsprintf.scnprintf(slots[24..36], "err={s}", .{known[0..3]});
    try std.testing.expectEqual(@as(usize, 7), err_written);
    try std.testing.expectEqualStrings("err=Can", slots[24 .. 24 + err_written]);
    try std.testing.expectEqual(@as(u8, 0), slots[24 + err_written]);

    zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes == null);
    zbytes = try zalloc.zallocBytes(allocator, 24);
    for (zbytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(slab_owner);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
