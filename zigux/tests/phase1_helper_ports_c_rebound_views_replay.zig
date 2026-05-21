const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-sized byte and array allocations stay balanced across frees" {
    slab.kmalloc_nr_allocated = 0;

    var bytes: ?[]u8 = slab.kmallocBytes(0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var array: ?[]u8 = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), array.?.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(array);
    array = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(bytes);
    bytes = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR rebinds from a tiny caller view back to an exact-fit slice" {
    const message = "Permission denied";
    var backing = [_]u8{0xaa} ** 32;

    const tiny_view = backing[3..7];
    const tiny = str_error_r.strErrorR(13, tiny_view);
    try std.testing.expectEqualStrings("Per", tiny);
    try std.testing.expectEqual(@as(u8, 0), tiny_view[3]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[2]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[7]);

    const full_view = backing[3 .. 3 + message.len + 1];
    const full = str_error_r.strErrorR(13, full_view);
    try std.testing.expectEqualStrings(message, full);
    try std.testing.expectEqual(@as(u8, 0), full_view[message.len]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[2]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[3 + message.len + 1]);
}

test "vsprintf reuses an offset caller slice after a zero-logical-size pad render" {
    var backing = [_]u8{0xcc} ** 16;
    const view = backing[4..12];

    @memset(view, 0xdd);
    const padded = vsprintf.scnprintfPad(view, 0, "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), padded);
    try std.testing.expectEqual(@as(u8, 0), view[0]);
    try std.testing.expectEqual(@as(u8, 0xdd), view[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[3]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[12]);

    const written = vsprintf.vscnprintf(view, "{s}:{d}", .{ "io", 7 });
    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualStrings("io:7", view[0..written]);
    try std.testing.expectEqual(@as(u8, 0), view[written]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[3]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[12]);
}

test "zalloc optional frees stay idempotent and later allocations return zeroed state" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        bytes: [4]u8,
        count: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0xee);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expect(value != null);
    @memset(&value.?.bytes, 0xab);
    value.?.count = 17;
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);

    var rebound: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &rebound);
    try std.testing.expect(rebound != null);
    for (rebound.?.bytes) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }
    try std.testing.expectEqual(@as(u16, 0), rebound.?.count);
}
