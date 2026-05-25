const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 replay keeps slab zero-size and reclaim edges balanced" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const pair = slab.kmallocArray(2, 0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), pair.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(pair);
    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 replay keeps strerror_r guard bytes stable across known and unknown windows" {
    var backing = [_]u8{'?'} ** 16;

    const known = str_error_r.strErrorR(0, backing[2..5]);
    try std.testing.expectEqualStrings("Su", known);
    try std.testing.expectEqual(@as(u8, '?'), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[4]);
    try std.testing.expectEqual(@as(u8, '?'), backing[5]);

    const unknown = str_error_r.strErrorR(4096, backing[8..9]);
    try std.testing.expectEqualStrings("", unknown);
    try std.testing.expectEqual(@as(u8, '?'), backing[7]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, '?'), backing[9]);
}

test "lane10 replay keeps vsprintf guard bands stable across logical-size resets" {
    var backing = [_]u8{0x5a} ** 10;
    const inner = backing[1..8];

    const padded = vsprintf.scnprintfPad(inner, 4, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 3), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'd', ' ', ' ', 0, 0x5a, 0x5a }, inner);
    try std.testing.expectEqual(@as(u8, 0x5a), backing[0]);
    try std.testing.expectEqual(@as(u8, 0x5a), backing[8]);

    const reset = vsprintf.scnprintfPad(inner, 0, "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), reset);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 'd', ' ', ' ', 0, 0x5a, 0x5a }, inner);
    try std.testing.expectEqual(@as(u8, 0x5a), backing[0]);
    try std.testing.expectEqual(@as(u8, 0x5a), backing[8]);
}

test "lane10 replay keeps zalloc byte and value resets isolated" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        a: u16,
        b: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 2);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);
    bytes.?[0] = 0xaa;
    bytes.?[1] = 0x55;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), value.?.a);
    try std.testing.expectEqual(@as(u16, 0), value.?.b);
    value.?.a = 9;
    value.?.b = 12;
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expectEqual(@as(u16, 0), value.?.a);
    try std.testing.expectEqual(@as(u16, 0), value.?.b);
}
