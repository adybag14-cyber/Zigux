const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "split slab and zalloc owners keep helper writes bounded" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var slab_owner: ?[]u8 = slab.kmallocArray(6, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer {
        slab.kfree(slab_owner);
        slab_owner = null;
    }

    var zalloc_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &zalloc_owner);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    for (zalloc_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const message = str_error_r.strErrorR(22, zalloc_owner.?[3..15]);
    try std.testing.expectEqualStrings("Invalid arg", message);
    try std.testing.expectEqual(@as(u8, 0), zalloc_owner.?[14]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, zalloc_owner.?[0..3]);

    const written = vsprintf.scnprintf(slab_owner.?[2..18], "err:{s}:{d}", .{ message, slab.kmalloc_nr_allocated });
    try std.testing.expectEqual(@as(usize, 15), written);
    try std.testing.expectEqualStrings("err:Invalid arg", slab_owner.?[2 .. 2 + written]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner.?[2 + written]);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &zalloc_owner);
    zalloc.zfreeBytes(allocator, &zalloc_owner);
    try std.testing.expect(zalloc_owner == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "failed slab paths do not disturb reused zalloc formatter windows" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 9);
    defer zalloc.zfreeBytes(allocator, &owner);

    try std.testing.expect(slab.kmallocBytes(8, slab.__GFP_ZERO) == null);
    try std.testing.expect(slab.kmallocArray(3, 4, slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const padded = vsprintf.scnprintfPad(owner.?, 6, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 5), padded);
    try std.testing.expectEqualStrings("xy    ", owner.?[0..6]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[6]);

    const fallback = str_error_r.strErrorR(4096, owner.?[1..4]);
    try std.testing.expectEqualStrings("IN", fallback);
    try std.testing.expectEqual(@as(u8, 'x'), owner.?[0]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[3]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[6]);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &owner);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
}
