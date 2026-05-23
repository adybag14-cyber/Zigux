const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-span allocations still balance counters" {
    slab.kmalloc_nr_allocated = 0;

    const empty_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const empty_array = slab.kmallocArray(0, 16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty_array.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR truncates inside narrow interior slices without touching neighbors" {
    var known = [_]u8{ 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L' };
    const known_view = known[2..6];
    const known_text = str_error_r.strErrorR(12, known_view);
    try std.testing.expectEqualStrings("Can", known_text);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'L', 'L', 'C', 'a', 'n', 0, 'L', 'L' }, &known);

    var unknown = [_]u8{ 'R', 'R', 'R', 'R', 'R', 'R' };
    const unknown_view = unknown[1..2];
    const unknown_text = str_error_r.strErrorR(4096, unknown_view);
    try std.testing.expectEqual(@as(usize, 0), unknown_text.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'R', 0, 'R', 'R', 'R', 'R' }, &unknown);
}

test "scnprintfPad honors logical limits inside caller sub-slices" {
    var padded = [_]u8{'.'} ** 10;
    const padded_view = padded[2..8];
    const padded_written = vsprintf.scnprintfPad(padded_view, 4, "{s}", .{"alpha"});
    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '.', '.', 'a', 'l', 'p', 'h', 0, '.', '.', '.' }, &padded);

    var empty_backing = [_]u8{ 'Q', 'Q', 'Q' };
    const empty_written = vsprintf.vscnprintf(empty_backing[1..1], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'Q', 'Q', 'Q' }, &empty_backing);
}

test "zalloc zero-size bytes and nested values reset cleanly" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u16,
        ready: bool,
        pair: [2]u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.ready);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, &value.?.pair);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
