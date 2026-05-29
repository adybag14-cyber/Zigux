const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zeroed array hosts independent strerror and vsprintf windows" {
    slab.kmalloc_nr_allocated = 0;

    const arena = slab.kmallocArray(3, 16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    errdefer slab.kfree(arena);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (arena) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(arena, 0x7c);

    const err_window = arena[3..15];
    const err = str_error_r.strErrorR(12, err_window);
    try std.testing.expectEqualStrings("Cannot allo", err);
    try std.testing.expectEqual(@as(u8, 0), err_window[err.len]);
    try std.testing.expectEqual(@as(u8, 0x7c), arena[2]);
    try std.testing.expectEqual(@as(u8, 0x7c), arena[15]);

    const fmt_window = arena[18..34];
    const fmt_written = vsprintf.scnprintf(fmt_window, "{s}:{d}", .{ err[0..6], err.len });
    try std.testing.expectEqual(@as(usize, 9), fmt_written);
    try std.testing.expectEqualStrings("Cannot:11", fmt_window[0..fmt_written]);
    try std.testing.expectEqual(@as(u8, 0), fmt_window[fmt_written]);
    try std.testing.expectEqual(@as(u8, 0x7c), arena[17]);
    try std.testing.expectEqual(@as(u8, 0x7c), arena[34]);

    slab.kfree(arena);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "zalloc scratch survives oversize render before bounded error fallback" {
    const allocator = std.testing.allocator;

    var scratch: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &scratch);

    for (scratch.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(scratch.?, 0xa5);
    const pad_window = scratch.?[2..14];
    const padded = vsprintf.scnprintfPad(pad_window, 8, "{s}", .{"io"});
    try std.testing.expectEqual(@as(usize, 7), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'o', ' ', ' ', ' ', ' ', ' ', ' ', 0 }, pad_window[0..9]);

    var too_large: [vsprintf.max_render_bytes + 1]u8 = undefined;
    @memset(&too_large, 'x');
    const oversized = vsprintf.scnprintf(scratch.?[14..22], "{s}", .{&too_large});
    try std.testing.expectEqual(@as(usize, 0), oversized);
    try std.testing.expectEqualSlices(u8, &[_]u8{0xa5} ** 8, scratch.?[14..22]);

    const fallback = str_error_r.strErrorR(4096, scratch.?[14..22]);
    try std.testing.expectEqualStrings("INTERNA", fallback);
    try std.testing.expectEqual(@as(u8, 0), scratch.?[21]);
    try std.testing.expectEqual(@as(u8, 0xa5), scratch.?[22]);

    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);
    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);
}
