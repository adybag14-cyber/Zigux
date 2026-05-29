const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "tiny caller views preserve terminators and allocation counters" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;

    var zalloc_one: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &zalloc_one);
    try std.testing.expectEqual(@as(usize, 1), zalloc_one.?.len);
    try std.testing.expectEqual(@as(u8, 0), zalloc_one.?[0]);

    const strerror_len = str_error_r.strErrorR(13, zalloc_one.?);
    try std.testing.expectEqual(@as(usize, 0), strerror_len.len);
    try std.testing.expectEqual(@as(u8, 0), zalloc_one.?[0]);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const slab_one = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_one);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), slab_one[0]);

    slab_one[0] = 0xaa;
    const written = vsprintf.scnprintf(slab_one, "err={d}", .{22});
    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqual(@as(u8, 0), slab_one[0]);

    zalloc.zfreeBytes(allocator, &zalloc_one);
    zalloc.zfreeBytes(allocator, &zalloc_one);
    try std.testing.expect(zalloc_one == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zero length zalloc and non reclaim slab failures stay reusable" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;

    var empty_zalloc: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &empty_zalloc);
    try std.testing.expect(empty_zalloc != null);
    try std.testing.expectEqual(@as(usize, 0), empty_zalloc.?.len);

    const strerror_empty = str_error_r.strErrorR(4096, empty_zalloc.?);
    try std.testing.expectEqual(@as(usize, 0), strerror_empty.len);

    var backing = [_]u8{0xbb};
    const empty_written = vsprintf.scnprintf(backing[0..0], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqual(@as(u8, 0xbb), backing[0]);

    try std.testing.expect(slab.kmallocBytes(8, slab.__GFP_IO | slab.__GFP_FS) == null);
    try std.testing.expect(slab.kmallocArray(2, 4, slab.__GFP_IO | slab.__GFP_FS) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &empty_zalloc);
    try std.testing.expect(empty_zalloc == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
