const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-length allocations still balance nullable frees" {
    slab.kmalloc_nr_allocated = 0;

    const nothing: ?[]u8 = null;
    slab.kfree(nothing);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR truncates tiny windows and leaves empty views untouched" {
    var tiny = [_]u8{0xaa} ** 5;
    const tiny_rendered = str_error_r.strErrorR(13, &tiny);
    try std.testing.expectEqualStrings("Perm", tiny_rendered);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'P', 'e', 'r', 'm', 0 }, &tiny);

    var untouched = [_]u8{0xbb};
    const empty_rendered = str_error_r.strErrorR(0, untouched[0..0]);
    try std.testing.expectEqual(@as(usize, 0), empty_rendered.len);
    try std.testing.expectEqual(@as(u8, 0xbb), untouched[0]);
}

test "vsprintf rewrites shorter text and clamps pad windows" {
    var rewrite = [_]u8{0xcc} ** 7;
    _ = vsprintf.scnprintf(&rewrite, "{s}", .{"abcdef"});
    const shorter = vsprintf.vscnprintf(&rewrite, "{s}", .{"xy"});

    try std.testing.expectEqual(@as(usize, 2), shorter);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', 0, 'd' }, rewrite[0..4]);

    var padded = [_]u8{0xdd} ** 6;
    const padded_written = vsprintf.scnprintfPad(&padded, 3, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 0, 0xdd, 0xdd }, &padded);
}

test "zalloc keeps zeroed state and reset helpers idempotent" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u16,
        right: bool,
        bytes: [2]u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), value.?.left);
    try std.testing.expectEqual(false, value.?.right);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, &value.?.bytes);
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);
}
