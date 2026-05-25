const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab alternates rejected and live allocations without leaking counters" {
    slab.kmalloc_nr_allocated = 0;

    const zero = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(2, 3, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const array = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (array) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps sibling caller windows isolated across exact and narrow writes" {
    var backing = [_]u8{0xaa} ** 40;

    const exact = str_error_r.strErrorR(22, backing[1..18]);
    try std.testing.expectEqualStrings("Invalid argument", exact);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[0]);
    try std.testing.expectEqual(@as(u8, 0), backing[17]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[18]);

    const narrow = str_error_r.strErrorR(12, backing[20..23]);
    try std.testing.expectEqualStrings("Ca", narrow);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'C', 'a', 0 }, backing[20..23]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[19]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[23]);
}

test "vsprintf reuses sibling caller windows without crossing sentinels" {
    var backing = [_]u8{0xcc} ** 13;

    const left_written = vsprintf.vscnprintf(backing[1..6], "{s}", .{"wxyz"});
    try std.testing.expectEqual(@as(usize, 4), left_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'w', 'x', 'y', 'z', 0 }, backing[1..6]);

    const right_written = vsprintf.scnprintfPad(backing[7..12], 4, "{s}", .{"q"});
    try std.testing.expectEqual(@as(usize, 3), right_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'q', ' ', ' ', ' ', 0 }, backing[7..12]);

    try std.testing.expectEqual(@as(u8, 0xcc), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[6]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[12]);
}

test "zalloc rezeros bytes and values after alternating frees" {
    const allocator = std.testing.allocator;
    const Value = struct {
        flag: bool,
        count: u16,
        bytes: [3]u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    var value: ?*Value = try zalloc.zallocValue(allocator, Value);

    bytes.?[0] = 0x5a;
    bytes.?[4] = 0xa5;
    value.?.flag = true;
    value.?.count = 9;
    value.?.bytes = .{ 1, 2, 3 };

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &bytes);
    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    try std.testing.expectEqual(false, value.?.flag);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.bytes);
}
