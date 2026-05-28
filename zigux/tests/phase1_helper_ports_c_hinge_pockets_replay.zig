const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 slab hinge pockets keep fail paths and sibling counters isolated" {
    slab.kmalloc_nr_allocated = 0;

    const left = slab.kmallocArray(2, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(left);
    var right: ?[]u8 = slab.kmallocBytes(3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(right);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (left) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    try std.testing.expect(slab.kmallocArray(3, 3, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(right);
    right = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), left[0]);
}

test "lane10 strErrorR hinge pockets respect exact-fit and fallback caller views" {
    var known = [_]u8{0xaa} ** 21;
    const known_view = known[3..21];
    const known_rendered = str_error_r.strErrorR(13, known_view);
    try std.testing.expectEqualStrings("Permission denied", known_rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), known[2]);
    try std.testing.expectEqual(@as(u8, 0), known[20]);

    var fallback = [_]u8{0xbb} ** 14;
    const fallback_view = fallback[2..11];
    const fallback_rendered = str_error_r.strErrorR(9999, fallback_view);
    try std.testing.expectEqualStrings("INTERNAL", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback[1]);
    try std.testing.expectEqual(@as(u8, 0), fallback[10]);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback[11]);
}

test "lane10 vsprintf hinge pockets clamp logical width inside interior windows" {
    var padded = [_]u8{0xcc} ** 9;
    const padded_view = padded[2..8];
    const padded_written = vsprintf.scnprintfPad(padded_view, 5, "{s}", .{"zig"});
    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqualStrings("zig  ", padded_view[0..5]);
    try std.testing.expectEqual(@as(u8, 0), padded_view[5]);
    try std.testing.expectEqual(@as(u8, 0xcc), padded[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), padded[8]);

    var direct = [_]u8{0xdd} ** 7;
    const direct_view = direct[1..5];
    const direct_written = vsprintf.scnprintf(direct_view, "{s}", .{"hinge"});
    try std.testing.expectEqual(@as(usize, 3), direct_written);
    try std.testing.expectEqualStrings("hin", direct_view[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), direct_view[direct_written]);
}

test "lane10 zalloc hinge pockets keep zero-length and value owners independent" {
    const allocator = std.testing.allocator;
    const Value = struct {
        a: u8,
        b: u16,
    };

    var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &zero_bytes);
    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    try std.testing.expectEqual(@as(usize, 0), zero_bytes.?.len);
    for (bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }
    try std.testing.expectEqual(@as(u8, 0), value.?.a);
    try std.testing.expectEqual(@as(u16, 0), value.?.b);

    zalloc.zfreeBytes(allocator, &zero_bytes);
    try std.testing.expect(zero_bytes == null);
    try std.testing.expect(bytes != null);
    try std.testing.expect(value != null);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    try std.testing.expect(bytes != null);
}
