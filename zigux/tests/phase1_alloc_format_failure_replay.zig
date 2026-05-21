const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 alloc-format failure replay keeps slab counters honest on fail paths" {
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocBytes(32, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(8, 4, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const kept = slab.kmallocBytes(6, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(kept);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "phase1 alloc-format failure replay keeps zalloc frees idempotent" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        count: u16,
        ready: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0, 0, 0 }, bytes.?);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.ready);
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);
}

test "phase1 alloc-format failure replay keeps strerror and snprintf truncation explicit" {
    var empty: [0]u8 = .{};
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(13, &empty));

    var short_error: [12]u8 = undefined;
    try std.testing.expectEqualStrings("Cannot allo", str_error_r.strErrorR(12, &short_error));

    var unknown: [16]u8 = undefined;
    try std.testing.expectEqualStrings("INTERNAL ERROR:", str_error_r.strErrorR(4096, &unknown));

    var tiny_render: [5]u8 = undefined;
    const tiny_len = vsprintf.scnprintf(&tiny_render, "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 4), tiny_len);
    try std.testing.expectEqualStrings("abcd", tiny_render[0..tiny_len]);

    var tiny_vrender: [4]u8 = undefined;
    const tiny_vlen = vsprintf.vscnprintf(&tiny_vrender, "{s}", .{"wxyz"});
    try std.testing.expectEqual(@as(usize, 3), tiny_vlen);
    try std.testing.expectEqualStrings("wxy", tiny_vrender[0..tiny_vlen]);

    var padded: [6]u8 = undefined;
    const padded_len = vsprintf.scnprintfPad(&padded, 0, "{s}", .{"zz"});
    try std.testing.expectEqual(@as(usize, 0), padded_len);
    try std.testing.expectEqual(@as(u8, 0), padded[0]);
}
