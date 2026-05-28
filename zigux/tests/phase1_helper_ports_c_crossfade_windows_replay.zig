const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps sibling allocation accounting isolated across frees" {
    slab.kmalloc_nr_allocated = 0;

    var first: ?[]u8 = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(first);
    var second: ?[]u8 = slab.kmallocArray(3, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(second);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (first.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(first);
    first = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memset(second.?, 0x5a);
    try std.testing.expectEqual(@as(u8, 0x5a), second.?[0]);

    slab.kfree(second);
    second = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR stays inside caller subviews and preserves neighboring sentinels" {
    var backing = [_]u8{0xa1} ** 18;

    const known = str_error_r.strErrorR(13, backing[2..8]);
    try std.testing.expectEqualStrings("Permi", known);
    try std.testing.expectEqual(@as(u8, 0xa1), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);
    try std.testing.expectEqual(@as(u8, 0xa1), backing[8]);

    const fallback = str_error_r.strErrorR(4096, backing[10..16]);
    try std.testing.expectEqualStrings("INTER", fallback);
    try std.testing.expectEqual(@as(u8, 0xa1), backing[9]);
    try std.testing.expectEqual(@as(u8, 0), backing[15]);
    try std.testing.expectEqual(@as(u8, 0xa1), backing[16]);
}

test "vsprintf keeps disjoint caller windows fenced and terminated" {
    var backing = [_]u8{0xc3} ** 16;

    const padded = vsprintf.scnprintfPad(backing[1..8], 6, "{s}", .{"zx"});
    try std.testing.expectEqual(@as(usize, 5), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'x', ' ', ' ', ' ', ' ', 0 }, backing[1..8]);
    try std.testing.expectEqual(@as(u8, 0xc3), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xc3), backing[8]);

    const direct = vsprintf.vscnprintf(backing[9..14], "{s}", .{"shift"});
    try std.testing.expectEqual(@as(usize, 4), direct);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 's', 'h', 'i', 'f', 0 }, backing[9..14]);
    try std.testing.expectEqual(@as(u8, 0xc3), backing[8]);
    try std.testing.expectEqual(@as(u8, 0xc3), backing[14]);
}

test "zalloc releases one owner without disturbing the other and re-zeroes fresh bytes" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u16,
        right: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expectEqual(@as(u16, 0), pair.?.left);
    try std.testing.expectEqual(@as(u16, 0), pair.?.right);

    bytes.?[0] = 0x44;
    pair.?.left = 9;
    pair.?.right = 12;

    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);
    try std.testing.expectEqual(@as(u8, 0x44), bytes.?[0]);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var fresh: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &fresh);
    for (fresh.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}
