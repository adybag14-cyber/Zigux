const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab overflow failures do not disturb live zeroed allocations" {
    slab.kmalloc_nr_allocated = 0;

    const live = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer {
        slab.kfree(live);
        slab.kmalloc_nr_allocated = 0;
    }

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (live) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps neighbors intact for empty and narrow subslices" {
    var backing = [_]u8{ '#', '#', '#', '#', '#', '#', '#', '#' };

    const empty = str_error_r.strErrorR(2, backing[2..2]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#', '#', '#', '#', '#', '#', '#' }, &backing);

    const known = str_error_r.strErrorR(0, backing[2..4]);
    try std.testing.expectEqualStrings("S", known);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#', 'S', 0, '#', '#', '#', '#' }, &backing);

    const unknown = str_error_r.strErrorR(4096, backing[4..8]);
    try std.testing.expectEqualStrings("INT", unknown);
    try std.testing.expectEqualSlices(u8, &[_]u8{ '#', '#', 'S', 0, 'I', 'N', 'T', 0 }, &backing);
}

test "vsprintf reuses interior slices without touching outer sentinels" {
    var backing = [_]u8{'!'} ** 10;
    const window = backing[2..8];

    const first_written = vsprintf.vscnprintf(window, "{s}", .{"alpha"});
    try std.testing.expectEqual(@as(usize, 5), first_written);
    try std.testing.expectEqualStrings("alpha", window[0..first_written]);
    try std.testing.expectEqual(@as(u8, 0), window[first_written]);
    try std.testing.expectEqual(@as(u8, '!'), backing[1]);
    try std.testing.expectEqual(@as(u8, '!'), backing[8]);

    const second_written = vsprintf.scnprintfPad(window, 4, "{s}", .{"b"});
    try std.testing.expectEqual(@as(usize, 3), second_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'b', ' ', ' ', ' ', 0, 0 }, window);
    try std.testing.expectEqual(@as(u8, '!'), backing[1]);
    try std.testing.expectEqual(@as(u8, '!'), backing[8]);
}

test "zalloc re-zeroes bytes and values after dirty frees" {
    const allocator = std.testing.allocator;
    const Value = extern struct {
        words: [2]u16,
        flag: bool,
        marker: u8,
    };

    var first_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expect(first_bytes != null);
    @memset(first_bytes.?, 0xab);
    zalloc.zfreeBytes(allocator, &first_bytes);
    try std.testing.expect(first_bytes == null);

    var second_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &second_bytes);
    try std.testing.expect(second_bytes != null);
    for (second_bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    var first_value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expect(first_value != null);
    first_value.?.words = .{ 9, 10 };
    first_value.?.flag = true;
    first_value.?.marker = 0xff;
    zalloc.zfreeValue(allocator, Value, &first_value);
    try std.testing.expect(first_value == null);

    var second_value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &second_value);
    try std.testing.expect(second_value != null);
    try std.testing.expectEqualSlices(u16, &[_]u16{ 0, 0 }, &second_value.?.words);
    try std.testing.expectEqual(false, second_value.?.flag);
    try std.testing.expectEqual(@as(u8, 0), second_value.?.marker);
}
