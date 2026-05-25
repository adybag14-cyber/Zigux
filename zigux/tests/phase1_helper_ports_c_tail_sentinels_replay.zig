const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 replay keeps mixed slab edge allocations balanced" {
    slab.kmalloc_nr_allocated = 0;

    const one = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), one.len);
    try std.testing.expectEqual(@as(u8, 0), one[0]);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zero_array = slab.kmallocArray(0, 7, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(1, 8, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(one);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 replay keeps strerror_r tail sentinels intact on tiny windows" {
    var backing = [_]u8{'!'} ** 10;

    const single = str_error_r.strErrorR(13, backing[3..4]);
    try std.testing.expectEqualStrings("", single);
    try std.testing.expectEqual(@as(u8, '!'), backing[2]);
    try std.testing.expectEqual(@as(u8, 0), backing[3]);
    try std.testing.expectEqual(@as(u8, '!'), backing[4]);

    const exact = str_error_r.strErrorR(12, backing[1..4]);
    try std.testing.expectEqualStrings("Ca", exact);
    try std.testing.expectEqual(@as(u8, '!'), backing[0]);
    try std.testing.expectEqual(@as(u8, 0), backing[3]);
    try std.testing.expectEqual(@as(u8, '!'), backing[4]);
}

test "lane10 replay keeps vsprintf tail sentinels stable across one-byte reuse" {
    var backing = [_]u8{0x7c} ** 9;
    const inner = backing[2..7];

    const padded_written = vsprintf.scnprintfPad(inner, 1, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 1), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 0, 0x7c, 0x7c, 0x7c }, inner);
    try std.testing.expectEqual(@as(u8, 0x7c), backing[1]);
    try std.testing.expectEqual(@as(u8, 0x7c), backing[7]);

    const direct_written = vsprintf.vscnprintf(inner, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 2), direct_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0x7c, 0x7c }, inner);
    try std.testing.expectEqual(@as(u8, 0x7c), backing[1]);
    try std.testing.expectEqual(@as(u8, 0x7c), backing[7]);
}

test "lane10 replay keeps zalloc zero and nonzero byte reuse reset" {
    const allocator = std.testing.allocator;

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);

    var single: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    try std.testing.expectEqual(@as(usize, 1), single.?.len);
    try std.testing.expectEqual(@as(u8, 0), single.?[0]);
    single.?[0] = 0xaa;
    zalloc.zfreeBytes(allocator, &single);
    try std.testing.expect(single == null);

    single = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &single);
    try std.testing.expectEqual(@as(u8, 0), single.?[0]);
}
