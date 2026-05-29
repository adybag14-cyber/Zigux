const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectAll(slice: []const u8, value: u8) !void {
    for (slice) |byte| {
        try std.testing.expectEqual(value, byte);
    }
}

test "slab recycled spans survive failed allocation and helper rewrites" {
    slab.kmalloc_nr_allocated = 0;

    const owner = slab.kmallocArray(3, 9, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(owner);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectAll(owner, 0);

    @memset(owner, 0x4c);

    try std.testing.expect(slab.kmallocBytes(6, slab.__GFP_IO) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const errno_window = owner[2..13];
    const rendered_errno = str_error_r.strErrorR(12, errno_window);
    try std.testing.expectEqualStrings("Cannot all", rendered_errno);
    try std.testing.expectEqual(@as(u8, 0), errno_window[10]);

    const fmt_window = owner[14..24];
    const direct_written = vsprintf.scnprintf(fmt_window, "{s}-{d}", .{ "span", 7 });
    try std.testing.expectEqual(@as(usize, 6), direct_written);
    try std.testing.expectEqualStrings("span-7", fmt_window[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), fmt_window[direct_written]);
    try expectAll(fmt_window[direct_written + 1 ..], 0x4c);

    const padded_written = vsprintf.scnprintfPad(fmt_window, fmt_window.len - 1, "{s}", .{"z"});
    try std.testing.expectEqual(@as(usize, 8), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0 }, fmt_window);

    try expectAll(owner[0..2], 0x4c);
    try std.testing.expectEqual(@as(u8, 0x4c), owner[13]);
    try expectAll(owner[24..], 0x4c);
}

test "zalloc recycled span remains bounded after helper fallback and free" {
    const allocator = std.testing.allocator;

    var scratch: ?[]u8 = try zalloc.zallocBytes(allocator, 22);
    defer zalloc.zfreeBytes(allocator, &scratch);

    try expectAll(scratch.?, 0);
    @memset(scratch.?, 0x57);

    const fallback = scratch.?[1..11];
    const fallback_text = str_error_r.strErrorR(777, fallback);
    try std.testing.expectEqualStrings("INTERNAL ", fallback_text);
    try std.testing.expectEqual(@as(u8, 0), fallback[9]);

    const middle = scratch.?[12..20];
    const mirrored = vsprintf.vscnprintf(middle, "{s}{d}", .{ "r", 10 });
    try std.testing.expectEqual(@as(usize, 3), mirrored);
    try std.testing.expectEqualStrings("r10", middle[0..mirrored]);
    try std.testing.expectEqual(@as(u8, 0), middle[mirrored]);
    try expectAll(middle[mirrored + 1 ..], 0x57);

    try std.testing.expectEqual(@as(usize, 0), vsprintf.scnprintf(scratch.?[21..21], "{s}", .{"ignored"}));
    try std.testing.expectEqual(@as(u8, 0x57), scratch.?[0]);
    try std.testing.expectEqual(@as(u8, 0x57), scratch.?[11]);
    try std.testing.expectEqual(@as(u8, 0x57), scratch.?[20]);
    try std.testing.expectEqual(@as(u8, 0x57), scratch.?[21]);

    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);
    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);

    scratch = try zalloc.zallocBytes(allocator, 5);
    try expectAll(scratch.?, 0);
}
