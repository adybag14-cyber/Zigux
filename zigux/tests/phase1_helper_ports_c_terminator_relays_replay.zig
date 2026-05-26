const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab reclaim and free relays preserve neighbor contents and counters" {
    slab.kmalloc_nr_allocated = 0;

    const left = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    const right = slab.kmallocArray(2, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(right);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    @memcpy(left, &[_]u8{ 0x21, 0x22, 0x23, 0x24 });
    @memcpy(right, &[_]u8{ 0x61, 0x62, 0x63, 0x64 });

    slab.kfree(left);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(3, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x61, 0x62, 0x63, 0x64 }, right);

    const replacement = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(replacement);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, replacement);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x61, 0x62, 0x63, 0x64 }, right);
}

test "strErrorR relays terminators across shrinking and offset caller windows" {
    var backing = [_]u8{0x5c} ** 28;

    const exact = str_error_r.strErrorR(0, backing[1..9]);
    try std.testing.expectEqualStrings("Success", exact);
    try std.testing.expectEqual(@as(u8, 0x5c), backing[0]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, 0x5c), backing[9]);

    const fallback = str_error_r.strErrorR(4096, backing[9..14]);
    try std.testing.expectEqualStrings("INTE", fallback);
    try std.testing.expectEqual(@as(u8, 0), backing[13]);
    try std.testing.expectEqual(@as(u8, 0x5c), backing[14]);

    const tiny = str_error_r.strErrorR(13, backing[14..15]);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, 0), backing[14]);
    try std.testing.expectEqual(@as(u8, 0x5c), backing[15]);
}

test "vsprintf relays terminators between padded, direct, and single-byte views" {
    var backing = [_]u8{0x33} ** 18;

    const padded = backing[1..8];
    const padded_written = vsprintf.scnprintfPad(padded, 5, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', ' ', 0, 0x33 }, padded);
    try std.testing.expectEqual(@as(u8, 0x33), backing[0]);
    try std.testing.expectEqual(@as(u8, 0x33), backing[8]);

    const direct = backing[8..13];
    const direct_written = vsprintf.vscnprintf(direct, "{s}", .{"tool"});
    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqualStrings("tool", direct[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), direct[4]);
    try std.testing.expectEqual(@as(u8, 0x33), backing[13]);

    const tiny = backing[13..14];
    const tiny_written = vsprintf.scnprintf(tiny, "{s}", .{"abc"});
    try std.testing.expectEqual(@as(usize, 0), tiny_written);
    try std.testing.expectEqual(@as(u8, 0), backing[13]);
    try std.testing.expectEqual(@as(u8, 0x33), backing[14]);
}

test "zalloc free relays clear one optional without disturbing the live sibling" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        left: u16,
        right: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &value);

    @memcpy(bytes.?, &[_]u8{ 0xa1, 0xa2, 0xa3 });
    value.?.left = 7;
    value.?.right = 11;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u16, 7), value.?.left);
    try std.testing.expectEqual(@as(u16, 11), value.?.right);

    bytes = try zalloc.zallocBytes(allocator, 2);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), value.?.left);
    try std.testing.expectEqual(@as(u16, 0), value.?.right);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);
}
