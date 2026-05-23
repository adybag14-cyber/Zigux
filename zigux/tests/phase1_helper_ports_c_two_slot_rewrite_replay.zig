const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 slab zero-product allocations still balance counters" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocArray(0, 7, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 strErrorR rewrites two-slot subslices without touching neighbors" {
    var backing = [_]u8{ 'L', 'L', 'x', 'x', 'x', 'R' };
    const inner = backing[2..5];

    const known = str_error_r.strErrorR(2, inner);
    try std.testing.expectEqualStrings("No", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'L', 'L', 'N', 'o', 0, 'R' }, &backing);

    const unknown = str_error_r.strErrorR(4096, inner);
    try std.testing.expectEqualStrings("IN", unknown);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'L', 'L', 'I', 'N', 0, 'R' }, &backing);
}

test "lane10 vsprintf rewrites padded two-slot windows in place" {
    var backing = [_]u8{ '#', '#', '#', '#', '#', '#' };
    const inner = backing[1..4];

    const padded = vsprintf.scnprintfPad(inner, inner.len, "{s}", .{"z"});
    try std.testing.expectEqual(@as(usize, 1), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', 'z', ' ', 0, '#', '#' }, &backing);

    const rewritten = vsprintf.scnprintf(inner, "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 2), rewritten);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', 'a', 'b', 0, '#', '#' }, &backing);
}

test "lane10 zalloc re-zeroes two-byte storage and nested values after reuse" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [2]u8,
        flag: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 2);
    try std.testing.expectEqual(@as(usize, 2), bytes.?.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);
    bytes.?[0] = 0xaa;
    bytes.?[1] = 0x55;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 2);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    value.?.bytes = .{ 9, 7 };
    value.?.flag = true;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, &value.?.bytes);
    try std.testing.expectEqual(false, value.?.flag);
}
