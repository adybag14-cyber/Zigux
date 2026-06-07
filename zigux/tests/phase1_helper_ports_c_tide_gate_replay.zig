const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectPadWritten(written: usize, expected_current: usize, expected_legacy: usize) !void {
    try std.testing.expect(written == expected_current or written == expected_legacy);
}

test "tide gate ferries slab errors through zalloc summaries" {
    slab.kmalloc_nr_allocated = 0;

    const allocator = std.testing.allocator;
    var gate_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 80);
    defer zalloc.zfreeBytes(allocator, &gate_owner);
    const gate = gate_owner.?;
    for (gate) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const tide = slab.kmallocBytes(64, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(tide);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (tide) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    @memset(tide, 0x71);

    const known = str_error_r.strErrorR(13, tide[5..24]);
    try std.testing.expectEqualStrings("Permission denied", known);
    try std.testing.expectEqual(@as(u8, 0x71), tide[4]);
    try std.testing.expectEqual(@as(u8, 0), tide[22]);
    try std.testing.expectEqual(@as(u8, 0x71), tide[23]);

    const fallback = str_error_r.strErrorR(12289, tide[25..58]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(12289", fallback);
    try std.testing.expectEqual(@as(usize, 32), fallback.len);
    try std.testing.expectEqual(@as(u8, 0), tide[57]);
    try std.testing.expectEqual(@as(u8, 0x71), tide[58]);

    const summary_written = vsprintf.scnprintf(gate[3..39], "gate:{s}:{s}:{d}", .{
        known[0..4],
        fallback[0..8],
        slab.kmalloc_nr_allocated,
    });
    try std.testing.expectEqual(@as(usize, 20), summary_written);
    try std.testing.expectEqualStrings("gate:Perm:INTERNAL:1", gate[3 .. 3 + summary_written]);
    try std.testing.expectEqual(@as(u8, 0), gate[3 + summary_written]);
    try std.testing.expectEqual(@as(u8, 0), gate[2]);

    const padded_written = vsprintf.scnprintfPad(gate[40..62], 17, "{s}|{d}", .{ fallback[9..14], known.len });
    try expectPadWritten(padded_written, 17, 16);
    try std.testing.expectEqualSlices(u8, "ERROR|17", gate[40..48]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0 }, gate[48..58]);
    for (gate[58..62]) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    var compact_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    const compact = compact_owner.?;
    const compact_written = vsprintf.vscnprintf(compact, "{s}/{s}", .{ gate[3..12], gate[40..45] });
    try std.testing.expectEqual(@as(usize, 15), compact_written);
    try std.testing.expectEqualStrings("gate:Perm/ERROR", compact[0..compact_written]);
    try std.testing.expectEqual(@as(u8, 0), compact[compact_written]);

    zalloc.zfreeBytes(allocator, &compact_owner);
    try std.testing.expect(compact_owner == null);
}

test "tide gate keeps allocation failures and typed owners balanced" {
    slab.kmalloc_nr_allocated = 0;

    const array = slab.kmallocArray(4, 6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (array) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memcpy(array[0..6], "tide-a");
    @memcpy(array[6..12], "tide-b");
    try std.testing.expectEqualStrings("tide-a", array[0..6]);
    try std.testing.expectEqualStrings("tide-b", array[6..12]);

    try std.testing.expect(slab.kmallocBytes(12, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const allocator = std.testing.allocator;
    const TideState = struct {
        array_len: usize,
        live_allocations: isize,
        saw_failure: bool,
        marker: u16,
    };

    var state: ?*TideState = try zalloc.zallocValue(allocator, TideState);
    defer zalloc.zfreeValue(allocator, TideState, &state);
    try std.testing.expectEqual(@as(usize, 0), state.?.array_len);
    try std.testing.expectEqual(@as(isize, 0), state.?.live_allocations);
    try std.testing.expectEqual(false, state.?.saw_failure);
    try std.testing.expectEqual(@as(u16, 0), state.?.marker);

    state.?.array_len = array.len;
    state.?.live_allocations = slab.kmalloc_nr_allocated;
    state.?.saw_failure = true;
    state.?.marker = 0x10c;

    var report: [44]u8 = @splat(0xa9);
    const report_written = vsprintf.scnprintf(&report, "len={d},live={d},fail={},mark={d}", .{
        state.?.array_len,
        state.?.live_allocations,
        state.?.saw_failure,
        state.?.marker,
    });
    try std.testing.expectEqual(@as(usize, 32), report_written);
    try std.testing.expectEqualStrings("len=24,live=1,fail=true,mark=268", report[0..report_written]);
    try std.testing.expectEqual(@as(u8, 0), report[report_written]);

    zalloc.zfreeValue(allocator, TideState, &state);
    try std.testing.expect(state == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
