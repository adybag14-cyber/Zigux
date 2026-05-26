const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps the remaining owner live across a handoff allocation" {
    slab.kmalloc_nr_allocated = 0;

    const anchor = slab.kmallocArray(2, 2, slab.GFP_KERNEL) orelse
        return error.TestUnexpectedResult;
    const zero = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(zero);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 0), zero.len);

    @memset(anchor, 0x41);
    slab.kfree(anchor);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const refill = slab.kmallocArray(3, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(refill);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, refill);
    try std.testing.expect(slab.kmallocArray(2, 2, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
}

test "strErrorR hands off exact-fit and truncated windows without bleed" {
    var backing = [_]u8{0x6d} ** 18;

    const exact = str_error_r.strErrorR(0, backing[1..9]);
    try std.testing.expectEqualStrings("Success", exact);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, 0x6d), backing[0]);
    try std.testing.expectEqual(@as(u8, 0x6d), backing[9]);

    const clipped = str_error_r.strErrorR(13, backing[9..15]);
    try std.testing.expectEqualStrings("Permi", clipped);
    try std.testing.expectEqual(@as(u8, 0), backing[14]);
    try std.testing.expectEqualStrings("Success", backing[1..8]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, 0x6d), backing[15]);
}

test "vsprintf hands off padded and direct windows independently" {
    var backing = [_]u8{0x4e} ** 14;

    const left = backing[1..6];
    const left_written = vsprintf.scnprintfPad(left, left.len, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 3), left_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'd', ' ', ' ', 0 }, left);
    try std.testing.expectEqual(@as(u8, 0x4e), backing[0]);
    try std.testing.expectEqual(@as(u8, 0x4e), backing[6]);

    const right = backing[8..13];
    const right_written = vsprintf.vscnprintf(right, "{s}:{d}", .{ "q", 7 });
    try std.testing.expectEqual(@as(usize, 3), right_written);
    try std.testing.expectEqualStrings("q:7", right[0..right_written]);
    try std.testing.expectEqual(@as(u8, 0), right[right_written]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'd', ' ', ' ', 0 }, left);
    try std.testing.expectEqual(@as(u8, 0x4e), backing[7]);
    try std.testing.expectEqual(@as(u8, 0x4e), backing[13]);
}

test "zalloc hands off bytes and values without losing zero-reset guarantees" {
    const allocator = std.testing.allocator;
    const Payload = extern struct {
        tag: u8,
        count: u16,
        armed: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &value);

    @memset(bytes.?, 0xa4);
    value.?.tag = 9;
    value.?.count = 33;
    value.?.armed = true;

    zalloc.zfreeValue(allocator, Payload, &value);
    try std.testing.expect(value == null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa4, 0xa4, 0xa4, 0xa4 }, bytes.?);

    value = try zalloc.zallocValue(allocator, Payload);
    defer zalloc.zfreeValue(allocator, Payload, &value);
    try std.testing.expectEqual(@as(u8, 0), value.?.tag);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.armed);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);
    try std.testing.expectEqual(@as(u8, 0), value.?.tag);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.armed);
}
