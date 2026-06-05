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

test "exact fit slab render transfers into zalloc strerror owner" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_owner = slab.kmallocBytes(18, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const slab_window = slab_owner[2..10];
    const slab_written = vsprintf.scnprintf(slab_window, "{s}", .{"handoff"});
    try std.testing.expectEqual(@as(usize, 7), slab_written);
    try std.testing.expectEqualStrings("handoff", slab_window[0..slab_written]);
    try std.testing.expectEqual(@as(u8, 0), slab_window[slab_written]);
    try expectZeroed(slab_owner[0..2]);
    try expectZeroed(slab_owner[10..]);

    var zalloc_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &zalloc_owner);
    try expectZeroed(zalloc_owner.?);

    @memcpy(zalloc_owner.?[1 .. 1 + slab_written], slab_window[0..slab_written]);
    try std.testing.expectEqualStrings("handoff", zalloc_owner.?[1 .. 1 + slab_written]);
    try std.testing.expectEqual(@as(u8, 0), zalloc_owner.?[0]);
    try expectZeroed(zalloc_owner.?[1 + slab_written ..]);

    const rendered = str_error_r.strErrorR(22, zalloc_owner.?[0..17]);
    try std.testing.expectEqualStrings("Invalid argument", rendered);
    try std.testing.expectEqual(@as(u8, 0), zalloc_owner.?[16]);
    try std.testing.expectEqual(@as(u8, 0), zalloc_owner.?[17]);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zero length zalloc view and slab exact strerror summary keep owners balanced" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var empty_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(empty_owner != null);
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(13, empty_owner.?).len);
    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(empty_owner.?, "{s}", .{"ignored"}));
    zalloc.zfreeBytes(allocator, &empty_owner);
    try std.testing.expect(empty_owner == null);
    zalloc.zfreeBytes(allocator, &empty_owner);
    try std.testing.expect(empty_owner == null);

    const summary = slab.kmallocBytes(30, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(summary);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const exact = str_error_r.strErrorR(12, summary[1..24]);
    try std.testing.expectEqualStrings("Cannot allocate memory", exact);
    try std.testing.expectEqual(@as(u8, 0), summary[0]);
    try std.testing.expectEqual(@as(u8, 0), summary[23]);
    try expectZeroed(summary[24..]);

    const Record = struct {
        exact_len: usize,
        padded_len: usize,
        zero_len: usize,
    };
    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expectEqual(@as(usize, 0), record.?.exact_len);
    try std.testing.expectEqual(@as(usize, 0), record.?.padded_len);
    try std.testing.expectEqual(@as(usize, 0), record.?.zero_len);

    record.?.exact_len = exact.len;
    record.?.zero_len = str_error_r.strErrorR(4096, summary[0..0]).len;
    const padded = vsprintf.scnprintfPad(summary[24..30], 5, "{s}", .{"ok"});
    try std.testing.expect(padded == 4 or padded == 5);
    record.?.padded_len = padded;
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', ' ', ' ', ' ', 0 }, summary[24..30]);

    try std.testing.expectEqual(@as(usize, 22), record.?.exact_len);
    try std.testing.expectEqual(@as(usize, 0), record.?.zero_len);
    try std.testing.expect(record.?.padded_len == 4 or record.?.padded_len == 5);

    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);
    zalloc.zfreeValue(allocator, Record, &record);
    try std.testing.expect(record == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
