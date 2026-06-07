const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const MergeRecord = struct {
    errnum: i32,
    caller_len: usize,
    rendered_len: usize,
    summary_len: usize,
};

test "lane10 merge ladder carries slab strerror windows into zalloc summaries" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    defer std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated) catch @panic("slab allocation counter leaked");

    var caller_a = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(caller_a);
    var caller_b = slab.kmallocBytes(28, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(caller_b);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    const known = str_error_r.strErrorR(12, caller_a[3..26]);
    const fallback = str_error_r.strErrorR(5101, caller_b[2..24]);
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strer", fallback);
    try std.testing.expectEqual(@as(u8, 0), caller_a[3 + known.len]);
    try std.testing.expectEqual(@as(u8, 0), caller_b[2 + fallback.len]);
    try std.testing.expectEqual(@as(u8, 0), caller_a[0]);
    try std.testing.expectEqual(@as(u8, 0), caller_b[0]);

    var merged: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &merged);
    for (merged.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const merged_len = vsprintf.scnprintf(
        merged.?,
        "{s}|{s}|{d}",
        .{ known[0..6], fallback[0..8], caller_b[2..24].len },
    );
    try std.testing.expectEqualStrings("Cannot|INTERNAL|22", merged.?[0..merged_len]);
    try std.testing.expectEqual(@as(u8, 0), merged.?[merged_len]);

    var padded = slab.kmallocBytes(24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(padded);
    const padded_len = vsprintf.scnprintfPad(padded[1..20], 12, "{s}", .{merged.?[0..merged_len]});
    try std.testing.expect(padded_len == 11 or padded_len == 12);
    try std.testing.expectEqualStrings("Cannot|INTER", padded[1..13]);
    try std.testing.expectEqual(@as(u8, 0), padded[13]);

    const records = slab.kmallocArray(2, @sizeOf(MergeRecord), slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(records);
    try std.testing.expectEqual(@as(isize, 4), slab.kmalloc_nr_allocated);

    const typed_records = std.mem.bytesAsSlice(MergeRecord, records);
    typed_records[0] = .{
        .errnum = 12,
        .caller_len = caller_a[3..26].len,
        .rendered_len = known.len,
        .summary_len = merged_len,
    };
    typed_records[1] = .{
        .errnum = 5101,
        .caller_len = caller_b[2..24].len,
        .rendered_len = fallback.len,
        .summary_len = padded_len,
    };

    try std.testing.expectEqual(@as(usize, 23), typed_records[0].caller_len);
    try std.testing.expectEqual(@as(usize, 22), typed_records[1].caller_len);
    try std.testing.expectEqual(@as(usize, 18), typed_records[0].summary_len);
    try std.testing.expect(typed_records[1].summary_len == 11 or typed_records[1].summary_len == 12);

    zalloc.zfreeBytes(allocator, &merged);
    try std.testing.expect(merged == null);

    var reacquired: ?[]u8 = try zalloc.zallocBytes(allocator, 16);
    defer zalloc.zfreeBytes(allocator, &reacquired);
    for (reacquired.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "lane10 merge ladder resets zalloc value owners while slab counters rebalance" {
    const allocator = std.testing.allocator;
    const SummaryOwner = struct {
        known_len: usize,
        fallback_len: usize,
        padded_len: usize,
    };

    slab.kmalloc_nr_allocated = 0;

    var slab_window = slab.kmallocBytes(48, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_window);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const fallback = str_error_r.strErrorR(9007, slab_window[4..44]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(9007, [buf],", fallback);

    var value: ?*SummaryOwner = try zalloc.zallocValue(allocator, SummaryOwner);
    defer zalloc.zfreeValue(allocator, SummaryOwner, &value);
    try std.testing.expectEqual(@as(usize, 0), value.?.known_len);
    try std.testing.expectEqual(@as(usize, 0), value.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 0), value.?.padded_len);

    var summary: [20]u8 = @splat(0xaa);
    const summary_len = vsprintf.scnprintf(&summary, "{s}:{d}", .{ "merge", fallback.len });
    try std.testing.expectEqualStrings("merge:39", summary[0..summary_len]);
    try std.testing.expectEqual(@as(u8, 0), summary[summary_len]);

    value.?.known_len = str_error_r.strErrorR(22, slab_window[0..18]).len;
    value.?.fallback_len = fallback.len;
    value.?.padded_len = vsprintf.scnprintfPad(slab_window[12..28], 9, "{s}", .{"ok"});

    try std.testing.expectEqual(@as(usize, 16), value.?.known_len);
    try std.testing.expectEqual(@as(usize, 39), value.?.fallback_len);
    try std.testing.expect(value.?.padded_len == 8 or value.?.padded_len == 9);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0 }, slab_window[12..22]);

    zalloc.zfreeValue(allocator, SummaryOwner, &value);
    try std.testing.expect(value == null);

    var reset_value: ?*SummaryOwner = try zalloc.zallocValue(allocator, SummaryOwner);
    defer zalloc.zfreeValue(allocator, SummaryOwner, &reset_value);
    try std.testing.expectEqual(@as(usize, 0), reset_value.?.known_len);
    try std.testing.expectEqual(@as(usize, 0), reset_value.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 0), reset_value.?.padded_len);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
