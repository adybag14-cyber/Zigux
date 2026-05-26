const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab sibling allocations keep zeroed rebound windows isolated" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    first[0] = 0x11;
    first[1] = 0x22;
    first[2] = 0x33;
    first[3] = 0x44;
    first[4] = 0x55;

    const second = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (second) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x11, 0x22, 0x33, 0x44, 0x55 }, first);
}

test "strErrorR reuses offset windows without clobbering neighboring bytes" {
    var backing = [_]u8{0xaa} ** 16;

    const first = str_error_r.strErrorR(13, backing[0..6]);
    try std.testing.expectEqualStrings("Permi", first);
    try std.testing.expectEqual(@as(u8, 0), backing[5]);

    const second = str_error_r.strErrorR(0, backing[2..10]);
    try std.testing.expectEqualStrings("Success", second);
    try std.testing.expectEqualSlices(u8, "Pe", backing[0..2]);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
}

test "vsprintf caller windows can rebound from padded to direct writes on one slice" {
    var backing = [_]u8{0xcc} ** 12;
    const window = backing[1..10];

    _ = vsprintf.scnprintfPad(window, 6, "{s}", .{"xy"});
    const direct_written = vsprintf.scnprintf(window, "{s}:{d}", .{ "q", 7 });

    try std.testing.expectEqual(@as(usize, 3), direct_written);
    try std.testing.expectEqualStrings("q:7", window[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), window[direct_written]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[10]);
}

test "zalloc optionals rebound to fresh zeroed state after free" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u16,
        right: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0x5a);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), pair.?.left);
    try std.testing.expectEqual(@as(u16, 0), pair.?.right);
    pair.?.left = 9;
    pair.?.right = 12;
    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);

    pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expectEqual(@as(u16, 0), pair.?.left);
    try std.testing.expectEqual(@as(u16, 0), pair.?.right);
}
