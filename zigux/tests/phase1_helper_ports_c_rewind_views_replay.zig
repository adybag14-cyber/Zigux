const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab rewinds zero-extent allocations out of order without counter drift" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    const second = slab.kmallocArray(0, 9, slab.GFP_KERNEL) orelse {
        return error.TestUnexpectedResult;
    };

    try std.testing.expectEqual(@as(usize, 0), first.len);
    try std.testing.expectEqual(@as(usize, 0), second.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR rewinds a caller subview from fallback to known text" {
    var backing = [_]u8{ '#', '#', '#', '#', '#', '#', '#', '#', '#' };
    const window = backing[2..8];

    const fallback = str_error_r.strErrorR(2048, window);
    try std.testing.expectEqualStrings("INTER", fallback);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#', 'I', 'N', 'T', 'E', 'R', 0, '#' }, &backing);

    const known = str_error_r.strErrorR(0, window);
    try std.testing.expectEqualStrings("Succe", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#', 'S', 'u', 'c', 'c', 'e', 0, '#' }, &backing);
}

test "vsprintf rewinds padded interior views after truncation" {
    var backing = [_]u8{ '!', '!', '!', '!', '!', '!', '!', '!', '!', '!' };
    const window = backing[3..9];

    const truncated = vsprintf.scnprintf(window, "{s}", .{"abcdefghi"});
    try std.testing.expectEqual(@as(usize, 5), truncated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', '!', 'a', 'b', 'c', 'd', 'e', 0, '!' }, &backing);

    const padded = vsprintf.scnprintfPad(window, 5, "{s}", .{"q"});
    try std.testing.expectEqual(@as(usize, 4), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', '!', 'q', ' ', ' ', ' ', ' ', 0, '!' }, &backing);

    const reset = vsprintf.vscnprintf(window, "{s}", .{""});
    try std.testing.expectEqual(@as(usize, 0), reset);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', '!', 0, ' ', ' ', ' ', ' ', 0, '!' }, &backing);
}

test "zalloc rewinds byte and value owners back to a zero state" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u16,
        right: u16,
        child: ?*u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 2);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);
    bytes.?[0] = 0x7f;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);

    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), value.?.left);
    try std.testing.expectEqual(@as(u16, 0), value.?.right);
    try std.testing.expect(value.?.child == null);
    value.?.left = 9;
    value.?.right = 11;
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);

    var second_value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &second_value);
    try std.testing.expectEqual(@as(u16, 0), second_value.?.left);
    try std.testing.expectEqual(@as(u16, 0), second_value.?.right);
    try std.testing.expect(second_value.?.child == null);
}
