const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "ledger fold carries slab strerror windows into zalloc formatting" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_window_owner = slab.kmallocBytes(48, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    defer slab.kfree(slab_window_owner);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_window_owner) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(slab_window_owner, 0xcc);
    const known = str_error_r.strErrorR(12, slab_window_owner[3..28]);
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try std.testing.expectEqual(@as(u8, 0xcc), slab_window_owner[2]);
    try std.testing.expectEqual(@as(u8, 0), slab_window_owner[25]);
    try std.testing.expectEqual(@as(u8, 0xcc), slab_window_owner[28]);

    var formatted: ?[]u8 = try zalloc.zallocBytes(allocator, 64);
    defer zalloc.zfreeBytes(allocator, &formatted);
    const formatted_view = formatted orelse return error.TestUnexpectedResult;

    const written = vsprintf.scnprintf(
        formatted_view,
        "err={s};slab={d}",
        .{ known, slab.kmalloc_nr_allocated },
    );
    try std.testing.expectEqual(@as(usize, 33), written);
    try std.testing.expectEqualStrings("err=Cannot allocate memory;slab=1", formatted_view[0..written]);
    try std.testing.expectEqual(@as(u8, 0), formatted_view[written]);

    var padded: [24]u8 = @splat(0xdd);
    const padded_written = vsprintf.scnprintfPad(padded[2..22], 12, "{s}", .{"ledger"});
    try std.testing.expect(padded_written == 11 or padded_written == 12);
    try std.testing.expectEqual(@as(u8, 0xdd), padded[1]);
    try std.testing.expectEqualSlices(u8, "ledger      ", padded[2..14]);
    try std.testing.expectEqual(@as(u8, 0), padded[14]);
    try std.testing.expectEqual(@as(u8, 0xdd), padded[22]);
}

test "ledger fold preserves failure counters and zalloc reset handoffs" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocBytes(16, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const slab_summary = slab.kmallocArray(6, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    defer slab.kfree(slab_summary);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_summary) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(slab_summary, 0xbb);
    const fallback = str_error_r.strErrorR(7001, slab_summary[1..38]);
    try std.testing.expect(std.mem.startsWith(u8, fallback, "INTERNAL ERROR: strerror_r(7001"));
    try std.testing.expectEqual(@as(u8, 0xbb), slab_summary[0]);
    try std.testing.expectEqual(@as(u8, 0), slab_summary[37]);
    try std.testing.expectEqual(@as(u8, 0xbb), slab_summary[38]);

    const State = struct {
        err_len: u8,
        slab_count: isize,
        fallback_head: [8]u8,
    };

    var state: ?*State = try zalloc.zallocValue(allocator, State);
    defer zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expectEqual(@as(u8, 0), state.?.err_len);
    try std.testing.expectEqual(@as(isize, 0), state.?.slab_count);
    try std.testing.expectEqualSlices(u8, &[_]u8{0} ** 8, state.?.fallback_head[0..]);

    state.?.err_len = @intCast(fallback.len);
    state.?.slab_count = slab.kmalloc_nr_allocated;
    @memcpy(state.?.fallback_head[0..], fallback[0..8]);

    var summary: [40]u8 = @splat(0xee);
    const summary_len = vsprintf.vscnprintf(
        &summary,
        "len={d};head={s};live={d}",
        .{ state.?.err_len, state.?.fallback_head[0..], state.?.slab_count },
    );
    try std.testing.expectEqualStrings("len=36;head=INTERNAL;live=1", summary[0..summary_len]);
    try std.testing.expectEqual(@as(u8, 0), summary[summary_len]);

    zalloc.zfreeValue(allocator, State, &state);
    try std.testing.expect(state == null);

    var zeroed_again: ?[]u8 = try zalloc.zallocBytes(allocator, 16);
    defer zalloc.zfreeBytes(allocator, &zeroed_again);
    for (zeroed_again.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}
