const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps live owners separate from rejected requests" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(first);
    const second = slab.kmallocArray(2, 3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(second);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    @memset(first, 0x11);
    @memset(second, 0x22);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x11, 0x11, 0x11, 0x11 }, first);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x22, 0x22, 0x22, 0x22, 0x22, 0x22 }, second);
}

test "str_error_r keeps caller ownership inside the chosen subslice" {
    var backing = [_]u8{0xaa} ** 16;
    const rendered = str_error_r.strErrorR(13, backing[3..9]);

    try std.testing.expectEqualStrings("Permi", rendered);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa }, backing[0..3]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa }, backing[9..16]);

    const fallback = str_error_r.strErrorR(4096, backing[4..8]);
    try std.testing.expectEqualStrings("INT", fallback);
    try std.testing.expectEqual(@as(u8, 0), backing[7]);
    try std.testing.expectEqual(@as(u8, 'P'), backing[3]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa }, backing[8..16]);
}

test "vsprintf keeps writes inside the active caller view" {
    var backing = [_]u8{0xcc} ** 12;
    const outer = backing[2..7];
    const outer_written = vsprintf.scnprintf(outer, "{s}:{d}", .{ "ab", 3 });

    try std.testing.expectEqual(@as(usize, 4), outer_written);
    try std.testing.expectEqualStrings("ab:3", outer[0..outer_written]);
    try std.testing.expectEqual(@as(u8, 0), outer[outer_written]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc }, backing[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc, 0xcc, 0xcc }, backing[7..12]);

    const inner = outer[1..4];
    const inner_written = vsprintf.vscnprintf(inner, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 2), inner_written);
    try std.testing.expectEqualStrings("zi", inner[0..inner_written]);
    try std.testing.expectEqual(@as(u8, 0), inner[inner_written]);
    try std.testing.expectEqual(@as(u8, 'a'), outer[0]);
    try std.testing.expectEqual(@as(u8, 0), outer[4]);
}

test "zalloc frees one owner without disturbing another" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u16,
        flag: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    @memset(bytes.?, 0x5a);
    value.?.count = 9;
    value.?.flag = true;

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    try std.testing.expect(value != null);
    try std.testing.expectEqual(@as(u16, 9), value.?.count);
    try std.testing.expectEqual(true, value.?.flag);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    bytes = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &bytes);
    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, bytes.?);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.flag);
}
