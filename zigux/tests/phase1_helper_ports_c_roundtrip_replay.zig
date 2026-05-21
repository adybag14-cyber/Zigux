const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 roundtrip replay keeps slab allocations isolated across byte and array helpers" {
    slab.kmalloc_nr_allocated = 0;

    const dirty = slab.kmallocBytes(6, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(dirty);
    @memset(dirty, 0xaa);

    const zeroed = slab.kmallocArray(3, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);

    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    for (dirty) |byte| {
        try std.testing.expectEqual(@as(u8, 0xaa), byte);
    }
}

test "lane10 roundtrip replay shrinks strErrorR writes on the same caller-owned view" {
    var backing = [_]u8{0xaa} ** 80;
    const view = backing[7..40];

    const generated = str_error_r.strErrorR(4096, view);
    try std.testing.expect(@intFromPtr(generated.ptr) == @intFromPtr(view.ptr));
    try std.testing.expect(std.mem.startsWith(u8, generated, "INTERNAL ERROR: strerror_r("));

    const known = str_error_r.strErrorR(0, view);
    try std.testing.expectEqualStrings("Success", known);
    try std.testing.expect(@intFromPtr(known.ptr) == @intFromPtr(view.ptr));
    try std.testing.expectEqual(@as(u8, 0), view["Success".len]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[6]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[40]);
}

test "lane10 roundtrip replay reuses offset vsprintf views after padded output" {
    var backing = [_]u8{0xcc} ** 12;
    const view = backing[2..10];

    const padded = vsprintf.scnprintfPad(view, 6, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 5), padded);
    try std.testing.expectEqualStrings("id    ", view[0..6]);
    try std.testing.expectEqual(@as(u8, 0), view[6]);

    const plain = vsprintf.scnprintf(view, "{d}", .{73});
    try std.testing.expectEqual(@as(usize, 2), plain);
    try std.testing.expectEqualStrings("73", view[0..plain]);
    try std.testing.expectEqual(@as(u8, 0), view[plain]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[1]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[10]);
}

test "lane10 roundtrip replay re-zeroes zalloc bytes after freeing a dirty earlier slice" {
    const allocator = std.testing.allocator;
    const Value = struct {
        bytes: [4]u8,
        ready: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    try std.testing.expect(bytes != null);
    @memset(bytes.?, 0xfe);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const zeroed = try zalloc.zallocBytes(allocator, 6);
    defer allocator.free(zeroed);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value != null);
    try std.testing.expectEqual([_]u8{ 0, 0, 0, 0 }, value.?.bytes);
    try std.testing.expectEqual(false, value.?.ready);
}
