const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "single-slot and zero-sized helper views rebound cleanly" {
    slab.kmalloc_nr_allocated = 0;
    const empty_alloc = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty_alloc.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty_alloc);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var known_buffer = [_]u8{0xaa};
    const known = str_error_r.strErrorR(2, &known_buffer);
    try std.testing.expectEqual(@as(usize, 0), known.len);
    try std.testing.expectEqual(@as(u8, 0), known_buffer[0]);

    var unknown_buffer = [_]u8{0xbb};
    const unknown = str_error_r.strErrorR(4096, &unknown_buffer);
    try std.testing.expectEqual(@as(usize, 0), unknown.len);
    try std.testing.expectEqual(@as(u8, 0), unknown_buffer[0]);

    var tiny_direct = [_]u8{0xcc};
    const tiny_written = vsprintf.scnprintf(&tiny_direct, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), tiny_written);
    try std.testing.expectEqual(@as(u8, 0), tiny_direct[0]);

    var rebound = [_]u8{0xdd} ** 6;
    const rebound_written = vsprintf.scnprintfPad(&rebound, rebound.len - 1, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 4), rebound_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', ' ', ' ', ' ', 0 }, &rebound);

    const allocator = std.testing.allocator;
    var zero_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(zero_bytes != null);
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.?.len);
    zalloc.zfreeBytes(allocator, &zero_bytes);
    try std.testing.expect(zero_bytes == null);
    zalloc.zfreeBytes(allocator, &zero_bytes);
    try std.testing.expect(zero_bytes == null);
}
