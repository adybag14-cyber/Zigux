const std = @import("std");
const ida_bitmap_view = @import("ida_bitmap_view");
const ida_range_view = @import("ida_range_view");

test "ida range starter packet keeps clamped window geometry explicit" {
    const words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const view = ida_range_view.fromWords(&words, 1024);
    const window = view.clampWindow(ida_range_view.range(1000, 1027)) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(u32, 1024), window.first_id);
    try std.testing.expectEqual(@as(u32, 1027), window.last_id);
    try std.testing.expectEqual(@as(u32, 4), window.spanLen());
}

test "ida range starter packet keeps partial allocation counting explicit" {
    var words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    words[0] |= (@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 3);
    const view = ida_range_view.fromWords(&words, 1024);
    const summary = view.summarize(ida_range_view.range(1000, 1027)) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(u32, 3), summary.allocated_bits);
    try std.testing.expect(!summary.isFullyAllocated());
    try std.testing.expect(!summary.isFullyFree());
}

test "ida range starter packet keeps ceiling clamping and full windows explicit" {
    var words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const high_a: u32 = ida_bitmap_view.bitmap_bits - 2;
    const high_b: u32 = ida_bitmap_view.bitmap_bits - 1;
    words[high_a / ida_bitmap_view.word_bits] |= @as(usize, 1) << @intCast(high_a % ida_bitmap_view.word_bits);
    words[high_b / ida_bitmap_view.word_bits] |= @as(usize, 1) << @intCast(high_b % ida_bitmap_view.word_bits);

    const view = ida_range_view.fromWords(&words, 2048);
    const summary = view.summarize(ida_range_view.range(3070, 4096)) orelse return error.TestUnexpectedResult;

    try std.testing.expect(summary.isFullyAllocated());
    try std.testing.expectEqual(@as(?ida_range_view.Selection, null), summary.first_free);
}

test "ida range starter packet keeps clear windows distinct from invalid ones" {
    const words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const view = ida_range_view.fromWords(&words, 0);
    const summary = view.summarize(ida_range_view.range(8, 11)) orelse return error.TestUnexpectedResult;

    try std.testing.expect(summary.isFullyFree());
    try std.testing.expectEqual(@as(?ida_range_view.Selection, null), summary.first_allocated);
    try std.testing.expectEqual(@as(?ida_range_view.RangeSummary, null), view.summarize(ida_range_view.range(2048, 2050)));
}

test "ida range starter packet keeps ordered-range failure explicit" {
    const words = std.mem.zeroes(ida_bitmap_view.BitmapWords);
    const view = ida_range_view.fromWords(&words, 4096);

    try std.testing.expectEqual(@as(?ida_range_view.ClampedWindow, null), view.clampWindow(ida_range_view.range(17, 12)));
    try std.testing.expectEqual(@as(?u32, null), view.allocatedCount(ida_range_view.range(17, 12)));
}
