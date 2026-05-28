const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab balances zero-length owners around null frees and reclaim-less failures" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    const alias = slab.kmallocArray(3, 0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(usize, 0), alias.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(1, 8, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(alias);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps one-slot and two-slot caller windows fenced" {
    var backing = [_]u8{'#'} ** 10;

    const empty_known = str_error_r.strErrorR(13, backing[3..4]);
    try std.testing.expectEqualStrings("", empty_known);
    try std.testing.expectEqualSlices(u8, "###", backing[0..3]);
    try std.testing.expectEqual(@as(u8, 0), backing[3]);
    try std.testing.expectEqual(@as(u8, '#'), backing[4]);

    const tiny_fallback = str_error_r.strErrorR(4096, backing[5..7]);
    try std.testing.expectEqualStrings("I", tiny_fallback);
    try std.testing.expectEqual(@as(u8, '#'), backing[4]);
    try std.testing.expectEqual(@as(u8, 'I'), backing[5]);
    try std.testing.expectEqual(@as(u8, 0), backing[6]);
    try std.testing.expectEqual(@as(u8, '#'), backing[7]);
}

test "vsprintf preserves terminator pockets in one-byte and shifted caller windows" {
    var backing = [_]u8{'!'} ** 8;

    const padded = vsprintf.scnprintfPad(backing[2..3], 8, "{s}", .{"abc"});
    try std.testing.expectEqual(@as(usize, 0), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', 0, '!', '!', '!', '!', '!' }, &backing);

    const shifted = vsprintf.vscnprintf(backing[4..7], "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 2), shifted);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', '!', 0, '!', 'x', 'y', 0, '!' }, &backing);
}

test "zalloc keeps null frees idempotent and reacquires zeroed owners" {
    const allocator = std.testing.allocator;
    const Owner = struct {
        count: u16,
        enabled: bool,
    };

    var bytes: ?[]u8 = null;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);
    @memset(bytes.?, 0x44);
    zalloc.zfreeBytes(allocator, &bytes);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);

    var owner: ?*Owner = null;
    zalloc.zfreeValue(allocator, Owner, &owner);
    owner = try zalloc.zallocValue(allocator, Owner);
    try std.testing.expectEqual(@as(u16, 0), owner.?.count);
    try std.testing.expectEqual(false, owner.?.enabled);
    owner.?.count = 7;
    owner.?.enabled = true;
    zalloc.zfreeValue(allocator, Owner, &owner);
    zalloc.zfreeValue(allocator, Owner, &owner);
    try std.testing.expect(owner == null);

    owner = try zalloc.zallocValue(allocator, Owner);
    defer zalloc.zfreeValue(allocator, Owner, &owner);
    try std.testing.expectEqual(@as(u16, 0), owner.?.count);
    try std.testing.expectEqual(false, owner.?.enabled);
}
