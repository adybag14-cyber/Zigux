const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab caller windows keep strerror and vsprintf sentinels isolated" {
    slab.kmalloc_nr_allocated = 0;

    const storage = slab.kmallocBytes(40, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(storage);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), storage[7]);

    storage[1] = 0xa1;
    storage[20] = 0xb2;
    storage[34] = 0xc3;

    const strerror_window = storage[2..20];
    const rendered = str_error_r.strErrorR(22, strerror_window);
    try std.testing.expectEqualStrings("Invalid argument", rendered);
    try std.testing.expectEqual(@as(u8, 0), storage[2 + rendered.len]);

    _ = vsprintf.scnprintfPad(storage[22..34], 9, "io={d}", .{5});
    try std.testing.expectEqualStrings("io=5     ", storage[22..31]);
    try std.testing.expectEqual(@as(u8, 0), storage[31]);

    try std.testing.expectEqual(@as(u8, 0xa1), storage[1]);
    try std.testing.expectEqual(@as(u8, 0xb2), storage[20]);
    try std.testing.expectEqual(@as(u8, 0xc3), storage[34]);
}

test "reused zalloc storage moves from tiny strerror fallback to full formatting" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &bytes);

    try std.testing.expect(bytes != null);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const tiny = bytes.?[3..8];
    const truncated = str_error_r.strErrorR(4096, tiny);
    try std.testing.expectEqualStrings("INTE", truncated);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[7]);

    const written = vsprintf.scnprintf(bytes.?[10..], "{s}:{d}", .{ "reuse", truncated.len });
    try std.testing.expectEqual(@as(usize, 7), written);
    try std.testing.expectEqualStrings("reuse:4", bytes.?[10 .. 10 + written]);
    try std.testing.expectEqual(@as(u8, 0), bytes.?[10 + written]);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
}

test "array allocations preserve counters across interleaved helper releases" {
    slab.kmalloc_nr_allocated = 0;

    const first = slab.kmallocArray(3, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    const second = slab.kmallocArray(2, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (first) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    _ = str_error_r.strErrorR(13, first[1..19]);
    _ = vsprintf.vscnprintf(second[2..], "perm={d}", .{13});

    try std.testing.expectEqualStrings("Permission denied", first[1..19][0..17]);
    try std.testing.expectEqualStrings("perm=13", second[2..9]);
    try std.testing.expectEqual(@as(u8, 0), second[9]);

    slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(first);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "zalloc value reset survives dirty free after formatted slab handoff" {
    const allocator = std.testing.allocator;
    const Value = struct {
        len: usize,
        tag: u8,
    };

    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kmallocBytes(16, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    _ = vsprintf.scnprintf(slab_bytes, "{s}", .{"handoff"});

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    try std.testing.expectEqual(@as(usize, 0), value.?.len);
    try std.testing.expectEqual(@as(u8, 0), value.?.tag);

    value.?.len = std.mem.len(@as([*:0]const u8, @ptrCast(slab_bytes.ptr)));
    value.?.tag = slab_bytes[0];
    try std.testing.expectEqual(@as(usize, 7), value.?.len);
    try std.testing.expectEqual(@as(u8, 'h'), value.?.tag);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(usize, 0), value.?.len);
    try std.testing.expectEqual(@as(u8, 0), value.?.tag);
}
