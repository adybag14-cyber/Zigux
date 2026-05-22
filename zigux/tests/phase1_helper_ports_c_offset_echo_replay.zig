const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "kmalloc keeps zeroed siblings isolated across reverse frees" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const second = slab.kmallocBytes(6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        slab.kfree(first);
        return error.TestUnexpectedResult;
    };

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memset(first, 0xaa);
    for (second) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR truncates inside offset windows and keeps sentinels" {
    var single = [_]u8{ 0xaa, 0xbb, 0xcc };
    const tiny = str_error_r.strErrorR(13, single[1..2]);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, 0xaa), single[0]);
    try std.testing.expectEqual(@as(u8, 0), single[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), single[2]);

    var windowed = [_]u8{'#'} ** 12;
    const rendered = str_error_r.strErrorR(4096, windowed[2..8]);
    try std.testing.expectEqualStrings("INTER", rendered);
    try std.testing.expectEqual(@as(u8, '#'), windowed[1]);
    try std.testing.expectEqual(@as(u8, 0), windowed[7]);
    try std.testing.expectEqual(@as(u8, '#'), windowed[8]);
}

test "scnprintfPad respects offset windows and current padded return" {
    var arena = [_]u8{'#'} ** 10;
    const written = vsprintf.scnprintfPad(arena[2..8], 5, "{s}", .{"xy"});

    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualStrings("xy   ", arena[2..7]);
    try std.testing.expectEqual(@as(u8, 0), arena[7]);
    try std.testing.expectEqual(@as(u8, '#'), arena[1]);
    try std.testing.expectEqual(@as(u8, '#'), arena[8]);
}

test "zalloc zeroes nested values and free helpers stay idempotent" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [3]u8,
        marker: ?u16,
        count: u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    try std.testing.expect(bytes != null);
    for (bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }
    bytes.?[0] = 0xaa;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expect(value != null);
    for (value.?.bytes) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }
    try std.testing.expect(value.?.marker == null);
    try std.testing.expectEqual(@as(u8, 0), value.?.count);

    value.?.bytes[1] = 9;
    value.?.marker = 7;
    value.?.count = 3;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
