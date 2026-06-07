const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "anchor chain hands slab messages through zalloc summaries" {
    slab.kmalloc_nr_allocated = 0;
    const allocator = std.testing.allocator;

    var slab_owner: ?[]u8 = slab.kmallocBytes(48, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer {
        slab.kfree(slab_owner);
        slab_owner = null;
    }
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const known_window = slab_owner.?[4..27];
    const known = str_error_r.strErrorR(12, known_window);
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try std.testing.expectEqual(@as(u8, 0), known_window[known.len]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner.?[3]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner.?[27]);

    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    const written = vsprintf.scnprintf(summary_owner.?, "A:{d}:{s}", .{ known.len, known[0..6] });
    try std.testing.expectEqualStrings("A:22:Cannot", summary_owner.?[0..written]);
    try std.testing.expectEqual(@as(u8, 0), summary_owner.?[written]);

    const fallback_window = slab_owner.?[10..42];
    const fallback = str_error_r.strErrorR(8128, fallback_window);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(8128", fallback);
    try std.testing.expectEqual(@as(u8, 0), fallback_window[fallback.len]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner.?[42]);

    zalloc.zfreeBytes(allocator, &summary_owner);
    try std.testing.expect(summary_owner == null);

    summary_owner = try zalloc.zallocBytes(allocator, 32);
    for (summary_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const padded = vsprintf.scnprintfPad(summary_owner.?, 16, "F:{d}:{s}", .{ fallback.len, fallback[0..3] });
    try std.testing.expect(padded == 16 or padded == 15);
    try std.testing.expectEqualStrings("F:31:INT        ", summary_owner.?[0..16]);
    try std.testing.expectEqual(@as(u8, 0), summary_owner.?[16]);
}

test "anchor chain keeps independent value owners and slab counters balanced" {
    slab.kmalloc_nr_allocated = 0;
    const allocator = std.testing.allocator;

    const Anchor = struct {
        errno: i32,
        copied: usize,
        padded: usize,
    };

    var record: ?*Anchor = try zalloc.zallocValue(allocator, Anchor);
    defer zalloc.zfreeValue(allocator, Anchor, &record);
    try std.testing.expectEqual(@as(i32, 0), record.?.errno);
    try std.testing.expectEqual(@as(usize, 0), record.?.copied);
    try std.testing.expectEqual(@as(usize, 0), record.?.padded);

    var first: ?[]u8 = slab.kmallocBytes(24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    var second: ?[]u8 = slab.kmallocBytes(24, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer {
        slab.kfree(second);
        second = null;
        slab.kfree(first);
        first = null;
    }
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    const first_msg = str_error_r.strErrorR(0, first.?[1..10]);
    const second_len = vsprintf.vscnprintf(second.?[2..14], "ok:{d}:{s}", .{ first_msg.len, first_msg });

    record.?.errno = 0;
    record.?.copied = first_msg.len;
    record.?.padded = second_len;

    try std.testing.expectEqualStrings("Success", first_msg);
    try std.testing.expectEqualStrings("ok:7:Succes", second.?[2 .. 2 + second_len]);
    try std.testing.expectEqual(@as(u8, 0), first.?[1 + first_msg.len]);
    try std.testing.expectEqual(@as(u8, 0), second.?[2 + second_len]);
    try std.testing.expectEqual(@as(usize, 7), record.?.copied);
    try std.testing.expectEqual(@as(usize, 11), record.?.padded);

    slab.kfree(second);
    second = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeValue(allocator, Anchor, &record);
    try std.testing.expect(record == null);

    record = try zalloc.zallocValue(allocator, Anchor);
    try std.testing.expectEqual(@as(i32, 0), record.?.errno);
    try std.testing.expectEqual(@as(usize, 0), record.?.copied);
    try std.testing.expectEqual(@as(usize, 0), record.?.padded);

    slab.kfree(first);
    first = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
