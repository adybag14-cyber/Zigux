const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab caller carry keeps allocation accounting stable across interleaved frees" {
    slab.kmalloc_nr_allocated = 0;

    const left = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(left);
    const right = slab.kmallocBytes(6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(right);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    @memset(left, 0x5a);
    for (right) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "strErrorR carries caller-owned subviews without clobbering neighboring bytes" {
    var backing = [_]u8{0xaa} ** 16;

    const wide = str_error_r.strErrorR(13, backing[1..9]);
    try std.testing.expectEqualStrings("Permiss", wide);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);

    const nested = str_error_r.strErrorR(0, backing[3..7]);
    try std.testing.expectEqualStrings("Suc", nested);
    try std.testing.expectEqualSlices(u8, "Pe", backing[1..3]);
    try std.testing.expectEqual(@as(u8, 0), backing[6]);

    const fallback = str_error_r.strErrorR(4096, backing[7..12]);
    try std.testing.expectEqualStrings("INTE", fallback);
    try std.testing.expectEqual(@as(u8, 0), backing[11]);
}

test "vsprintf carries overlapping caller windows with stable padded and direct writes" {
    var backing = [_]u8{0xcc} ** 12;

    const padded = vsprintf.scnprintfPad(backing[1..7], 5, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 4), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'd', ' ', ' ', ' ', 0 }, backing[1..7]);

    const direct = vsprintf.scnprintf(backing[3..8], "{s}", .{"WXYZ"});
    try std.testing.expectEqual(@as(usize, 4), direct);
    try std.testing.expectEqualSlices(u8, "id", backing[1..3]);
    try std.testing.expectEqualSlices(u8, "WXYZ", backing[3..7]);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);

    const alias = vsprintf.vscnprintf(backing[7..12], "{d}", .{42});
    try std.testing.expectEqual(@as(usize, 2), alias);
    try std.testing.expectEqualSlices(u8, "42", backing[7..9]);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
}

test "zalloc caller carry re-zeroes bytes and nested value state after release" {
    const allocator = std.testing.allocator;
    const Nested = extern union {
        bytes: [4]u8,
        value: u32,
    };
    const Value = extern struct {
        tag: u8,
        pad: [3]u8,
        nested: Nested,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0xab);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var bytes_again: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &bytes_again);
    for (bytes_again.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expect(value != null);
    value.?.tag = 0xff;
    value.?.pad = .{ 1, 2, 3 };
    value.?.nested.value = std.math.maxInt(u32);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    var value_again: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value_again);
    try std.testing.expectEqual(@as(u8, 0), value_again.?.tag);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value_again.?.pad);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &value_again.?.nested.bytes);
}
