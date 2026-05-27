const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps live allocation count stable across sibling windows" {
    slab.kmalloc_nr_allocated = 0;

    const left = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const right = slab.kmallocArray(2, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(right);
    defer slab.kfree(left);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    for (left) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "strErrorR respects caller subviews and keeps outer sentinels intact" {
    var backing = [_]u8{0xaa} ** 12;
    const rendered = str_error_r.strErrorR(13, backing[2..8]);

    try std.testing.expectEqualStrings("Permi", rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[8]);
}

test "vsprintf reuses disjoint caller windows without leaking across boundaries" {
    var backing = [_]u8{0xcc} ** 14;

    const left_written = vsprintf.scnprintf(backing[1..6], "{s}", .{"alpha"});
    const right_written = vsprintf.scnprintfPad(backing[7..13], 4, "{s}", .{"z"});

    try std.testing.expectEqual(@as(usize, 4), left_written);
    try std.testing.expectEqual(@as(usize, 3), right_written);
    try std.testing.expectEqualStrings("alph", backing[1 .. 1 + left_written]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', ' ', ' ', ' ', 0 }, backing[7..12]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[6]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[13]);
}

test "zalloc resets only the released owner and preserves the sibling" {
    const allocator = std.testing.allocator;
    const Pair = struct {
        value: u16,
        enabled: bool,
    };

    var left: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &left);
    var right: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &right);

    left.?[0] = 0x5a;
    right.?.value = 99;
    right.?.enabled = true;

    zalloc.zfreeBytes(allocator, &left);
    try std.testing.expect(left == null);
    try std.testing.expectEqual(@as(u16, 99), right.?.value);
    try std.testing.expectEqual(true, right.?.enabled);

    zalloc.zfreeValue(allocator, Pair, &right);
    try std.testing.expect(right == null);
}
