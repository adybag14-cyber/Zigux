const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab cursor windows keep sentinels through strerror and padded formatting" {
    slab.kmalloc_nr_allocated = 0;

    const storage = slab.kmallocArray(3, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(storage);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memset(storage, 0x7a);
    storage[2] = 0xa2;
    storage[11] = 0xb1;
    storage[19] = 0xc3;

    const err_window = storage[3..12];
    const rendered_err = str_error_r.strErrorR(12, err_window);
    try std.testing.expectEqualStrings("Cannot a", rendered_err);
    try std.testing.expectEqual(@as(u8, 0), err_window[8]);
    try std.testing.expectEqual(@as(u8, 0xa2), storage[2]);

    const fmt_window = storage[12..21];
    const written = vsprintf.scnprintfPad(fmt_window, 6, "x{d}", .{7});
    try std.testing.expectEqual(@as(usize, 5), written);
    try std.testing.expectEqualStrings("x7    ", fmt_window[0..6]);
    try std.testing.expectEqual(@as(u8, 0), fmt_window[6]);
    try std.testing.expectEqual(@as(u8, 0xc3), storage[19]);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zalloc cursor windows reset after fallback strerror and bounded formatting" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 30);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memset(bytes.?, 0x51);
    bytes.?[0] = 0xa0;
    bytes.?[13] = 0xb3;
    bytes.?[24] = 0xc7;

    const fallback_window = bytes.?[1..14];
    const fallback = str_error_r.strErrorR(70001, fallback_window);
    try std.testing.expectEqualStrings("INTERNAL ERR", fallback);
    try std.testing.expectEqual(@as(u8, 0), fallback_window[12]);
    try std.testing.expectEqual(@as(u8, 0xa0), bytes.?[0]);

    const direct_window = bytes.?[14..24];
    const direct_written = vsprintf.scnprintf(direct_window, "{s}:{d}", .{ "lane10", 42 });
    try std.testing.expectEqual(@as(usize, 9), direct_written);
    try std.testing.expectEqualStrings("lane10:42", direct_window[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), direct_window[direct_written]);
    try std.testing.expectEqual(@as(u8, 0xc7), bytes.?[24]);

    const empty_written = vsprintf.vscnprintf(bytes.?[25..25], "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqual(@as(u8, 0x51), bytes.?[25]);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expect(bytes != null);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}
