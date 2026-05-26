const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zeroed sibling allocation leaves earlier bytes intact" {
    slab.kmalloc_nr_allocated = 0;

    const plain = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(plain);
    @memset(plain, 0x5a);

    const zeroed = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x5a, 0x5a, 0x5a, 0x5a }, plain);
    for (zeroed) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}

test "strErrorR one-byte caller windows only touch their own slot" {
    var backing = [_]u8{0xaa} ** 8;

    const known = str_error_r.strErrorR(13, backing[2..3]);
    try std.testing.expectEqual(@as(usize, 0), known.len);
    try std.testing.expectEqual(@as(u8, 0), backing[2]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[1]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[3]);

    const fallback = str_error_r.strErrorR(4096, backing[5..6]);
    try std.testing.expectEqual(@as(usize, 0), fallback.len);
    try std.testing.expectEqual(@as(u8, 0), backing[5]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[4]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[6]);
}

test "vsprintf interior micro windows keep outside guard bytes unchanged" {
    var scn = [_]u8{0xcc} ** 8;
    const scn_written = vsprintf.scnprintf(scn[2..5], "{s}", .{"tool"});
    try std.testing.expectEqual(@as(usize, 2), scn_written);
    try std.testing.expectEqual(@as(u8, 't'), scn[2]);
    try std.testing.expectEqual(@as(u8, 'o'), scn[3]);
    try std.testing.expectEqual(@as(u8, 0), scn[4]);
    try std.testing.expectEqual(@as(u8, 0xcc), scn[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), scn[5]);

    var pad = [_]u8{0xdd} ** 8;
    const pad_written = vsprintf.scnprintfPad(pad[3..7], 2, "{s}", .{"abc"});
    try std.testing.expectEqual(@as(usize, 2), pad_written);
    try std.testing.expectEqual(@as(u8, 'a'), pad[3]);
    try std.testing.expectEqual(@as(u8, 'b'), pad[4]);
    try std.testing.expectEqual(@as(u8, 0), pad[5]);
    try std.testing.expectEqual(@as(u8, 0xdd), pad[2]);
    try std.testing.expectEqual(@as(u8, 0xdd), pad[6]);
}

test "zalloc refreshed bytes do not disturb a live sibling value" {
    const allocator = std.testing.allocator;
    const Value = struct {
        left: u16,
        right: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &bytes);
    bytes.?[0] = 9;
    bytes.?[1] = 8;

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    value.?.left = 17;
    value.?.right = 19;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u16, 17), value.?.left);
    try std.testing.expectEqual(@as(u16, 19), value.?.right);

    bytes = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expect(bytes != null);
    for (bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }
}
