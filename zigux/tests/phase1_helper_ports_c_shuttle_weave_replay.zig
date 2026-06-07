const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectPadReturn(actual: usize, padded_len: usize) !void {
    if (actual != padded_len and actual != padded_len -| 1) {
        return error.UnexpectedPadReturn;
    }
}

test "shuttle weave preserves slab sentinels while zalloc owns copied summaries" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var arena = slab.kmallocBytes(80, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(arena);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memset(arena, 0xcc);
    const known_window = arena[4..22];
    const known = str_error_r.strErrorR(22, known_window);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0xcc), arena[3]);
    try std.testing.expectEqual(@as(u8, 0), arena[20]);
    try std.testing.expectEqual(@as(u8, 0xcc), arena[22]);

    const summary_window = arena[32..68];
    const summary_len = vsprintf.scnprintfPad(
        summary_window,
        31,
        "known={s}|len={d}",
        .{ known, known.len },
    );
    try expectPadReturn(summary_len, 31);
    try std.testing.expectEqualStrings("known=Invalid argument|len=16", summary_window[0..29]);
    try std.testing.expectEqual(@as(u8, ' '), summary_window[29]);
    try std.testing.expectEqual(@as(u8, ' '), summary_window[30]);
    try std.testing.expectEqual(@as(u8, 0), summary_window[31]);
    try std.testing.expectEqual(@as(u8, 0xcc), arena[31]);
    try std.testing.expectEqual(@as(u8, 0xcc), arena[68]);

    var copy_owner: ?[]u8 = try zalloc.zallocBytes(allocator, summary_window[0..31].len);
    defer zalloc.zfreeBytes(allocator, &copy_owner);
    @memcpy(copy_owner.?, summary_window[0..31]);
    @memset(summary_window[0..31], 0xee);
    try std.testing.expectEqualStrings("known=Invalid argument|len=16  ", copy_owner.?);

    zalloc.zfreeBytes(allocator, &copy_owner);
    try std.testing.expect(copy_owner == null);

    copy_owner = try zalloc.zallocBytes(allocator, 12);
    for (copy_owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "shuttle weave keeps failed slab allocation accounting and value owners balanced" {
    const allocator = std.testing.allocator;
    const Record = struct {
        fallback_len: usize,
        rendered_len: usize,
        slab_allocs_seen: isize,
    };

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocBytes(32, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var records = slab.kmallocArray(3, 16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(records);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var fallback_storage: [28]u8 = @splat(0xaa);
    const fallback = str_error_r.strErrorR(7007, fallback_storage[2..27]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror", fallback);
    try std.testing.expectEqual(@as(u8, 0xaa), fallback_storage[1]);
    try std.testing.expectEqual(@as(u8, 0), fallback_storage[26]);
    try std.testing.expectEqual(@as(u8, 0xaa), fallback_storage[27]);

    const first = records[0..16];
    const first_len = vsprintf.scnprintf(first, "f={d}", .{fallback.len});
    try std.testing.expectEqual(@as(usize, 4), first_len);
    try std.testing.expectEqualStrings("f=24", first[0..first_len]);
    try std.testing.expectEqual(@as(u8, 0), first[first_len]);

    var value_owner: ?*Record = try zalloc.zallocValue(allocator, Record);
    defer zalloc.zfreeValue(allocator, Record, &value_owner);
    try std.testing.expectEqual(@as(usize, 0), value_owner.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 0), value_owner.?.rendered_len);
    try std.testing.expectEqual(@as(isize, 0), value_owner.?.slab_allocs_seen);

    value_owner.?.* = .{
        .fallback_len = fallback.len,
        .rendered_len = first_len,
        .slab_allocs_seen = slab.kmalloc_nr_allocated,
    };
    try std.testing.expectEqual(@as(usize, 24), value_owner.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 4), value_owner.?.rendered_len);
    try std.testing.expectEqual(@as(isize, 1), value_owner.?.slab_allocs_seen);

    zalloc.zfreeValue(allocator, Record, &value_owner);
    try std.testing.expect(value_owner == null);

    value_owner = try zalloc.zallocValue(allocator, Record);
    try std.testing.expectEqual(@as(usize, 0), value_owner.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 0), value_owner.?.rendered_len);
    try std.testing.expectEqual(@as(isize, 0), value_owner.?.slab_allocs_seen);

    slab.kfree(records);
    records = &[_]u8{};
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
