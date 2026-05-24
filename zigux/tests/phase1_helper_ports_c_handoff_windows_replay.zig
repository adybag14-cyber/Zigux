const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps allocation counters stable across failed handoff attempts" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocBytes(1, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const second = slab.kmallocArray(2, 0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqual(@as(usize, 0), second.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(4, 2, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR reuses the same shifted caller window across long and short messages" {
    var backing = [_]u8{ '^', '^', '^', '^', '^', '^', '^', '^' };
    const window = backing[2..6];

    const first = str_error_r.strErrorR(4096, window);
    try std.testing.expectEqualStrings("INT", first);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '^', '^', 'I', 'N', 'T', 0, '^', '^' }, &backing);

    const second = str_error_r.strErrorR(0, window);
    try std.testing.expectEqualStrings("Suc", second);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '^', '^', 'S', 'u', 'c', 0, '^', '^' }, &backing);
}

test "vsprintf hands off overlapping caller windows between direct and padded renders" {
    var backing = [_]u8{ '?', '?', '?', '?', '?', '?', '?', '?', '?', '?' };

    const left_written = vsprintf.scnprintf(backing[1..6], "{s}", .{"wxyz"});
    try std.testing.expectEqual(@as(usize, 4), left_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '?', 'w', 'x', 'y', 'z', 0, '?', '?', '?', '?' }, &backing);

    const right_written = vsprintf.scnprintfPad(backing[4..9], 3, "{s}", .{"Q"});
    try std.testing.expectEqual(@as(usize, 2), right_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '?', 'w', 'x', 'y', 'Q', ' ', ' ', 0, '?', '?' }, &backing);
}

test "zalloc alternates byte and value owners without leaking dirty state" {
    const allocator = std.testing.allocator;
    const Record = struct {
        bytes: [2]u8,
        tag: u16,
        seen: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);
    bytes.?[1] = 0xaa;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Record = try zalloc.zallocValue(allocator, Record);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, &value.?.bytes);
    try std.testing.expectEqual(@as(u16, 0), value.?.tag);
    try std.testing.expectEqual(false, value.?.seen);
    value.?.* = .{ .bytes = .{ 9, 8 }, .tag = 7, .seen = true };
    zalloc.zfreeValue(allocator, Record, &value);
    try std.testing.expect(value == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);
}
