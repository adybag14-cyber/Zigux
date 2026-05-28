const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab reuse boundaries balance accounting after mixed releases" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const second = slab.kmallocArray(3, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    for (first) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    @memset(second, 0x5a);

    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const third = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(third);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), third[0]);

    slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR rewrites only the supplied reuse window" {
    var backing = [_]u8{0x31} ** 24;
    const window = backing[4..16];

    const denied = str_error_r.strErrorR(13, window);
    try std.testing.expectEqualStrings("Permission ", denied);
    try std.testing.expectEqual(@as(u8, 0), backing[15]);
    try std.testing.expectEqual(@as(u8, 0x31), backing[3]);
    try std.testing.expectEqual(@as(u8, 0x31), backing[16]);

    const invalid = str_error_r.strErrorR(22, backing[7..11]);
    try std.testing.expectEqualStrings("Inv", invalid);
    try std.testing.expectEqual(@as(u8, 0), backing[10]);
    try std.testing.expectEqual(@as(u8, 'P'), backing[4]);
    try std.testing.expectEqual(@as(u8, 0), backing[15]);
}

test "vsprintf reused views update terminators without leaking past bounds" {
    var backing = [_]u8{0x44} ** 14;

    const first = vsprintf.scnprintf(backing[2..9], "{s}-{d}", .{ "aa", 17 });
    try std.testing.expectEqual(@as(usize, 5), first);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'a', '-', '1', '7', 0, 0x44 }, backing[2..9]);

    const second = vsprintf.scnprintfPad(backing[4..10], 5, "{s}", .{"z"});
    try std.testing.expectEqual(@as(usize, 4), second);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', ' ', ' ', ' ', ' ', 0 }, backing[4..10]);
    try std.testing.expectEqual(@as(u8, 'a'), backing[2]);
    try std.testing.expectEqual(@as(u8, 'a'), backing[3]);
    try std.testing.expectEqual(@as(u8, 0x44), backing[10]);
}

test "zalloc reuse boundaries reset optional owners independently" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u16,
        right: [3]u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    bytes.?[2] = 0xa5;

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), pair.?.left);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &pair.?.right);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expect(pair != null);

    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);
    zalloc.zfreeBytes(allocator, &bytes);
    zalloc.zfreeValue(allocator, Pair, &pair);
}
