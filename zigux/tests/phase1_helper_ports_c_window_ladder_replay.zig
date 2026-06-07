const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectRenderedFallback(errnum: i32, window: []u8, rendered: []const u8) !void {
    var expected_storage: [64]u8 = undefined;
    const expected = std.fmt.bufPrint(
        &expected_storage,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ errnum, window.len },
    ) catch unreachable;
    const expected_len = @min(expected.len, window.len - 1);
    try std.testing.expectEqualStrings(expected[0..expected_len], rendered);
    try std.testing.expectEqual(@as(u8, 0), window[expected_len]);
}

test "slab caller window ladder feeds fallback text into zalloc summary storage" {
    slab.kmalloc_nr_allocated = 0;

    var slab_owner: ?[]u8 = slab.kmallocBytes(80, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer {
        slab.kfree(slab_owner);
        slab_owner = null;
    }
    const owner = slab_owner orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (owner) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const header_window = owner[3..22];
    const header_len = vsprintf.scnprintf(header_window, "slot-{d}:{s}", .{ 4, "slab" });
    try std.testing.expectEqual(@as(usize, 11), header_len);
    try std.testing.expectEqualStrings("slot-4:slab", header_window[0..header_len]);
    try std.testing.expectEqual(@as(u8, 0), header_window[header_len]);
    try std.testing.expectEqual(@as(u8, 0), owner[2]);
    try std.testing.expectEqual(@as(u8, 0), owner[22]);

    const fallback_window = owner[28..68];
    const fallback = str_error_r.strErrorR(7301, fallback_window);
    try expectRenderedFallback(7301, fallback_window, fallback);
    try std.testing.expectEqual(@as(u8, 0), owner[27]);
    try std.testing.expectEqual(@as(u8, 0), owner[68]);

    const allocator = std.testing.allocator;
    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    const summary = summary_owner.?;
    for (summary) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memcpy(summary[0..fallback.len], fallback);
    const pad_window = summary[36..48];
    const padded_len = vsprintf.scnprintfPad(pad_window, 11, "h={d}", .{header_len});
    try std.testing.expect(padded_len == 11 or padded_len == 10);
    try std.testing.expectEqualStrings("h=11       ", pad_window[0..11]);
    try std.testing.expectEqual(@as(u8, 0), pad_window[11]);

    zalloc.zfreeBytes(allocator, &summary_owner);
    try std.testing.expect(summary_owner == null);

    slab.kfree(slab_owner);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "array windows carry known errors and padded summaries through value owner cleanup" {
    slab.kmalloc_nr_allocated = 0;

    var array_owner: ?[]u8 = slab.kmallocArray(3, 24, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer {
        slab.kfree(array_owner);
        array_owner = null;
    }
    const array = array_owner orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 72), array.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const known = str_error_r.strErrorR(22, array[1..19]);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0), array[18]);
    try std.testing.expectEqual(@as(u8, 0), array[0]);
    try std.testing.expectEqual(@as(u8, 0), array[19]);

    const padded = vsprintf.scnprintfPad(array[25..43], 17, "known:{d}", .{known.len});
    try std.testing.expect(padded == 17 or padded == 16);
    try std.testing.expectEqualStrings("known:16         ", array[25..42]);
    try std.testing.expectEqual(@as(u8, 0), array[42]);
    try std.testing.expectEqual(@as(u8, 0), array[24]);
    try std.testing.expectEqual(@as(u8, 0), array[43]);

    const fallback = str_error_r.strErrorR(8802, array[49..71]);
    try expectRenderedFallback(8802, array[49..71], fallback);
    try std.testing.expectEqual(@as(u8, 0), array[48]);
    try std.testing.expectEqual(@as(u8, 0), array[71]);

    const allocator = std.testing.allocator;
    const Summary = struct {
        known_len: usize,
        padded_len: usize,
        fallback_len: usize,
    };
    var summary_owner: ?*Summary = try zalloc.zallocValue(allocator, Summary);
    defer zalloc.zfreeValue(allocator, Summary, &summary_owner);
    try std.testing.expectEqual(@as(usize, 0), summary_owner.?.known_len);
    try std.testing.expectEqual(@as(usize, 0), summary_owner.?.padded_len);
    try std.testing.expectEqual(@as(usize, 0), summary_owner.?.fallback_len);

    summary_owner.?.* = .{
        .known_len = known.len,
        .padded_len = padded,
        .fallback_len = fallback.len,
    };
    try std.testing.expectEqual(@as(usize, 16), summary_owner.?.known_len);
    try std.testing.expect(summary_owner.?.padded_len == 17 or summary_owner.?.padded_len == 16);
    try std.testing.expectEqual(@as(usize, 21), summary_owner.?.fallback_len);

    zalloc.zfreeValue(allocator, Summary, &summary_owner);
    try std.testing.expect(summary_owner == null);

    slab.kfree(array_owner);
    array_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
