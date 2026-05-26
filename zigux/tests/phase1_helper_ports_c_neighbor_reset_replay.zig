const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps neighboring zero-sized and non-zero owners balanced" {
    slab.kmalloc_nr_allocated = 0;

    const zero_array = slab.kmallocArray(3, 0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(zero_array);
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);

    const bytes = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    defer slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(2, 2, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0 }, bytes);
}

test "strErrorR resets adjacent caller windows independently" {
    var backing = [_]u8{0x7a} ** 18;

    const known = str_error_r.strErrorR(0, backing[2..10]);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[1]);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[10]);

    const fallback = str_error_r.strErrorR(4096, backing[10..15]);
    try std.testing.expectEqualStrings("INTE", fallback);
    try std.testing.expectEqual(@as(u8, 0), backing[14]);
    try std.testing.expectEqual(@as(u8, 0), backing[9]);
    try std.testing.expectEqual(@as(u8, 0x7a), backing[15]);
}

test "vsprintf resets neighboring caller windows without crossing the fence" {
    var backing = [_]u8{0x5c} ** 12;
    const outer = backing[1..7];
    const outer_written = vsprintf.scnprintf(outer, "{s}:{d}", .{ "xy", 9 });

    try std.testing.expectEqual(@as(usize, 4), outer_written);
    try std.testing.expectEqualStrings("xy:9", outer[0..outer_written]);
    try std.testing.expectEqual(@as(u8, 0), outer[outer_written]);
    try std.testing.expectEqual(@as(u8, 0x5c), backing[0]);
    try std.testing.expectEqual(@as(u8, 0x5c), backing[7]);

    const inner = backing[7..12];
    const inner_written = vsprintf.scnprintfPad(inner, 3, "{s}", .{"tools"});
    try std.testing.expectEqual(@as(usize, 3), inner_written);
    try std.testing.expectEqualStrings("too", inner[0..inner_written]);
    try std.testing.expectEqual(@as(u8, 0), inner[inner_written]);
    try std.testing.expectEqual(@as(u8, 0), outer[outer_written]);
}

test "zalloc reuses one owner from zero after a neighboring free" {
    const allocator = std.testing.allocator;
    const Pair = extern struct {
        left: u8,
        right: u8,
        armed: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &value);

    @memset(bytes.?, 0x33);
    value.?.left = 4;
    value.?.right = 9;
    value.?.armed = true;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expectEqual(@as(u8, 4), value.?.left);
    try std.testing.expectEqual(@as(u8, 9), value.?.right);
    try std.testing.expectEqual(true, value.?.armed);

    bytes = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);

    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);
    value = try zalloc.zallocValue(allocator, Pair);
    defer zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expectEqual(@as(u8, 0), value.?.left);
    try std.testing.expectEqual(@as(u8, 0), value.?.right);
    try std.testing.expectEqual(false, value.?.armed);
}
