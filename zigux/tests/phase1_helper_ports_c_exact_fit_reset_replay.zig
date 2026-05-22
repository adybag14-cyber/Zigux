const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps zero-length and non-zero allocations independently balanced" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const live = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(live);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (live) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR preserves exact-fit and zero-length caller windows" {
    var exact: [18]u8 = [_]u8{0xaa} ** 18;
    const exact_text = str_error_r.strErrorR(13, &exact);
    try std.testing.expectEqualStrings("Permission denied", exact_text);
    try std.testing.expectEqual(@as(u8, 0), exact[17]);

    var larger: [24]u8 = [_]u8{0xaa} ** 24;
    const inner = larger[3..11];
    const short_text = str_error_r.strErrorR(4096, inner);
    try std.testing.expectEqualStrings("INTERNA", short_text);
    try std.testing.expectEqual(@as(u8, 0xaa), larger[2]);
    try std.testing.expectEqual(@as(u8, 0xaa), larger[11]);

    var empty: [0]u8 = .{};
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(22, &empty).len);
}

test "vsprintf resets exact-fit and zero-logical-size offset slices" {
    var buffer: [16]u8 = [_]u8{0xaa} ** 16;
    const view = buffer[2..10];
    const written = vsprintf.scnprintf(view, "{s}", .{"zigux:9"});
    try std.testing.expectEqual(@as(usize, 7), written);
    try std.testing.expectEqualStrings("zigux:9", view[0..written]);
    try std.testing.expectEqual(@as(u8, 0), view[written]);
    try std.testing.expectEqual(@as(u8, 0xaa), buffer[1]);
    try std.testing.expectEqual(@as(u8, 0xaa), buffer[10]);

    var padded: [8]u8 = [_]u8{'x'} ** 8;
    const padded_view = padded[1..7];
    const padded_written = vsprintf.scnprintfPad(padded_view, 0, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 0), padded_written);
    try std.testing.expectEqual(@as(u8, 0), padded_view[0]);
    try std.testing.expectEqual(@as(u8, 'x'), padded[0]);
    try std.testing.expectEqual(@as(u8, 'x'), padded[7]);
}

test "zalloc keeps zero-sized bytes and repeated frees stable" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const Payload = struct {
        count: u16,
        enabled: bool,
    };
    var value: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.enabled);
    zalloc.zfreeValue(allocator, Payload, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Payload, &value);
    try std.testing.expect(value == null);
}
