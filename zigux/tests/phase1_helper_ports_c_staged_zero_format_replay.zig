const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "staged slab formatting can move into a zalloc owner" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const stage = slab.kmallocArray(4, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse
        return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (stage) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memset(stage, 0xa5);
    const stage_window = stage[5..24];
    const formatted = vsprintf.scnprintf(stage_window, "lane10:{d}:{s}", .{ 4, "ports" });
    try std.testing.expectEqualStrings("lane10:4:ports", stage_window[0..formatted]);
    try std.testing.expectEqual(@as(u8, 0), stage_window[formatted]);
    try std.testing.expectEqual(@as(u8, 0xa5), stage[4]);
    try std.testing.expectEqual(@as(u8, 0xa5), stage[24]);

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, formatted + 1);
    defer zalloc.zfreeBytes(allocator, &owner);
    for (owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    @memcpy(owner.?[0..formatted], stage_window[0..formatted]);
    owner.?[formatted] = 0;

    slab.kfree(stage);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualStrings("lane10:4:ports", owner.?[0..formatted]);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
}

test "error and padded formatting share bounded zalloc subviews" {
    const allocator = std.testing.allocator;
    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &owner);

    @memset(owner.?, 0xcc);
    const error_window = owner.?[3..23];
    const message = str_error_r.strErrorR(22, error_window);
    try std.testing.expectEqualStrings("Invalid argument", message);
    try std.testing.expectEqual(@as(u8, 0xcc), owner.?[2]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[3 + message.len]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner.?[23]);

    const pad_window = owner.?[24..40];
    const written = vsprintf.scnprintfPad(pad_window, 12, "ok:{d}", .{7});
    try std.testing.expectEqual(@as(usize, 12), written);
    try std.testing.expectEqualStrings("ok:7        ", pad_window[0..12]);
    try std.testing.expectEqual(@as(u8, 0), pad_window[12]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner.?[40]);
}

test "slab failure leaves zalloc fallback owner balanced" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocBytes(16, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var fallback_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 14);
    defer zalloc.zfreeBytes(allocator, &fallback_owner);

    const rendered = str_error_r.strErrorR(4096, fallback_owner.?);
    try std.testing.expectEqual(@as(usize, fallback_owner.?.len - 1), rendered.len);
    try std.testing.expectEqualStrings("INTERNAL ERRO", rendered);
    try std.testing.expectEqual(@as(u8, 0), fallback_owner.?[rendered.len]);

    zalloc.zfreeBytes(allocator, &fallback_owner);
    try std.testing.expect(fallback_owner == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
