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

test "slab zero and exact windows keep neighboring bytes stable" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocArray(2, 12, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(bytes);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectAll(bytes, 0);

    @memset(bytes, 0x6b);

    const empty_view = bytes[3..3];
    const exact_errno = bytes[4..12];
    const exact_fmt = bytes[13..20];

    const empty_written = vsprintf.scnprintf(empty_view, "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqual(@as(u8, 0x6b), bytes[3]);

    const known = str_error_r.strErrorR(22, exact_errno);
    try std.testing.expectEqualStrings("Invalid", known);
    try std.testing.expectEqual(@as(u8, 0), exact_errno[7]);

    const padded = vsprintf.scnprintfPad(exact_fmt, exact_fmt.len - 1, "z{d}", .{9});
    try std.testing.expectEqual(@as(usize, 5), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', '9', ' ', ' ', ' ', ' ', 0 }, exact_fmt);

    try expectAll(bytes[0..3], 0x6b);
    try std.testing.expectEqual(@as(u8, 0x6b), bytes[12]);
    try expectAll(bytes[20..], 0x6b);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zalloc exact windows reset after zero-length helper calls" {
    const allocator = std.testing.allocator;

    var scratch: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &scratch);

    try expectAll(scratch.?, 0);
    @memset(scratch.?, 0x3d);

    const zero_slice = scratch.?[0..0];
    try std.testing.expectEqual(@as(usize, 0), vsprintf.vscnprintf(zero_slice, "{d}", .{10}));
    try std.testing.expectEqual(@as(usize, 0), str_error_r.strErrorR(4096, zero_slice).len);

    const exact = scratch.?[1..9];
    const written = vsprintf.scnprintf(exact, "{s}{d}", .{ "L", 10 });
    try std.testing.expectEqual(@as(usize, 3), written);
    try std.testing.expectEqualStrings("L10", exact[0..written]);
    try std.testing.expectEqual(@as(u8, 0), exact[written]);
    try expectAll(exact[written + 1 ..], 0x3d);

    const fallback = str_error_r.strErrorR(4096, scratch.?[10..18]);
    try std.testing.expectEqualStrings("INTERNA", fallback);
    try std.testing.expectEqual(@as(u8, 0), scratch.?[17]);

    try std.testing.expectEqual(@as(u8, 0x3d), scratch.?[0]);
    try std.testing.expectEqual(@as(u8, 0x3d), scratch.?[9]);

    zalloc.zfreeBytes(allocator, &scratch);
    try std.testing.expect(scratch == null);

    scratch = try zalloc.zallocBytes(allocator, 4);
    try expectAll(scratch.?, 0);
}
