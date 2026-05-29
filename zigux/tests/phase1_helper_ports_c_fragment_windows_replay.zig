const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectBytes(expected: []const u8, actual: []const u8) !void {
    try std.testing.expectEqualSlices(u8, expected, actual);
}

test "fragmented slab helper windows preserve unrelated bytes" {
    slab.kmalloc_nr_allocated = 0;

    const backing = slab.kmallocArray(3, 12, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(backing);

    try std.testing.expectEqual(@as(usize, 36), backing.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (backing) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memset(backing, 0xcc);

    const pad_fragment = backing[5..15];
    const pad_written = vsprintf.scnprintfPad(pad_fragment, 8, "{s}", .{"io"});
    try std.testing.expectEqual(@as(usize, 7), pad_written);
    try expectBytes("io      ", pad_fragment[0..8]);
    try std.testing.expectEqual(@as(u8, 0), pad_fragment[8]);

    const err_fragment = backing[19..28];
    const err_rendered = str_error_r.strErrorR(22, err_fragment);
    try std.testing.expectEqualStrings("Invalid ", err_rendered);
    try std.testing.expectEqual(@as(u8, 0), err_fragment[8]);

    try std.testing.expectEqual(@as(u8, 0xcc), backing[4]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[15]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[18]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[28]);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "fragmented zalloc helper windows survive fallback rewrites and reuse" {
    const allocator = std.testing.allocator;

    var maybe_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &maybe_bytes);

    var bytes = maybe_bytes.?;
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memset(bytes, 0x7e);

    const fallback_fragment = bytes[3..19];
    const fallback = str_error_r.strErrorR(4096, fallback_fragment);
    try std.testing.expectEqualStrings("INTERNAL ERROR:", fallback);
    try std.testing.expectEqual(@as(u8, 0), fallback_fragment[15]);

    const format_fragment = bytes[24..34];
    const direct_written = vsprintf.scnprintf(format_fragment, "{s}:{d}", .{ "frag", 17 });
    try std.testing.expectEqual(@as(usize, 7), direct_written);
    try std.testing.expectEqualStrings("frag:17", format_fragment[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), format_fragment[direct_written]);

    const zero_view = bytes[34..34];
    try std.testing.expectEqual(@as(usize, 0), vsprintf.vscnprintf(zero_view, "{s}", .{"ignored"}));

    try std.testing.expectEqual(@as(u8, 0x7e), bytes[2]);
    try std.testing.expectEqual(@as(u8, 0x7e), bytes[19]);
    try std.testing.expectEqual(@as(u8, 0x7e), bytes[23]);
    try std.testing.expectEqual(@as(u8, 0x7e), bytes[34]);

    zalloc.zfreeBytes(allocator, &maybe_bytes);
    try std.testing.expect(maybe_bytes == null);
    zalloc.zfreeBytes(allocator, &maybe_bytes);
    try std.testing.expect(maybe_bytes == null);

    maybe_bytes = try zalloc.zallocBytes(allocator, 8);
    bytes = maybe_bytes.?;
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}
