const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab reclaim-gated retries preserve live sentinels and counter state" {
    slab.kmalloc_nr_allocated = 0;

    const live = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(live);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memcpy(live, &[_]u8{ 0x91, 0x92, 0x93, 0x94, 0x95, 0x96 });

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x91, 0x92, 0x93, 0x94, 0x95, 0x96 }, live);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, zeroed);
}

test "strErrorR respects single-byte and neighboring sentinel fences across retries" {
    var backing = [_]u8{0x6d} ** 20;

    const fallback = str_error_r.strErrorR(4096, backing[1..9]);
    try std.testing.expectEqualStrings("INTERNA", fallback);
    try std.testing.expectEqual(@as(u8, 0x6d), backing[0]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);

    const tiny = str_error_r.strErrorR(13, backing[9..10]);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try std.testing.expectEqual(@as(u8, 0x6d), backing[10]);

    const exact = str_error_r.strErrorR(0, backing[11..19]);
    try std.testing.expectEqualStrings("Success", exact);
    try std.testing.expectEqual(@as(u8, 0x6d), backing[10]);
    try std.testing.expectEqual(@as(u8, 0), backing[18]);
    try std.testing.expectEqual(@as(u8, 0x6d), backing[19]);
}

test "vsprintf retries keep one-byte and reused caller windows inside their sentinels" {
    var backing = [_]u8{0x44} ** 16;

    const tiny = backing[2..3];
    const tiny_written = vsprintf.scnprintf(tiny, "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 0), tiny_written);
    try std.testing.expectEqual(@as(u8, 0x44), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[2]);
    try std.testing.expectEqual(@as(u8, 0x44), backing[3]);

    const window = backing[4..9];
    const first_written = vsprintf.vscnprintf(window, "{s}", .{"tool"});
    try std.testing.expectEqual(@as(usize, 4), first_written);
    try std.testing.expectEqualStrings("tool", window[0..first_written]);
    try std.testing.expectEqual(@as(u8, 0), window[first_written]);
    try std.testing.expectEqual(@as(u8, 0x44), backing[9]);

    const second_written = vsprintf.scnprintf(window, "{s}:{d}", .{ "x", 3 });
    try std.testing.expectEqual(@as(usize, 3), second_written);
    try std.testing.expectEqualStrings("x:3", window[0..second_written]);
    try std.testing.expectEqual(@as(u8, 0), window[second_written]);
    try std.testing.expectEqual(@as(u8, 0x44), backing[3]);
    try std.testing.expectEqual(@as(u8, 0x44), backing[9]);
}

test "zalloc frees can cross without breaking live sentinel state" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u8,
        right: u8,
    };

    var bytes: ?[]u8 = null;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes);
    @memcpy(bytes.?, &[_]u8{ 0xa1, 0xa2, 0xa3 });

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &pair);
    pair.?.left = 7;
    pair.?.right = 9;

    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa1, 0xa2, 0xa3 }, bytes.?);

    pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u8, 0), pair.?.left);
    try std.testing.expectEqual(@as(u8, 0), pair.?.right);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u8, 0), pair.?.left);
    try std.testing.expectEqual(@as(u8, 0), pair.?.right);
}
