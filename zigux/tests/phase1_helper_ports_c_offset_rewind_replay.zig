const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 offset rewrites keep neighboring helper windows stable" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    const slab_window = slab.kmallocBytes(32, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_window);

    var zero_owner: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &zero_owner);
    const zero_window = zero_owner.?;

    @memset(slab_window, 0xa5);
    @memset(zero_window, 0x5a);

    const slab_written = vsprintf.scnprintf(slab_window[5..18], "{s}:{d}", .{ "off", 17 });
    try std.testing.expectEqual(@as(usize, 6), slab_written);
    try std.testing.expectEqualStrings("off:17", slab_window[5 .. 5 + slab_written]);
    try std.testing.expectEqual(@as(u8, 0), slab_window[5 + slab_written]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_window[4]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_window[18]);

    const zero_error = str_error_r.strErrorR(22, zero_window[3..15]);
    try std.testing.expectEqualStrings("Invalid arg", zero_error);
    try std.testing.expectEqual(@as(u8, 0), zero_window[3 + zero_error.len]);
    try std.testing.expectEqual(@as(u8, 0x5a), zero_window[2]);
    try std.testing.expectEqual(@as(u8, 0x5a), zero_window[15]);

    const pad_written = vsprintf.scnprintfPad(zero_window[16..28], 8, "{s}", .{"rw"});
    try std.testing.expectEqual(@as(usize, 7), pad_written);
    try std.testing.expectEqualStrings("rw      ", zero_window[16..24]);
    try std.testing.expectEqual(@as(u8, 0), zero_window[24]);
    try std.testing.expectEqual(@as(u8, 0x5a), zero_window[15]);
    try std.testing.expectEqual(@as(u8, 0x5a), zero_window[28]);

    const alias_written = vsprintf.vscnprintf(slab_window[19..31], "{s}:{d}", .{ "rv", 4 });
    try std.testing.expectEqual(@as(usize, 4), alias_written);
    try std.testing.expectEqualStrings("rv:4", slab_window[19 .. 19 + alias_written]);
    try std.testing.expectEqual(@as(u8, 0), slab_window[19 + alias_written]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_window[18]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_window[31]);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "lane10 offset frees reset owners after failed slab attempts" {
    const allocator = std.testing.allocator;

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocBytes(12, slab.__GFP_ZERO) == null);
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 8, slab.GFP_KERNEL | slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    try std.testing.expect(owner != null);
    for (owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const first = vsprintf.scnprintf(owner.?[4..16], "{s}", .{"rewind"});
    try std.testing.expectEqual(@as(usize, 6), first);
    try std.testing.expectEqualStrings("rewind", owner.?[4 .. 4 + first]);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);

    var reacquired: ?[]u8 = try zalloc.zallocBytes(allocator, 24);
    defer zalloc.zfreeBytes(allocator, &reacquired);
    for (reacquired.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const fallback = str_error_r.strErrorR(4096, reacquired.?[6..22]);
    try std.testing.expectEqualStrings("INTERNAL ERROR:", fallback);
    try std.testing.expectEqual(@as(u8, 0), reacquired.?[6 + fallback.len]);
    try std.testing.expectEqual(@as(u8, 0), reacquired.?[5]);
    try std.testing.expectEqual(@as(u8, 0), reacquired.?[22]);
}
