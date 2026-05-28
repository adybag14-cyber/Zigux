const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 slab turnstile keeps counters balanced across interleaved owners" {
    slab.kmalloc_nr_allocated = 0;

    var left: ?[]u8 = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(left);
    const right: ?[]u8 = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(right);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (right.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    left.?[0] = 0x11;
    left.?[1] = 0x22;
    try std.testing.expectEqual(@as(u8, 0x11), left.?[0]);
    try std.testing.expectEqual(@as(u8, 0x22), left.?[1]);

    slab.kfree(left);
    left = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(2, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var tail: ?[]u8 = slab.kmallocBytes(1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(tail);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(tail);
    tail = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "lane10 strErrorR turnstile preserves gutters around caller subviews" {
    var known = [_]u8{0xaa} ** 12;
    const known_view = known[2..10];
    const known_rendered = str_error_r.strErrorR(13, known_view);
    try std.testing.expectEqualStrings("Permiss", known_rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), known[1]);
    try std.testing.expectEqual(@as(u8, 0), known[9]);
    try std.testing.expectEqual(@as(u8, 0xaa), known[10]);

    var fallback = [_]u8{0xbb} ** 11;
    const fallback_view = fallback[1..9];
    const fallback_rendered = str_error_r.strErrorR(4096, fallback_view);
    try std.testing.expectEqualStrings("INTERNA", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback[0]);
    try std.testing.expectEqual(@as(u8, 0), fallback[8]);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback[9]);
}

test "lane10 vsprintf turnstile keeps mirrored gutters and zero-logical reset" {
    var direct = [_]u8{0xaa} ** 8;
    var alias = [_]u8{0xbb} ** 8;

    const direct_view = direct[1..6];
    const alias_view = alias[2..7];
    const direct_written = vsprintf.scnprintf(direct_view, "{s}", .{"turnstile"});
    const alias_written = vsprintf.vscnprintf(alias_view, "{s}", .{"turnstile"});

    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqual(direct_written, alias_written);
    try std.testing.expectEqualStrings("turn", direct_view[0..direct_written]);
    try std.testing.expectEqualStrings(direct_view[0..direct_written], alias_view[0..alias_written]);
    try std.testing.expectEqual(@as(u8, 0), direct_view[direct_written]);
    try std.testing.expectEqual(@as(u8, 0), alias_view[alias_written]);
    try std.testing.expectEqual(@as(u8, 0xaa), direct[0]);
    try std.testing.expectEqual(@as(u8, 0xaa), direct[6]);
    try std.testing.expectEqual(@as(u8, 0xbb), alias[1]);
    try std.testing.expectEqual(@as(u8, 0xbb), alias[7]);

    var padded = [_]u8{0xcc} ** 6;
    const padded_view = padded[1..5];
    const padded_written = vsprintf.scnprintfPad(padded_view, 0, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), padded_written);
    try std.testing.expectEqual(@as(u8, 0xcc), padded[0]);
    try std.testing.expectEqual(@as(u8, 0), padded[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), padded[2]);
    try std.testing.expectEqual(@as(u8, 0xcc), padded[5]);
}

test "lane10 zalloc turnstile releases one owner without disturbing the others" {
    const allocator = std.testing.allocator;
    const Value = struct {
        a: u16,
        b: bool,
    };

    var left_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &left_bytes);
    var right_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &right_bytes);
    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    for (left_bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }
    for (right_bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }
    try std.testing.expectEqual(@as(u16, 0), value.?.a);
    try std.testing.expectEqual(false, value.?.b);

    zalloc.zfreeBytes(allocator, &left_bytes);
    try std.testing.expect(left_bytes == null);
    try std.testing.expect(right_bytes != null);
    try std.testing.expectEqual(@as(u8, 0), right_bytes.?[0]);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    try std.testing.expect(right_bytes != null);

    zalloc.zfreeBytes(allocator, &right_bytes);
    try std.testing.expect(right_bytes == null);
}
