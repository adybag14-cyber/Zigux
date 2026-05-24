const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab balances zero-length byte and array allocations" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const array = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR confines tiny caller views to the provided sub-slice" {
    var backing = [_]u8{ 'L', 'L', 'L', 'L', 'L', 'L', 'L' };

    const empty = str_error_r.strErrorR(2, backing[2..2]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'L', 'L', 'L', 'L', 'L', 'L', 'L' }, &backing);

    const one = str_error_r.strErrorR(13, backing[1..2]);
    try std.testing.expectEqual(@as(usize, 0), one.len);
    try std.testing.expectEqual(@as(u8, 'L'), backing[0]);
    try std.testing.expectEqual(@as(u8, 0), backing[1]);
    try std.testing.expectEqual(@as(u8, 'L'), backing[2]);

    const three = str_error_r.strErrorR(13, backing[3..6]);
    try std.testing.expectEqualStrings("Pe", three);
    try std.testing.expectEqual(@as(u8, 'L'), backing[2]);
    try std.testing.expectEqual(@as(u8, 'P'), backing[3]);
    try std.testing.expectEqual(@as(u8, 'e'), backing[4]);
    try std.testing.expectEqual(@as(u8, 0), backing[5]);
    try std.testing.expectEqual(@as(u8, 'L'), backing[6]);
}

test "vsprintf preserves neighbors when formatting into a tiny subview" {
    var backing = [_]u8{ '#', '#', '#', '#', '#', '#', '#', '#', '#', '#' };

    const written = vsprintf.scnprintf(backing[2..7], "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqual(@as(u8, '#'), backing[1]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 'd' }, backing[2..6]);
    try std.testing.expectEqual(@as(u8, 0), backing[6]);
    try std.testing.expectEqual(@as(u8, '#'), backing[7]);

    @memset(backing[2..7], '!');
    const reset_written = vsprintf.scnprintfPad(backing[2..7], 0, "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), reset_written);
    try std.testing.expectEqual(@as(u8, '#'), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', '!', '!' }, backing[3..7]);
    try std.testing.expectEqual(@as(u8, '#'), backing[7]);
}

test "zalloc re-zeroes fresh values after dirty frees and resets zero-length optionals" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        bytes: [3]u8,
        flag: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var first: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expect(first != null);
    first.?.* = .{ .bytes = .{ 9, 8, 7 }, .flag = true };
    zalloc.zfreeValue(allocator, Pair, &first);
    try std.testing.expect(first == null);

    var second: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &second);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &second.?.bytes);
    try std.testing.expectEqual(false, second.?.flag);
}
