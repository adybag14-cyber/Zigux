const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 owner edge replay keeps borrowed views independent of owned buffers" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner != null);

    const owned = owner.?;
    for (owned) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const slab_buf = slab.kmallocBytes(24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_buf);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const rendered = vsprintf.scnprintf(slab_buf[2..17], "edge:{d}:{s}", .{ 7, "ok" });
    try std.testing.expectEqual(@as(usize, 9), rendered);
    try std.testing.expectEqualStrings("edge:7:ok", slab_buf[2 .. 2 + rendered]);
    try std.testing.expectEqual(@as(u8, 0), slab_buf[2 + rendered]);

    const copied = str_error_r.strErrorR(13, owned[4..15]);
    try std.testing.expectEqualStrings("Permission", copied);
    try std.testing.expectEqual(@as(u8, 0), owned[14]);

    try std.testing.expectEqualStrings("edge:7:ok", slab_buf[2 .. 2 + rendered]);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "lane10 owner edge replay bounds failed slab allocation beside zalloc owner" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 7);
    defer zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner != null);

    const rejected = slab.kmallocArray(3, 3, slab.__GFP_KSWAPD_RECLAIM | slab.__GFP_ZERO);
    try std.testing.expect(rejected == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const owned = owner.?;
    const written = vsprintf.scnprintfPad(owned, owned.len, "{s}", .{"io"});
    try std.testing.expectEqual(@as(usize, 5), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'o', ' ', ' ', ' ', ' ', 0 }, owned);

    var tiny = [_]u8{ 0xaa, 0xaa, 0xaa };
    const fallback = str_error_r.strErrorR(4096, &tiny);
    try std.testing.expectEqualStrings("IN", fallback);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'I', 'N', 0 }, &tiny);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
