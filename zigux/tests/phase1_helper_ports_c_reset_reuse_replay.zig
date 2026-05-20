const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab allocation counters recover across mixed reverse frees" {
    slab.kmalloc_nr_allocated = 0;

    const plain = slab.kmallocBytes(6, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(plain, 0xaa);

    const zeroed_array = slab.kmallocArray(3, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zeroed_array) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(zeroed_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zeroed_bytes = slab.kmallocBytes(6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zeroed_bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zeroed_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR resets exact-fit caller slices after tiny reuse" {
    var backing = [_]u8{'#'} ** 40;

    const tiny = str_error_r.strErrorR(13, backing[3..4]);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, '#'), backing[2]);
    try std.testing.expectEqual(@as(u8, 0), backing[3]);
    try std.testing.expectEqual(@as(u8, '#'), backing[4]);

    const exact = str_error_r.strErrorR(0, backing[3..11]);
    try std.testing.expectEqualStrings("Success", exact);
    try std.testing.expectEqual(@as(u8, 0), backing[10]);
    try std.testing.expectEqual(@as(u8, '#'), backing[11]);
}

test "vsprintf reuses caller slices without leaking old padding" {
    var backing = [_]u8{'?'} ** 16;

    const padded = vsprintf.scnprintfPad(backing[2..12], 6, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 5), padded);
    try std.testing.expectEqualStrings("id    ", backing[2..8]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, '?'), backing[1]);
    try std.testing.expectEqual(@as(u8, '?'), backing[9]);

    const reused = vsprintf.vscnprintf(backing[2..12], "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 2), reused);
    try std.testing.expectEqualStrings("ok", backing[2 .. 2 + reused]);
    try std.testing.expectEqual(@as(u8, 0), backing[4]);
}

test "zalloc restores zero state after dirty frees" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [4]u8,
        nested: struct {
            count: u16,
            flag: bool,
        },
        maybe: ?[]const u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expect(value != null);
    value.?.bytes = .{ 1, 2, 3, 4 };
    value.?.nested = .{ .count = 9, .flag = true };
    value.?.maybe = "zigux";
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0, 0 }, &value.?.bytes);
    try std.testing.expectEqual(@as(u16, 0), value.?.nested.count);
    try std.testing.expectEqual(false, value.?.nested.flag);
    try std.testing.expect(value.?.maybe == null);
}
