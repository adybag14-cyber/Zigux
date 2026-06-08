const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C forge bridge replay" {
    const allocator = std.testing.allocator;
    const Record = struct {
        slab_len: usize,
        known_len: usize,
        fallback_len: usize,
        summary_len: usize,
        slab_count_after_failures: isize,
        slab_available: bool,
    };

    slab.kmalloc_nr_allocated = 0;

    var slab_bytes = slab.kmallocArray(2, 16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 32), slab_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memset(slab_bytes, 0x5a);
    const known = str_error_r.strErrorR(22, slab_bytes[1..18]);
    const fallback = str_error_r.strErrorR(4096, slab_bytes[18..31]);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqualStrings("INTERNAL ERR", fallback);
    try std.testing.expectEqual(@as(u8, 0x5a), slab_bytes[0]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[17]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[30]);
    try std.testing.expectEqual(@as(u8, 0x5a), slab_bytes[31]);

    var summary: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &summary);
    for (summary.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const written = vsprintf.scnprintfPad(summary.?, 20, "{s}:{s}:{d}", .{
        known[0..7],
        fallback[0..8],
        slab_bytes.len,
    });
    try std.testing.expectEqual(@as(usize, 20), written);
    try std.testing.expectEqualStrings("Invalid:INTERNAL:32 ", summary.?[0..written]);
    try std.testing.expectEqual(@as(u8, 0), summary.?[written]);
    try std.testing.expectEqual(@as(u8, 0), summary.?[written + 1]);

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expectEqual(@as(usize, 0), record.?.summary_len);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    record.?.* = .{
        .slab_len = slab_bytes.len,
        .known_len = known.len,
        .fallback_len = fallback.len,
        .summary_len = written,
        .slab_count_after_failures = slab.kmalloc_nr_allocated,
        .slab_available = slab.slabIsAvailable(),
    };
    try std.testing.expectEqual(@as(usize, 32), record.?.slab_len);
    try std.testing.expectEqual(@as(usize, 16), record.?.known_len);
    try std.testing.expectEqual(@as(usize, 12), record.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 20), record.?.summary_len);
    try std.testing.expectEqual(@as(isize, 1), record.?.slab_count_after_failures);
    try std.testing.expect(record.?.slab_available);

    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);
    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);

    slab.kfree(slab_bytes);
    slab_bytes = &[_]u8{};
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
