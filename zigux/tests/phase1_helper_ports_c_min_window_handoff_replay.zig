const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-length allocations keep reclaim accounting honest" {
    slab.kmalloc_nr_allocated = 0;

    const empty = slab.kmallocArray(0, 9, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const plain = slab.kmallocArray(3, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 6), plain.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    @memset(plain, 0x5a);
    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps one-byte caller windows and outer guards stable" {
    var bytes = [_]u8{0xaa} ** 12;

    const tiny = str_error_r.strErrorR(13, bytes[2..3]);
    try std.testing.expectEqual(@as(usize, 0), tiny.len);
    try std.testing.expectEqual(@as(u8, 0xaa), bytes[1]);
    try std.testing.expectEqual(@as(u8, 0), bytes[2]);
    try std.testing.expectEqual(@as(u8, 0xaa), bytes[3]);

    const exact = str_error_r.strErrorR(0, bytes[4..12]);
    try std.testing.expectEqualStrings("Success", exact);
    try std.testing.expectEqual(@as(u8, 0), bytes[11]);
}

test "vsprintf respects narrow subviews and preserves surrounding bytes" {
    var padded = [_]u8{0xcc} ** 6;
    const padded_written = vsprintf.scnprintfPad(padded[1..5], 3, "{s}", .{"w"});
    try std.testing.expectEqual(@as(usize, 2), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 'w', ' ', ' ', 0, 0xcc }, &padded);

    var narrow = [_]u8{0xdd} ** 3;
    const narrow_written = vsprintf.vscnprintf(narrow[1..2], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), narrow_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 0, 0xdd }, &narrow);
}

test "zalloc zeroes nested values and double-free leaves null optionals alone" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [3]u8,
        nested: struct {
            mark: u16,
        },
        flag: bool,
    };

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(empty != null);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.bytes);
    try std.testing.expectEqual(@as(u16, 0), value.?.nested.mark);
    try std.testing.expectEqual(false, value.?.flag);

    zalloc.zfreeBytes(allocator, &empty);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);

    zalloc.zfreeValue(allocator, Value, &value);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
