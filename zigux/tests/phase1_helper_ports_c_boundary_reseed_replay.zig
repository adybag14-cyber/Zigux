const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab reseeds zeroed storage after a reclaimed dirty allocation" {
    slab.kmalloc_nr_allocated = 0;

    const dirty = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse
        return error.TestUnexpectedResult;
    @memset(dirty, 0xa1);
    slab.kfree(dirty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocArray(2, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, zeroed);

    const tail = slab.kmallocBytes(1, slab.GFP_KERNEL) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(tail);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
}

test "strErrorR reseeds the same caller window from known to fallback and back" {
    var backing = [_]u8{0x6d} ** 20;

    const known = str_error_r.strErrorR(13, backing[4..15]);
    try std.testing.expectEqualStrings("Permission", known);
    try std.testing.expectEqual(@as(u8, 0), backing[14]);
    try std.testing.expectEqual(@as(u8, 0x6d), backing[3]);
    try std.testing.expectEqual(@as(u8, 0x6d), backing[15]);

    const fallback = str_error_r.strErrorR(4096, backing[4..9]);
    try std.testing.expectEqualStrings("INTE", fallback);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, 's'), backing[9]);

    const rebound = str_error_r.strErrorR(0, backing[4..12]);
    try std.testing.expectEqualStrings("Success", rebound);
    try std.testing.expectEqual(@as(u8, 0), backing[11]);
    try std.testing.expectEqual(@as(u8, 'o'), backing[12]);
}

test "vsprintf reseeds one caller slice without touching the outer fence" {
    var backing = [_]u8{0x4c} ** 14;
    const view = backing[2..10];

    const first_written = vsprintf.scnprintf(view, "{s}:{d}", .{ "host", 7 });
    try std.testing.expectEqual(@as(usize, 6), first_written);
    try std.testing.expectEqualStrings("host:7", view[0..first_written]);
    try std.testing.expectEqual(@as(u8, 0), view[first_written]);
    try std.testing.expectEqual(@as(u8, 0x4c), backing[1]);
    try std.testing.expectEqual(@as(u8, 0x4c), backing[10]);

    const second_written = vsprintf.scnprintf(view, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 2), second_written);
    try std.testing.expectEqualStrings("ok", view[0..second_written]);
    try std.testing.expectEqual(@as(u8, 0), view[second_written]);
    try std.testing.expectEqual(@as(u8, 't'), view[3]);
    try std.testing.expectEqual(@as(u8, 0x4c), backing[10]);
}

test "zalloc reseeds bytes and values independently after staggered frees" {
    const allocator = std.testing.allocator;
    const Pair = extern struct {
        left: u16,
        right: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeBytes(allocator, &bytes);
    defer zalloc.zfreeValue(allocator, Pair, &value);

    @memset(bytes.?, 0x44);
    value.?.left = 7;
    value.?.right = 9;

    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x44, 0x44, 0x44, 0x44 }, bytes.?);

    value = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), value.?.left);
    try std.testing.expectEqual(@as(u16, 0), value.?.right);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);
    try std.testing.expectEqual(@as(u16, 0), value.?.left);
    try std.testing.expectEqual(@as(u16, 0), value.?.right);
}
