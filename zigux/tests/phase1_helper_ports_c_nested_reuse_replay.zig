const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 replay keeps slab counters balanced across nested zero and failed paths" {
    slab.kmalloc_nr_allocated = 0;

    const zeroed = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), zeroed.len);
    try std.testing.expectEqual(@as(u8, 0), zeroed[0]);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const empty = slab.kmallocArray(0, 5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 replay keeps strErrorR exact-fit and tiny nested views fenced" {
    var backing = [_]u8{'%'} ** 16;

    const exact = str_error_r.strErrorR(0, backing[2..10]);
    try std.testing.expectEqualStrings("Success", exact);
    try std.testing.expectEqual(@as(u8, '%'), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try std.testing.expectEqual(@as(u8, '%'), backing[10]);

    const tiny = str_error_r.strErrorR(13, backing[11..12]);
    try std.testing.expectEqualStrings("", tiny);
    try std.testing.expectEqual(@as(u8, '%'), backing[10]);
    try std.testing.expectEqual(@as(u8, 0), backing[11]);
    try std.testing.expectEqual(@as(u8, '%'), backing[12]);
}

test "lane10 replay keeps nested vsprintf rewrites inside the caller view" {
    var backing = [_]u8{'?'} ** 14;
    const outer = backing[2..12];

    const direct = vsprintf.scnprintf(outer, "{s}", .{"hello"});
    try std.testing.expectEqual(@as(usize, 5), direct);
    try std.testing.expectEqual(@as(u8, 0), outer[5]);
    try std.testing.expectEqual(@as(u8, '?'), backing[1]);
    try std.testing.expectEqual(@as(u8, '?'), backing[12]);

    const nested = vsprintf.scnprintfPad(outer[4..9], 4, "{s}", .{"z"});
    try std.testing.expectEqual(@as(usize, 3), nested);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'e', 'l', 'l', 'z', ' ', ' ', ' ', 0, '?' }, outer);
    try std.testing.expectEqual(@as(u8, '?'), backing[1]);
    try std.testing.expectEqual(@as(u8, '?'), backing[12]);
}

test "lane10 replay keeps zalloc byte and value reuses independently zeroed" {
    const allocator = std.testing.allocator;
    const State = struct {
        bytes: [3]u8,
        ready: bool,
    };

    var left: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, left.?);

    var right: ?[]u8 = try zalloc.zallocBytes(allocator, 2);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, right.?);

    left.?[0] = 0xff;
    right.?[0] = 7;
    right.?[1] = 9;

    zalloc.zfreeBytes(allocator, &left);
    try std.testing.expect(left == null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 7, 9 }, right.?);

    left = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &left);
    defer zalloc.zfreeBytes(allocator, &right);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, left.?);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 7, 9 }, right.?);

    var state: ?*State = try zalloc.zallocValue(allocator, State);
    try std.testing.expectEqual(@as([3]u8, .{ 0, 0, 0 }), state.?.bytes);
    try std.testing.expectEqual(false, state.?.ready);
    state.?.bytes = .{ 1, 2, 3 };
    state.?.ready = true;
    zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expect(state == null);

    state = try zalloc.zallocValue(allocator, State);
    defer zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expectEqual(@as([3]u8, .{ 0, 0, 0 }), state.?.bytes);
    try std.testing.expectEqual(false, state.?.ready);
}
