const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "helper ports C keep zero-length and ring windows isolated" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const zero = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var ring = [_]u8{
        0xa0, 0xa1, 0xa2, 0xa3,
        0xa4, 0xa5, 0xa6, 0xa7,
        0xa8, 0xa9, 0xaa, 0xab,
    };

    const err = str_error_r.strErrorR(12, ring[1..9]);
    try std.testing.expectEqualStrings("Cannot ", err);
    try std.testing.expectEqualSlices(u8, &[_]u8{0xa0}, ring[0..1]);
    try std.testing.expectEqual(@as(u8, 0), ring[8]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa9, 0xaa, 0xab }, ring[9..12]);

    const written = vsprintf.scnprintf(ring[4..10], "{s}", .{"ring"});
    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualSlices(u8, "ring", ring[4..8]);
    try std.testing.expectEqual(@as(u8, 0), ring[8]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa0, 'C', 'a', 'n' }, ring[0..4]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa9, 0xaa, 0xab }, ring[9..12]);

    var owned: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(owned != null);
    try std.testing.expectEqual(@as(usize, 0), owned.?.len);
    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);
    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);
}

test "helper ports C preserve neighboring owners through padded rewrites" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kmallocArray(2, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var owned: ?[]u8 = try zalloc.zallocBytes(allocator, 8);
    defer zalloc.zfreeBytes(allocator, &owned);
    for (owned.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var backing = [_]u8{
        0xb0, 0xb1, 0xb2, 0xb3,
        0xb4, 0xb5, 0xb6, 0xb7,
        0xb8, 0xb9, 0xba, 0xbb,
    };

    const padded = vsprintf.scnprintfPad(backing[2..9], 5, "{s}", .{"io"});
    try std.testing.expect(padded == 4 or padded == 5);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xb0, 0xb1 }, backing[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'o', ' ', ' ', ' ', 0 }, backing[2..8]);
    try std.testing.expectEqual(@as(u8, 0xb8), backing[8]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xb9, 0xba, 0xbb }, backing[9..12]);

    const fallback = str_error_r.strErrorR(4096, backing[4..11]);
    try std.testing.expectEqualStrings("INTERN", fallback);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xb0, 0xb1, 'i', 'o' }, backing[0..4]);
    try std.testing.expectEqual(@as(u8, 0), backing[10]);
    try std.testing.expectEqual(@as(u8, 0xbb), backing[11]);

    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
