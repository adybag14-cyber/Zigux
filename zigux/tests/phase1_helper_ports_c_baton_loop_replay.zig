const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "baton loop preserves caller windows across helper owners" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const baton = slab.kmallocBytes(64, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (baton) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(baton, 0xa5);
    const known_window = baton[4..23];
    const known = str_error_r.strErrorR(22, known_window);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0xa5), baton[3]);
    try std.testing.expectEqual(@as(u8, 0), baton[20]);
    try std.testing.expectEqual(@as(u8, 0xa5), baton[21]);
    try std.testing.expectEqual(@as(u8, 0xa5), baton[23]);

    const format_window = baton[24..42];
    const formatted = vsprintf.scnprintf(format_window, "errno={d}:{s}", .{ 22, known });
    try std.testing.expectEqual(@as(usize, 17), formatted);
    try std.testing.expectEqualStrings("errno=22:Invalid ", format_window[0..formatted]);
    try std.testing.expectEqual(@as(u8, 0), format_window[formatted]);
    try std.testing.expectEqual(@as(u8, 0xa5), baton[42]);

    var summary: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &summary);
    for (summary.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const summary_written = vsprintf.scnprintf(
        summary.?,
        "loop:{s}:{d}",
        .{ format_window[0..formatted], slab.kmalloc_nr_allocated },
    );
    try std.testing.expectEqualStrings("loop:errno=22:Invalid :1", summary.?[0..summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary.?[summary_written]);

    const BatonState = struct {
        first: u8,
        count: usize,
        active: bool,
        next: ?*u8,
    };

    var state: ?*BatonState = try zalloc.zallocValue(allocator, BatonState);
    defer zalloc.zfreeValue(allocator, BatonState, &state);
    try std.testing.expectEqual(@as(u8, 0), state.?.first);
    try std.testing.expectEqual(@as(usize, 0), state.?.count);
    try std.testing.expectEqual(false, state.?.active);
    try std.testing.expect(state.?.next == null);

    state.?.first = summary.?[0];
    state.?.count = summary_written;
    state.?.active = true;
    try std.testing.expectEqual(@as(u8, 'l'), state.?.first);
    try std.testing.expectEqual(@as(usize, 24), state.?.count);
    try std.testing.expectEqual(true, state.?.active);

    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);
    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);

    slab.kfree(baton);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "baton loop fallback formatting keeps failure paths leak-free" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocBytes(16, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const fallback_owner = slab.kmallocArray(4, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 32), fallback_owner.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (fallback_owner) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(fallback_owner, 0x7c);
    const fallback_window = fallback_owner[1..31];
    const fallback = str_error_r.strErrorR(-5, fallback_window);
    try std.testing.expectEqual(@as(usize, 29), fallback.len);
    try std.testing.expect(std.mem.startsWith(u8, fallback, "INTERNAL ERROR: strerror_r("));
    try std.testing.expectEqual(@as(u8, 0x7c), fallback_owner[0]);
    try std.testing.expectEqual(@as(u8, 0), fallback_owner[30]);
    try std.testing.expectEqual(@as(u8, 0x7c), fallback_owner[31]);

    var padded: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &padded);
    const padded_written = vsprintf.scnprintfPad(padded.?, 18, "fb={d}", .{fallback.len});
    try std.testing.expect(padded_written == 18 or padded_written == 17);
    try std.testing.expectEqualStrings("fb=29", padded.?[0..5]);
    for (padded.?[5..18]) |byte| {
        try std.testing.expectEqual(@as(u8, ' '), byte);
    }
    try std.testing.expectEqual(@as(u8, 0), padded.?[18]);

    zalloc.zfreeBytes(allocator, &padded);
    try std.testing.expect(padded == null);
    slab.kfree(fallback_owner);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
