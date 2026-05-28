const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab clamped turnover keeps live sibling counts stable across failed and reclaimed requests" {
    slab.kmalloc_nr_allocated = 0;

    const array = slab.kmallocArray(3, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (array) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const reclaimed = slab.kmallocBytes(2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, reclaimed);
    slab.kfree(reclaimed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR clamped turnover preserves sentinels across one-byte and fallback windows" {
    var backing = [_]u8{0xab} ** 20;

    const one_byte = str_error_r.strErrorR(13, backing[4..5]);
    try std.testing.expectEqual(@as(usize, 0), one_byte.len);
    try std.testing.expectEqual(@as(u8, 0xab), backing[3]);
    try std.testing.expectEqual(@as(u8, 0), backing[4]);
    try std.testing.expectEqual(@as(u8, 0xab), backing[5]);

    const fallback = str_error_r.strErrorR(4096, backing[9..16]);
    try std.testing.expectEqualStrings("INTERN", fallback);
    try std.testing.expectEqual(@as(u8, 0xab), backing[8]);
    try std.testing.expectEqual(@as(u8, 0), backing[15]);
    try std.testing.expectEqual(@as(u8, 0xab), backing[16]);
}

test "vsprintf clamped turnover reuses the same window after zero logical size and direct truncation" {
    var backing = [_]u8{0x44} ** 13;
    const window = backing[3..8];

    const zero_written = vsprintf.scnprintfPad(window, 0, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), zero_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0x44, 0x44, 0x44, 0x44 }, window);
    try std.testing.expectEqual(@as(u8, 0x44), backing[2]);
    try std.testing.expectEqual(@as(u8, 0x44), backing[8]);

    const direct_written = vsprintf.scnprintf(window, "{s}", .{"tooling"});
    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 't', 'o', 'o', 'l', 0 }, window);
    try std.testing.expectEqual(@as(u8, 0x44), backing[2]);
    try std.testing.expectEqual(@as(u8, 0x44), backing[8]);
}

test "zalloc clamped turnover rezeroes fresh owners after free while repeated null cleanup stays safe" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u32,
        enabled: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    @memcpy(bytes.?, &[_]u8{ 1, 2, 3, 4 });
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    value.?.count = 99;
    value.?.enabled = true;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.enabled);
}
