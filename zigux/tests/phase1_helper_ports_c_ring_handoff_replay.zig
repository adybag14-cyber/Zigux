const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab strerror windows hand off through zalloc formatting rings" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var ring_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &ring_owner);
    for (ring_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const slab_owner = slab.kmallocBytes(24, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(slab_owner, 0xcc);

    const message = str_error_r.strErrorR(22, slab_owner[3..21]);
    try std.testing.expectEqualStrings("Invalid argument", message);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc }, slab_owner[0..3]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[19]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc }, slab_owner[21..24]);

    const rendered = vsprintf.scnprintf(ring_owner.?[4..24], "K:{s}", .{message});
    try std.testing.expectEqual(@as(usize, 18), rendered);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, ring_owner.?[0..4]);
    try std.testing.expectEqualStrings("K:Invalid argument", ring_owner.?[4 .. 4 + rendered]);
    try std.testing.expectEqual(@as(u8, 0), ring_owner.?[4 + rendered]);
    for (ring_owner.?[24..]) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(slab_owner);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &ring_owner);
    try std.testing.expect(ring_owner == null);
}

test "array rows preserve counters while fallback text pads into zeroed value owners" {
    const allocator = std.testing.allocator;
    const Summary = struct {
        padded: [8]u8,
        fallback_len: usize,
        count_after_fail: isize,
        cleaned: bool,
    };

    slab.kmalloc_nr_allocated = 0;
    var summary: ?*Summary = try zalloc.zallocValue(allocator, Summary);
    defer zalloc.zfreeValue(allocator, Summary, &summary);
    try std.testing.expectEqual(@as(usize, 0), summary.?.fallback_len);
    try std.testing.expectEqual(false, summary.?.cleaned);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0, 0, 0 }, &summary.?.padded);

    const rows = slab.kmallocArray(2, 8, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(rows, 0xee);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    summary.?.count_after_fail = slab.kmalloc_nr_allocated;

    const fallback = str_error_r.strErrorR(4096, rows[2..14]);
    try std.testing.expectEqualStrings("INTERNAL ER", fallback);
    try std.testing.expectEqual(@as(u8, 0), rows[13]);
    try std.testing.expectEqual(@as(u8, 0xee), rows[14]);
    summary.?.fallback_len = fallback.len;

    const padded_len = vsprintf.scnprintfPad(summary.?.padded[0..], 7, "r{d}", .{summary.?.fallback_len});
    try std.testing.expect(padded_len <= 7);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'r', '1', '1', ' ', ' ', ' ', ' ', 0 }, &summary.?.padded);

    slab.kfree(rows);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    summary.?.cleaned = true;
    try std.testing.expectEqual(true, summary.?.cleaned);

    zalloc.zfreeValue(allocator, Summary, &summary);
    try std.testing.expect(summary == null);
    zalloc.zfreeValue(allocator, Summary, &summary);
    try std.testing.expect(summary == null);
}
