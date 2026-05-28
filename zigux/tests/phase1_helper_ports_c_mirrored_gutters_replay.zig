const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 slab mirrored zeroed array and sibling plain allocation keep counters balanced" {
    slab.kmalloc_nr_allocated = 0;

    const plain = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocArray(3, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 6), zeroed.len);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 6), zeroed.len);
    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 strErrorR mirrored gutters keep writes inside exact-fit and fallback subviews" {
    var backing = [_]u8{'~'} ** 40;

    const known = str_error_r.strErrorR(0, backing[4..12]);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, '~'), backing[3]);
    try std.testing.expectEqual(@as(u8, 0), backing[11]);
    try std.testing.expectEqual(@as(u8, '~'), backing[12]);

    const fallback = str_error_r.strErrorR(4096, backing[20..29]);
    try std.testing.expectEqualStrings("INTERNAL", fallback);
    try std.testing.expectEqual(@as(u8, '~'), backing[19]);
    try std.testing.expectEqual(@as(u8, 0), backing[28]);
    try std.testing.expectEqual(@as(u8, '~'), backing[29]);
}

test "lane10 vsprintf mirrored gutters preserve exterior sentinels across padded and direct views" {
    var backing = [_]u8{'?'} ** 18;

    const padded_written = vsprintf.scnprintfPad(backing[2..9], 6, "{s}", .{"zig"});
    const direct_written = vsprintf.vscnprintf(backing[11..16], "{s}", .{"ports"});

    try std.testing.expectEqual(@as(usize, 5), padded_written);
    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqualSlices(u8, "zig   ", backing[2..8]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqualSlices(u8, "port", backing[11..15]);
    try std.testing.expectEqual(@as(u8, 0), backing[15]);
    try std.testing.expectEqual(@as(u8, '?'), backing[1]);
    try std.testing.expectEqual(@as(u8, '?'), backing[9]);
    try std.testing.expectEqual(@as(u8, '?'), backing[10]);
    try std.testing.expectEqual(@as(u8, '?'), backing[16]);
}

test "lane10 zalloc mirrored gutters keep zero-length bytes and values independently releasable" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u16,
        right: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &value);

    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    try std.testing.expectEqual(@as(u16, 0), value.?.left);
    try std.testing.expectEqual(@as(u16, 0), value.?.right);

    value.?.left = 41;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u16, 41), value.?.left);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);
}
