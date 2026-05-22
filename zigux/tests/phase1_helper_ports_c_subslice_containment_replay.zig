const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab balances mixed zero-length and non-zero allocations" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocArray(0, 16, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const bytes = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(bytes);
    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR stays inside a shifted caller view" {
    var storage = [_]u8{0x7e} ** 24;
    const view = storage[4..16];

    const rendered = str_error_r.strErrorR(13, view);
    try std.testing.expectEqualStrings("Permission ", rendered);
    try std.testing.expectEqual(@as(u8, 0x7e), storage[3]);
    try std.testing.expectEqual(@as(u8, 0), storage[15]);
    try std.testing.expectEqual(@as(u8, 0x7e), storage[16]);
}

test "scnprintfPad clamps and pads only within a shifted caller view" {
    var storage = [_]u8{'.'} ** 16;
    const view = storage[2..10];

    const written = vsprintf.scnprintfPad(view, 99, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 6), written);
    try std.testing.expectEqualStrings("xy     ", view[0..7]);
    try std.testing.expectEqual(@as(u8, 0), view[7]);
    try std.testing.expectEqual(@as(u8, '.'), storage[1]);
    try std.testing.expectEqual(@as(u8, '.'), storage[10]);
}

test "zalloc resets empty byte slices and nested values" {
    const allocator = std.testing.allocator;
    const Nested = struct {
        header: [3]u8,
        count: usize,
        seen: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Nested = try zalloc.zallocValue(allocator, Nested);
    defer zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0 }, &value.?.header);
    try std.testing.expectEqual(@as(usize, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.seen);
}
