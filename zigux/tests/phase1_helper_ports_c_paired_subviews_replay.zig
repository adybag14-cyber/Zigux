const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps paired allocations stable when one neighbor is released" {
    slab.kmalloc_nr_allocated = 0;

    const zeroed = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const plain = slab.kmallocBytes(5, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memset(plain, 0x33);
    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps paired subviews independent" {
    var backing = [_]u8{0xaa} ** 20;

    const left = str_error_r.strErrorR(13, backing[1..7]);
    const right = str_error_r.strErrorR(4096, backing[9..18]);

    try std.testing.expectEqualStrings("Permi", left);
    try std.testing.expectEqualStrings("INTERNAL", right);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[0]);
    try std.testing.expectEqual(@as(u8, 0), backing[6]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[7]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[8]);
    try std.testing.expectEqual(@as(u8, 0), backing[17]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[18]);
}

test "vsprintf keeps paired subviews and sentinels intact" {
    var backing = [_]u8{0x7c} ** 16;

    const left_written = vsprintf.scnprintf(backing[1..6], "{s}", .{"tide"});
    const right_written = vsprintf.scnprintfPad(backing[8..15], 5, "{d}", .{12});

    try std.testing.expectEqual(@as(usize, 4), left_written);
    try std.testing.expectEqual(@as(usize, 4), right_written);
    try std.testing.expectEqualStrings("tide", backing[1 .. 1 + left_written]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '1', '2', ' ', ' ', ' ', 0 }, backing[8..14]);
    try std.testing.expectEqual(@as(u8, 0x7c), backing[0]);
    try std.testing.expectEqual(@as(u8, 0), backing[5]);
    try std.testing.expectEqual(@as(u8, 0x7c), backing[6]);
    try std.testing.expectEqual(@as(u8, 0x7c), backing[7]);
    try std.testing.expectEqual(@as(u8, 0x7c), backing[14]);
    try std.testing.expectEqual(@as(u8, 0x7c), backing[15]);
}

test "zalloc frees one paired owner without disturbing the other" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        count: u16,
        ok: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &value);

    bytes.?[1] = 0x11;
    value.?.count = 4;
    value.?.ok = true;

    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);
    try std.testing.expectEqual(@as(u8, 0x11), bytes.?[1]);
    bytes.?[4] = 0x44;
    try std.testing.expectEqual(@as(u8, 0x44), bytes.?[4]);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
}
