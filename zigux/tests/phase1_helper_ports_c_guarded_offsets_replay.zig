const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zero-sized allocations still obey the allocation counter contract" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const array = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), array.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR preserves bytes outside guarded caller subviews" {
    var known = [_]u8{0xaa} ** 12;
    const known_view = known[2..10];
    const known_rendered = str_error_r.strErrorR(13, known_view);
    try std.testing.expectEqualStrings("Permiss", known_rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), known[1]);
    try std.testing.expectEqual(@as(u8, 0), known[9]);
    try std.testing.expectEqual(@as(u8, 0xaa), known[10]);

    var fallback = [_]u8{0xbb} ** 11;
    const fallback_view = fallback[3..9];
    const fallback_rendered = str_error_r.strErrorR(4096, fallback_view);
    try std.testing.expectEqualStrings("INTER", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback[2]);
    try std.testing.expectEqual(@as(u8, 0), fallback[8]);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback[9]);
}

test "vsprintf reuses guarded subviews without touching outer sentinels" {
    var backing = [_]u8{0xee} ** 8;
    const window = backing[1..7];

    const zero_written = vsprintf.scnprintfPad(window, 0, "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), zero_written);
    try std.testing.expectEqual(@as(u8, 0), backing[1]);
    try std.testing.expectEqual(@as(u8, 0xee), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xee), backing[7]);

    const direct_written = vsprintf.vscnprintf(window, "{s}:{d}", .{ "id", 7 });
    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqualStrings("id:7", backing[1 .. 1 + direct_written]);
    try std.testing.expectEqual(@as(u8, 0), backing[1 + direct_written]);
    try std.testing.expectEqual(@as(u8, 0xee), backing[0]);
    try std.testing.expectEqual(@as(u8, 0xee), backing[7]);
}

test "zalloc zero-length bytes and fresh owners remain zeroed across reuse" {
    const allocator = std.testing.allocator;
    const Value = struct {
        count: u16,
        flags: [3]u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    value.?.count = 99;
    value.?.flags = .{ 1, 2, 3 };
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.flags);
}
