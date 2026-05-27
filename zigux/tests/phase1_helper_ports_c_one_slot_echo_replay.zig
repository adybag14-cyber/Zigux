const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab balances empty and one-slot owners across failed side requests" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(empty);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const one = slab.kmallocArray(1, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(one);
    try std.testing.expectEqual(@as(usize, 1), one.len);
    try std.testing.expectEqual(@as(u8, 0), one[0]);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocBytes(1, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps one-slot and empty caller windows fenced" {
    var backing = [_]u8{0x51} ** 10;

    const empty = str_error_r.strErrorR(2, backing[2..2]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, 0x51), backing[1]);
    try std.testing.expectEqual(@as(u8, 0x51), backing[2]);

    const one = str_error_r.strErrorR(0, backing[2..3]);
    try std.testing.expectEqual(@as(usize, 0), one.len);
    try std.testing.expectEqual(@as(u8, 0), backing[2]);
    try std.testing.expectEqual(@as(u8, 0x51), backing[3]);

    const fallback = str_error_r.strErrorR(4096, backing[3..5]);
    try std.testing.expectEqualStrings("I", fallback);
    try std.testing.expectEqual(@as(u8, 0), backing[4]);
    try std.testing.expectEqual(@as(u8, 0x51), backing[5]);
}

test "vsprintf echoes through one-slot and tiny padded windows only" {
    var backing = [_]u8{0x52} ** 8;

    const one_written = vsprintf.scnprintf(backing[1..2], "{s}", .{"abc"});
    try std.testing.expectEqual(@as(usize, 0), one_written);
    try std.testing.expectEqual(@as(u8, 0x52), backing[0]);
    try std.testing.expectEqual(@as(u8, 0), backing[1]);
    try std.testing.expectEqual(@as(u8, 0x52), backing[2]);

    const two_written = vsprintf.scnprintfPad(backing[3..6], 3, "{s}", .{"a"});
    try std.testing.expectEqual(@as(usize, 1), two_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', ' ', 0 }, backing[3..6]);
    try std.testing.expectEqual(@as(u8, 0x52), backing[6]);
}

test "zalloc re-zeroes one-slot bytes after the paired value is freed later" {
    const allocator = std.testing.allocator;
    const Tiny = extern struct {
        seen: u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Tiny = try zalloc.zallocValue(allocator, Tiny);
    defer zalloc.zfreeValue(allocator, Tiny, &value);

    bytes.?[0] = 0x7f;
    value.?.seen = 9;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u8, 9), value.?.seen);

    bytes = try zalloc.zallocBytes(allocator, 1);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[0]);

    zalloc.zfreeValue(allocator, Tiny, &value);
    try std.testing.expect(value == null);
    value = try zalloc.zallocValue(allocator, Tiny);
    try std.testing.expectEqual(@as(u8, 0), value.?.seen);
}
