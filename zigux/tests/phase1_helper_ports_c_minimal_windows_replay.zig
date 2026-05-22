const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps single-byte allocations balanced across reclaim and zero flags" {
    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocBytes(1, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocArray(1, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 1), zeroed.len);
    try std.testing.expectEqual(@as(u8, 0), zeroed[0]);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR one-byte windows collapse to empty strings without neighbor writes" {
    var known_backing = [_]u8{'K'} ** 5;
    const known = str_error_r.strErrorR(0, known_backing[2..3]);
    try std.testing.expectEqualStrings("", known);
    try std.testing.expectEqual(@as(u8, 'K'), known_backing[1]);
    try std.testing.expectEqual(@as(u8, 0), known_backing[2]);
    try std.testing.expectEqual(@as(u8, 'K'), known_backing[3]);

    var unknown_backing = [_]u8{'U'} ** 5;
    const unknown = str_error_r.strErrorR(4096, unknown_backing[1..2]);
    try std.testing.expectEqualStrings("", unknown);
    try std.testing.expectEqual(@as(u8, 'U'), unknown_backing[0]);
    try std.testing.expectEqual(@as(u8, 0), unknown_backing[1]);
    try std.testing.expectEqual(@as(u8, 'U'), unknown_backing[2]);
}

test "vsprintf tiny windows keep terminators local" {
    var narrow_backing = [_]u8{'?'} ** 5;
    const narrow = narrow_backing[2..3];
    const written = vsprintf.vscnprintf(narrow, "{s}", .{"abc"});
    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqual(@as(u8, '?'), narrow_backing[1]);
    try std.testing.expectEqual(@as(u8, 0), narrow_backing[2]);
    try std.testing.expectEqual(@as(u8, '?'), narrow_backing[3]);

    var padded_backing = [_]u8{'!'} ** 5;
    const padded = padded_backing[1..3];
    const padded_written = vsprintf.scnprintfPad(padded, 0, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 0), padded_written);
    try std.testing.expectEqual(@as(u8, '!'), padded_backing[0]);
    try std.testing.expectEqual(@as(u8, 0), padded_backing[1]);
    try std.testing.expectEqual(@as(u8, '!'), padded_backing[2]);
    try std.testing.expectEqual(@as(u8, '!'), padded_backing[3]);
}

test "zalloc zero-size bytes and tiny values reset their optionals cleanly" {
    const allocator = std.testing.allocator;
    const Tiny = struct {
        tag: u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Tiny = try zalloc.zallocValue(allocator, Tiny);
    try std.testing.expect(value != null);
    try std.testing.expectEqual(@as(u8, 0), value.?.tag);
    value.?.tag = 9;
    zalloc.zfreeValue(allocator, Tiny, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Tiny, &value);
    try std.testing.expect(value == null);
}
