const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const Value = struct {
    a: u32,
    b: [2]u8,
};

test "helper ports hand off caller storage cleanly across resets" {
    slab.kmalloc_nr_allocated = 0;

    const live_zero = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const live_array = slab.kmallocArray(2, 3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(2, 3, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    slab.kfree(live_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(std.math.maxInt(usize), slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(live_zero);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var strerror_storage = [_]u8{0xaa} ** 12;
    const strerror_view = strerror_storage[2..10];
    const unknown = str_error_r.strErrorR(4096, strerror_view);
    try std.testing.expectEqualStrings("INTERNA", unknown);
    try std.testing.expectEqual(@as(u8, 0xaa), strerror_storage[1]);
    try std.testing.expectEqual(@as(u8, 0xaa), strerror_storage[10]);
    const known = str_error_r.strErrorR(0, strerror_view);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 0), strerror_view[known.len]);
    try std.testing.expectEqual(@as(u8, 0xaa), strerror_storage[1]);
    try std.testing.expectEqual(@as(u8, 0xaa), strerror_storage[10]);

    var format_storage = [_]u8{0xcc} ** 10;
    const format_view = format_storage[1..8];
    const padded = vsprintf.scnprintfPad(format_view, format_view.len - 1, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 5), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', ' ', ' ', 0 }, format_view);
    const rewritten = vsprintf.scnprintf(format_view, "{d}", .{9});
    try std.testing.expectEqual(@as(usize, 1), rewritten);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '9', 0, ' ', ' ', ' ', ' ', 0 }, format_view);
    try std.testing.expectEqual(@as(u8, 0xcc), format_storage[0]);
    try std.testing.expectEqual(@as(u8, 0xcc), format_storage[8]);

    const allocator = std.testing.allocator;
    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    for (bytes.?) |*item| item.* = 0xff;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    value.?.a = 77;
    value.?.b = .{ 1, 2 };
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.a);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, &value.?.b);
}
