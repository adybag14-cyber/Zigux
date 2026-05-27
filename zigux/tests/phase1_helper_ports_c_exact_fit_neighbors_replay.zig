const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab mixed exact-fit allocations keep accounting stable across null-safe frees" {
    slab.kmalloc_nr_allocated = 0;

    const zeroed = slab.kmallocArray(3, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(usize, 6), zeroed.len);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const plain = slab.kmallocBytes(1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR exact-fit subviews preserve neighboring bytes" {
    var known_backing = [_]u8{0xaa} ** 16;
    const known_view = known_backing[4..12];
    const known_rendered = str_error_r.strErrorR(0, known_view);
    try std.testing.expectEqualStrings("Success", known_rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), known_backing[3]);
    try std.testing.expectEqual(@as(u8, 0xaa), known_backing[12]);
    try std.testing.expectEqual(@as(u8, 0), known_backing[11]);

    var fallback_backing = [_]u8{0xbb} ** 12;
    const fallback_view = fallback_backing[2..10];
    const fallback_rendered = str_error_r.strErrorR(4096, fallback_view);
    try std.testing.expectEqualStrings("INTERNA", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback_backing[1]);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback_backing[10]);
    try std.testing.expectEqual(@as(u8, 0), fallback_backing[9]);
}

test "vsprintf logical-size padding respects exact-fit windows and spare tails" {
    var direct_backing = [_]u8{0xcc} ** 12;
    const direct_view = direct_backing[2..9];
    const direct_written = vsprintf.scnprintf(direct_view, "{s}", .{"zigux!"});
    try std.testing.expectEqual(@as(usize, 6), direct_written);
    try std.testing.expectEqualStrings("zigux!", direct_view[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), direct_view[6]);
    try std.testing.expectEqual(@as(u8, 0xcc), direct_backing[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), direct_backing[9]);

    var padded_backing = [_]u8{0xdd} ** 12;
    const padded_view = padded_backing[3..10];
    const padded_written = vsprintf.scnprintfPad(padded_view, 5, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', ' ', 0, 0xdd }, padded_view);
    try std.testing.expectEqual(@as(u8, 0xdd), padded_backing[2]);
    try std.testing.expectEqual(@as(u8, 0xdd), padded_backing[10]);
}

test "zalloc byte reallocation re-zeroes without disturbing a live value" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u32,
        ready: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    bytes.?[0] = 0xaa;
    bytes.?[1] = 0xbb;
    bytes.?[2] = 0xcc;
    value.?.count = 7;
    value.?.ready = true;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u32, 7), value.?.count);
    try std.testing.expectEqual(true, value.?.ready);

    bytes = try zalloc.zallocBytes(allocator, 3);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    zalloc.zfreeBytes(allocator, &bytes);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
}
