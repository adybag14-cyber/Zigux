const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 shared edges keep slab counters balanced across null and dirty frees" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (first) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memset(first, 0xaa);
    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const second = slab.kmallocBytes(6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (second) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "lane10 shared edges keep strErrorR exact-fit and tiny-buffer contracts stable" {
    const expected_known = "Permission denied";
    var known_buffer: [expected_known.len + 1]u8 = undefined;
    const known = str_error_r.strErrorR(13, &known_buffer);
    try std.testing.expectEqualStrings(expected_known, known);
    try std.testing.expectEqual(@intFromPtr(known_buffer[0..].ptr), @intFromPtr(known.ptr));

    var tiny_buffer = [_]u8{0xaa};
    const tiny = str_error_r.strErrorR(4096, &tiny_buffer);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, 0), tiny_buffer[0]);
}

test "lane10 shared edges keep vsprintf truncation routes aligned" {
    var scn_buffer: [5]u8 = undefined;
    var vscn_buffer: [5]u8 = undefined;

    const scn_written = vsprintf.scnprintf(&scn_buffer, "{s}", .{"abcdef"});
    const vscn_written = vsprintf.vscnprintf(&vscn_buffer, "{s}", .{"abcdef"});
    try std.testing.expectEqual(scn_written, vscn_written);
    try std.testing.expectEqual(@as(usize, 4), scn_written);
    try std.testing.expectEqualStrings(scn_buffer[0..scn_written], vscn_buffer[0..vscn_written]);

    var single = [_]u8{0xaa};
    var single_v = [_]u8{0xbb};
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(&single, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(usize, 0), vsprintf.vscnprintf(&single_v, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(u8, 0), single[0]);
    try std.testing.expectEqual(@as(u8, 0), single_v[0]);

    var padded = [_]u8{0xaa} ** 4;
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintfPad(&padded, 0, "{s}", .{"zig"}));
    try std.testing.expectEqual(@as(u8, 0), padded[0]);
}

test "lane10 shared edges keep zalloc bytes and values zeroed across frees" {
    const allocator = std.testing.allocator;
    const Value = struct {
        ptr: ?*u8,
        len: usize,
        enabled: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0xcc);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    value.?.ptr = @ptrFromInt(0x1234);
    value.?.len = 99;
    value.?.enabled = true;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(?*u8, null), value.?.ptr);
    try std.testing.expectEqual(@as(usize, 0), value.?.len);
    try std.testing.expectEqual(false, value.?.enabled);
}
