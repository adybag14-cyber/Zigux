const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps live allocation counters stable across null frees and fail paths" {
    slab.kmalloc_nr_allocated = 0;

    const zeroed = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    for (zeroed) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const array = slab.kmallocArray(2, 3, slab.GFP_KERNEL) orelse {
        slab.kfree(zeroed);
        return error.TestUnexpectedResult;
    };

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    slab.kfree(null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR reuses offset caller buffers without touching outside bytes" {
    var storage: [80]u8 = [_]u8{'!'} ** 80;
    const offset_view = storage[3..9];

    const short_message = str_error_r.strErrorR(13, offset_view);
    try std.testing.expectEqualStrings("Permi", short_message);
    try std.testing.expectEqual(@as(u8, '!'), storage[2]);
    try std.testing.expectEqual(@as(u8, 0), storage[8]);

    const full_message = str_error_r.strErrorR(77, storage[16..]);
    try std.testing.expectEqualStrings(
        "INTERNAL ERROR: strerror_r(77, [buf], 64)=22",
        full_message,
    );
    try std.testing.expectEqual(@as(u8, '!'), storage[15]);
}

test "vsprintf reuses offset slices for truncation and zero logical padding" {
    var storage: [12]u8 = [_]u8{'#'} ** 12;
    const offset_view = storage[2..10];

    const truncated = vsprintf.vscnprintf(offset_view, "{s}", .{"abcdefghi"});
    try std.testing.expectEqual(@as(usize, 7), truncated);
    try std.testing.expectEqualStrings("abcdefg", offset_view[0..truncated]);
    try std.testing.expectEqual(@as(u8, 0), offset_view[truncated]);
    try std.testing.expectEqual(@as(u8, '#'), storage[1]);

    const zero_logical = vsprintf.scnprintfPad(offset_view, 0, "{d}", .{99});
    try std.testing.expectEqual(@as(usize, 0), zero_logical);
    try std.testing.expectEqual(@as(u8, 0), offset_view[0]);
    try std.testing.expectEqual(@as(u8, 'b'), offset_view[1]);
}

test "zalloc re-zeroes bytes and nested extern-union values across reuse" {
    const allocator = std.testing.allocator;
    const Inner = extern union {
        bytes: [2]u8,
        word: u16,
    };
    const Value = extern struct {
        count: u32,
        inner: Inner,
        flag: bool,
    };

    var empty: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty != null);
    try std.testing.expectEqual(@as(usize, 0), empty.?.len);
    zalloc.zfreeBytes(allocator, &empty);
    try std.testing.expect(empty == null);

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    @memset(bytes.?, 0xa5);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.count);
    try std.testing.expectEqual(@as(u16, 0), value.?.inner.word);
    try std.testing.expectEqual(false, value.?.flag);

    value.?.count = 9;
    value.?.inner.bytes = .{ 0xaa, 0xbb };
    value.?.flag = true;
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u32, 0), value.?.count);
    try std.testing.expectEqual(@as(u16, 0), value.?.inner.word);
    try std.testing.expectEqual(false, value.?.flag);
}
