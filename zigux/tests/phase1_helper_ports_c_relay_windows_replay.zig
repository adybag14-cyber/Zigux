const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab relays zeroed allocations without counter drift" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const array = slab.kmallocArray(2, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (array) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR relays exact and tiny windows without touching neighbors" {
    var backing = [_]u8{0xaa} ** 18;

    const exact = str_error_r.strErrorR(13, backing[2..8]);
    try std.testing.expectEqualStrings("Permi", exact);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[8]);

    @memset(backing[0..], 0xbb);
    const tiny = str_error_r.strErrorR(4096, backing[9..11]);
    try std.testing.expectEqualStrings("I", tiny);
    try std.testing.expectEqual(@as(u8, 0xbb), backing[8]);
    try std.testing.expectEqual(@as(u8, 'I'), backing[9]);
    try std.testing.expectEqual(@as(u8, 0), backing[10]);
    try std.testing.expectEqual(@as(u8, 0xbb), backing[11]);
}

test "vsprintf relays empty, truncated, and padded windows independently" {
    var backing = [_]u8{0xcc} ** 14;

    const empty_written = vsprintf.scnprintf(backing[4..4], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[3]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[4]);

    const trunc_written = vsprintf.vscnprintf(backing[0..4], "{s}", .{"wide"});
    try std.testing.expectEqual(@as(usize, 3), trunc_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'w', 'i', 'd', 0 }, backing[0..4]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[4]);

    const pad_written = vsprintf.scnprintfPad(backing[7..13], 5, "{s}:{d}", .{ "id", 7 });
    try std.testing.expectEqual(@as(usize, 4), pad_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'd', ':', '7', ' ', 0 }, backing[7..13]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[6]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[13]);
}

test "zalloc relays byte and value ownership through repeated resets" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u16,
        right: u16,
        armed: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);
    bytes.?[2] = 0x7f;

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expectEqual(@as(u16, 0), pair.?.left);
    try std.testing.expectEqual(@as(u16, 0), pair.?.right);
    try std.testing.expectEqual(false, pair.?.armed);
    pair.?.* = .{ .left = 3, .right = 9, .armed = true };

    zalloc.zfreeBytes(allocator, &bytes);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    bytes = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);

    zalloc.zfreeValue(allocator, Pair, &pair);
    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);
    pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), pair.?.left);
    try std.testing.expectEqual(@as(u16, 0), pair.?.right);
    try std.testing.expectEqual(false, pair.?.armed);
}
