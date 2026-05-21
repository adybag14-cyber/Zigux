const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C keep zero-sized allocations and frees isolated" {
    slab.kmalloc_nr_allocated = 0;

    const empty_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const empty_array = slab.kmallocArray(0, 8, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(usize, 0), empty_bytes.len);
    try std.testing.expectEqual(@as(usize, 0), empty_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(empty_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "phase1 helper ports C keep strErrorR writes inside caller windows" {
    const message = "Permission denied";

    var exact_storage = [_]u8{0xaa} ** (message.len + 3);
    const exact_view = exact_storage[1 .. 1 + message.len + 1];
    const exact = str_error_r.strErrorR(13, exact_view);
    try std.testing.expectEqualStrings(message, exact);
    try std.testing.expectEqualStrings(message, exact_view[0..message.len]);
    try std.testing.expectEqual(@as(u8, 0), exact_view[message.len]);
    try std.testing.expectEqual(@as(u8, 0xaa), exact_storage[0]);
    try std.testing.expectEqual(@as(u8, 0xaa), exact_storage[exact_storage.len - 1]);

    var tiny_storage = [_]u8{0xbb} ** 3;
    const tiny_view = tiny_storage[1..2];
    const tiny = str_error_r.strErrorR(4096, tiny_view);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, 0), tiny_view[0]);
    try std.testing.expectEqual(@as(u8, 0xbb), tiny_storage[0]);
    try std.testing.expectEqual(@as(u8, 0xbb), tiny_storage[2]);
}

test "phase1 helper ports C keep vsprintf writes inside exact-fit and one-byte views" {
    var exact_storage = [_]u8{0xcc} ** 10;
    const exact_view = exact_storage[1..9];
    const exact_written = vsprintf.scnprintf(exact_view, "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqual(@as(usize, 7), exact_written);
    try std.testing.expectEqualStrings("zigux:7", exact_view[0..exact_written]);
    try std.testing.expectEqual(@as(u8, 0), exact_view[exact_written]);
    try std.testing.expectEqual(@as(u8, 0xcc), exact_storage[0]);
    try std.testing.expectEqual(@as(u8, 0xcc), exact_storage[9]);

    var one_byte_storage = [_]u8{0xdd} ** 3;
    const one_byte_view = one_byte_storage[1..2];
    const padded_written = vsprintf.scnprintfPad(one_byte_view, 4, "id={d}", .{7});
    try std.testing.expectEqual(@as(usize, 0), padded_written);
    try std.testing.expectEqual(@as(u8, 0), one_byte_view[0]);
    try std.testing.expectEqual(@as(u8, 0xdd), one_byte_storage[0]);
    try std.testing.expectEqual(@as(u8, 0xdd), one_byte_storage[2]);
}

test "phase1 helper ports C keep zalloc zero-state and optional reset visible" {
    const allocator = std.testing.allocator;

    var empty_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.?.len);
    zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expect(empty_bytes == null);
    zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expect(empty_bytes == null);

    const Pair = struct {
        bytes: [4]u8,
        enabled: bool,
    };

    var first: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &first);
    first.?.bytes = .{ 1, 2, 3, 4 };
    first.?.enabled = true;
    zalloc.zfreeValue(allocator, Pair, &first);
    try std.testing.expect(first == null);

    var second: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &second);
    try std.testing.expectEqual(std.mem.zeroes([4]u8), second.?.bytes);
    try std.testing.expectEqual(false, second.?.enabled);
}
