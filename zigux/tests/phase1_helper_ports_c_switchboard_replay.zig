const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const testing = std.testing;

test "switchboard relays slab windows through strerror and formatted summaries" {
    slab.kmalloc_nr_allocated = 0;

    const board = slab.kmallocBytes(96, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(board);
    try testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (board) |byte| {
        try testing.expectEqual(@as(u8, 0), byte);
    }

    const known_window = board[5..29];
    const known = str_error_r.strErrorR(22, known_window);
    try testing.expectEqualStrings("Invalid argument", known);
    try testing.expectEqual(@as(u8, 0), board[5 + known.len]);
    try testing.expectEqual(@as(u8, 0), board[4]);
    try testing.expectEqual(@as(u8, 0), board[29]);

    const fallback_window = board[40..84];
    const fallback = str_error_r.strErrorR(901, fallback_window);
    try testing.expectEqualStrings("INTERNAL ERROR: strerror_r(901, [buf], 44)=", fallback);
    try testing.expectEqual(@as(usize, 43), fallback.len);
    try testing.expectEqual(@as(u8, 0), board[40 + fallback.len]);
    try testing.expectEqual(@as(u8, 0), board[39]);
    try testing.expectEqual(@as(u8, 0), board[84]);

    var summary: [36]u8 = @splat(0xaa);
    const summary_len = vsprintf.scnprintf(&summary, "switch:{d}:{d}", .{ known.len, fallback.len });
    try testing.expectEqual(@as(usize, 12), summary_len);
    try testing.expectEqualStrings("switch:16:43", summary[0..summary_len]);
    try testing.expectEqual(@as(u8, 0), summary[summary_len]);
    try testing.expectEqual(@as(u8, 0xaa), summary[summary_len + 1]);

    var padded: [24]u8 = @splat(0xbb);
    const padded_len = vsprintf.scnprintfPad(padded[3..20], 15, "slot:{d}", .{slab.kmalloc_nr_allocated});
    try testing.expect(padded_len == 14 or padded_len == 15);
    try testing.expectEqualSlices(u8, &[_]u8{ 0xbb, 0xbb, 0xbb }, padded[0..3]);
    try testing.expectEqualStrings("slot:1         ", padded[3..18]);
    try testing.expectEqual(@as(u8, 0), padded[18]);
    try testing.expectEqual(@as(u8, 0xbb), padded[20]);
}

test "switchboard resets zalloc owners while slab failure counters stay stable" {
    const allocator = testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 28);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try testing.expectEqual(@as(u8, 0), byte);
    }

    const denial = str_error_r.strErrorR(13, bytes.?[1..21]);
    try testing.expectEqualStrings("Permission denied", denial);
    try testing.expectEqual(@as(u8, 0), bytes.?[1 + denial.len]);
    try testing.expectEqual(@as(u8, 0), bytes.?[0]);

    const relay_len = vsprintf.vscnprintf(bytes.?[3..18], "deny:{d}", .{denial.len});
    try testing.expectEqual(@as(usize, 7), relay_len);
    try testing.expectEqualStrings("deny:17", bytes.?[3 .. 3 + relay_len]);
    try testing.expectEqual(@as(u8, 0), bytes.?[3 + relay_len]);

    zalloc.zfreeBytes(allocator, &bytes);
    try testing.expect(bytes == null);

    var reacquired: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &reacquired);
    try testing.expect(reacquired != null);
    try testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0 }, reacquired.?);

    const before_failed = slab.kmalloc_nr_allocated;
    try testing.expect(slab.kmallocBytes(16, 0) == null);
    try testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try testing.expectEqual(before_failed, slab.kmalloc_nr_allocated);

    const Record = struct {
        count: usize,
        ok: bool,
        tag: [4]u8,
    };

    var record: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &record);
    try testing.expect(record != null);
    try testing.expectEqual(@as(usize, 0), record.?.count);
    try testing.expectEqual(false, record.?.ok);
    try testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &record.?.tag);

    record.?.count = relay_len;
    record.?.ok = true;
    record.?.tag = "swbd".*;
    try testing.expectEqual(@as(usize, 7), record.?.count);
    try testing.expect(record.?.ok);
    try testing.expectEqualSlices(u8, "swbd", &record.?.tag);

    zalloc.zfreeValue(allocator, Record, &record);
    try testing.expect(record == null);
}
