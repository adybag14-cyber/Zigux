const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const StrideState = struct {
    fallback_len: usize,
    known_len: usize,
    padded: [6]u8,
    ready: bool,
};

fn expectPaddedReturn(written: usize, logical_size: usize) !void {
    try std.testing.expect(written == logical_size or written + 1 == logical_size);
}

test "stride latch alternates slab windows through formatted zalloc state" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kmallocArray(4, 12, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    var release_slab = true;
    defer if (release_slab) slab.kfree(slab_bytes);

    try std.testing.expectEqual(@as(usize, 48), slab_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memset(slab_bytes, 0x71);

    const fallback_window = slab_bytes[1..18];
    const fallback_rendered = str_error_r.strErrorR(77, fallback_window);
    try std.testing.expectEqualStrings("INTERNAL ERROR: ", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0x71), slab_bytes[0]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[17]);
    try std.testing.expectEqual(@as(u8, 0x71), slab_bytes[18]);

    const known_window = slab_bytes[22..40];
    const known_rendered = str_error_r.strErrorR(13, known_window);
    try std.testing.expectEqualStrings("Permission denied", known_rendered);
    try std.testing.expectEqual(@as(u8, 0x71), slab_bytes[21]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[39]);
    try std.testing.expectEqual(@as(u8, 0x71), slab_bytes[40]);

    var summary_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &summary_owner);
    for (summary_owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const summary_written = vsprintf.scnprintf(
        summary_owner.?,
        "{s}/{s}/{d}",
        .{ fallback_rendered[0..8], known_rendered, slab.kmalloc_nr_allocated },
    );
    try std.testing.expectEqualStrings("INTERNAL/Permission denied/1", summary_owner.?[0..summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary_owner.?[summary_written]);

    const pad_window = slab_bytes[41..47];
    const pad_written = vsprintf.scnprintfPad(pad_window, 5, "s{d}", .{7});
    try expectPaddedReturn(pad_written, 5);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 's', '7', ' ', ' ', ' ', 0 }, pad_window);
    try std.testing.expectEqual(@as(u8, 0x71), slab_bytes[47]);

    var state_owner: ?*StrideState = try zalloc.zallocValue(allocator, StrideState);
    defer zalloc.zfreeValue(allocator, StrideState, &state_owner);
    try std.testing.expectEqual(@as(usize, 0), state_owner.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 0), state_owner.?.known_len);
    try std.testing.expectEqual(false, state_owner.?.ready);
    for (state_owner.?.padded) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    state_owner.?.fallback_len = fallback_rendered.len;
    state_owner.?.known_len = known_rendered.len;
    @memcpy(state_owner.?.padded[0..], pad_window);
    state_owner.?.ready = true;
    try std.testing.expectEqual(@as(usize, 16), state_owner.?.fallback_len);
    try std.testing.expectEqual(@as(usize, 17), state_owner.?.known_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 's', '7', ' ', ' ', ' ', 0 }, state_owner.?.padded[0..]);
    try std.testing.expect(state_owner.?.ready);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeValue(allocator, StrideState, &state_owner);
    try std.testing.expect(state_owner == null);
    zalloc.zfreeValue(allocator, StrideState, &state_owner);
    try std.testing.expect(state_owner == null);

    zalloc.zfreeBytes(allocator, &summary_owner);
    try std.testing.expect(summary_owner == null);
    zalloc.zfreeBytes(allocator, &summary_owner);
    try std.testing.expect(summary_owner == null);

    slab.kfree(slab_bytes);
    release_slab = false;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
