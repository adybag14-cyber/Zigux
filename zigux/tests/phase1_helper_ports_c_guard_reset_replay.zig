const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports replay keeps slab zero-extent counters balanced" {
    slab.kmalloc_nr_allocated = 0;

    var empty_bytes: ?[]u8 = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.?.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var empty_array: ?[]u8 = slab.kmallocArray(4, 0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty_array.?.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(empty_array);
    empty_array = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(empty_bytes);
    empty_bytes = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "phase1 helper ports replay keeps strErrorR writes inside caller subviews" {
    var known_backing = [_]u8{0xaa} ** 12;
    const known_view = known_backing[2..8];
    const known = str_error_r.strErrorR(0, known_view);

    try std.testing.expectEqualStrings("Succe", known);
    try std.testing.expectEqual(@as(u8, 0xaa), known_backing[1]);
    try std.testing.expectEqual(@as(u8, 'S'), known_backing[2]);
    try std.testing.expectEqual(@as(u8, 0), known_backing[7]);
    try std.testing.expectEqual(@as(u8, 0xaa), known_backing[8]);

    var unknown_backing = [_]u8{0xbb} ** 14;
    const unknown_view = unknown_backing[3..7];
    const unknown = str_error_r.strErrorR(77, unknown_view);

    try std.testing.expectEqualStrings("INT", unknown);
    try std.testing.expectEqual(@as(u8, 0xbb), unknown_backing[2]);
    try std.testing.expectEqual(@as(u8, 'I'), unknown_backing[3]);
    try std.testing.expectEqual(@as(u8, 0), unknown_backing[6]);
    try std.testing.expectEqual(@as(u8, 0xbb), unknown_backing[7]);
}

test "phase1 helper ports replay keeps vsprintf caller windows isolated" {
    var direct_backing = [_]u8{0xcc} ** 11;
    var alias_backing = [_]u8{0xdd} ** 11;
    const direct_view = direct_backing[2..8];
    const alias_view = alias_backing[2..8];

    const direct_written = vsprintf.scnprintf(direct_view, "{s}", .{"status"});
    const alias_written = vsprintf.vscnprintf(alias_view, "{s}", .{"status"});

    try std.testing.expectEqual(@as(usize, 5), direct_written);
    try std.testing.expectEqual(direct_written, alias_written);
    try std.testing.expectEqualStrings("statu", direct_view[0..direct_written]);
    try std.testing.expectEqualStrings(direct_view[0..direct_written], alias_view[0..alias_written]);
    try std.testing.expectEqual(@as(u8, 0), direct_view[direct_written]);
    try std.testing.expectEqual(@as(u8, 0), alias_view[alias_written]);
    try std.testing.expectEqual(@as(u8, 0xcc), direct_backing[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), direct_backing[8]);
    try std.testing.expectEqual(@as(u8, 0xdd), alias_backing[1]);
    try std.testing.expectEqual(@as(u8, 0xdd), alias_backing[8]);

    var padded_backing = [_]u8{0xee} ** 10;
    const padded_view = padded_backing[1..7];
    const padded_written = vsprintf.scnprintfPad(padded_view, 5, "{s}", .{"ok"});

    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', ' ', ' ', ' ', 0 }, padded_view);
    try std.testing.expectEqual(@as(u8, 0xee), padded_backing[0]);
    try std.testing.expectEqual(@as(u8, 0xee), padded_backing[7]);
}

test "phase1 helper ports replay keeps zalloc zeroed and repeated resets safe" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [3]u8,
        count: u16,
        enabled: bool,
        child: ?*u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    try std.testing.expect(bytes != null);
    for (bytes.?) |item| {
        try std.testing.expectEqual(@as(u8, 0), item);
    }
    bytes.?[0] = 9;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.bytes);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.enabled);
    try std.testing.expect(value.?.child == null);
    value.?.bytes[1] = 7;

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
