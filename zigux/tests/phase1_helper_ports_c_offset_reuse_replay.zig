const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectBytes(expected: []const u8, actual: []const u8) !void {
    try std.testing.expectEqualSlices(u8, expected, actual);
}

test "offset helper windows survive failed allocs and owner reuse" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocBytes(16, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var slab_owner = slab.kmallocBytes(24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memset(slab_owner, 0x71);
    const slab_error = str_error_r.strErrorR(22, slab_owner[4..21]);
    try std.testing.expectEqualStrings("Invalid argument", slab_error);
    try expectBytes(&[_]u8{ 0x71, 0x71, 0x71, 0x71 }, slab_owner[0..4]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[20]);
    try expectBytes(&[_]u8{ 0x71, 0x71, 0x71 }, slab_owner[21..24]);

    const slab_written = vsprintf.scnprintfPad(slab_owner[2..11], 7, "s={d}", .{5});
    try std.testing.expectEqual(@as(usize, 7), slab_written);
    try expectBytes(&[_]u8{ 0x71, 0x71 }, slab_owner[0..2]);
    try std.testing.expectEqualStrings("s=5    ", slab_owner[2..9]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[9]);
    try std.testing.expectEqual(@as(u8, 0x71), slab_owner[21]);

    var zero_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 12);
    try std.testing.expect(zero_owner != null);
    for (zero_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const z_written = vsprintf.vscnprintf(zero_owner.?[1..8], "z:{d}", .{17});
    try std.testing.expectEqual(@as(usize, 4), z_written);
    try std.testing.expectEqual(@as(u8, 0), zero_owner.?[0]);
    try std.testing.expectEqualStrings("z:17", zero_owner.?[1..5]);
    try std.testing.expectEqual(@as(u8, 0), zero_owner.?[5]);
    try std.testing.expectEqual(@as(u8, 0), zero_owner.?[8]);

    zalloc.zfreeBytes(allocator, &zero_owner);
    try std.testing.expect(zero_owner == null);
    zalloc.zfreeBytes(allocator, &zero_owner);
    try std.testing.expect(zero_owner == null);

    zero_owner = try zalloc.zallocBytes(allocator, 12);
    defer zalloc.zfreeBytes(allocator, &zero_owner);
    for (zero_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const slab_array = slab.kmallocArray(3, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (slab_array) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    slab.kfree(slab_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "fallback strerror and direct format reuse narrow interior pockets" {
    var backing = [_]u8{
        0xa0, 0xa1, 0xa2, 0xa3,
        0xa4, 0xa5, 0xa6, 0xa7,
        0xa8, 0xa9, 0xaa, 0xab,
        0xac, 0xad, 0xae, 0xaf,
    };

    const fallback = str_error_r.strErrorR(4096, backing[3..12]);
    try std.testing.expectEqualStrings("INTERNAL", fallback);
    try expectBytes(&[_]u8{ 0xa0, 0xa1, 0xa2 }, backing[0..3]);
    try std.testing.expectEqual(@as(u8, 0), backing[11]);
    try expectBytes(&[_]u8{ 0xac, 0xad, 0xae, 0xaf }, backing[12..16]);

    const direct = vsprintf.scnprintf(backing[5..10], "{s}", .{"coretools"});
    try std.testing.expectEqual(@as(usize, 4), direct);
    try std.testing.expectEqualStrings("core", backing[5..9]);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try expectBytes(&[_]u8{ 0xa0, 0xa1, 0xa2 }, backing[0..3]);
    try expectBytes(&[_]u8{ 0xac, 0xad, 0xae, 0xaf }, backing[12..16]);
}
