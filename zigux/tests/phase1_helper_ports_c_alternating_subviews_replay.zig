const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps alternating failed and live probes balanced" {
    slab.kmalloc_nr_allocated = 0;

    const left = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, left);

    try std.testing.expect(slab.kmallocBytes(4, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const right = slab.kmallocArray(2, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, right);

    slab.kfree(right);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(left);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps alternating tiny caller subviews fenced" {
    var backing = [_]u8{0xaa} ** 12;

    const left = str_error_r.strErrorR(0, backing[1..3]);
    try std.testing.expectEqualStrings("S", left);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[0]);
    try std.testing.expectEqual(@as(u8, 'S'), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[2]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[3]);

    const right = str_error_r.strErrorR(4096, backing[5..10]);
    try std.testing.expectEqualStrings("INTE", right);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[4]);
    try std.testing.expectEqual(@as(u8, 'I'), backing[5]);
    try std.testing.expectEqual(@as(u8, 'N'), backing[6]);
    try std.testing.expectEqual(@as(u8, 'T'), backing[7]);
    try std.testing.expectEqual(@as(u8, 'E'), backing[8]);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[10]);
}

test "vsprintf clamps alternating tiny subviews independently" {
    var backing = [_]u8{0xcc} ** 12;

    const direct_written = vsprintf.scnprintf(backing[1..4], "{s}", .{"wide"});
    try std.testing.expectEqual(@as(usize, 2), direct_written);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xcc, 'w', 'i', 0, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc },
        &backing,
    );

    const padded_written = vsprintf.scnprintfPad(backing[6..11], 4, "{s}", .{"Q"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0xcc, 'w', 'i', 0, 0xcc, 0xcc, 'Q', ' ', ' ', ' ', 0, 0xcc },
        &backing,
    );
}

test "zalloc refreshes alternating byte and value lifetimes" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u8,
        right: u8,
        armed: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);
    bytes.?[1] = 0x7f;

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u8, 0), pair.?.left);
    try std.testing.expectEqual(@as(u8, 0), pair.?.right);
    try std.testing.expectEqual(false, pair.?.armed);
    pair.?.* = .{ .left = 3, .right = 9, .armed = true };

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    bytes = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);

    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);
    pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expectEqual(@as(u8, 0), pair.?.left);
    try std.testing.expectEqual(@as(u8, 0), pair.?.right);
    try std.testing.expectEqual(false, pair.?.armed);
}
