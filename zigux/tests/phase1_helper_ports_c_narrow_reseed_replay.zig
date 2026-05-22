const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps allocation counters balanced across failed and reordered frees" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const second = slab.kmallocArray(2, 3, slab.GFP_KERNEL) orelse {
        slab.kfree(first);
        return error.TestUnexpectedResult;
    };
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR can reseed a narrower caller window without touching outer bytes" {
    var backing = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x' };

    try std.testing.expectEqualStrings("Permi", str_error_r.strErrorR(13, backing[1..7]));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'P', 'e', 'r', 'm', 'i', 0, 'x' }, &backing);

    try std.testing.expectEqualStrings("S", str_error_r.strErrorR(0, backing[1..3]));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'S', 0, 'r', 'm', 'i', 0, 'x' }, &backing);
}

test "scnprintf can reseed a narrower caller window and preserve surrounding bytes" {
    var backing = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x' };

    const first = vsprintf.scnprintf(backing[1..7], "{s}", .{"abcde"});
    try std.testing.expectEqual(@as(usize, 5), first);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'a', 'b', 'c', 'd', 'e', 0, 'x' }, &backing);

    const second = vsprintf.scnprintf(backing[1..4], "{s}", .{"Q"});
    try std.testing.expectEqual(@as(usize, 1), second);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'Q', 0, 'c', 'd', 'e', 0, 'x' }, &backing);
}

test "zalloc reallocation zeroes bytes and values after prior mutation" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u32,
        flag: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expect(value != null);
    value.?.count = 99;
    value.?.flag = true;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.flag);
}
