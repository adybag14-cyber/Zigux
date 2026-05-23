const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps live allocation count steady across null free and disabled reclaim" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(2, 3, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const second = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (second) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR tiny buffers rewrite prefixes and preserve terminators" {
    var single = [_]u8{0xaa};
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(0, &single));
    try std.testing.expectEqual(@as(u8, 0), single[0]);

    var pair = [_]u8{ 0xbb, 0xcc };
    try std.testing.expectEqualStrings("P", str_error_r.strErrorR(13, &pair));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'P', 0 }, &pair);

    try std.testing.expectEqualStrings("I", str_error_r.strErrorR(4096, &pair));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'I', 0 }, &pair);
}

test "vsprintf tiny interior views clamp writes without disturbing neighbors" {
    var buffer = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x' };

    const padded = vsprintf.scnprintfPad(buffer[1..5], 3, "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 3), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'a', 'b', 'c', 0, 'x' }, &buffer);

    const zero_logical = vsprintf.scnprintfPad(buffer[2..4], 0, "{s}", .{"z"});
    try std.testing.expectEqual(@as(usize, 0), zero_logical);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'a', 0, 'c', 0, 'x' }, &buffer);

    const one_slot = vsprintf.vscnprintf(buffer[3..4], "{s}", .{"host"});
    try std.testing.expectEqual(@as(usize, 0), one_slot);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'a', 0, 0, 0, 'x' }, &buffer);
}

test "zalloc leaves optionals null after repeated frees and zeroes fresh values" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u8,
        right: u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);
    bytes.?[0] = 0xaa;
    bytes.?[1] = 0xbb;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var first: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u8, 0), first.?.left);
    try std.testing.expectEqual(@as(u8, 0), first.?.right);
    first.?.left = 9;
    first.?.right = 7;
    zalloc.zfreeValue(allocator, Pair, &first);
    try std.testing.expect(first == null);
    zalloc.zfreeValue(allocator, Pair, &first);
    try std.testing.expect(first == null);

    var second: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &second);
    try std.testing.expectEqual(@as(u8, 0), second.?.left);
    try std.testing.expectEqual(@as(u8, 0), second.?.right);
}
