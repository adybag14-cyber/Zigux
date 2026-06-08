const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "segment map carries strerror and formatter windows through slab storage" {
    slab.kmalloc_nr_allocated = 0;

    var map = slab.kmallocArray(3, 24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(map);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const known_window = map[1..19];
    const known = str_error_r.strErrorR(13, known_window);
    try std.testing.expectEqualStrings("Permission denied", known);
    try std.testing.expectEqual(@as(u8, 0), map[0]);
    try std.testing.expectEqual(@as(u8, 0), map[18]);
    try std.testing.expectEqual(@as(u8, 0), map[19]);

    const summary_window = map[26..42];
    const summary_len = vsprintf.scnprintf(summary_window, "seg:{d}:{d}", .{ known.len, slab.kmalloc_nr_allocated });
    try std.testing.expectEqual(@as(usize, 8), summary_len);
    try std.testing.expectEqualStrings("seg:17:1", summary_window[0..summary_len]);
    try std.testing.expectEqual(@as(u8, 0), summary_window[summary_len]);
    try std.testing.expectEqual(@as(u8, 0), map[25]);
    try std.testing.expectEqual(@as(u8, 0), map[42]);

    const pad_window = map[52..64];
    const padded_len = vsprintf.scnprintfPad(pad_window, 10, "pad={d}", .{summary_len});
    try std.testing.expect(padded_len == 9 or padded_len == 10);
    try std.testing.expectEqualSlices(u8, "pad=8     ", pad_window[0..10]);
    try std.testing.expectEqual(@as(u8, 0), pad_window[10]);
    try std.testing.expectEqual(@as(u8, 0), map[51]);
    try std.testing.expectEqual(@as(u8, 0), map[64]);

    const SegmentState = struct {
        known_len: usize,
        summary_len: usize,
        padded_len: usize,
    };
    const allocator = std.testing.allocator;
    var state: ?*SegmentState = try zalloc.zallocValue(allocator, SegmentState);
    defer zalloc.zfreeValue(allocator, SegmentState, &state);
    try std.testing.expectEqual(@as(usize, 0), state.?.known_len);

    state.?.known_len = known.len;
    state.?.summary_len = summary_len;
    state.?.padded_len = padded_len;
    try std.testing.expectEqual(@as(usize, 17), state.?.known_len);
    try std.testing.expectEqual(@as(usize, 8), state.?.summary_len);
    try std.testing.expect(state.?.padded_len == 9 or state.?.padded_len == 10);

    zalloc.zfreeValue(allocator, SegmentState, &state);
    try std.testing.expect(state == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "segment map preserves zalloc owners across fallback rendering and slab failures" {
    slab.kmalloc_nr_allocated = 0;

    const anchor = slab.kmallocBytes(16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(anchor);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const allocator = std.testing.allocator;
    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &owner);
    for (owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const fallback = str_error_r.strErrorR(7777, owner.?[2..45]);
    try std.testing.expect(std.mem.startsWith(u8, fallback, "INTERNAL ERROR: strerror_r(7777"));
    try std.testing.expectEqual(@as(usize, 42), fallback.len);
    try std.testing.expectEqual(@as(u8, 0), owner.?[0]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[1]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[44]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[45]);

    var result = [_]u8{0xaa} ** 24;
    const result_len = vsprintf.vscnprintf(&result, "fallback:{d}:{d}", .{ fallback.len, slab.kmalloc_nr_allocated });
    try std.testing.expectEqual(@as(usize, 13), result_len);
    try std.testing.expectEqualStrings("fallback:42:1", result[0..result_len]);
    try std.testing.expectEqual(@as(u8, 0), result[result_len]);
    try std.testing.expectEqual(@as(u8, 0xaa), result[result_len + 1]);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);

    owner = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0 }, owner.?);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
