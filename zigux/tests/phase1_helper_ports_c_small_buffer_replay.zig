const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C zero-sized allocation contracts stay balanced" {
    slab.kmalloc_nr_allocated = 0;

    const empty_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const empty_array = slab.kmallocArray(4, 0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty_array.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const allocator = std.testing.allocator;
    var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.?.len);
    zalloc.zfreeBytes(allocator, &zero_bytes);
    try std.testing.expect(zero_bytes == null);
    zalloc.zfreeBytes(allocator, &zero_bytes);
    try std.testing.expect(zero_bytes == null);
}

test "phase1 helper ports C tiny strerror buffers stay terminated" {
    var one_byte_known = [_]u8{0xaa};
    const known = str_error_r.strErrorR(13, &one_byte_known);
    try std.testing.expectEqual(@as(usize, 0), known.len);
    try std.testing.expectEqual(@as(u8, 0), one_byte_known[0]);

    var one_byte_unknown = [_]u8{0xbb};
    const unknown = str_error_r.strErrorR(4096, &one_byte_unknown);
    try std.testing.expectEqual(@as(usize, 0), unknown.len);
    try std.testing.expectEqual(@as(u8, 0), one_byte_unknown[0]);

    var zero_len: [0]u8 = .{};
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(2, &zero_len).len);
}

test "phase1 helper ports C tiny vsprintf buffers stay empty strings" {
    var one_byte_buffer = [_]u8{0xaa};
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(&one_byte_buffer, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(u8, 0), one_byte_buffer[0]);

    one_byte_buffer[0] = 0xbb;
    try std.testing.expectEqual(@as(usize, 0), vsprintf.vscnprintf(&one_byte_buffer, "{s}:{d}", .{ "zigux", 10 }));
    try std.testing.expectEqual(@as(u8, 0), one_byte_buffer[0]);

    one_byte_buffer[0] = 0xcc;
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintfPad(&one_byte_buffer, 6, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(u8, 0), one_byte_buffer[0]);

    var zero_len: [0]u8 = .{};
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(&zero_len, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(usize, 0), vsprintf.vscnprintf(&zero_len, "{s}", .{"zigux"}));
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintfPad(&zero_len, 3, "{s}", .{"zigux"}));
}

test "phase1 helper ports C zalloc zeroes optional pointer-like fields" {
    const allocator = std.testing.allocator;
    const Complex = struct {
        label: ?[]const u8,
        nested: ?*u8,
        count: usize,
    };

    var value: ?*Complex = try zalloc.zallocValue(allocator, Complex);
    defer zalloc.zfreeValue(allocator, Complex, &value);

    try std.testing.expect(value != null);
    try std.testing.expect(value.?.label == null);
    try std.testing.expect(value.?.nested == null);
    try std.testing.expectEqual(@as(usize, 0), value.?.count);
}
