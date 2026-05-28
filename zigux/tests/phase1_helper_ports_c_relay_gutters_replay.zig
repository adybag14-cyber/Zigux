const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-length arrays and sibling frees keep the allocation counter balanced" {
    slab.kmalloc_nr_allocated = 0;

    const zero = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const sibling = slab.kmallocBytes(3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(sibling);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(zero);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR reuses caller gutters across known and fallback subviews" {
    var known_backing = [_]u8{0xaa} ** 12;
    const known_rendered = str_error_r.strErrorR(2, known_backing[2..9]);
    try std.testing.expectEqualStrings("No suc", known_rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), known_backing[1]);
    try std.testing.expectEqual(@as(u8, 0), known_backing[8]);
    try std.testing.expectEqual(@as(u8, 0xaa), known_backing[9]);

    var fallback_backing = [_]u8{0xbb} ** 13;
    const fallback_rendered = str_error_r.strErrorR(4096, fallback_backing[3..11]);
    try std.testing.expectEqualStrings("INTERNA", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback_backing[2]);
    try std.testing.expectEqual(@as(u8, 0), fallback_backing[10]);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback_backing[11]);
}

test "vsprintf can hand off a padded window to a direct window without leaking past the terminator" {
    var backing = [_]u8{0xcc} ** 10;
    const window = backing[2..8];

    const padded_written = vsprintf.scnprintfPad(window, 5, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', ' ', 0 }, window);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[8]);

    const direct_written = vsprintf.vscnprintf(window, "{s}", .{"k"});
    try std.testing.expectEqual(@as(usize, 1), direct_written);
    try std.testing.expectEqual(@as(u8, 'k'), window[0]);
    try std.testing.expectEqual(@as(u8, 0), window[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[8]);
}

test "zalloc zero-length bytes and fresh value owners stay independent across release" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u8,
        right: u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);

    var first: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u8, 0), first.?.left);
    try std.testing.expectEqual(@as(u8, 0), first.?.right);
    first.?.left = 9;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expect(first != null);

    zalloc.zfreeValue(allocator, Pair, &first);
    try std.testing.expect(first == null);

    var second: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &second);
    try std.testing.expectEqual(@as(u8, 0), second.?.left);
    try std.testing.expectEqual(@as(u8, 0), second.?.right);
}
