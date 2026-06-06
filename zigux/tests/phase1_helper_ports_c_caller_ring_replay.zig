const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 caller ring carries strerror output into zalloc summary" {
    slab.kmalloc_nr_allocated = 0;

    var slab_owner: ?[]u8 = slab.kmallocBytes(64, slab.GFP_KERNEL | slab.__GFP_ZERO);
    const slab_bytes = slab_owner orelse return error.TestUnexpectedResult;
    defer {
        slab.kfree(slab_owner);
        slab_owner = null;
    }

    const rendered = str_error_r.strErrorR(4096, slab_bytes[4..42]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf", rendered);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[41]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[42]);

    const allocator = std.testing.allocator;
    var summary: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary != null);

    const summary_bytes = summary.?;
    const summary_written = vsprintf.scnprintf(summary_bytes[1..18], "{s}|{d}", .{ rendered[0..8], rendered.len });
    try std.testing.expectEqual(@as(usize, 11), summary_written);
    try std.testing.expectEqual(@as(u8, 0), summary_bytes[0]);
    try std.testing.expectEqualStrings("INTERNAL|37", summary_bytes[1 .. 1 + summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary_bytes[1 + summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary_bytes[18]);

    const padded_written = vsprintf.scnprintfPad(slab_bytes[44..58], 12, "{s}", .{summary_bytes[1..9]});
    try std.testing.expectEqual(@as(usize, 12), padded_written);
    try std.testing.expectEqualStrings("INTERNAL    ", slab_bytes[44 .. 44 + padded_written]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[56]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[58]);

    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);

    slab.kfree(slab_owner);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 ring release keeps failure paths from disturbing owners" {
    slab.kmalloc_nr_allocated = 0;

    var live: ?[]u8 = slab.kmallocBytes(16, slab.GFP_KERNEL | slab.__GFP_ZERO);
    const live_bytes = live orelse return error.TestUnexpectedResult;
    defer {
        slab.kfree(live);
        live = null;
    }
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const known = str_error_r.strErrorR(22, live_bytes[2..]);
    try std.testing.expectEqualStrings("Invalid argum", known);
    try std.testing.expectEqual(@as(u8, 0), live_bytes[15]);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualStrings("Invalid argum", live_bytes[2..15]);

    const allocator = std.testing.allocator;
    const Record = struct {
        count: usize,
        ok: bool,
        bytes: [3]u8,
    };

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record != null);
    try std.testing.expectEqual(@as(usize, 0), record.?.count);
    try std.testing.expectEqual(false, record.?.ok);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &record.?.bytes);

    record.?.count = vsprintf.vscnprintf(live_bytes[0..8], "r={d}", .{known.len});
    try std.testing.expectEqual(@as(usize, 4), record.?.count);
    try std.testing.expectEqualStrings("r=13", live_bytes[0..4]);
    try std.testing.expectEqual(@as(u8, 0), live_bytes[4]);

    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);

    slab.kfree(live);
    live = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
