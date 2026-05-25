const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab interleaved zero-length allocations keep counters balanced" {
    slab.kmalloc_nr_allocated = 0;

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zero_array = slab.kmallocArray(3, 0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);

    try std.testing.expect(slab.kmallocArray(2, 4, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
}

test "strErrorR tiny and exact-fit subviews preserve neighboring bytes" {
    var backing = [_]u8{0x5a} ** 16;

    const tiny = backing[3..5];
    try std.testing.expectEqualStrings("S", str_error_r.strErrorR(0, tiny));
    try std.testing.expectEqual(@as(u8, 'S'), backing[3]);
    try std.testing.expectEqual(@as(u8, 0), backing[4]);
    try std.testing.expectEqual(@as(u8, 0x5a), backing[2]);
    try std.testing.expectEqual(@as(u8, 0x5a), backing[5]);

    const exact = backing[3..11];
    try std.testing.expectEqualStrings("Success", str_error_r.strErrorR(0, exact));
    try std.testing.expectEqual(@as(u8, 0x5a), backing[2]);
    try std.testing.expectEqual(@as(u8, 0x5a), backing[11]);
}

test "vsprintf reuses a padded inner view without touching outer sentinels" {
    var backing = [_]u8{0x44} ** 10;
    const inner = backing[2..8];

    const padded_written = vsprintf.scnprintfPad(inner, 4, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', 0, 0x44 }, inner);
    try std.testing.expectEqual(@as(u8, 0x44), backing[1]);
    try std.testing.expectEqual(@as(u8, 0x44), backing[8]);

    const direct_written = vsprintf.vscnprintf(inner, "{s}:{d}", .{ "ab", 9 });
    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', ':', '9', 0, 0x44 }, inner);
    try std.testing.expectEqual(@as(u8, 0x44), backing[1]);
    try std.testing.expectEqual(@as(u8, 0x44), backing[8]);
}

test "zalloc re-zeroes byte and value storage after dirty frees" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [3]u8,
        flag: bool,
        count: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expect(value != null);
    value.?.bytes = .{ 1, 2, 3 };
    value.?.flag = true;
    value.?.count = 9;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as([3]u8, .{ 0, 0, 0 }), value.?.bytes);
    try std.testing.expectEqual(false, value.?.flag);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
}
