const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab keeps zeroed sibling allocations stable across dirty peers and failed requests" {
    slab.kmalloc_nr_allocated = 0;

    var plain: ?[]u8 = slab.kmallocBytes(5, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var zeroed: ?[]u8 = slab.kmallocArray(3, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zeroed.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memset(plain.?, 0xaa);
    try std.testing.expect(slab.kmallocBytes(3, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zeroed.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(plain);
    plain = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (zeroed.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    slab.kfree(zeroed);
    zeroed = null;
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR keeps surrounding sentinels intact for zero-width and exact-fit caller windows" {
    var empty_storage = [_]u8{ '#', '#', '#', '#', '#', '#' };
    const empty = str_error_r.strErrorR(2, empty_storage[3..3]);
    try std.testing.expectEqual(@as(usize, 0), empty.len);
    try std.testing.expectEqual(@as(u8, '#'), empty_storage[2]);
    try std.testing.expectEqual(@as(u8, '#'), empty_storage[3]);

    const message = "Permission denied";
    var exact_storage = [_]u8{ '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#' };
    const rendered = str_error_r.strErrorR(13, exact_storage[2 .. 2 + message.len + 1]);
    try std.testing.expectEqualStrings(message, rendered);
    try std.testing.expectEqual(@as(u8, '#'), exact_storage[1]);
    try std.testing.expectEqual(@as(u8, 'P'), exact_storage[2]);
    try std.testing.expectEqual(@as(u8, 0), exact_storage[2 + message.len]);
    try std.testing.expectEqual(@as(u8, '#'), exact_storage[2 + message.len + 1]);
}

test "vsprintf narrows writes to caller windows and preserves outer sentinels" {
    var storage = [_]u8{ '#', '#', '#', '#', '#', '#', '#', '#', '#', '#' };

    const exact_len = vsprintf.vscnprintf(storage[2..7], "{s}", .{"zig!"});
    try std.testing.expectEqual(@as(usize, 4), exact_len);
    try std.testing.expectEqualStrings("zig!", storage[2..6]);
    try std.testing.expectEqual(@as(u8, 0), storage[6]);
    try std.testing.expectEqual(@as(u8, '#'), storage[1]);
    try std.testing.expectEqual(@as(u8, '#'), storage[7]);

    const reset_len = vsprintf.scnprintfPad(storage[2..7], 0, "{s}", .{"later"});
    try std.testing.expectEqual(@as(usize, 0), reset_len);
    try std.testing.expectEqual(@as(u8, 0), storage[2]);
    try std.testing.expectEqual(@as(u8, 'i'), storage[3]);
    try std.testing.expectEqual(@as(u8, '#'), storage[1]);
    try std.testing.expectEqual(@as(u8, '#'), storage[7]);
}

test "zalloc resets optionals without touching sibling fields and re-zeroes nested values" {
    const allocator = std.testing.allocator;

    const BytesHolder = struct {
        keep: u8,
        bytes: ?[]u8,
        tail: u8,
    };

    var bytes_holder = BytesHolder{
        .keep = 0x2a,
        .bytes = try zalloc.zallocBytes(allocator, 4),
        .tail = 0x5b,
    };
    for (bytes_holder.bytes.?) |*byte| {
        byte.* = 0xcc;
    }
    zalloc.zfreeBytes(allocator, &bytes_holder.bytes);
    try std.testing.expect(bytes_holder.bytes == null);
    try std.testing.expectEqual(@as(u8, 0x2a), bytes_holder.keep);
    try std.testing.expectEqual(@as(u8, 0x5b), bytes_holder.tail);

    const NestedValue = extern struct {
        tag: u16,
        payload: extern union {
            words: [2]u32,
            flag: u8,
        },
        tail: u8,
    };
    const ValueHolder = struct {
        keep: u8,
        value: ?*NestedValue,
        tail: u8,
    };

    var value_holder = ValueHolder{
        .keep = 0x31,
        .value = try zalloc.zallocValue(allocator, NestedValue),
        .tail = 0x73,
    };
    try std.testing.expectEqual(@as(u16, 0), value_holder.value.?.tag);
    try std.testing.expectEqual(@as(u32, 0), value_holder.value.?.payload.words[0]);
    try std.testing.expectEqual(@as(u32, 0), value_holder.value.?.payload.words[1]);
    try std.testing.expectEqual(@as(u8, 0), value_holder.value.?.tail);

    value_holder.value.?.tag = 19;
    value_holder.value.?.payload.words = .{ 7, 9 };
    value_holder.value.?.tail = 5;
    zalloc.zfreeValue(allocator, NestedValue, &value_holder.value);
    try std.testing.expect(value_holder.value == null);
    try std.testing.expectEqual(@as(u8, 0x31), value_holder.keep);
    try std.testing.expectEqual(@as(u8, 0x73), value_holder.tail);

    value_holder.value = try zalloc.zallocValue(allocator, NestedValue);
    defer zalloc.zfreeValue(allocator, NestedValue, &value_holder.value);
    try std.testing.expectEqual(@as(u16, 0), value_holder.value.?.tag);
    try std.testing.expectEqual(@as(u32, 0), value_holder.value.?.payload.words[0]);
    try std.testing.expectEqual(@as(u32, 0), value_holder.value.?.payload.words[1]);
    try std.testing.expectEqual(@as(u8, 0), value_holder.value.?.tail);
}
