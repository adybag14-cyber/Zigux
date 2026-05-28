const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "zero-length slab owners still keep counters balanced across bytes and arrays" {
    slab.kmalloc_nr_allocated = 0;

    const empty_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const empty_array = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(empty_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR exact-fit subviews keep surrounding sentinels intact" {
    var known = [_]u8{ 0xaa, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xcc };
    const known_rendered = str_error_r.strErrorR(13, known[1..9]);
    try std.testing.expectEqualStrings("Permiss", known_rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), known[0]);
    try std.testing.expectEqual(@as(u8, 0), known[8]);
    try std.testing.expectEqual(@as(u8, 0xcc), known[9]);

    var fallback = [_]u8{ 0x11, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x33 };
    const fallback_rendered = str_error_r.strErrorR(4096, fallback[1..9]);
    try std.testing.expectEqualStrings("INTERNA", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0x11), fallback[0]);
    try std.testing.expectEqual(@as(u8, 0), fallback[8]);
    try std.testing.expectEqual(@as(u8, 0x33), fallback[9]);
}

test "vsprintf can reuse the same interior caller window across direct and padded routes" {
    var buffer = [_]u8{ 0xd0, 0xd1, 0xd2, 0xd3, 0xd4, 0xd5 };
    const view = buffer[1..5];

    const direct_written = vsprintf.scnprintf(view, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 3), direct_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xd0, 'z', 'i', 'g', 0x00, 0xd5 }, &buffer);

    const padded_written = vsprintf.scnprintfPad(view, 3, "{s}", .{"x"});
    try std.testing.expectEqual(@as(usize, 2), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xd0, 'x', ' ', ' ', 0x00, 0xd5 }, &buffer);

    const mirrored_written = vsprintf.vscnprintf(view, "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 2), mirrored_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xd0, 'a', 'b', 0x00, 0x00, 0xd5 }, &buffer);
}

test "zalloc zero-length bytes and scalar owners survive repeated release cycles" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const Owner = struct {
        count: u16,
        enabled: bool,
    };

    var owner: ?*Owner = try zalloc.zallocValue(allocator, Owner);
    try std.testing.expectEqual(@as(u16, 0), owner.?.count);
    try std.testing.expectEqual(false, owner.?.enabled);

    owner.?.count = 9;
    owner.?.enabled = true;
    zalloc.zfreeValue(allocator, Owner, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeValue(allocator, Owner, &owner);
    try std.testing.expect(owner == null);
}
