const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "single-byte slab allocations keep counters balanced across bytes and arrays" {
    slab.kmalloc_nr_allocated = 0;

    const one_byte = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), one_byte.len);
    try std.testing.expectEqual(@as(u8, 0), one_byte[0]);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const one_array = slab.kmallocArray(1, 1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), one_array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(one_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(one_byte);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps one-slot caller windows fenced to the terminator byte" {
    var known = [_]u8{ 0xaa, 0xbb, 0xcc };
    const known_rendered = str_error_r.strErrorR(13, known[1..2]);
    try std.testing.expectEqual(@as(usize, 0), known_rendered.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0x00, 0xcc }, &known);

    var fallback = [_]u8{ 0x11, 0x22, 0x33 };
    const fallback_rendered = str_error_r.strErrorR(4096, fallback[1..2]);
    try std.testing.expectEqual(@as(usize, 0), fallback_rendered.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x11, 0x00, 0x33 }, &fallback);
}

test "vsprintf one-slot windows preserve sentinels for direct and padded routes" {
    var direct = [_]u8{ 0x44, 0x55, 0x66 };
    const direct_written = vsprintf.scnprintf(direct[1..2], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), direct_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x44, 0x00, 0x66 }, &direct);

    var padded = [_]u8{ 0x77, 0x88, 0x99, 0xaa };
    const padded_written = vsprintf.scnprintfPad(padded[1..3], 2, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 1), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x77, 'z', 0x00, 0xaa }, &padded);

    var mirrored = [_]u8{ 0xde, 0xad, 0xbe };
    const mirrored_written = vsprintf.vscnprintf(mirrored[1..2], "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), mirrored_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xde, 0x00, 0xbe }, &mirrored);
}

test "zalloc one-byte routes zero memory and make repeated frees inert" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 1);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 1), bytes.?.len);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[0]);

    bytes.?[0] = 0xff;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const Flag = struct {
        value: u8,
    };

    var flag: ?*Flag = try zalloc.zallocValue(allocator, Flag);
    try std.testing.expectEqual(@as(u8, 0), flag.?.value);
    flag.?.value = 0xaa;
    zalloc.zfreeValue(allocator, Flag, &flag);
    try std.testing.expect(flag == null);
    zalloc.zfreeValue(allocator, Flag, &flag);
    try std.testing.expect(flag == null);
}
