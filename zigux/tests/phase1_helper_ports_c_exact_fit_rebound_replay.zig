const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps allocation counts balanced across exact-fit array and byte rebounds" {
    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocArray(2, 3, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 6), zeroed.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const single = slab.kmallocBytes(1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    single[0] = 0x5a;

    slab.kfree(single);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR exact-fit catalog rewrites rebound cleanly on reused caller buffers" {
    var backing = [_]u8{0xaa} ** 8;

    const success = str_error_r.strErrorR(0, backing[0..]);
    try std.testing.expectEqualStrings("Success", success);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);

    const tiny = str_error_r.strErrorR(13, backing[0..5]);
    try std.testing.expectEqualStrings("Perm", tiny);
    try std.testing.expectEqual(@as(u8, 0), backing[4]);
    try std.testing.expectEqual(@as(u8, 's'), backing[5]);
}

test "vsprintf exact-fit padded views can rebound into direct rewrites on shared backing" {
    var backing = [_]u8{0xaa} ** 8;

    const padded_written = vsprintf.scnprintfPad(backing[1..], 4, "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[0]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', ' ', ' ', 0 }, backing[1..6]);

    const direct_written = vsprintf.vscnprintf(backing[1..], "{s}:{d}", .{ "z", 9 });
    try std.testing.expectEqual(@as(usize, 3), direct_written);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[0]);
    try std.testing.expectEqualStrings("z:9", backing[1 .. 1 + direct_written]);
    try std.testing.expectEqual(@as(u8, 0), backing[1 + direct_written]);
}

test "zalloc rebound cleanup stays null-safe across bytes and value reallocation" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    bytes.?[0] = 0x44;
    bytes.?[1] = 0x55;
    bytes.?[2] = 0x66;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const ZeroValue = struct {
        count: u16,
        enabled: bool,
    };

    var value: ?*ZeroValue = try zalloc.zallocValue(allocator, ZeroValue);
    defer zalloc.zfreeValue(allocator, ZeroValue, &value);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.enabled);

    zalloc.zfreeValue(allocator, ZeroValue, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, ZeroValue, &value);
    try std.testing.expect(value == null);
}
