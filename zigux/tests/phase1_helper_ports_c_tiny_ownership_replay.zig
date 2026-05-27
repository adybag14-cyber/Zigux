const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-length ownership stays independent from live neighbors" {
    slab.kmalloc_nr_allocated = 0;

    var empty: ?[]u8 = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(empty);
    const live: ?[]u8 = slab.kmallocBytes(2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(live);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    @memcpy(live.?, &[_]u8{ 0x31, 0x32 });

    slab.kfree(empty);
    empty = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x31, 0x32 }, live.?);

    const refill: ?[]u8 = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(refill);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, refill.?);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x31, 0x32 }, live.?);
}

test "strErrorR keeps tiny caller windows fenced from neighboring bytes" {
    var backing = [_]u8{0x7a} ** 18;

    const one = str_error_r.strErrorR(13, backing[2..3]);
    try std.testing.expectEqual(@as(usize, 0), one.len);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[2]);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[3]);

    const two = str_error_r.strErrorR(0, backing[4..6]);
    try std.testing.expectEqualStrings("S", two);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[3]);
    try std.testing.expectEqual(@as(u8, 0), backing[5]);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[6]);

    const fallback = str_error_r.strErrorR(4096, backing[7..9]);
    try std.testing.expectEqualStrings("I", fallback);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[6]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[9]);
}

test "vsprintf keeps one-character ownership inside tiny caller windows" {
    var backing = [_]u8{0x55} ** 12;

    const padded_written = vsprintf.scnprintfPad(backing[1..5], 1, "{s}", .{"abcd"});
    try std.testing.expectEqual(@as(usize, 1), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 0, 0x55, 0x55 }, backing[1..5]);
    try std.testing.expectEqual(@as(u8, 0x55), backing[0]);
    try std.testing.expectEqual(@as(u8, 0x55), backing[5]);

    const direct_written = vsprintf.vscnprintf(backing[5..7], "{d}", .{42});
    try std.testing.expectEqual(@as(usize, 1), direct_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '4', 0 }, backing[5..7]);
    try std.testing.expectEqual(@as(u8, 0x55), backing[4]);
    try std.testing.expectEqual(@as(u8, 0x55), backing[7]);

    const tiny_written = vsprintf.scnprintf(backing[7..8], "{s}", .{"zz"});
    try std.testing.expectEqual(@as(usize, 0), tiny_written);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);
    try std.testing.expectEqual(@as(u8, 0x55), backing[8]);
}

test "zalloc zero-length ownership can be released without touching live values" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u8,
        right: u8,
    };

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &pair);
    pair.?.left = 9;
    pair.?.right = 11;

    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);
    try std.testing.expectEqual(@as(u8, 9), pair.?.left);
    try std.testing.expectEqual(@as(u8, 11), pair.?.right);

    empty = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);

    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);

    var pair_again: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &pair_again);
    try std.testing.expectEqual(@as(u8, 0), pair_again.?.left);
    try std.testing.expectEqual(@as(u8, 0), pair_again.?.right);
}
