const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab turns over a reclaimed middle allocation without disturbing live neighbors" {
    slab.kmalloc_nr_allocated = 0;

    const left = slab.kmallocBytes(3, slab.GFP_KERNEL) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(left);
    const middle = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse
        return error.TestUnexpectedResult;
    const right = slab.kmallocArray(1, 5, slab.GFP_KERNEL) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(right);

    @memset(left, 0x31);
    @memset(middle, 0x62);
    @memset(right, 0x93);
    try std.testing.expectEqual(@as(isize, 3), slab.kmalloc_nr_allocated);

    slab.kfree(middle);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    const replacement = slab.kmallocArray(2, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(replacement);
    try std.testing.expectEqual(@as(isize, 3), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, replacement);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x31, 0x31, 0x31 }, left);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x93, 0x93, 0x93, 0x93, 0x93 }, right);
}

test "strErrorR turns over exact-fit, one-byte, and fallback caller windows in one backing buffer" {
    var backing = [_]u8{0x7a} ** 24;

    const exact = str_error_r.strErrorR(0, backing[2..10]);
    try std.testing.expectEqualStrings("Success", exact);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[1]);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[10]);

    const tiny = str_error_r.strErrorR(13, backing[10..11]);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, 0), backing[10]);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[11]);

    const fallback = str_error_r.strErrorR(4096, backing[12..18]);
    try std.testing.expectEqualStrings("INTER", fallback);
    try std.testing.expectEqual(@as(u8, 0), backing[17]);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[18]);
}

test "vsprintf turns padded and direct caller windows over without breaching their fences" {
    var backing = [_]u8{0x55} ** 18;

    const padded = backing[1..8];
    const padded_written = vsprintf.scnprintfPad(padded, padded.len, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 5), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', ' ', ' ', 0 }, padded);
    try std.testing.expectEqual(@as(u8, 0x55), backing[0]);
    try std.testing.expectEqual(@as(u8, 0x55), backing[8]);

    const direct = backing[9..14];
    const direct_written = vsprintf.vscnprintf(direct, "{s}", .{"tool"});
    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqualStrings("tool", direct[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), direct[direct_written]);
    try std.testing.expectEqual(@as(u8, 0x55), backing[14]);

    const reused_written = vsprintf.scnprintf(padded, "{s}", .{"q"});
    try std.testing.expectEqual(@as(usize, 1), reused_written);
    try std.testing.expectEqualStrings("q", padded[0..reused_written]);
    try std.testing.expectEqual(@as(u8, 0), padded[reused_written]);
    try std.testing.expectEqual(@as(u8, ' '), padded[2]);
    try std.testing.expectEqual(@as(u8, 0x55), backing[8]);
}

test "zalloc turns over bytes and values independently across alternating frees" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u16,
        right: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &value);

    @memset(bytes.?, 0xe1);
    value.?.left = 11;
    value.?.right = 29;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u16, 11), value.?.left);
    try std.testing.expectEqual(@as(u16, 29), value.?.right);

    bytes = try zalloc.zallocBytes(allocator, 2);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);
    try std.testing.expectEqual(@as(u16, 11), value.?.left);

    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), value.?.left);
    try std.testing.expectEqual(@as(u16, 0), value.?.right);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);
}
