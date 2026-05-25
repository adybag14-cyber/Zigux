const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 replay keeps slab counters balanced across single-byte, zero-extent, and rejected array paths" {
    slab.kmalloc_nr_allocated = 0;

    const one = slab.kmallocBytes(1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), one.len);
    try std.testing.expectEqual(@as(u8, 0), one[0]);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const empty = slab.kmallocArray(0, 9, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(one);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(empty);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 replay keeps strerror_r confined inside single-slot and short fallback windows" {
    var single = [_]u8{ '!', '!', '!' };
    const known = str_error_r.strErrorR(0, single[1..2]);
    try std.testing.expectEqual(@as(usize, 0), known.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '!', 0, '!' }, &single);

    var fallback = [_]u8{ '^', '^', '^', '^', '^', '^' };
    const unknown = str_error_r.strErrorR(4096, fallback[1..3]);
    try std.testing.expectEqualStrings("I", unknown);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '^', 'I', 0, '^', '^', '^' }, &fallback);
}

test "lane10 replay resets tiny vsprintf caller windows without touching the guard bytes" {
    var backing = [_]u8{ '~', '~', '~', '~', '~', '~' };
    const window = backing[1..5];

    const filled = vsprintf.scnprintfPad(window, 1, "{s}", .{"abcd"});
    try std.testing.expectEqual(@as(usize, 1), filled);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '~', 'a', 0, '~', '~', '~' }, &backing);

    const reset = vsprintf.scnprintfPad(window, 0, "{s}", .{"ignored"});
    try std.testing.expectEqual(@as(usize, 0), reset);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '~', 0, 0, '~', '~', '~' }, &backing);

    const direct = vsprintf.vscnprintf(window[1..], "{d}", .{7});
    try std.testing.expectEqual(@as(usize, 1), direct);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '~', 0, '7', 0, '~', '~' }, &backing);
}

test "lane10 replay re-zeroes zero-sized and nested zalloc owners after null-safe resets" {
    const allocator = std.testing.allocator;
    const Value = struct {
        tag: u8,
        inner: ?*u8,
        seen: [2]bool,
    };

    var empty_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expectEqual(@as(usize, 0), empty_bytes.?.len);
    zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expect(empty_bytes == null);
    zalloc.zfreeBytes(allocator, &empty_bytes);
    try std.testing.expect(empty_bytes == null);

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 2);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);
    bytes.?[0] = 9;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 2);
    defer zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, bytes.?);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u8, 0), value.?.tag);
    try std.testing.expect(value.?.inner == null);
    try std.testing.expectEqual(@as([2]bool, .{ false, false }), value.?.seen);
    value.?.tag = 3;
    value.?.seen = .{ true, true };
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u8, 0), value.?.tag);
    try std.testing.expect(value.?.inner == null);
    try std.testing.expectEqual(@as([2]bool, .{ false, false }), value.?.seen);
}
