const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab error window cascades through zalloc release and zeroed reacquire" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_owner = slab.kmallocBytes(20, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    @memset(slab_owner, 0x91);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var ring_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 28);
    defer zalloc.zfreeBytes(allocator, &ring_owner);
    for (ring_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const message = str_error_r.strErrorR(13, slab_owner[1..19]);
    try std.testing.expectEqualStrings("Permission denied", message);
    try std.testing.expectEqual(@as(u8, 0x91), slab_owner[0]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[18]);
    try std.testing.expectEqual(@as(u8, 0x91), slab_owner[19]);

    const written = vsprintf.scnprintfPad(
        ring_owner.?[3..23],
        12,
        "E:{s}:{d}",
        .{ message, slab.kmalloc_nr_allocated },
    );
    try std.testing.expectEqual(@as(usize, 12), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, ring_owner.?[0..3]);
    try std.testing.expectEqualStrings("E:Permission", ring_owner.?[3 .. 3 + written]);
    try std.testing.expectEqual(@as(u8, 0), ring_owner.?[3 + written]);
    for (ring_owner.?[23..]) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(slab_owner);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &ring_owner);
    try std.testing.expect(ring_owner == null);

    ring_owner = try zalloc.zallocBytes(allocator, 28);
    defer zalloc.zfreeBytes(allocator, &ring_owner);
    for (ring_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "array fallback summary survives failure then value owner zeroes after release" {
    const allocator = std.testing.allocator;
    const Summary = struct {
        headline: [10]u8,
        fallback_len: usize,
        slab_after_fail: isize,
    };

    slab.kmalloc_nr_allocated = 0;
    var summary: ?*Summary = try zalloc.zallocValue(allocator, Summary);
    defer zalloc.zfreeValue(allocator, Summary, &summary);
    try std.testing.expectEqual(@as(usize, 0), summary.?.fallback_len);
    try std.testing.expectEqual(@as(isize, 0), summary.?.slab_after_fail);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }, &summary.?.headline);

    const rows = slab.kmallocArray(3, 6, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 18), rows.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(rows, 0x77);

    try std.testing.expect(slab.kmallocBytes(4, slab.GFP_KERNEL & ~slab.__GFP_DIRECT_RECLAIM) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    summary.?.slab_after_fail = slab.kmalloc_nr_allocated;

    const fallback = str_error_r.strErrorR(5000, rows[4..17]);
    try std.testing.expectEqualStrings("INTERNAL ERR", fallback);
    try std.testing.expectEqual(@as(usize, 12), fallback.len);
    try std.testing.expectEqual(@as(u8, 0x77), rows[3]);
    try std.testing.expectEqual(@as(u8, 0), rows[16]);
    try std.testing.expectEqual(@as(u8, 0x77), rows[17]);
    summary.?.fallback_len = fallback.len;

    const note_len = vsprintf.scnprintf(
        summary.?.headline[0..],
        "F{d}:C{d}",
        .{ summary.?.fallback_len, summary.?.slab_after_fail },
    );
    try std.testing.expectEqual(@as(usize, 6), note_len);
    try std.testing.expectEqualStrings("F12:C1", summary.?.headline[0..note_len]);
    try std.testing.expectEqual(@as(u8, 0), summary.?.headline[note_len]);
    try std.testing.expectEqual(@as(u8, 0), summary.?.headline[9]);

    slab.kfree(rows);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    zalloc.zfreeValue(allocator, Summary, &summary);
    try std.testing.expect(summary == null);

    summary = try zalloc.zallocValue(allocator, Summary);
    defer zalloc.zfreeValue(allocator, Summary, &summary);
    try std.testing.expectEqual(@as(usize, 0), summary.?.fallback_len);
    try std.testing.expectEqual(@as(isize, 0), summary.?.slab_after_fail);
    for (summary.?.headline) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}
