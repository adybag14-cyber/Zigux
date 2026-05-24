const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-sized reclaim allocation still balances counters and null free is inert" {
    slab.kmalloc_nr_allocated = 0;
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zero = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zero);

    try std.testing.expectEqual(@as(usize, 0), zero.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR only mutates the caller window and still terminates tiny slices" {
    var backing = [_]u8{ '#', '#', '#', '#', '#', '#', '#' };
    const tiny = backing[2..5];
    const written = str_error_r.strErrorR(22, tiny);

    try std.testing.expectEqualStrings("In", written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#', 'I', 'n', 0, '#', '#' }, &backing);

    const empty = str_error_r.strErrorR(2, backing[4..4]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#', 'I', 'n', 0, '#', '#' }, &backing);
}

test "vsprintf confines padded renders to the provided interior view" {
    var backing = [_]u8{ 'L', 'L', 'L', 'L', 'L', 'L', 'L', 'L' };
    const interior = backing[2..7];
    const written = vsprintf.scnprintfPad(interior, 4, "{s}", .{"Z"});

    try std.testing.expectEqual(@as(usize, 3), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'L', 'L', 'Z', ' ', ' ', ' ', 0, 'L' }, &backing);
}

test "zalloc zeroes aggregates and repeated frees keep optionals null" {
    const allocator = std.testing.allocator;
    const Aggregate = struct {
        count: u16,
        flags: [3]bool,
        note: ?u8,
    };

    var value: ?*Aggregate = try zalloc.zallocValue(allocator, Aggregate);
    defer zalloc.zfreeValue(allocator, Aggregate, &value);

    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqualSlices(bool, &[_]bool{ false, false, false }, &value.?.flags);
    try std.testing.expect(value.?.note == null);

    zalloc.zfreeValue(allocator, Aggregate, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Aggregate, &value);
    try std.testing.expect(value == null);
}
