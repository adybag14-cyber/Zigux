const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 slab sibling allocations keep counters and contents isolated" {
    slab.kmalloc_nr_allocated = 0;

    var left: ?[]u8 = slab.kmallocBytes(3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(left);
    var right: ?[]u8 = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(right);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memcpy(left.?, "abc");
    try std.testing.expectEqualSlices(u8, "abc", left.?);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, right.?);

    slab.kfree(left);
    left = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, right.?);

    slab.kfree(right);
    right = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 strErrorR stays inside split caller windows" {
    var backing = [_]u8{'#'} ** 32;
    const left = str_error_r.strErrorR(13, backing[1..9]);
    const right = str_error_r.strErrorR(0, backing[16..24]);

    try std.testing.expectEqualStrings("Permiss", left);
    try std.testing.expectEqualStrings("Success", right);
    try std.testing.expectEqual(@as(u8, '#'), backing[0]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, '#'), backing[9]);
    try std.testing.expectEqual(@as(u8, '#'), backing[15]);
    try std.testing.expectEqual(@as(u8, 0), backing[23]);
    try std.testing.expectEqual(@as(u8, '#'), backing[24]);
}

test "lane10 vsprintf preserves sentinels around split caller views" {
    var backing = [_]u8{'!'} ** 16;

    const padded_written = vsprintf.scnprintfPad(backing[1..7], 5, "{s}", .{"xy"});
    const direct_written = vsprintf.vscnprintf(backing[9..14], "{s}", .{"tool"});

    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqualSlices(u8, "xy   ", backing[1..6]);
    try std.testing.expectEqual(@as(u8, 0), backing[6]);
    try std.testing.expectEqualSlices(u8, "tool", backing[9..13]);
    try std.testing.expectEqual(@as(u8, 0), backing[13]);
    try std.testing.expectEqual(@as(u8, '!'), backing[0]);
    try std.testing.expectEqual(@as(u8, '!'), backing[7]);
    try std.testing.expectEqual(@as(u8, '!'), backing[8]);
    try std.testing.expectEqual(@as(u8, '!'), backing[14]);
}

test "lane10 zalloc release order keeps sibling owners independent" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u8,
        right: u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeBytes(allocator, &bytes);
    defer zalloc.zfreeValue(allocator, Pair, &value);

    bytes.?[1] = 7;
    value.?.left = 9;
    try std.testing.expectEqual(@as(u8, 7), bytes.?[1]);
    try std.testing.expectEqual(@as(u8, 9), value.?.left);
    try std.testing.expectEqual(@as(u8, 0), value.?.right);

    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);
    try std.testing.expectEqual(@as(u8, 7), bytes.?[1]);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    zalloc.zfreeValue(allocator, Pair, &value);
}
