const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps zero-sized allocations balanced across byte and array paths" {
    slab.kmalloc_nr_allocated = 0;

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zero_array = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR confines writes to the provided subview" {
    var backing = [_]u8{0xaa} ** 8;
    const known = str_error_r.strErrorR(22, backing[1..7]);

    try std.testing.expectEqualStrings("Inval", known);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[0]);
    try std.testing.expectEqualSlices(u8, "Inval", backing[1..6]);
    try std.testing.expectEqual(@as(u8, 0), backing[6]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[7]);

    var empty_backing = [_]u8{0xbb} ** 4;
    const empty = str_error_r.strErrorR(0, empty_backing[2..2]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xbb, 0xbb, 0xbb, 0xbb }, &empty_backing);
}

test "vsprintf keeps neighbors intact when reusing anchored subviews" {
    var backing = [_]u8{0xcc} ** 8;
    const view = backing[1..6];

    const written = vsprintf.scnprintf(view, "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[0]);
    try std.testing.expectEqualSlices(u8, "abcd", view[0..written]);
    try std.testing.expectEqual(@as(u8, 0), view[written]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[6]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[7]);

    const padded = vsprintf.scnprintfPad(view, 3, "{s}", .{"x"});
    try std.testing.expectEqual(@as(usize, 2), padded);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[0]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', ' ', ' ', 0 }, view[0..4]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[6]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[7]);
}

test "zalloc zeroes aggregate values and repeated frees stay stable" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [3]u8,
        nested: struct {
            flag: bool,
            count: u16,
        },
        optional: ?u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqualDeep(std.mem.zeroes(Value), value.?.*);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
