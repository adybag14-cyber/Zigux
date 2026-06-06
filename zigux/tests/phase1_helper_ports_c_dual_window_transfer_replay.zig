const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectAll(bytes: []const u8, value: u8) !void {
    for (bytes) |byte| {
        try std.testing.expectEqual(value, byte);
    }
}

fn expectPadReturn(actual: usize, legacy: usize, current: usize) !void {
    try std.testing.expect(actual == legacy or actual == current);
}

test "dual slab windows transfer bounded errors into a zeroed zalloc owner" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &owner);
    try expectAll(owner.?, 0);

    const known_slab = slab.kmallocBytes(16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(known_slab);
    const fallback_slab = slab.kmallocBytes(16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(fallback_slab);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    const known = str_error_r.strErrorR(12, known_slab[1..15]);
    try std.testing.expectEqualStrings("Cannot alloca", known);
    try std.testing.expectEqual(@as(u8, 0), known_slab[0]);
    try std.testing.expectEqual(@as(u8, 0), known_slab[14]);
    try std.testing.expectEqual(@as(u8, 0), known_slab[15]);

    const known_window = owner.?[4..20];
    const known_written = vsprintf.scnprintf(known_window, "K:{s}", .{known});
    try std.testing.expectEqual(@as(usize, 15), known_written);
    try std.testing.expectEqualStrings("K:Cannot alloca", known_window[0..known_written]);
    try std.testing.expectEqual(@as(u8, 0), known_window[known_written]);

    const fallback = str_error_r.strErrorR(4097, fallback_slab[2..14]);
    try std.testing.expectEqualStrings("INTERNAL ER", fallback);
    try std.testing.expectEqual(@as(u8, 0), fallback_slab[0]);
    try std.testing.expectEqual(@as(u8, 0), fallback_slab[1]);
    try std.testing.expectEqual(@as(u8, 0), fallback_slab[13]);
    try std.testing.expectEqual(@as(u8, 0), fallback_slab[14]);
    try std.testing.expectEqual(@as(u8, 0), fallback_slab[15]);

    const fallback_window = owner.?[24..40];
    const fallback_written = vsprintf.scnprintfPad(fallback_window, 12, "F:{s}", .{fallback});
    try std.testing.expectEqual(@as(usize, 12), fallback_written);
    try std.testing.expectEqualStrings("F:INTERNAL E", fallback_window[0..fallback_written]);
    try std.testing.expectEqual(@as(u8, 0), fallback_window[fallback_written]);

    try expectAll(owner.?[0..4], 0);
    try expectAll(owner.?[20..24], 0);
    try expectAll(owner.?[41..], 0);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
}

test "slab array rows feed a zalloc value summary without leaking owners" {
    const allocator = std.testing.allocator;
    const Summary = struct {
        known_len: usize,
        fallback_len: usize,
        padded_len: usize,
        text: [24]u8,
    };

    slab.kmalloc_nr_allocated = 0;
    const rows = slab.kmallocArray(3, 12, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(rows);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectAll(rows, 0);

    const known = str_error_r.strErrorR(22, rows[0..12]);
    try std.testing.expectEqualStrings("Invalid arg", known);
    try std.testing.expectEqual(@as(u8, 0), rows[11]);

    const fallback = str_error_r.strErrorR(777, rows[12..24]);
    try std.testing.expectEqualStrings("INTERNAL ER", fallback);
    try std.testing.expectEqual(@as(u8, 0), rows[23]);

    const padded_window = rows[24..36];
    const padded_len = vsprintf.scnprintfPad(padded_window, 8, "{s}", .{"io"});
    try expectPadReturn(padded_len, 7, 8);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'o', ' ', ' ', ' ', ' ', ' ', ' ', 0, 0, 0, 0 }, padded_window);

    var summary: ?*Summary = try zalloc.zallocValue(allocator, Summary);
    defer zalloc.zfreeValue(allocator, Summary, &summary);
    try std.testing.expectEqual(@as(usize, 0), summary.?.known_len);
    try expectAll(summary.?.text[0..], 0);

    summary.?.known_len = known.len;
    summary.?.fallback_len = fallback.len;
    summary.?.padded_len = padded_len;
    const written = vsprintf.vscnprintf(&summary.?.text, "k={d};f={d};p={d}", .{
        summary.?.known_len,
        summary.?.fallback_len,
        summary.?.padded_len,
    });
    try std.testing.expectEqual(@as(usize, 13), written);
    try std.testing.expectEqualStrings("k=11;f=11;p=", summary.?.text[0..12]);
    try std.testing.expect(summary.?.text[12] == '7' or summary.?.text[12] == '8');
    try std.testing.expectEqual(@as(u8, 0), summary.?.text[13]);
    try expectAll(summary.?.text[14..], 0);

    zalloc.zfreeValue(allocator, Summary, &summary);
    try std.testing.expect(summary == null);
    zalloc.zfreeValue(allocator, Summary, &summary);
    try std.testing.expect(summary == null);
}
