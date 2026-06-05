const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectZeroed(bytes: []const u8) !void {
    for (bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "slab formatted window can be reset inside zalloc-owned strerror handoff" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var slab_owner: ?[]u8 = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(slab_owner.?);

    const slab_window = slab_owner.?[4..20];
    const padded = vsprintf.scnprintfPad(slab_window, 15, "slot={d}", .{7});
    try std.testing.expect(padded == 14 or padded == 15);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, slab_owner.?[0..4]);
    try std.testing.expectEqualSlices(u8, "slot=7         ", slab_owner.?[4..19]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner.?[19]);
    try expectZeroed(slab_owner.?[20..]);

    var zowner: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &zowner);
    try expectZeroed(zowner.?);

    @memcpy(zowner.?[2..17], slab_owner.?[4..19]);
    const rendered = str_error_r.strErrorR(13, zowner.?[1..19]);
    try std.testing.expectEqualStrings("Permission denied", rendered);
    try std.testing.expectEqual(@as(u8, 0), zowner.?[0]);
    try std.testing.expectEqualSlices(u8, "Permission denied", zowner.?[1..18]);
    try std.testing.expectEqual(@as(u8, 0), zowner.?[18]);
    try expectZeroed(zowner.?[19..]);

    slab.kfree(slab_owner);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    zalloc.zfreeBytes(allocator, &zowner);
    try std.testing.expect(zowner == null);
    zalloc.zfreeBytes(allocator, &zowner);
    try std.testing.expect(zowner == null);
}

test "zalloc fallback window can be summarized in slab storage after value reset" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const Record = struct {
        msg: [40]u8,
        observed_len: usize,
    };

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try expectZeroed(record.?.msg[0..]);
    try std.testing.expectEqual(@as(usize, 0), record.?.observed_len);

    const fallback = str_error_r.strErrorR(4096, record.?.msg[3..]);
    record.?.observed_len = fallback.len;
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [bu", fallback);
    try expectZeroed(record.?.msg[0..3]);
    try std.testing.expectEqual(@as(u8, 0), record.?.msg[39]);

    var summary: ?[]u8 = slab.kmallocBytes(48, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(summary);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const written = vsprintf.scnprintf(summary.?[5..35], "err-len={d}", .{record.?.observed_len});
    try std.testing.expectEqual(@as(usize, 10), written);
    try expectZeroed(summary.?[0..5]);
    try std.testing.expectEqualStrings("err-len=36", summary.?[5 .. 5 + written]);
    try std.testing.expectEqual(@as(u8, 0), summary.?[5 + written]);
    try expectZeroed(summary.?[16..]);

    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);
    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(summary);
    summary = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
