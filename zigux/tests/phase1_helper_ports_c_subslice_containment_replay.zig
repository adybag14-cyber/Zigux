const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab subslices keep live allocations isolated while counters unwind in order" {
    slab.kmalloc_nr_allocated = 0;

    const zeroed_array = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zeroed_array) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const sibling = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (sibling) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(zeroed_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 4), sibling.len);
    slab.kfree(sibling);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR contained subviews preserve outer sentinels across known and fallback windows" {
    var backing = [_]u8{0xcc} ** 28;

    const known = str_error_r.strErrorR(12, backing[2..8]);
    try std.testing.expectEqualStrings("Canno", known);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[8]);

    const fallback = str_error_r.strErrorR(4096, backing[15..25]);
    try std.testing.expectEqualStrings("INTERNAL ", fallback);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[14]);
    try std.testing.expectEqual(@as(u8, 0), backing[24]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[25]);
}

test "vsprintf contained interior windows keep neighboring bytes intact across padded and direct renders" {
    var backing = [_]u8{0x5d} ** 14;

    const padded_written = vsprintf.scnprintfPad(backing[1..7], 4, "{s}", .{"a"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', ' ', ' ', ' ', 0, 0x5d }, backing[1..7]);
    try std.testing.expectEqual(@as(u8, 0x5d), backing[0]);
    try std.testing.expectEqual(@as(u8, 0x5d), backing[7]);

    const direct_written = vsprintf.vscnprintf(backing[8..13], "{s}", .{"tooling"});
    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 't', 'o', 'o', 'l', 0 }, backing[8..13]);
    try std.testing.expectEqual(@as(u8, 0x5d), backing[7]);
    try std.testing.expectEqual(@as(u8, 0x5d), backing[13]);
}

test "zalloc contained owners stay independent when values and bytes release in staggered order" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u32,
        enabled: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    @memcpy(bytes.?, &[_]u8{ 9, 8, 7 });
    value.?.count = 12;
    value.?.enabled = true;

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 9, 8, 7 }, bytes.?);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
}
