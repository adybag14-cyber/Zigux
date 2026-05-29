const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab disjoint caller views preserve neighboring bytes" {
    slab.kmalloc_nr_allocated = 0;
    const owner = slab.kmallocArray(32, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(owner);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (owner) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    @memset(owner, 0xcc);

    const err_view = owner[4..15];
    const err_rendered = str_error_r.strErrorR(22, err_view);
    try std.testing.expectEqualStrings("Invalid ar", err_rendered);
    try std.testing.expectEqual(@as(u8, 0), owner[14]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner[3]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner[15]);

    const direct_view = owner[16..25];
    const direct_written = vsprintf.scnprintf(direct_view, "slab:{d}", .{1024});
    try std.testing.expectEqual(@as(usize, 8), direct_written);
    try std.testing.expectEqualStrings("slab:102", direct_view[0..direct_written]);
    try std.testing.expectEqual(@as(u8, 0), owner[24]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner[15]);
    try std.testing.expectEqual(@as(u8, 0xcc), owner[25]);

    const pad_view = owner[26..32];
    const pad_written = vsprintf.scnprintfPad(pad_view, pad_view.len - 1, "{s}", .{"io"});
    try std.testing.expectEqual(@as(usize, 4), pad_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'o', ' ', ' ', ' ', 0 }, pad_view);
    try std.testing.expectEqual(@as(u8, 0xcc), owner[25]);

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "zalloc disjoint caller views reset after formatting" {
    const allocator = std.testing.allocator;
    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &bytes);

    const owner = bytes.?;
    for (owner) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
    @memset(owner, 0x7e);

    const fallback_view = owner[2..14];
    const fallback = str_error_r.strErrorR(8192, fallback_view);
    try std.testing.expectEqualStrings("INTERNAL ER", fallback);
    try std.testing.expectEqual(@as(u8, 0), owner[13]);
    try std.testing.expectEqual(@as(u8, 0x7e), owner[1]);
    try std.testing.expectEqual(@as(u8, 0x7e), owner[14]);

    const alias_view = owner[16..25];
    const alias_written = vsprintf.vscnprintf(alias_view, "z:{d}:{s}", .{ 17, "tail" });
    try std.testing.expectEqual(@as(usize, 8), alias_written);
    try std.testing.expectEqualStrings("z:17:tai", alias_view[0..alias_written]);
    try std.testing.expectEqual(@as(u8, 0), owner[24]);
    try std.testing.expectEqual(@as(u8, 0x7e), owner[15]);
    try std.testing.expectEqual(@as(u8, 0x7e), owner[25]);

    const zero_written = vsprintf.scnprintf(owner[30..30], "{s}", .{"no-write"});
    try std.testing.expectEqual(@as(usize, 0), zero_written);
    try std.testing.expectEqual(@as(u8, 0x7e), owner[29]);
    try std.testing.expectEqual(@as(u8, 0x7e), owner[30]);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 8);
    for (bytes.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }
}
