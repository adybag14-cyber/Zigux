const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 staggered slab counters survive reclaimless gaps and partial frees" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO);
    defer slab.kfree(bytes);
    const array = slab.kmallocArray(3, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    var array_opt: ?[]u8 = array;
    defer slab.kfree(array_opt);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(array_opt);
    array_opt = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "lane10 staggered strErrorR offset windows keep neighbors untouched" {
    var backing = [_]u8{0x7e} ** 80;

    const known_view = backing[5..24];
    const known = str_error_r.strErrorR(13, known_view);
    try std.testing.expectEqualStrings("Permission denied", known);
    try std.testing.expectEqual(@as(u8, 0x7e), backing[4]);
    try std.testing.expectEqual(@as(u8, 0), backing[5 + known.len]);
    try std.testing.expectEqual(@as(u8, 0x7e), backing[24]);

    const generated_view = backing[33..65];
    const generated = str_error_r.strErrorR(4096, generated_view);
    try std.testing.expect(std.mem.startsWith(u8, generated, "INTERNAL ERROR: "));
    try std.testing.expectEqual(@as(u8, 0x7e), backing[32]);
    try std.testing.expectEqual(@as(u8, 0), backing[33 + generated.len]);
    try std.testing.expectEqual(@as(u8, 0x7e), backing[65]);
}

test "lane10 staggered vsprintf zero-size offset windows stay reusable" {
    var backing = [_]u8{'.'} ** 16;
    const offset_view = backing[4..10];

    const cleared = vsprintf.scnprintfPad(offset_view, 0, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), cleared);
    try std.testing.expectEqual(@as(u8, '.'), backing[3]);
    try std.testing.expectEqual(@as(u8, 0), backing[4]);
    try std.testing.expectEqual(@as(u8, '.'), backing[5]);
    try std.testing.expectEqual(@as(u8, '.'), backing[10]);

    const reused = vsprintf.scnprintf(offset_view, "{s}", .{"hi"});
    try std.testing.expectEqual(@as(usize, 2), reused);
    try std.testing.expectEqualStrings("hi", backing[4 .. 4 + reused]);
    try std.testing.expectEqual(@as(u8, 0), backing[4 + reused]);
    try std.testing.expectEqual(@as(u8, '.'), backing[7]);
}

test "lane10 staggered zalloc frees reset handles before fresh nested zeroing" {
    const allocator = std.testing.allocator;
    const Value = extern struct {
        bytes: [3]u8,
        nested: extern struct {
            left: u16,
            right: u8,
        },
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0xaa);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    value.?.* = .{
        .bytes = .{ 9, 8, 7 },
        .nested = .{ .left = 99, .right = 4 },
    };
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    var fresh: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &fresh);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &fresh.?.bytes);
    try std.testing.expectEqual(@as(u16, 0), fresh.?.nested.left);
    try std.testing.expectEqual(@as(u8, 0), fresh.?.nested.right);
}
