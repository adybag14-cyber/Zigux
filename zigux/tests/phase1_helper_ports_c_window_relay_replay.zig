const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps live allocations stable across zeroed relay windows" {
    slab.kmalloc_nr_allocated = 0;

    const left: ?[]u8 = slab.kmallocBytes(6, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(left);
    @memset(left.?, 0x4c);

    var zeroed: ?[]u8 = slab.kmallocBytes(6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zeroed.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(zeroed);
    zeroed = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x4c, 0x4c, 0x4c, 0x4c, 0x4c, 0x4c }, left.?);
}

test "strErrorR relays exact subview lengths without disturbing neighboring bytes" {
    var buffer = [_]u8{0xcc} ** 24;

    const known_view = buffer[2..11];
    const known = str_error_r.strErrorR(13, known_view);
    try std.testing.expectEqualStrings("Permissi", known);
    try std.testing.expectEqual(@as(u8, 0xcc), buffer[1]);
    try std.testing.expectEqual(@as(u8, 0), buffer[10]);
    try std.testing.expectEqual(@as(u8, 0xcc), buffer[11]);

    const fallback_view = buffer[12..17];
    const fallback = str_error_r.strErrorR(4096, fallback_view);
    try std.testing.expectEqualStrings("INTE", fallback);
    try std.testing.expectEqual(@as(u8, 0), buffer[16]);
    try std.testing.expectEqual(@as(u8, 0xcc), buffer[17]);
}

test "vsprintf relays direct and padded caller windows inside one backing buffer" {
    var buffer = [_]u8{0xaa} ** 18;

    const direct = buffer[1..7];
    const direct_written = vsprintf.vscnprintf(direct, "{s}", .{"relay"});
    try std.testing.expectEqual(@as(usize, 5), direct_written);
    try std.testing.expectEqualSlices(u8, "relay", direct[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), direct[direct_written]);
    try std.testing.expectEqual(@as(u8, 0xaa), buffer[0]);
    try std.testing.expectEqual(@as(u8, 0xaa), buffer[7]);

    const padded = buffer[8..15];
    const padded_written = vsprintf.scnprintfPad(padded, padded.len, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 5), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'd', ' ', ' ', ' ', ' ', 0 }, padded);
    try std.testing.expectEqual(@as(u8, 0xaa), buffer[15]);
}

test "zalloc relays zeroed ownership across bytes and values" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u16,
        right: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    @memset(bytes.?, 0xfe);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expectEqual(@as(u16, 0), value.?.left);
    try std.testing.expectEqual(@as(u16, 0), value.?.right);
    value.?.left = 9;
    value.?.right = 17;
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);

    bytes = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);
}
