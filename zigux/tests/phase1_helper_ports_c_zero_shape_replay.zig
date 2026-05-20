const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 zero-shape replay keeps slab counters balanced for zero-length allocations" {
    slab.kmalloc_nr_allocated = 0;

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    errdefer slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zero_count_array = slab.kmallocArray(0, 7, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    errdefer slab.kfree(zero_count_array);
    try std.testing.expectEqual(@as(usize, 0), zero_count_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    const zero_size_array = slab.kmallocArray(5, 0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    errdefer slab.kfree(zero_size_array);
    try std.testing.expectEqual(@as(usize, 0), zero_size_array.len);
    try std.testing.expectEqual(@as(isize, 3), slab.kmalloc_nr_allocated);

    slab.kfree(zero_count_array);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(zero_size_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 zero-shape replay keeps exact-fit strerror ownership stable across reuse" {
    var buffer: [48]u8 = undefined;

    const generated = str_error_r.strErrorR(4096, &buffer);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 48)=22", generated);
    try std.testing.expectEqual(@intFromPtr(&buffer[0]), @intFromPtr(generated.ptr));
    try std.testing.expectEqual(@as(u8, 0), buffer[generated.len]);

    const known = str_error_r.strErrorR(0, &buffer);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@intFromPtr(&buffer[0]), @intFromPtr(known.ptr));
    try std.testing.expectEqual(@as(u8, 0), buffer[known.len]);
}

test "lane10 zero-shape replay keeps minimal printf widths reusable" {
    var buffer: [6]u8 = undefined;

    const padded = vsprintf.scnprintfPad(&buffer, 1, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 1), padded);
    try std.testing.expectEqualStrings("z", buffer[0..padded]);
    try std.testing.expectEqual(@as(u8, 0), buffer[padded]);

    const plain = vsprintf.vscnprintf(&buffer, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 2), plain);
    try std.testing.expectEqualStrings("ok", buffer[0..plain]);
    try std.testing.expectEqual(@as(u8, 0), buffer[plain]);
}

test "lane10 zero-shape replay keeps zero-sized zalloc state free-safe" {
    const allocator = std.testing.allocator;
    const Empty = struct {};
    const Nested = struct {
        bytes: [3]u8,
        maybe_count: ?usize,
    };

    var empty_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(empty_bytes != null);
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.?.len);
    zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expect(empty_bytes == null);
    zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expect(empty_bytes == null);

    var empty_value: ?*Empty = try zalloc.zallocValue(allocator, Empty);
    zalloc.zfreeValue(allocator, Empty, &empty_value);
    try std.testing.expect(empty_value == null);
    zalloc.zfreeValue(allocator, Empty, &empty_value);
    try std.testing.expect(empty_value == null);

    var nested: ?*Nested = try zalloc.zallocValue(allocator, Nested);
    nested.?.bytes = .{ 0xaa, 0xbb, 0xcc };
    nested.?.maybe_count = 9;
    zalloc.zfreeValue(allocator, Nested, &nested);
    try std.testing.expect(nested == null);

    nested = try zalloc.zallocValue(allocator, Nested);
    defer zalloc.zfreeValue(allocator, Nested, &nested);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0 }, &nested.?.bytes);
    try std.testing.expect(nested.?.maybe_count == null);
}

test "lane10 zero-shape replay keeps zero-capacity caller views inert and reusable" {
    var buffer = [_]u8{0xaa} ** 32;

    const empty_error = str_error_r.strErrorR(13, buffer[0..0]);
    try std.testing.expectEqual(@as(usize, 0), empty_error.len);

    const empty_print = vsprintf.scnprintf(buffer[0..0], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), empty_print);

    for (buffer) |value| {
        try std.testing.expectEqual(@as(u8, 0xaa), value);
    }

    const rendered_error = str_error_r.strErrorR(13, &buffer);
    try std.testing.expectEqualStrings("Permission denied", rendered_error);
    try std.testing.expectEqual(@intFromPtr(&buffer[0]), @intFromPtr(rendered_error.ptr));
    try std.testing.expectEqual(@as(u8, 0), buffer[rendered_error.len]);

    const reused_print = vsprintf.vscnprintf(&buffer, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 2), reused_print);
    try std.testing.expectEqualStrings("ok", buffer[0..reused_print]);
    try std.testing.expectEqual(@as(u8, 0), buffer[reused_print]);
}
