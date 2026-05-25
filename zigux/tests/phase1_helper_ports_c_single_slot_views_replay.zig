const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps exact single-slot allocations balanced" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const unit = slab.kmallocArray(1, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(unit);
    try std.testing.expectEqual(@as(usize, 1), unit.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), unit[0]);
}

test "strErrorR keeps single-slot and exact-fit caller views isolated" {
    var backing = [_]u8{0xaa} ** 10;

    const single = str_error_r.strErrorR(22, backing[2..3]);
    try std.testing.expectEqual(@as(usize, 0), single.len);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[2]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[3]);

    const exact = str_error_r.strErrorR(0, backing[1..9]);
    try std.testing.expectEqualStrings("Success", exact);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[0]);
    try std.testing.expectEqual(@as(u8, 'S'), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[9]);
}

test "vsprintf confines single-slot and exact-fit writes to the caller view" {
    var backing = [_]u8{0xdd} ** 8;

    const single = vsprintf.scnprintfPad(backing[2..3], 1, "{s}", .{"wide"});
    try std.testing.expectEqual(@as(usize, 0), single);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 0xdd, 0, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd }, &backing);

    const exact = vsprintf.scnprintfPad(backing[1..7], 5, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 4), exact);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 'x', 'y', ' ', ' ', ' ', 0, 0xdd }, &backing);

    const direct = vsprintf.vscnprintf(backing[1..7], "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 5), direct);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 'a', 'b', 'c', 'd', 'e', 0, 0xdd }, &backing);
}

test "zalloc re-zeroes exact single-byte and single-field views" {
    const allocator = std.testing.allocator;
    const Flag = struct {
        value: u8,
    };

    var byte: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    try std.testing.expect(byte != null);
    try std.testing.expectEqual(@as(usize, 1), byte.?.len);
    try std.testing.expectEqual(@as(u8, 0), byte.?[0]);
    byte.?[0] = 0x7f;
    zalloc.zfreeBytes(allocator, &byte);
    try std.testing.expect(byte == null);

    byte = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &byte);
    try std.testing.expectEqual(@as(u8, 0), byte.?[0]);

    var flag: ?*Flag = try zalloc.zallocValue(allocator, Flag);
    flag.?.value = 0x33;
    zalloc.zfreeValue(allocator, Flag, &flag);
    try std.testing.expect(flag == null);

    flag = try zalloc.zallocValue(allocator, Flag);
    defer zalloc.zfreeValue(allocator, Flag, &flag);
    try std.testing.expectEqual(@as(u8, 0), flag.?.value);
}
