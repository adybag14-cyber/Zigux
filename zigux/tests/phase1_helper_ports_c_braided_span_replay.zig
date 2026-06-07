const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const Report = struct {
    fallback_len: usize,
    padded_len: usize,
    direct_len: usize,
    allocation_count: isize,
};

fn expectRepeated(bytes: []const u8, expected: u8) !void {
    for (bytes) |byte| {
        try std.testing.expectEqual(expected, byte);
    }
}

test "phase 1 helper ports C braid slab fallback spans into zalloc summaries" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_owner = slab.kzallocBytes(48, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectRepeated(slab_owner, 0);
    @memset(slab_owner, 0xcc);

    const fallback_window = slab_owner[4..33];
    const fallback = str_error_r.strErrorR(513, fallback_window);
    try std.testing.expectEqual(@as(usize, 28), fallback.len);
    try std.testing.expect(std.mem.startsWith(u8, fallback, "INTERNAL ERROR"));
    try std.testing.expectEqual(@as(u8, 0), slab_owner[32]);
    try expectRepeated(slab_owner[0..4], 0xcc);
    try expectRepeated(slab_owner[33..], 0xcc);

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &zbytes);
    try expectRepeated(zbytes.?, 0);

    const summary_window = zbytes.?[3..25];
    const padded = vsprintf.scnprintfPad(summary_window, 16, "len={d};{s}", .{ fallback.len, fallback[0..3] });
    try std.testing.expectEqual(@as(usize, 16), padded);
    try std.testing.expectEqualStrings("len=28;INT      ", summary_window[0..padded]);
    try std.testing.expectEqual(@as(u8, 0), summary_window[padded]);
    try expectRepeated(zbytes.?[0..3], 0);
    try expectRepeated(zbytes.?[25..], 0);

    const direct = vsprintf.scnprintf(slab_owner[34..47], "{s}:{d}", .{ summary_window[0..3], padded });
    try std.testing.expectEqual(@as(usize, 6), direct);
    try std.testing.expectEqualStrings("len:16", slab_owner[34 .. 34 + direct]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[34 + direct]);
    try std.testing.expectEqual(@as(u8, 0xcc), slab_owner[47]);

    var report: ?*Report = try zalloc.zallocValue(allocator, Report);
    defer zalloc.zfreeValue(allocator, Report, &report);
    try std.testing.expectEqual(@as(usize, 0), report.?.fallback_len);
    report.?.* = .{
        .fallback_len = fallback.len,
        .padded_len = padded,
        .direct_len = direct,
        .allocation_count = slab.kmalloc_nr_allocated,
    };
    try std.testing.expectEqual(@as(usize, 28), report.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 16), report.?.padded_len);
    try std.testing.expectEqual(@as(usize, 6), report.?.direct_len);
    try std.testing.expectEqual(@as(isize, 1), report.?.allocation_count);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "phase 1 helper ports C recycle braided array rows through known and fallback renderers" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const rows = slab.kcallocBytes(3, 12, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(rows);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectRepeated(rows, 0);
    @memset(rows, 0xdd);

    const row0 = rows[0..12];
    const row1 = rows[12..24];
    const row2 = rows[24..36];

    const known = str_error_r.strErrorR(0, row0[1..10]);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 0xdd), row0[0]);
    try std.testing.expectEqual(@as(u8, 0), row0[8]);
    try expectRepeated(row0[10..], 0xdd);

    const padded = vsprintf.scnprintfPad(row1[2..11], 7, "{s}", .{known[0..2]});
    try std.testing.expectEqual(@as(usize, 7), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 0xdd, 'S', 'u', ' ', ' ', ' ', ' ', ' ', 0, 0xdd }, row1[0..11]);

    const fallback = str_error_r.strErrorR(4097, row2[1..]);
    try std.testing.expectEqual(@as(usize, 10), fallback.len);
    try std.testing.expectEqualStrings("INTERNAL E", fallback);
    try std.testing.expectEqual(@as(u8, 0xdd), row2[0]);
    try std.testing.expectEqual(@as(u8, 0), row2[11]);

    var summary: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &summary);
    try expectRepeated(summary.?, 0);
    const summary_len = vsprintf.scnprintf(summary.?, "{s}|{s}|{d}", .{ known[0..2], fallback[0..3], padded });
    try std.testing.expectEqual(@as(usize, 8), summary_len);
    try std.testing.expectEqualStrings("Su|INT|7", summary.?[0..summary_len]);

    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);
    summary = try zalloc.zallocBytes(allocator, 6);
    try expectRepeated(summary.?, 0);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
