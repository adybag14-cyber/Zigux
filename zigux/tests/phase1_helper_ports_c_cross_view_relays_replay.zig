const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 slab keeps cross-view allocations stable across staggered release order" {
    slab.kmalloc_nr_allocated = 0;

    const plain = slab.kmallocArray(2, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    const zeroed = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memset(plain, 0x5a);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x5a, 0x5a, 0x5a, 0x5a }, plain);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, zeroed);

    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x5a, 0x5a, 0x5a, 0x5a }, plain);

    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 strErrorR relays across separated caller windows without bleeding guards" {
    var backing = [_]u8{'?'} ** 24;

    const left = str_error_r.strErrorR(22, backing[2..10]);
    const right = str_error_r.strErrorR(0, backing[13..21]);

    try std.testing.expectEqualStrings("Invalid", left);
    try std.testing.expectEqualStrings("Success", right);
    try std.testing.expectEqual(@as(u8, '?'), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try std.testing.expectEqual(@as(u8, '?'), backing[10]);
    try std.testing.expectEqual(@as(u8, '?'), backing[12]);
    try std.testing.expectEqual(@as(u8, 0), backing[20]);
    try std.testing.expectEqual(@as(u8, '?'), backing[21]);
}

test "lane10 vsprintf keeps cross-view relay windows and sentinels intact" {
    var backing = [_]u8{'~'} ** 18;

    const padded_written = vsprintf.scnprintfPad(backing[2..9], 4, "{s}", .{"yo"});
    const truncated_written = vsprintf.scnprintf(backing[11..16], "{s}", .{"value"});

    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqual(@as(usize, 4), truncated_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'y', 'o', ' ', ' ', 0 }, backing[2..7]);
    try std.testing.expectEqualSlices(u8, "valu", backing[11..15]);
    try std.testing.expectEqual(@as(u8, 0), backing[15]);
    try std.testing.expectEqual(@as(u8, '~'), backing[1]);
    try std.testing.expectEqual(@as(u8, '~'), backing[9]);
    try std.testing.expectEqual(@as(u8, '~'), backing[10]);
    try std.testing.expectEqual(@as(u8, '~'), backing[16]);
}

test "lane10 zalloc frees byte owners first without disturbing live value owners" {
    const allocator = std.testing.allocator;
    const Relay = struct {
        count: u16,
        enabled: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Relay = try zalloc.zallocValue(allocator, Relay);
    defer zalloc.zfreeValue(allocator, Relay, &value);

    bytes.?[2] = 0x44;
    value.?.count = 12;
    value.?.enabled = true;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u16, 12), value.?.count);
    try std.testing.expectEqual(true, value.?.enabled);

    zalloc.zfreeValue(allocator, Relay, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeBytes(allocator, &bytes);
    zalloc.zfreeValue(allocator, Relay, &value);
}
