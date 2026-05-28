const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab reclaim gates preserve counters across slice releases" {
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocBytes(5, slab.__GFP_ZERO) == null);
    try std.testing.expect(slab.kmallocArray(2, 4, slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const first = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0 }, first);

    const second = slab.kmallocArray(2, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0, 0, 0 }, second);

    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR writes only inside caller slices" {
    var backing = [_]u8{0xaa} ** 18;
    const known = str_error_r.strErrorR(22, backing[3..12]);

    try std.testing.expectEqualStrings("Invalid ", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa }, backing[0..3]);
    try std.testing.expectEqual(@as(u8, 0), backing[11]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa }, backing[12..18]);

    const fallback = str_error_r.strErrorR(4096, backing[6..11]);
    try std.testing.expectEqualStrings("INTE", fallback);
    try std.testing.expectEqual(@as(u8, 0), backing[10]);
    try std.testing.expectEqual(@as(u8, 0), backing[11]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[12]);
}

test "vsprintf clamps formatted output to disjoint slice pockets" {
    var backing = [_]u8{0xcc} ** 16;

    const left = vsprintf.scnprintf(backing[1..7], "{s}:{d}", .{ "zigux", 42 });
    try std.testing.expectEqual(@as(usize, 5), left);
    try std.testing.expectEqualStrings("zigux", backing[1 .. 1 + left]);
    try std.testing.expectEqual(@as(u8, 0), backing[6]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[0]);

    const right = vsprintf.scnprintfPad(backing[9..15], 4, "{s}", .{"go"});
    try std.testing.expectEqual(@as(usize, 3), right);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'g', 'o', ' ', ' ', 0 }, backing[9..14]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[15]);

    const empty = vsprintf.vscnprintf(backing[4..4], "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), empty);
    try std.testing.expectEqual(@as(u8, 'u'), backing[4]);
}

test "zalloc zeroes fresh owners after release and reacquire" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u16,
        right: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0 }, bytes.?);
    @memset(bytes.?, 0x7f);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0 }, bytes.?);

    var pair: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), pair.?.left);
    try std.testing.expectEqual(@as(u16, 0), pair.?.right);
    pair.?.* = .{ .left = 11, .right = 17 };
    zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expect(pair == null);

    pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &pair);
    try std.testing.expectEqual(@as(u16, 0), pair.?.left);
    try std.testing.expectEqual(@as(u16, 0), pair.?.right);
}
