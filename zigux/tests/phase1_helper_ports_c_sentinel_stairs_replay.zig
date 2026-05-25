const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps stair-step allocations balanced across failed, zero, and plain calls" {
    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocBytes(1, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocBytes(2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, zeroed);

    const empty = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    const plain = slab.kmallocArray(2, 1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 2), plain.len);
    plain[0] = 0x3c;
    plain[1] = 0x4d;
    try std.testing.expectEqual(@as(isize, 3), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps stair-step caller windows terminated and fenced" {
    var backing = [_]u8{0xaa} ** 24;

    const left = str_error_r.strErrorR(22, backing[1..4]);
    try std.testing.expectEqualStrings("In", left);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[0]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'I', 'n', 0 }, backing[1..4]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[4]);

    @memset(backing[0..], 0xbb);
    const middle = str_error_r.strErrorR(2, backing[6..12]);
    try std.testing.expectEqualStrings("No su", middle);
    try std.testing.expectEqual(@as(u8, 0xbb), backing[5]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'N', 'o', ' ', 's', 'u', 0 }, backing[6..12]);
    try std.testing.expectEqual(@as(u8, 0xbb), backing[12]);

    @memset(backing[0..], 0xcc);
    const right = str_error_r.strErrorR(4096, backing[14..19]);
    try std.testing.expectEqualStrings("INTE", right);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[13]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'I', 'N', 'T', 'E', 0 }, backing[14..19]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[19]);
}

test "vsprintf keeps stair-step windows isolated across short, padded, and exact renders" {
    var backing = [_]u8{0xdd} ** 16;

    const short_written = vsprintf.scnprintf(backing[1..3], "{d}", .{42});
    try std.testing.expectEqual(@as(usize, 1), short_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '4', 0 }, backing[1..3]);
    try std.testing.expectEqual(@as(u8, 0xdd), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xdd), backing[3]);

    const padded_written = vsprintf.scnprintfPad(backing[5..10], 4, "{s}", .{"z"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', ' ', ' ', ' ', 0 }, backing[5..10]);
    try std.testing.expectEqual(@as(u8, 0xdd), backing[4]);
    try std.testing.expectEqual(@as(u8, 0xdd), backing[10]);

    const exact_written = vsprintf.vscnprintf(backing[11..16], "{s}", .{"ab"});
    try std.testing.expectEqual(@as(usize, 2), exact_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, 0xdd, 0xdd }, backing[11..16]);
}

test "zalloc keeps stair-step byte and value lanes reusable after resets" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u8,
        right: u8,
        armed: bool,
    };

    var bytes_a: ?[]u8 = try zalloc.zallocBytes(allocator, 2);
    defer zalloc.zfreeBytes(allocator, &bytes_a);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes_a.?);
    bytes_a.?[1] = 0x7f;

    var bytes_b: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &bytes_b);
    try std.testing.expectEqual(@as(usize, 0), bytes_b.?.len);
    zalloc.zfreeBytes(allocator, &bytes_b);
    zalloc.zfreeBytes(allocator, &bytes_b);
    try std.testing.expect(bytes_b == null);

    bytes_b = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes_b.?);

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expectEqual(@as(u8, 0), pair.?.left);
    try std.testing.expectEqual(@as(u8, 0), pair.?.right);
    try std.testing.expectEqual(false, pair.?.armed);
    pair.?.* = .{ .left = 9, .right = 3, .armed = true };

    zalloc.zfreeValue(allocator, Pair, &pair);
    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);

    pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u8, 0), pair.?.left);
    try std.testing.expectEqual(@as(u8, 0), pair.?.right);
    try std.testing.expectEqual(false, pair.?.armed);
}
