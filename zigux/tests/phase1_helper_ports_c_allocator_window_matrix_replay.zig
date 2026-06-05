const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab formatted window can hand off through zalloc-owned strerror view" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kcallocBytes(32, 1, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(slab_bytes, 0x7e);
    const slab_window = slab_bytes[4..18];
    const padded = vsprintf.scnprintfPad(slab_window, 9, "id={d}", .{42});

    try std.testing.expectEqual(@as(usize, 9), padded);
    try std.testing.expectEqual(@as(u8, 0x7e), slab_bytes[3]);
    try std.testing.expectEqualStrings("id=42    ", slab_window[0..padded]);
    try std.testing.expectEqual(@as(u8, 0), slab_window[padded]);
    try std.testing.expectEqual(@as(u8, 0x7e), slab_bytes[18]);

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 12);
    defer zalloc.zfreeBytes(allocator, &owner);
    @memcpy(owner.?[0..padded], slab_window[0..padded]);

    const rendered = str_error_r.strErrorR(4096, owner.?[2..11]);
    try std.testing.expectEqualStrings("INTERNAL", rendered);
    try std.testing.expectEqualStrings("id", owner.?[0..2]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[10]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[11]);
}

test "reused caller windows preserve sentinels across errors, formats, and frees" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &owner);
    @memset(owner.?, 0x55);

    const err = str_error_r.strErrorR(12, owner.?[1..10]);
    const formatted = vsprintf.vscnprintf(owner.?[10..17], "{s}", .{"zigux"});

    try std.testing.expectEqualStrings("Cannot a", err);
    try std.testing.expectEqual(@as(usize, 5), formatted);
    try std.testing.expectEqual(@as(u8, 0x55), owner.?[0]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[9]);
    try std.testing.expectEqualStrings("zigux", owner.?[10 .. 10 + formatted]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[10 + formatted]);
    try std.testing.expectEqual(@as(u8, 0x55), owner.?[17]);

    try std.testing.expect(slab.kmallocBytes(8, slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
}

test "zalloc value reset and slab zero-sized owners keep allocation accounting bounded" {
    const allocator = std.testing.allocator;
    const Value = struct {
        tag: u32,
        active: bool,
        payload: [3]u8,
    };

    slab.kmalloc_nr_allocated = 0;

    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.tag);
    try std.testing.expectEqual(false, value.?.active);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, &value.?.payload);

    value.?.* = .{ .tag = 7, .active = true, .payload = .{ 1, 2, 3 } };
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL | slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const zero = slab.kzallocBytes(0, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), zero.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(zero);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
}
