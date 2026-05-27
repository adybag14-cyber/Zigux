const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps neighboring allocations isolated across interior ownership" {
    slab.kmalloc_nr_allocated = 0;

    const plain = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    const zeroed = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memset(plain, 0x5a);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, zeroed);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps writes inside the caller slice" {
    var backing = [_]u8{0xcc} ** 18;
    const rendered = str_error_r.strErrorR(13, backing[3..11]);

    try std.testing.expectEqualStrings("Permiss", rendered);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[2]);
    try std.testing.expectEqual(@as(u8, 0), backing[10]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[11]);
}

test "scnprintfPad respects leading and trailing bytes around interior views" {
    var backing = [_]u8{0x7e} ** 12;
    const written = vsprintf.scnprintfPad(backing[2..10], 7, "{s}", .{"hi"});

    try std.testing.expectEqual(@as(usize, 6), written);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 0x7e, 0x7e, 'h', 'i', ' ', ' ', ' ', ' ', ' ', 0, 0x7e, 0x7e },
        &backing,
    );
}

test "zalloc frees one owner without disturbing another" {
    const allocator = std.testing.allocator;
    const Value = struct {
        a: u16,
        b: u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    bytes.?[0] = 0xab;
    value.?.a = 9;
    value.?.b = 7;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u16, 9), value.?.a);
    try std.testing.expectEqual(@as(u8, 7), value.?.b);

    zalloc.zfreeBytes(allocator, &bytes);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
