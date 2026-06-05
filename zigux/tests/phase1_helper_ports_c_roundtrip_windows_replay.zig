const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab formatted window roundtrips through zalloc strerror owner" {
    slab.kmalloc_nr_allocated = 0;

    var slab_window = slab.kmallocArray(5, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_window);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_window) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const formatted_view = slab_window[4..22];
    const formatted_len = vsprintf.scnprintf(formatted_view, "slot={d}:{s}", .{ 17, "zigux" });
    try std.testing.expectEqual(@as(usize, 13), formatted_len);
    try std.testing.expectEqualStrings("slot=17:zigux", formatted_view[0..formatted_len]);
    try std.testing.expectEqual(@as(u8, 0), formatted_view[formatted_len]);
    try std.testing.expectEqual(@as(u8, 0), slab_window[3]);
    try std.testing.expectEqual(@as(u8, 0), slab_window[22]);

    const allocator = std.testing.allocator;
    var z_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &z_owner);
    try std.testing.expect(z_owner != null);
    for (z_owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memcpy(z_owner.?[0..formatted_len], formatted_view[0..formatted_len]);
    try std.testing.expectEqualStrings("slot=17:zigux", z_owner.?[0..formatted_len]);

    const err = str_error_r.strErrorR(12, z_owner.?);
    try std.testing.expectEqualStrings("Cannot allocate memory", err);
    try std.testing.expectEqual(@as(u8, 0), z_owner.?[err.len]);
    try std.testing.expectEqual(@as(u8, 0), z_owner.?[23]);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zalloc fallback window roundtrips into padded slab caller subview" {
    slab.kmalloc_nr_allocated = 0;

    const allocator = std.testing.allocator;
    var z_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &z_owner);
    @memset(z_owner.?, 0xdd);

    const fallback_view = z_owner.?[3..23];
    const fallback = str_error_r.strErrorR(4097, fallback_view);
    try std.testing.expectEqualStrings("INTERNAL ERROR: str", fallback);
    try std.testing.expectEqual(@as(u8, 0xdd), z_owner.?[2]);
    try std.testing.expectEqual(@as(u8, 0), z_owner.?[22]);
    try std.testing.expectEqual(@as(u8, 0xdd), z_owner.?[23]);

    const padded_written = vsprintf.scnprintfPad(fallback_view, 10, "{s}", .{"ok"});
    try std.testing.expect(padded_written == 9 or padded_written == 10);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0 }, fallback_view[0..11]);
    try std.testing.expectEqual(@as(u8, 0xdd), z_owner.?[2]);
    try std.testing.expectEqual(@as(u8, 0xdd), z_owner.?[23]);

    const slab_owner = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_owner);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memcpy(slab_owner[6..17], fallback_view[0..11]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 0 }, slab_owner[6..17]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[5]);
    try std.testing.expectEqual(@as(u8, 0), slab_owner[17]);

    zalloc.zfreeBytes(allocator, &z_owner);
    try std.testing.expect(z_owner == null);
    zalloc.zfreeBytes(allocator, &z_owner);
    try std.testing.expect(z_owner == null);
}
