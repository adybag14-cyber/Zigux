const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab retries cleanly after reclaim-gated failures" {
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expect(slab.kmallocArray(2, 3, slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const bytes = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const array = slab.kmallocArray(2, 3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 6), array.len);
    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR refreshes shared caller storage across unknown and known messages" {
    var backing = [_]u8{0xaa} ** 10;

    const unknown = str_error_r.strErrorR(4096, backing[0..8]);
    try std.testing.expectEqualStrings("INTERNA", unknown);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);

    const known = str_error_r.strErrorR(0, backing[0..8]);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 'S'), backing[0]);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);

    const empty = str_error_r.strErrorR(2, backing[0..0]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, 'S'), backing[0]);
}

test "vsprintf keeps writes inside caller views and exact-fit windows" {
    var backing = [_]u8{0xdd} ** 7;

    const padded = vsprintf.scnprintfPad(backing[1..6], 4, "{s}", .{"Q"});
    try std.testing.expectEqual(@as(usize, 3), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 'Q', ' ', ' ', ' ', 0, 0xdd }, &backing);

    const direct = vsprintf.vscnprintf(backing[1..6], "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 4), direct);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 'a', 'b', 'c', 'd', 0, 0xdd }, &backing);
}

test "zalloc re-zeroes byte and value allocations after release" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        count: u16,
        flag: bool,
        bytes: [2]u8,
    };

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(empty != null);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0x5a);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    value.?.* = .{ .count = 9, .flag = true, .bytes = .{ 1, 2 } };
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.flag);
    try std.testing.expectEqual(std.mem.zeroes([2]u8), value.?.bytes);
}
