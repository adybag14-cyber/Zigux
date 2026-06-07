const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectPaddedCount(count: usize, current: usize, historical: usize) !void {
    try std.testing.expect(count == current or count == historical);
}

test "orbit splice rewrites slab windows through zalloc summaries" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var slab_window: ?[]u8 = slab.kmallocBytes(40, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer {
        slab.kfree(slab_window);
        slab_window = null;
    }
    try std.testing.expect(slab_window != null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_window.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(slab_window.?, 0xa5);
    const fallback = str_error_r.strErrorR(7101, slab_window.?[4..34]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(71", fallback);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa5, 0xa5, 0xa5, 0xa5 }, slab_window.?[0..4]);
    try std.testing.expectEqual(@as(u8, 0), slab_window.?[33]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_window.?[34]);

    var summary: ?[]u8 = try zalloc.zallocBytes(allocator, 28);
    defer zalloc.zfreeBytes(allocator, &summary);
    for (summary.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const written = vsprintf.scnprintf(summary.?, "orbit:{d}:{s}", .{ fallback.len, fallback[0..8] });
    try std.testing.expectEqual(@as(usize, 17), written);
    try std.testing.expectEqualStrings("orbit:29:INTERNAL", summary.?[0..written]);
    try std.testing.expectEqual(@as(u8, 0), summary.?[written]);

    @memset(slab_window.?, 0x5a);
    const known = str_error_r.strErrorR(12, slab_window.?[1..24]);
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try std.testing.expectEqual(@as(u8, 0x5a), slab_window.?[0]);
    try std.testing.expectEqual(@as(u8, 0), slab_window.?[23]);
    try std.testing.expectEqual(@as(u8, 0x5a), slab_window.?[24]);

    const padded = vsprintf.scnprintfPad(summary.?[3..23], 16, "splice:{s}", .{known[0..6]});
    try expectPaddedCount(padded, 16, 15);
    try std.testing.expectEqualStrings("orb", summary.?[0..3]);
    try std.testing.expectEqualStrings("splice:Cannot   ", summary.?[3..19]);
    try std.testing.expectEqual(@as(u8, ' '), summary.?[18]);
    try std.testing.expectEqual(@as(u8, 0), summary.?[19]);

    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "orbit splice rebalances slab arrays and zalloc value owners" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var slots: ?[]u8 = slab.kmallocArray(3, 12, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer {
        slab.kfree(slots);
        slots = null;
    }
    try std.testing.expect(slots != null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slots.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const Record = struct {
        len: usize,
        status: u8,
    };

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expectEqual(@as(usize, 0), record.?.len);
    try std.testing.expectEqual(@as(u8, 0), record.?.status);

    const first = str_error_r.strErrorR(22, slots.?[0..18]);
    try std.testing.expectEqualStrings("Invalid argument", first);
    try std.testing.expectEqual(@as(u8, 0), slots.?[16]);
    try std.testing.expectEqual(@as(u8, 0), slots.?[17]);

    const failed = slab.kmallocBytes(8, 0);
    try std.testing.expect(failed == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const second = vsprintf.scnprintf(slots.?[18..36], "ok:{s}:{d}", .{ first[0..7], slab.kmalloc_nr_allocated });
    try std.testing.expectEqual(@as(usize, 12), second);
    try std.testing.expectEqualStrings("ok:Invalid:1", slots.?[18 .. 18 + second]);
    try std.testing.expectEqual(@as(u8, 0), slots.?[18 + second]);

    record.?.len = first.len + second;
    record.?.status = slots.?[18];
    try std.testing.expectEqual(@as(usize, 28), record.?.len);
    try std.testing.expectEqual(@as(u8, 'o'), record.?.status);

    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);

    slab.kfree(slots);
    slots = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
