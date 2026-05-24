const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps zero-sized and non-zero allocations balanced across mixed release order" {
    slab.kmalloc_nr_allocated = 0;

    const zero = slab.kmallocArray(0, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    const live = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        slab.kfree(zero);
        return error.TestUnexpectedResult;
    };
    defer slab.kfree(live);
    defer slab.kfree(zero);

    try std.testing.expectEqual(@as(usize, 0), zero.len);
    for (live) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    slab.kfree(zero);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const second_zero = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse {
        return error.TestUnexpectedResult;
    };
    defer slab.kfree(second_zero);
    try std.testing.expectEqual(@as(usize, 0), second_zero.len);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    try std.testing.expect(slab.kmallocArray(8, 2, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
}

test "strErrorR grows an offset caller view from a tiny known message to a generated one" {
    var storage = [_]u8{'!'} ** 80;
    const tiny_view = storage[4..6];
    const tiny = str_error_r.strErrorR(13, tiny_view);
    try std.testing.expectEqualStrings("P", tiny);
    try std.testing.expectEqual(@as(u8, '!'), storage[3]);
    try std.testing.expectEqual(@as(u8, 0), storage[5]);
    try std.testing.expectEqual(@as(u8, '!'), storage[6]);

    const generated_view = storage[12..56];
    var expected_storage: [64]u8 = undefined;
    const expected = try std.fmt.bufPrint(
        &expected_storage,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 77, generated_view.len },
    );
    const generated = str_error_r.strErrorR(77, generated_view);
    try std.testing.expectEqualStrings(expected[0 .. generated_view.len - 1], generated);
    try std.testing.expectEqual(@intFromPtr(&storage[12]), @intFromPtr(generated.ptr));
    try std.testing.expectEqual(@as(u8, '!'), storage[11]);
    try std.testing.expectEqual(@as(u8, 0), storage[12 + generated.len]);
    try std.testing.expectEqual(@as(u8, '!'), storage[12 + generated_view.len]);
}

test "vsprintf keeps offset caller views reusable across truncation and zero-logical reset" {
    var storage = [_]u8{'#'} ** 14;
    const view = storage[3..11];

    const truncated = vsprintf.scnprintf(view, "{s}", .{"abcdefghi"});
    try std.testing.expectEqual(@as(usize, 7), truncated);
    try std.testing.expectEqualStrings("abcdefg", view[0..truncated]);
    try std.testing.expectEqual(@as(u8, 0), view[truncated]);
    try std.testing.expectEqual(@as(u8, '#'), storage[2]);
    try std.testing.expectEqual(@as(u8, '#'), storage[11]);

    const zero_logical = vsprintf.scnprintfPad(view, 0, "{d}", .{99});
    try std.testing.expectEqual(@as(usize, 0), zero_logical);
    try std.testing.expectEqual(@as(u8, 0), view[0]);
    try std.testing.expectEqual(@as(u8, 'b'), view[1]);
    try std.testing.expectEqual(@as(u8, '#'), storage[2]);
    try std.testing.expectEqual(@as(u8, '#'), storage[11]);

    const regrown = vsprintf.vscnprintf(view, "{s}:{d}", .{ "id", 7 });
    try std.testing.expectEqual(@as(usize, 4), regrown);
    try std.testing.expectEqualStrings("id:7", view[0..regrown]);
    try std.testing.expectEqual(@as(u8, 0), view[regrown]);
}

test "zalloc re-zeroes bytes and nested extern-union values after dirty frees" {
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

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    @memset(bytes.?, 0xa5);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

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
