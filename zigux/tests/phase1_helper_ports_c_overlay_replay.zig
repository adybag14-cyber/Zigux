const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab caller windows can be overlaid through formatting and strerror" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(48, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(bytes, 0x5a);

    const padded = bytes[4..22];
    const padded_written = vsprintf.scnprintfPad(padded, 12, "slot={d}", .{7});
    try std.testing.expect(padded_written == 12 or padded_written == 11);
    try std.testing.expectEqualStrings("slot=7      ", padded[0..12]);
    try std.testing.expectEqual(@as(u8, 0), padded[12]);
    try std.testing.expectEqual(@as(u8, 0x5a), padded[13]);
    try std.testing.expectEqual(@as(u8, 0x5a), bytes[3]);
    try std.testing.expectEqual(@as(u8, 0x5a), bytes[22]);

    const err_window = bytes[24..41];
    const err_rendered = str_error_r.strErrorR(22, err_window);
    try std.testing.expectEqualStrings("Invalid argument", err_rendered);
    try std.testing.expectEqual(@as(u8, 0), err_window[16]);
    try std.testing.expectEqual(@as(u8, 0x5a), bytes[23]);
    try std.testing.expectEqual(@as(u8, 0x5a), bytes[41]);

    const rewrite = vsprintf.scnprintf(err_window, "{s}:{d}", .{ "ok", padded_written });
    try std.testing.expectEqual(@as(usize, 5), rewrite);
    if (padded_written == 12) {
        try std.testing.expectEqualStrings("ok:12", err_window[0..rewrite]);
    } else {
        try std.testing.expectEqualStrings("ok:11", err_window[0..rewrite]);
    }
    try std.testing.expectEqual(@as(u8, 0), err_window[rewrite]);
    try std.testing.expectEqual(@as(u8, 'd'), err_window[rewrite + 1]);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zalloc owners preserve zeroing around copied slab summaries" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const slab_written = vsprintf.scnprintf(slab_bytes[1..15], "{s}:{d}", .{ "owner", slab_bytes.len });
    try std.testing.expectEqual(@as(usize, 8), slab_written);
    try std.testing.expectEqualStrings("owner:32", slab_bytes[1 .. 1 + slab_written]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[1 + slab_written]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[0]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[15]);

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &owner);
    for (owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    @memcpy(owner.?[3 .. 3 + slab_written], slab_bytes[1 .. 1 + slab_written]);
    try std.testing.expectEqualStrings("owner:32", owner.?[3 .. 3 + slab_written]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[2]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[3 + slab_written]);

    const fallback = str_error_r.strErrorR(4096, owner.?[18..34]);
    try std.testing.expectEqualStrings("INTERNAL ERROR:", fallback);
    try std.testing.expectEqual(@as(u8, 0), owner.?[33]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[34]);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    owner = try zalloc.zallocBytes(allocator, 40);
    for (owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
