const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab replay keeps null-free and zeroed reentry counters aligned" {
    slab.kmalloc_nr_allocated = 0;
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const first = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const second = slab.kmallocArray(2, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (second) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
}

test "strErrorR replay fences offset caller views for known and fallback messages" {
    var known_backing = [_]u8{0xa1} ** 10;
    const known_view = known_backing[2..7];
    const known = str_error_r.strErrorR(0, known_view);
    try std.testing.expectEqualStrings("Succ", known);
    try std.testing.expectEqual(@as(u8, 0xa1), known_backing[1]);
    try std.testing.expectEqual(@as(u8, 0xa1), known_backing[7]);
    try std.testing.expectEqual(@as(u8, 0), known_backing[6]);

    var fallback_backing = [_]u8{0xb2} ** 12;
    const fallback_view = fallback_backing[1..9];
    const fallback = str_error_r.strErrorR(4096, fallback_view);
    try std.testing.expectEqualStrings("INTERNA", fallback);
    try std.testing.expectEqual(@as(u8, 0xb2), fallback_backing[0]);
    try std.testing.expectEqual(@as(u8, 0xb2), fallback_backing[9]);
    try std.testing.expectEqual(@as(u8, 0), fallback_backing[8]);
}

test "vsprintf replay keeps offset caller fences intact across narrow writes" {
    var padded_backing = [_]u8{0xc3} ** 9;
    const padded_view = padded_backing[2..8];
    const padded_written = vsprintf.scnprintfPad(padded_view, 1, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 1), padded_written);
    try std.testing.expectEqual(@as(u8, 0xc3), padded_backing[1]);
    try std.testing.expectEqual(@as(u8, 'z'), padded_backing[2]);
    try std.testing.expectEqual(@as(u8, 0), padded_backing[3]);
    try std.testing.expectEqual(@as(u8, 0xc3), padded_backing[8]);

    var direct_backing = [_]u8{0xd4} ** 8;
    const direct_view = direct_backing[1..6];
    const direct_written = vsprintf.vscnprintf(direct_view, "{s}", .{"abcdef"});
    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqualStrings("abcd", direct_view[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), direct_view[direct_written]);
    try std.testing.expectEqual(@as(u8, 0xd4), direct_backing[0]);
    try std.testing.expectEqual(@as(u8, 0xd4), direct_backing[6]);
}

test "zalloc replay zeroes aggregates and repeated frees stay null" {
    const allocator = std.testing.allocator;
    const Aggregate = extern struct {
        bytes: [4]u8,
        flag: bool,
        count: u16,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Aggregate = try zalloc.zallocValue(allocator, Aggregate);
    defer zalloc.zfreeValue(allocator, Aggregate, &value);
    try std.testing.expectEqualSlices(u8, &[_]u8{0} ** @sizeOf(Aggregate), std.mem.asBytes(value.?));
    zalloc.zfreeValue(allocator, Aggregate, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Aggregate, &value);
    try std.testing.expect(value == null);
}
