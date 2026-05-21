const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps counters balanced across failed and zeroed replay paths" {
    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocBytes(3, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const bytes = slab.kmallocBytes(6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    var array: ?[]u8 = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (array.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(array);
    array = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR respects caller windows during rotating reuse" {
    var tiny_storage = [_]u8{ '#', '#', '#', '#', '#', '#' };

    const tiny = str_error_r.strErrorR(13, tiny_storage[2..4]);
    try std.testing.expectEqualStrings("P", tiny);
    try std.testing.expectEqual(@as(u8, '#'), tiny_storage[0]);
    try std.testing.expectEqual(@as(u8, '#'), tiny_storage[1]);
    try std.testing.expectEqual(@as(u8, 'P'), tiny_storage[2]);
    try std.testing.expectEqual(@as(u8, 0), tiny_storage[3]);

    var full_storage: [64]u8 = undefined;
    @memset(&full_storage, '#');
    const unknown = str_error_r.strErrorR(4096, full_storage[4..]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 60)=22", unknown);
    try std.testing.expectEqual(@as(u8, '#'), full_storage[0]);
    try std.testing.expectEqual(@as(u8, '#'), full_storage[1]);
    try std.testing.expectEqual(@as(u8, 'I'), full_storage[4]);
}

test "vsprintf resets padded caller views before the next shorter render" {
    var storage = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x' };

    const padded_len = vsprintf.scnprintfPad(storage[2..], 5, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 4), padded_len);
    try std.testing.expectEqualStrings("ok   ", storage[2..7]);
    try std.testing.expectEqual(@as(u8, 0), storage[7]);
    try std.testing.expectEqual(@as(u8, 'x'), storage[0]);
    try std.testing.expectEqual(@as(u8, 'x'), storage[1]);

    const reset_len = vsprintf.scnprintfPad(storage[2..], 0, "{s}", .{"later"});
    try std.testing.expectEqual(@as(usize, 0), reset_len);
    try std.testing.expectEqual(@as(u8, 0), storage[2]);
    try std.testing.expectEqual(@as(u8, 'k'), storage[3]);
}

test "zalloc re-zeroes bytes and values after dirty frees" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u32,
        right: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    for (bytes.?) |*byte| {
        byte.* = 0xaa;
    }
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    value.?.left = 99;
    value.?.right = true;
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.left);
    try std.testing.expectEqual(false, value.?.right);
}
