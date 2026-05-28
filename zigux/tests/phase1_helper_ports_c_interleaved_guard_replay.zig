const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab interleaved zero and plain allocations keep sibling counters balanced" {
    slab.kmalloc_nr_allocated = 0;

    const plain = slab.kmallocBytes(3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    @memset(plain, 0x5a);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 5), zeroed.len);
    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR subviews keep outer sentinels intact across fallback and known messages" {
    var backing = [_]u8{0xaa} ** 24;

    const fallback = str_error_r.strErrorR(4096, backing[3..11]);
    try std.testing.expectEqualStrings("INTERNA", fallback);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[2]);
    try std.testing.expectEqual(@as(u8, 0), backing[10]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[11]);

    const known = str_error_r.strErrorR(13, backing[12..22]);
    try std.testing.expectEqualStrings("Permissio", known);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[11]);
    try std.testing.expectEqual(@as(u8, 0), backing[21]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[22]);
}

test "vsprintf padded interior windows preserve neighbors and current width contract" {
    var backing = [_]u8{0x7e} ** 12;
    const written = vsprintf.scnprintfPad(backing[2..8], 5, "{s}", .{"ab"});

    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqual(@as(u8, 0x7e), backing[1]);
    try std.testing.expectEqual(@as(u8, 0x7e), backing[8]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', ' ', ' ', ' ', 0 }, backing[2..8]);
}

test "zalloc owner release leaves live siblings intact until their own free" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u32,
        enabled: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    @memcpy(bytes.?, &[_]u8{ 1, 2, 3, 4 });
    value.?.count = 7;
    value.?.enabled = true;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u32, 7), value.?.count);
    try std.testing.expectEqual(true, value.?.enabled);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
