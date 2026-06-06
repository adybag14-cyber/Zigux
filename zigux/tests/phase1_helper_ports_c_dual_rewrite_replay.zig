const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectZeroed(bytes: []const u8) !void {
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

fn expectPadReturn(written: usize, logical_size: usize) !void {
    try std.testing.expect(written == logical_size or written == logical_size -| 1);
}

test "slab caller window rewrites through strerror and zalloc summary storage" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const owner = slab.kmallocBytes(40, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(owner);

    const window = owner[4..24];
    const first_written = vsprintf.scnprintf(window, "pre:{d}:{s}", .{ 7, "alpha" });
    try std.testing.expectEqual(@as(usize, 11), first_written);
    try std.testing.expectEqualStrings("pre:7:alpha", window[0..first_written]);
    try std.testing.expectEqual(@as(u8, 0), window[first_written]);

    const permission = str_error_r.strErrorR(13, window[0..18]);
    try std.testing.expectEqualStrings("Permission denied", permission);
    try std.testing.expectEqual(@as(u8, 0), window[permission.len]);
    try std.testing.expectEqual(@as(u8, 0), window[permission.len + 1]);

    var summary: ?[]u8 = try zalloc.zallocBytes(allocator, 28);
    defer zalloc.zfreeBytes(allocator, &summary);
    try expectZeroed(summary.?);

    const summary_written = vsprintf.scnprintf(summary.?, "{s}:{d}", .{ permission, window.len });
    try std.testing.expectEqualStrings("Permission denied:20", summary.?[0..summary_written]);
    try std.testing.expectEqual(@as(u8, 0), summary.?[summary_written]);
    try expectZeroed(summary.?[summary_written + 1 ..]);

    const padded_written = vsprintf.scnprintfPad(window[0..12], 8, "{s}", .{"io"});
    try expectPadReturn(padded_written, 8);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'o', ' ', ' ', ' ', ' ', ' ', ' ', 0 }, window[0..9]);
    try std.testing.expectEqual(@as(u8, ' '), summary.?[10]);
    try std.testing.expectEqual(@as(u8, 'd'), summary.?[11]);

    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zalloc caller window rewrites into slab array storage and clean release" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var scratch: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &scratch);
    try expectZeroed(scratch.?);
    @memset(scratch.?, 0xdd);

    const fallback_window = scratch.?[3..34];
    const fallback = str_error_r.strErrorR(4099, fallback_window);
    const fallback_expected = "INTERNAL ERROR: strerror_r(4099, [buf], 31)=22";
    try std.testing.expectEqualStrings(fallback_expected[0 .. fallback_window.len - 1], fallback);
    try std.testing.expectEqual(@as(u8, 0), fallback_window[fallback.len]);
    try std.testing.expectEqual(@as(u8, 0xdd), scratch.?[2]);
    try std.testing.expectEqual(@as(u8, 0xdd), scratch.?[34]);

    const short_written = vsprintf.scnprintf(fallback_window, "ok:{d}", .{5});
    try std.testing.expectEqual(@as(usize, 4), short_written);
    try std.testing.expectEqualStrings("ok:5", fallback_window[0..short_written]);
    try std.testing.expectEqual(@as(u8, 0), fallback_window[short_written]);
    try std.testing.expectEqual(@as(u8, 'N'), fallback_window[short_written + 1]);

    const array = slab.kmallocArray(2, 16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const copied = vsprintf.vscnprintf(array[1..20], "copy:{s}", .{fallback_window[0..short_written]});
    try std.testing.expectEqualStrings("copy:ok:5", array[1 .. 1 + copied]);
    try std.testing.expectEqual(@as(u8, 0), array[1 + copied]);

    const success = str_error_r.strErrorR(0, array[10..20]);
    try std.testing.expectEqualStrings("Success", success);
    try std.testing.expectEqual(@as(u8, 0), array[10 + success.len]);
    try std.testing.expectEqual(@as(u8, 0xdd), scratch.?[35]);

    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);
    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
