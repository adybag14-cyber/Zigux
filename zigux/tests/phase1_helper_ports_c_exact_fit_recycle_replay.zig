const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "exact fit helper windows preserve sentinels and slab accounting" {
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kmallocBytes(40, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqualSlices(u8, &[_]u8{0} ** 40, slab_bytes);

    const errno_window = slab_bytes[3..20];
    const errno_written = str_error_r.strErrorR(22, errno_window);
    try std.testing.expectEqualStrings("Invalid argument", errno_written);
    try std.testing.expectEqual(@as(u8, 0), errno_window[16]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[2]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[20]);

    const fmt_window = slab_bytes[24..32];
    const fmt_written = vsprintf.scnprintf(fmt_window, "{s}:{d}", .{ "ok", 128 });
    try std.testing.expectEqual(@as(usize, 6), fmt_written);
    try std.testing.expectEqualStrings("ok:128", fmt_window[0..fmt_written]);
    try std.testing.expectEqual(@as(u8, 0), fmt_window[fmt_written]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[23]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[32]);

    slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "zalloc recycle keeps zeroed owners before formatting into slab arrays" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &owner);

    var expected_fallback: [64]u8 = undefined;
    const expected = try std.fmt.bufPrint(
        &expected_fallback,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 4096, owner.?.len },
    );
    const fallback = str_error_r.strErrorR(4096, owner.?);
    try std.testing.expectEqualStrings(expected, fallback);
    try std.testing.expectEqual(@as(u8, 0), owner.?[fallback.len]);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);

    owner = try zalloc.zallocBytes(allocator, 48);
    for (owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const summary_len = vsprintf.vscnprintf(owner.?[4..18], "{s}-{d}", .{ "lane", 10 });
    try std.testing.expectEqual(@as(usize, 7), summary_len);
    try std.testing.expectEqualStrings("lane-10", owner.?[4 .. 4 + summary_len]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[4 + summary_len]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[3]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[18]);

    const slab_copy = slab.kmallocArray(2, summary_len + 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_copy);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    @memcpy(slab_copy[0..summary_len], owner.?[4 .. 4 + summary_len]);
    slab_copy[summary_len] = 0;
    try std.testing.expectEqualStrings("lane-10", slab_copy[0..summary_len]);
    try std.testing.expectEqual(@as(u8, 0), slab_copy[summary_len]);
    for (slab_copy[summary_len + 1 ..]) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}
