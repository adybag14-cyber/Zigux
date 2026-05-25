const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-extent cycles keep allocation counters balanced" {
    slab.kmalloc_nr_allocated = 0;

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zero_array = slab.kmallocArray(0, 7, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocBytes(1, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR sibling subslices keep terminators inside each caller window" {
    var backing = [_]u8{'#'} ** 14;

    const known = str_error_r.strErrorR(0, backing[1..4]);
    try std.testing.expectEqualStrings("Su", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', 'S', 'u', 0, '#', '#', '#', '#', '#', '#', '#', '#', '#', '#' }, &backing);

    const unknown = str_error_r.strErrorR(77, backing[6..10]);
    try std.testing.expectEqualStrings("INT", unknown);
    try std.testing.expectEqual(@as(u8, '#'), backing[5]);
    try std.testing.expectEqual(@as(u8, 'I'), backing[6]);
    try std.testing.expectEqual(@as(u8, 'N'), backing[7]);
    try std.testing.expectEqual(@as(u8, 'T'), backing[8]);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try std.testing.expectEqual(@as(u8, '#'), backing[10]);
}

test "vsprintf sibling subslices alternate padded and direct renders without bleed" {
    var backing = [_]u8{'!'} ** 13;
    const left = backing[1..6];
    const right = backing[7..12];

    const left_written = vsprintf.scnprintfPad(left, 3, "{s}", .{"q"});
    try std.testing.expectEqual(@as(usize, 2), left_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'q', ' ', ' ', 0, '!' }, left);
    try std.testing.expectEqual(@as(u8, '!'), backing[0]);
    try std.testing.expectEqual(@as(u8, '!'), backing[6]);

    const right_written = vsprintf.vscnprintf(right, "{s}", .{"wxyz"});
    try std.testing.expectEqual(@as(usize, 4), right_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'w', 'x', 'y', 'z', 0 }, right);
    try std.testing.expectEqual(@as(u8, '!'), backing[6]);
    try std.testing.expectEqual(@as(u8, '!'), backing[12]);
}

test "zalloc cycles re-zero bytes and values independently" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u8,
        right: u8,
        active: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 2);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);
    bytes.?[0] = 0xaa;
    bytes.?[1] = 0x55;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u8, 0), value.?.left);
    try std.testing.expectEqual(@as(u8, 0), value.?.right);
    try std.testing.expectEqual(false, value.?.active);
    value.?.left = 9;
    value.?.right = 3;
    value.?.active = true;
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);

    bytes = try zalloc.zallocBytes(allocator, 2);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);

    value = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expectEqual(@as(u8, 0), value.?.left);
    try std.testing.expectEqual(@as(u8, 0), value.?.right);
    try std.testing.expectEqual(false, value.?.active);
}
