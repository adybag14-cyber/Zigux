const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-length allocations still balance live counters" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const array = slab.kmallocArray(0, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(usize, 0), bytes.len);
    try std.testing.expectEqual(@as(usize, 0), array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(bytes);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR respects exact-fit and terminator-only caller windows" {
    var backing = [_]u8{0xaa} ** 12;

    const exact = str_error_r.strErrorR(0, backing[2..10]);
    try std.testing.expectEqualStrings("Success", exact);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[10]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[11]);

    const tiny = str_error_r.strErrorR(4096, backing[4..5]);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, 'u'), backing[3]);
    try std.testing.expectEqual(@as(u8, 0), backing[4]);
    try std.testing.expectEqual(@as(u8, 'c'), backing[5]);
    try std.testing.expectEqual(@as(u8, 'e'), backing[6]);
}

test "vsprintf keeps neighboring sentinels outside exact-fit and padded rewrites" {
    var backing = [_]u8{0xcc} ** 12;

    const exact_written = vsprintf.scnprintf(backing[1..9], "{s}", .{"Success"});
    try std.testing.expectEqual(@as(usize, 7), exact_written);
    try std.testing.expectEqualSlices(u8, "Success", backing[1..8]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[9]);

    const padded_written = vsprintf.scnprintfPad(backing[3..10], 4, "{s}", .{"x"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqual(@as(u8, 'S'), backing[1]);
    try std.testing.expectEqual(@as(u8, 'u'), backing[2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', ' ', ' ', ' ', 0 }, backing[3..8]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[9]);
}

test "zalloc re-zeroes values after dirty writes and frees zero-length byte views" {
    const allocator = std.testing.allocator;
    const Pair = extern struct {
        left: u16,
        right: u16,
    };

    var first: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expect(first != null);
    first.?.* = .{ .left = 0x1234, .right = 0x5678 };
    zalloc.zfreeValue(allocator, Pair, &first);
    try std.testing.expect(first == null);

    var second: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &second);
    try std.testing.expectEqual(@as(u16, 0), second.?.left);
    try std.testing.expectEqual(@as(u16, 0), second.?.right);

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
}
