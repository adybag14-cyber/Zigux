const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab strerror vsprintf zalloc handoff chain preserves windows and owners" {
    slab.kmalloc_nr_allocated = 0;
    const allocator = std.testing.allocator;

    var slab_owner: ?[]u8 = slab.kzallocBytes(80, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memset(slab_owner.?[0..], 0x7d);
    const first_window = slab_owner.?[6..38];
    const fallback = str_error_r.strErrorR(7001, first_window);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(7001", fallback);
    try std.testing.expectEqual(@as(u8, 0x7d), slab_owner.?[5]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner.?[37]);
    try std.testing.expectEqual(@as(u8, 0x7d), slab_owner.?[38]);

    const summary_window = slab_owner.?[40..62];
    const padded = vsprintf.scnprintfPad(summary_window, 15, "err={d}", .{fallback.len});
    try std.testing.expectEqual(@as(usize, 15), padded);
    try std.testing.expectEqualSlices(u8, "err=31         ", summary_window[0..15]);
    try std.testing.expectEqual(@as(u8, 0), summary_window[15]);
    try std.testing.expectEqual(@as(u8, 0x7d), slab_owner.?[39]);
    try std.testing.expectEqual(@as(u8, 0x7d), slab_owner.?[62]);

    var z_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &z_owner);
    for (z_owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const copied = @min(padded, z_owner.?.len - 1);
    @memcpy(z_owner.?[0..copied], summary_window[0..copied]);
    z_owner.?[copied] = 0;
    try std.testing.expectEqualStrings("err=31         ", z_owner.?[0..copied]);

    const rewritten = vsprintf.scnprintf(z_owner.?[3..16], "{s}:{d}", .{ "ok", fallback.len });
    try std.testing.expectEqual(@as(usize, 5), rewritten);
    try std.testing.expectEqualSlices(u8, "err", z_owner.?[0..3]);
    try std.testing.expectEqualStrings("ok:31", z_owner.?[3 .. 3 + rewritten]);
    try std.testing.expectEqual(@as(u8, 0), z_owner.?[3 + rewritten]);

    zalloc.zfreeBytes(allocator, &z_owner);
    try std.testing.expect(z_owner == null);

    z_owner = try zalloc.zallocBytes(allocator, 32);
    try std.testing.expect(z_owner != null);
    for (z_owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "handoff chain keeps slab counters stable across failure and value reset" {
    slab.kmalloc_nr_allocated = 0;
    const allocator = std.testing.allocator;
    const Record = struct {
        errno_len: usize,
        slab_live: isize,
        ok: bool,
    };

    try std.testing.expect(slab.kmallocBytes(24, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var slab_bytes: ?[]u8 = slab.kcallocBytes(3, 16, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const known = str_error_r.strErrorR(22, slab_bytes.?[4..24]);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes.?[20]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes.?[21]);

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expectEqual(@as(usize, 0), record.?.errno_len);
    try std.testing.expectEqual(@as(isize, 0), record.?.slab_live);
    try std.testing.expectEqual(false, record.?.ok);

    record.?.errno_len = known.len;
    record.?.slab_live = slab.kmalloc_nr_allocated;
    record.?.ok = slab.slabIsAvailable();

    var report: [24]u8 = @splat(0xaa);
    const written = vsprintf.scnprintf(&report, "len={d},live={d}", .{ record.?.errno_len, record.?.slab_live });
    try std.testing.expectEqual(@as(usize, 13), written);
    try std.testing.expectEqualStrings("len=16,live=1", report[0..written]);
    try std.testing.expectEqual(@as(u8, 0), report[written]);
    try std.testing.expectEqual(@as(u8, 0xaa), report[written + 1]);

    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);
    record = try zalloc.zallocValue(allocator, Record);
    try std.testing.expectEqual(@as(usize, 0), record.?.errno_len);
    try std.testing.expectEqual(@as(isize, 0), record.?.slab_live);
    try std.testing.expectEqual(false, record.?.ok);

    slab.kfree(slab_bytes);
    slab_bytes = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
