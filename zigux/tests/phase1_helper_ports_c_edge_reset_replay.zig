const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 replay keeps zero-length slab allocations balanced" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const array = slab.kmallocArray(0, 16, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), array.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 replay keeps strerror_r writes fenced to caller subviews" {
    var exact_backing = [_]u8{'#'} ** 12;
    const exact = str_error_r.strErrorR(0, exact_backing[1..9]);
    try std.testing.expectEqualStrings("Success", exact);
    try std.testing.expectEqual(@as(u8, '#'), exact_backing[0]);
    try std.testing.expectEqual(@as(u8, '#'), exact_backing[9]);

    var tiny_backing = [_]u8{'#'} ** 12;
    const tiny = str_error_r.strErrorR(4096, tiny_backing[4..8]);
    try std.testing.expectEqualStrings("INT", tiny);
    try std.testing.expectEqual(@as(u8, '#'), tiny_backing[3]);
    try std.testing.expectEqual(@as(u8, '#'), tiny_backing[8]);
    try std.testing.expectEqual(@as(u8, 0), tiny_backing[7]);
}

test "lane10 replay reuses padded vsprintf caller windows without leaking outside the view" {
    var padded_backing = [_]u8{0xfa} ** 12;
    const padded_written = vsprintf.scnprintfPad(padded_backing[2..9], 6, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 5), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'd', ' ', ' ', ' ', ' ', 0 }, padded_backing[2..9]);
    try std.testing.expectEqual(@as(u8, 0xfa), padded_backing[1]);
    try std.testing.expectEqual(@as(u8, 0xfa), padded_backing[9]);

    var alias_backing = [_]u8{0xfb} ** 9;
    const alias_written = vsprintf.vscnprintf(alias_backing[1..8], "{s}:{d}", .{ "z", 7 });
    try std.testing.expectEqual(@as(usize, 3), alias_written);
    try std.testing.expectEqualStrings("z:7", alias_backing[1 .. 1 + alias_written]);
    try std.testing.expectEqual(@as(u8, 0), alias_backing[4]);
    try std.testing.expectEqual(@as(u8, 0xfb), alias_backing[0]);
    try std.testing.expectEqual(@as(u8, 0xfb), alias_backing[8]);
}

test "lane10 replay keeps zalloc zero-sized bytes and repeated frees stable" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u32,
        flags: [3]u8,
        ready: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u32, 0), value.?.count);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.flags);
    try std.testing.expectEqual(false, value.?.ready);
    value.?.count = 9;
    value.?.flags = .{ 1, 2, 3 };
    value.?.ready = true;

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
