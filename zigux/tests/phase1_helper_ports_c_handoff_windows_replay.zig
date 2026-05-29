const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab handoff windows keep counters balanced across mixed release order" {
    slab.kmalloc_nr_allocated = 0;

    const zeroed = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const plain = slab.kmallocArray(3, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    for (zeroed) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    @memset(plain, 0x5a);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR confines reused caller windows and leaves gutters intact" {
    var backing = [_]u8{0xaa} ** 20;

    const known = str_error_r.strErrorR(13, backing[2..8]);
    try std.testing.expectEqualStrings("Permi", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa }, backing[0..2]);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[8]);

    const fallback = str_error_r.strErrorR(70000, backing[9..19]);
    try std.testing.expectEqualStrings("INTERNAL ", fallback);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[8]);
    try std.testing.expectEqual(@as(u8, 0), backing[18]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[19]);
}

test "vsprintf direct and padded handoff windows preserve neighboring sentinels" {
    var backing = [_]u8{0xcc} ** 18;

    const direct = vsprintf.vscnprintf(backing[1..7], "{s}:{d}", .{ "id", 42 });
    try std.testing.expectEqual(@as(usize, 5), direct);
    try std.testing.expectEqualStrings("id:42", backing[1 .. 1 + direct]);
    try std.testing.expectEqual(@as(u8, 0), backing[6]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[7]);

    const padded = vsprintf.scnprintfPad(backing[9..16], 6, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 5), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', ' ', ' ', 0 }, backing[9..16]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[8]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[16]);
}

test "zalloc optional handoffs zero fresh storage and tolerate repeated release" {
    const allocator = std.testing.allocator;
    const Payload = struct {
        tag: u16,
        enabled: bool,
        bytes: [3]u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    var payload: ?*Payload = try zalloc.zallocValue(allocator, Payload);
    try std.testing.expectEqual(@as(u16, 0), payload.?.tag);
    try std.testing.expectEqual(false, payload.?.enabled);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &payload.?.bytes);

    bytes.?[0] = 0xfe;
    payload.?.tag = 9;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expect(payload == null);
    zalloc.zfreeValue(allocator, Payload, &payload);
    try std.testing.expect(payload == null);
}
