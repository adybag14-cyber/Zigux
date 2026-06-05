const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab zeroed buffer can be formatted then reused for strerror" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(18, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(bytes);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (bytes) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    const formatted = vsprintf.scnprintf(bytes[2..15], "err={d}", .{22});
    try std.testing.expectEqual(@as(usize, 6), formatted);
    try std.testing.expectEqualStrings("err=22", bytes[2 .. 2 + formatted]);
    try std.testing.expectEqual(@as(u8, 0), bytes[2 + formatted]);
    try std.testing.expectEqual(@as(u8, 0), bytes[0]);
    try std.testing.expectEqual(@as(u8, 0), bytes[1]);
    try std.testing.expectEqual(@as(u8, 0), bytes[15]);
    try std.testing.expectEqual(@as(u8, 0), bytes[16]);
    try std.testing.expectEqual(@as(u8, 0), bytes[17]);

    const rendered = str_error_r.strErrorR(12, bytes[2..15]);
    try std.testing.expectEqualStrings("Cannot alloc", rendered);
    try std.testing.expectEqual(@as(u8, 0), bytes[14]);
    try std.testing.expectEqual(@as(u8, 0), bytes[0]);
    try std.testing.expectEqual(@as(u8, 0), bytes[1]);
    try std.testing.expectEqual(@as(u8, 0), bytes[15]);
    try std.testing.expectEqual(@as(u8, 0), bytes[16]);
    try std.testing.expectEqual(@as(u8, 0), bytes[17]);
}

test "zalloc caller window survives fallback rewrite and cleanup" {
    const allocator = std.testing.allocator;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 28);
    defer zalloc.zfreeBytes(allocator, &owner);

    for (owner.?) |value| {
        try std.testing.expectEqual(@as(u8, 0), value);
    }

    owner.?[0] = 0xa1;
    owner.?[1] = 0xa2;
    owner.?[26] = 0xe1;
    owner.?[27] = 0xe2;

    const window = owner.?[2..26];
    const first = vsprintf.scnprintf(window, "{s}:{d}", .{ "phase1", 10 });
    try std.testing.expectEqual(@as(usize, 9), first);
    try std.testing.expectEqualStrings("phase1:10", window[0..first]);
    try std.testing.expectEqual(@as(u8, 0), window[first]);

    const fallback = str_error_r.strErrorR(5000, window);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerro", fallback);
    try std.testing.expectEqual(@as(u8, 0), window[23]);
    try std.testing.expectEqual(@as(u8, 0xa1), owner.?[0]);
    try std.testing.expectEqual(@as(u8, 0xa2), owner.?[1]);
    try std.testing.expectEqual(@as(u8, 0xe1), owner.?[26]);
    try std.testing.expectEqual(@as(u8, 0xe2), owner.?[27]);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
}
