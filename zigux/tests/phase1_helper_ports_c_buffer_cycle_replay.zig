const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 replay keeps slab allocation cycles balanced across zeroed and empty buffers" {
    slab.kmalloc_nr_allocated = 0;

    const zeroed = slab.kmallocArray(1, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 3), zeroed.len);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(2, 4, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 replay keeps strerror_r writes inside alternating caller windows" {
    var backing = [_]u8{'#'} ** 18;

    const known = str_error_r.strErrorR(22, backing[1..4]);
    try std.testing.expectEqualStrings("In", known);
    try std.testing.expectEqual(@as(u8, '#'), backing[0]);
    try std.testing.expectEqual(@as(u8, 0), backing[3]);
    try std.testing.expectEqual(@as(u8, '#'), backing[4]);

    const unknown = str_error_r.strErrorR(4096, backing[10..16]);
    try std.testing.expectEqualStrings("INTER", unknown);
    try std.testing.expectEqual(@as(u8, '#'), backing[9]);
    try std.testing.expectEqual(@as(u8, 0), backing[15]);
    try std.testing.expectEqual(@as(u8, '#'), backing[16]);
}

test "lane10 replay keeps vsprintf buffer cycles inside inner views" {
    var backing = [_]u8{0x41} ** 11;
    const inner = backing[1..9];

    const padded = vsprintf.scnprintfPad(inner, 6, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 5), padded);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', ' ', ' ', 0, 0x41 }, inner);
    try std.testing.expectEqual(@as(u8, 0x41), backing[0]);
    try std.testing.expectEqual(@as(u8, 0x41), backing[9]);

    const direct = vsprintf.vscnprintf(inner[2..], "{d}", .{42});
    try std.testing.expectEqual(@as(usize, 2), direct);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', '4', '2', 0, ' ', 0, 0x41 }, inner);
    try std.testing.expectEqual(@as(u8, 0x41), backing[0]);
    try std.testing.expectEqual(@as(u8, 0x41), backing[9]);
}

test "lane10 replay keeps zalloc bytes and values reusable after null-safe frees" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [2]u8,
        ready: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);
    bytes.?[0] = 7;
    bytes.?[1] = 8;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);

    var value: ?*Value = null;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as([2]u8, .{ 0, 0 }), value.?.bytes);
    try std.testing.expectEqual(false, value.?.ready);
    value.?.bytes = .{ 9, 3 };
    value.?.ready = true;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as([2]u8, .{ 0, 0 }), value.?.bytes);
    try std.testing.expectEqual(false, value.?.ready);
}
