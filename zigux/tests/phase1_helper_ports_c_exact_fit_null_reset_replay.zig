const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-length arrays still balance allocation counters" {
    slab.kmalloc_nr_allocated = 0;

    const zeroed = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(usize, 0), zeroed.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR exact-fit and tiny buffers terminate cleanly" {
    var exact = [_]u8{0xaa} ** 8;
    const exact_text = str_error_r.strErrorR(0, &exact);
    try std.testing.expectEqualStrings("Success", exact_text);
    try std.testing.expectEqual(@as(u8, 0), exact[7]);

    var one_byte = [_]u8{0xbb};
    const tiny_text = str_error_r.strErrorR(22, &one_byte);
    try std.testing.expectEqual(@as(usize, 0), tiny_text.len);
    try std.testing.expectEqual(@as(u8, 0), one_byte[0]);

    var empty_backing = [_]u8{0xcc};
    const empty_text = str_error_r.strErrorR(4096, empty_backing[0..0]);
    try std.testing.expectEqual(@as(usize, 0), empty_text.len);
    try std.testing.expectEqual(@as(u8, 0xcc), empty_backing[0]);
}

test "vsprintf keeps exact-fit and one-byte caller views null-terminated" {
    var exact = [_]u8{0xdd} ** 8;
    const exact_written = vsprintf.scnprintf(&exact, "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqual(@as(usize, 7), exact_written);
    try std.testing.expectEqualStrings("zigux:7", exact[0..exact_written]);
    try std.testing.expectEqual(@as(u8, 0), exact[7]);

    var one_byte = [_]u8{0xee};
    const tiny_written = vsprintf.vscnprintf(&one_byte, "{s}", .{"abc"});
    try std.testing.expectEqual(@as(usize, 0), tiny_written);
    try std.testing.expectEqual(@as(u8, 0), one_byte[0]);

    var padded = [_]u8{0xff} ** 4;
    const padded_written = vsprintf.scnprintfPad(&padded, 1, "{s}", .{"abc"});
    try std.testing.expectEqual(@as(usize, 1), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 0, 0xff, 0xff }, &padded);
}

test "zalloc refill and repeated frees reset optionals cleanly" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const Value = struct {
        pair: [2]u16,
        flag: bool,
    };

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqualSlices(u16, &[_]u16{ 0, 0 }, &value.?.pair);
    try std.testing.expectEqual(false, value.?.flag);
    value.?.pair = .{ 9, 12 };
    value.?.flag = true;

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqualSlices(u16, &[_]u16{ 0, 0 }, &value.?.pair);
    try std.testing.expectEqual(false, value.?.flag);
}
