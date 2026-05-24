const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-sized reclaim allocations still balance counters" {
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocArray(0, 8, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const empty = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    defer slab.kfree(empty);

    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps tiny known and unknown caller views contained" {
    var known_backing = [_]u8{ 'L', 'L', 'L', 'L', 'L', 'L' };
    const tiny_known = known_backing[2..4];
    const known = str_error_r.strErrorR(13, tiny_known);
    try std.testing.expectEqualStrings("P", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'L', 'L', 'P', 0, 'L', 'L' }, &known_backing);

    var unknown_backing = [_]u8{ 'R', 'R', 'R', 'R', 'R', 'R', 'R' };
    const tiny_unknown = unknown_backing[1..6];
    const unknown = str_error_r.strErrorR(77, tiny_unknown);
    try std.testing.expectEqualStrings("INTE", unknown);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'R', 'I', 'N', 'T', 'E', 0, 'R' }, &unknown_backing);
}

test "vsprintf caller slices can switch from padded to unpadded reuse" {
    var backing = [_]u8{ '#', '#', '#', '#', '#', '#', '#', '#' };
    const window = backing[1..6];

    const padded_written = vsprintf.scnprintfPad(window, 4, "{s}", .{"z"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', 'z', ' ', ' ', ' ', 0, '#', '#' }, &backing);

    const reused_written = vsprintf.vscnprintf(window, "{s}:{d}", .{ "ab", 9 });
    try std.testing.expectEqual(@as(usize, 4), reused_written);
    try std.testing.expectEqualStrings("ab:9", window[0..reused_written]);
    try std.testing.expectEqual(@as(u8, 0), window[reused_written]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', 'a', 'b', ':', '9', 0, '#', '#' }, &backing);
}

test "zalloc zero-sized bytes and recreated values reset cleanly" {
    const allocator = std.testing.allocator;
    const Value = struct {
        left: u16,
        right: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var first: ?*Value = try zalloc.zallocValue(allocator, Value);
    first.?.left = 99;
    first.?.right = true;
    zalloc.zfreeValue(allocator, Value, &first);
    try std.testing.expect(first == null);

    var second: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &second);
    try std.testing.expectEqual(@as(u16, 0), second.?.left);
    try std.testing.expectEqual(false, second.?.right);
}
