const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab stitched lifetimes keep allocation counters balanced" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const array = slab.kmallocArray(2, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (array) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps stitched caller windows isolated" {
    var backing = [_]u8{0xaa} ** 20;

    const permission = str_error_r.strErrorR(13, backing[2..7]);
    try std.testing.expectEqualStrings("Perm", permission);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[6]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[7]);

    const internal = str_error_r.strErrorR(4096, backing[10..12]);
    try std.testing.expectEqualStrings("I", internal);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[9]);
    try std.testing.expectEqual(@as(u8, 0), backing[11]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[12]);
}

test "vsprintf keeps stitched subviews fenced to their caller windows" {
    var padded = [_]u8{0x7f} ** 12;
    const padded_written = vsprintf.scnprintfPad(padded[3..10], 5, "v={d}", .{7});
    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0x7f, 0x7f, 0x7f, 'v', '=', '7', ' ', ' ', 0, 0x7f, 0x7f, 0x7f },
        &padded,
    );

    var truncated = [_]u8{0x6d} ** 8;
    const trunc_written = vsprintf.vscnprintf(truncated[2..6], "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 3), trunc_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x6d, 0x6d, 'a', 'b', 'c', 0, 0x6d, 0x6d }, &truncated);
}

test "zalloc stitched reuse zeroes fresh bytes and nested values" {
    const allocator = std.testing.allocator;
    const Payload = struct {
        lanes: [3]u16,
        armed: bool,
        child: ?*u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0x5a);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    var payload: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expectEqualSlices(u16, &[_]u16{ 0, 0, 0 }, &payload.?.lanes);
    try std.testing.expectEqual(false, payload.?.armed);
    try std.testing.expectEqual(@as(?*u8, null), payload.?.child);
}
