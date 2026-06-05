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

fn expectPaddedReturn(actual: usize, current: usize) !void {
    try std.testing.expect(actual == current or actual == current -| 1);
}

test "slab error window feeds padded zalloc summary and releases cleanly" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var slab_owner: ?[]u8 = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer if (slab_owner) |bytes| slab.kfree(bytes);
    const slab_bytes = slab_owner.?;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(slab_bytes);

    const error_window = slab_bytes[3..24];
    const rendered_error = str_error_r.strErrorR(7777, error_window);
    try std.testing.expectEqual(@as(u8, 0), error_window[rendered_error.len]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[0]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[2]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[24]);

    var zowned: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &zowned);
    try expectZeroed(zowned.?);

    const summary = zowned.?[4..22];
    const written = vsprintf.scnprintfPad(summary, 13, "err={d}:{d}", .{ 7777, rendered_error.len });
    try expectPaddedReturn(written, 13);
    try std.testing.expectEqualStrings("err=7777:20  ", summary[0..13]);
    try std.testing.expectEqual(@as(u8, 0), summary[13]);
    try expectZeroed(zowned.?[0..4]);
    try expectZeroed(zowned.?[22..]);

    zalloc.zfreeBytes(allocator, &zowned);
    try std.testing.expect(zowned == null);
    slab.kfree(slab_owner);
    slab_owner = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "zalloc value records known error formatting while slab accounting survives failures" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const Capture = struct {
        code: i32,
        rendered_len: usize,
        padded_len: usize,
        saw_known_error: bool,
    };

    var capture: ?*Capture = try zalloc.zallocValue(allocator, Capture);
    defer zalloc.zfreeValue(allocator, Capture, &capture);
    try std.testing.expectEqual(@as(i32, 0), capture.?.code);
    try std.testing.expectEqual(@as(usize, 0), capture.?.rendered_len);
    try std.testing.expectEqual(false, capture.?.saw_known_error);

    const slab_ring = slab.kmallocArray(4, 16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_ring);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectZeroed(slab_ring);

    const known_window = slab_ring[5..35];
    const known_error = str_error_r.strErrorR(12, known_window);
    try std.testing.expectEqualStrings("Cannot allocate memory", known_error);
    try std.testing.expectEqual(@as(u8, 0), known_window[known_error.len]);

    var formatted: ?[]u8 = try zalloc.zallocBytes(allocator, 28);
    defer zalloc.zfreeBytes(allocator, &formatted);
    const formatted_window = formatted.?[2..20];
    const padded = vsprintf.scnprintfPad(formatted_window, 14, "kmem:{d}", .{known_error.len});
    try expectPaddedReturn(padded, 14);
    try std.testing.expectEqualStrings("kmem:22       ", formatted_window[0..14]);
    try std.testing.expectEqual(@as(u8, 0), formatted_window[14]);

    capture.?.code = 12;
    capture.?.rendered_len = known_error.len;
    capture.?.padded_len = 14;
    capture.?.saw_known_error = true;
    try std.testing.expectEqual(@as(usize, 22), capture.?.rendered_len);
    try std.testing.expectEqual(@as(usize, 14), capture.?.padded_len);
    try std.testing.expect(capture.?.saw_known_error);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeValue(allocator, Capture, &capture);
    try std.testing.expect(capture == null);
}
