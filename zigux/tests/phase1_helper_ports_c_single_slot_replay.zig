const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab tracks zero-sized single-element arrays separately from one-byte arrays" {
    slab.kmalloc_nr_allocated = 0;

    const zero_sized = slab.kmallocArray(1, 0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    const single_byte = slab.kmallocArray(1, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        slab.kfree(zero_sized);
        return error.TestUnexpectedResult;
    };

    try std.testing.expectEqual(@as(usize, 0), zero_sized.len);
    try std.testing.expectEqual(@as(usize, 1), single_byte.len);
    try std.testing.expectEqual(@as(u8, 0), single_byte[0]);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(single_byte);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero_sized);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR renders adjacent known-message prefixes into two-byte windows" {
    var backing = [_]u8{'+'} ** 8;

    const success = str_error_r.strErrorR(0, backing[1..3]);
    try std.testing.expectEqualStrings("S", success);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '+', 'S', 0, '+', '+', '+', '+', '+' }, &backing);

    const invalid = str_error_r.strErrorR(22, backing[4..6]);
    try std.testing.expectEqualStrings("I", invalid);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '+', 'S', 0, '+', 'I', 0, '+', '+' }, &backing);
}

test "vsprintf keeps one-slot and zero-slot pad windows isolated" {
    var backing = [_]u8{'^'} ** 8;

    const one_written = vsprintf.scnprintfPad(backing[2..5], 1, "{s}", .{"alpha"});
    try std.testing.expectEqual(@as(usize, 1), one_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '^', '^', 'a', 0, '^', '^', '^', '^' }, &backing);

    const zero_written = vsprintf.scnprintfPad(backing[4..7], 0, "{s}", .{"beta"});
    try std.testing.expectEqual(@as(usize, 0), zero_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '^', '^', 'a', 0, 0, '^', '^', '^' }, &backing);
}

test "zalloc re-zeroes single-byte buffers and single-field values" {
    const allocator = std.testing.allocator;
    const ByteValue = extern struct {
        value: u8,
    };

    var first_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    try std.testing.expect(first_bytes != null);
    try std.testing.expectEqual(@as(usize, 1), first_bytes.?.len);
    try std.testing.expectEqual(@as(u8, 0), first_bytes.?[0]);
    first_bytes.?[0] = 0xff;
    zalloc.zfreeBytes(allocator, &first_bytes);
    try std.testing.expect(first_bytes == null);

    var second_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    defer zalloc.zfreeBytes(allocator, &second_bytes);
    try std.testing.expect(second_bytes != null);
    try std.testing.expectEqual(@as(u8, 0), second_bytes.?[0]);

    var first_value: ?*ByteValue = try zalloc.zallocValue(allocator, ByteValue);
    try std.testing.expect(first_value != null);
    try std.testing.expectEqual(@as(u8, 0), first_value.?.value);
    first_value.?.value = 0xee;
    zalloc.zfreeValue(allocator, ByteValue, &first_value);
    try std.testing.expect(first_value == null);

    var second_value: ?*ByteValue = try zalloc.zallocValue(allocator, ByteValue);
    defer zalloc.zfreeValue(allocator, ByteValue, &second_value);
    try std.testing.expect(second_value != null);
    try std.testing.expectEqual(@as(u8, 0), second_value.?.value);
}
