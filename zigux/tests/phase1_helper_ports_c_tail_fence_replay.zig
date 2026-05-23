const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps split allocation lifetimes visible" {
    slab.kmalloc_nr_allocated = 0;

    var plain: ?[]u8 = slab.kmallocBytes(3, slab.GFP_KERNEL);
    defer slab.kfree(plain);
    try std.testing.expect(plain != null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memset(plain.?, 0xaa);

    var zeroed: ?[]u8 = slab.kmallocArray(2, 2, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer slab.kfree(zeroed);
    try std.testing.expect(zeroed != null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zeroed.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(plain);
    plain = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(zeroed);
    zeroed = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps caller fences intact around shorter rewrites" {
    var backing = [_]u8{0x7a} ** 14;
    const window = backing[2..12];

    const known = str_error_r.strErrorR(0, window);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 'S', 'u', 'c', 'c', 'e', 's', 's', 0, 0x7a, 0x7a },
        window,
    );

    const unknown = str_error_r.strErrorR(4096, window);
    try std.testing.expectEqualStrings("INTERNAL ", unknown);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[1]);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[12]);
}

test "vsprintf preserves bytes past the logical tail fence" {
    var backing = [_]u8{0x6b} ** 16;
    const window = backing[3..11];

    const written = vsprintf.scnprintfPad(window, 5, "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 'a', 'b', ' ', ' ', ' ', 0, 0x6b, 0x6b },
        window,
    );
    try std.testing.expectEqual(@as(u8, 0x6b), backing[2]);
    try std.testing.expectEqual(@as(u8, 0x6b), backing[11]);
}

test "zalloc frees independent optionals without cross-resetting" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u16,
        right: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &pair);

    try std.testing.expect(bytes != null);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    try std.testing.expectEqual(@as(u16, 0), pair.?.left);
    try std.testing.expectEqual(@as(u16, 0), pair.?.right);

    @memset(bytes.?, 0xcc);
    pair.?.left = 9;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expect(pair != null);
    try std.testing.expectEqual(@as(u16, 9), pair.?.left);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);
    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);
}
