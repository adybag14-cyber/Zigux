const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports replay keeps slab counters balanced across interleaved frees" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(8, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    errdefer slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const array = slab.kmallocArray(3, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    errdefer slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    for (array) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    bytes[0] = 0x5a;
    try std.testing.expectEqual(@as(u8, 0x5a), bytes[0]);

    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "phase1 helper ports replay lets strErrorR reuse a caller buffer after truncation" {
    var buffer: [48]u8 = undefined;

    try std.testing.expectEqualStrings("INTERNAL ER", str_error_r.strErrorR(4096, buffer[0..12]));

    const reused = str_error_r.strErrorR(0, &buffer);
    try std.testing.expectEqualStrings("Success", reused);
    try std.testing.expectEqual(@as(u8, 0), buffer[reused.len]);
}

test "phase1 helper ports replay keeps scnprintf and vscnprintf aligned across reuse" {
    var direct: [6]u8 = undefined;
    var variadic: [6]u8 = undefined;

    const first_direct = vsprintf.scnprintf(&direct, "{s}", .{"abcdefghi"});
    const first_variadic = vsprintf.vscnprintf(&variadic, "{s}", .{"abcdefghi"});
    try std.testing.expectEqual(first_direct, first_variadic);
    try std.testing.expectEqualStrings(direct[0..first_direct], variadic[0..first_variadic]);

    const second_direct = vsprintf.scnprintf(&direct, "{s}:{d}", .{ "ok", 7 });
    const second_variadic = vsprintf.vscnprintf(&variadic, "{s}:{d}", .{ "ok", 7 });
    try std.testing.expectEqual(second_direct, second_variadic);
    try std.testing.expectEqualStrings("ok:7", direct[0..second_direct]);
    try std.testing.expectEqualStrings(direct[0..second_direct], variadic[0..second_variadic]);
    try std.testing.expectEqual(@as(u8, 0), direct[second_direct]);
    try std.testing.expectEqual(@as(u8, 0), variadic[second_variadic]);
}

test "phase1 helper ports replay re-zeroes zalloc state after mixed frees" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u8,
        active: bool,
        note: ?[]const u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    @memset(bytes.?, 0xa5);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    value.?.count = 9;
    value.?.active = true;
    value.?.note = "dirty";

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u8, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.active);
    try std.testing.expect(value.?.note == null);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    for (bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }
}
