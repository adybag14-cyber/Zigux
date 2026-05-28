const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab sparse failures leave allocation accounting stable" {
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocBytes(16, slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 8, slab.GFP_KERNEL | slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const left = slab.kmallocArray(2, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(left);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (left) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const right = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memset(right, 0x7a);
    slab.kfree(right);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR confines sparse caller windows" {
    var backing = [_]u8{0xcc} ** 18;

    const known = str_error_r.strErrorR(0, backing[5..13]);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 0), backing[12]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[4]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[13]);

    const tiny = str_error_r.strErrorR(4096, backing[2..3]);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, 0), backing[2]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[3]);

    const empty = str_error_r.strErrorR(13, backing[9..9]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
}

test "vsprintf sparse windows keep sentinels outside the caller view" {
    var truncated = [_]u8{0xdd} ** 10;
    const truncated_written = vsprintf.scnprintf(truncated[3..7], "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 3), truncated_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0 }, truncated[3..7]);
    try std.testing.expectEqual(@as(u8, 0xdd), truncated[2]);
    try std.testing.expectEqual(@as(u8, 0xdd), truncated[7]);

    var padded = [_]u8{0xee} ** 9;
    const padded_written = vsprintf.scnprintfPad(padded[1..6], 4, "{s}", .{"x"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', ' ', ' ', ' ', 0 }, padded[1..6]);
    try std.testing.expectEqual(@as(u8, 0xee), padded[0]);
    try std.testing.expectEqual(@as(u8, 0xee), padded[6]);

    const empty_written = vsprintf.vscnprintf(padded[4..4], "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
}

test "zalloc sparse edges zero and reset ownership" {
    const allocator = std.testing.allocator;
    const Nested = struct {
        bytes: [5]u8,
        maybe: ?*u8,
        flag: bool,
    };

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(empty != null);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);

    var value: ?*Nested = try zalloc.zallocValue(allocator, Nested);
    defer zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0 }, &value.?.bytes);
    try std.testing.expect(value.?.maybe == null);
    try std.testing.expectEqual(false, value.?.flag);

    value.?.bytes[3] = 0x55;
    zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Nested, &value);
    try std.testing.expect(value == null);
}
