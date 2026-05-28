const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab allocations keep sibling ownership and counts through staggered release" {
    slab.kmalloc_nr_allocated = 0;

    var first: ?[]u8 = slab.kmallocBytes(6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(first);
    var second: ?[]u8 = slab.kmallocArray(3, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(second);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expect(@intFromPtr(first.?.ptr) != @intFromPtr(second.?.ptr));
    for (first.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memset(second.?, 0x5a);
    slab.kfree(first);
    first = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x5a, 0x5a, 0x5a, 0x5a, 0x5a, 0x5a }, second.?);

    slab.kfree(second);
    second = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR respects caller subviews and keeps neighboring sentinels untouched" {
    var backing = [_]u8{0xaa} ** 40;
    const known_view = backing[3..11];
    const known_rendered = str_error_r.strErrorR(13, known_view);
    try std.testing.expectEqualStrings("Permiss", known_rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[2]);
    try std.testing.expectEqual(@as(u8, 0), backing[10]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[11]);

    var fallback_backing = [_]u8{0xbb} ** 24;
    const fallback_view = fallback_backing[5..14];
    const fallback_rendered = str_error_r.strErrorR(4096, fallback_view);
    try std.testing.expectEqualStrings("INTERNAL", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback_backing[4]);
    try std.testing.expectEqual(@as(u8, 0), fallback_backing[13]);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback_backing[14]);
}

test "vsprintf keeps writes inside staggered caller windows" {
    var padded = [_]u8{0xcc} ** 16;
    const padded_written = vsprintf.scnprintfPad(padded[2..10], 6, "{s}", .{"zig"});
    try std.testing.expectEqual(@as(usize, 5), padded_written);
    try std.testing.expectEqual(@as(u8, 0xcc), padded[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), padded[10]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', ' ', ' ', ' ', 0, 0xcc }, padded[2..10]);

    var direct = [_]u8{0xdd} ** 12;
    const direct_written = vsprintf.vscnprintf(direct[4..9], "{s}", .{"widen"});
    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqual(@as(u8, 0xdd), direct[3]);
    try std.testing.expectEqual(@as(u8, 0), direct[8]);
    try std.testing.expectEqual(@as(u8, 0xdd), direct[9]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'w', 'i', 'd', 'e', 0 }, direct[4..9]);
}

test "zalloc re-zeroes fresh owners after earlier writes and releases" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0x7f);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var second: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &second);
    for (second.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const Value = struct {
        lane: u8,
        armed: bool,
    };

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u8, 0), value.?.lane);
    try std.testing.expectEqual(false, value.?.armed);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
