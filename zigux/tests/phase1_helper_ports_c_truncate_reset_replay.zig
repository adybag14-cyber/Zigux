const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab caller windows survive formatted truncation and strerror reset" {
    slab.kmalloc_nr_allocated = 0;

    const bytes = slab.kmallocBytes(12, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const window = bytes[2..10];
    const rendered = vsprintf.scnprintf(window, "{s}", .{"abcdefghi"});
    try std.testing.expectEqual(@as(usize, 7), rendered);
    try std.testing.expectEqualStrings("abcdefg", window[0..rendered]);
    try std.testing.expectEqual(@as(u8, 0), window[rendered]);
    try std.testing.expectEqual(@as(u8, 0), bytes[0]);
    try std.testing.expectEqual(@as(u8, 0), bytes[1]);
    try std.testing.expectEqual(@as(u8, 0), bytes[10]);
    try std.testing.expectEqual(@as(u8, 0), bytes[11]);

    const reset = str_error_r.strErrorR(22, window);
    try std.testing.expectEqualStrings("Invalid", reset);
    try std.testing.expectEqual(@as(u8, 0), window[reset.len]);
    try std.testing.expectEqual(@as(u8, 0), bytes[0]);
    try std.testing.expectEqual(@as(u8, 0), bytes[1]);
    try std.testing.expectEqual(@as(u8, 0), bytes[10]);
    try std.testing.expectEqual(@as(u8, 0), bytes[11]);
}

test "zalloc windows reset after fallback truncation while slab failures keep counters" {
    const allocator = std.testing.allocator;
    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 10);
    defer zalloc.zfreeBytes(allocator, &owner);

    const bytes = owner.?;
    bytes[0] = 0xa1;
    bytes[1] = 0xa2;
    bytes[8] = 0xa8;
    bytes[9] = 0xa9;

    const window = bytes[2..8];
    const rendered = vsprintf.scnprintf(window, "reset={d}", .{12345});
    try std.testing.expectEqual(@as(usize, 5), rendered);
    try std.testing.expectEqualStrings("reset", window[0..rendered]);
    try std.testing.expectEqual(@as(u8, 0), window[rendered]);

    const fallback = str_error_r.strErrorR(4096, window);
    try std.testing.expectEqualStrings("INTER", fallback);
    try std.testing.expectEqual(@as(u8, 0), window[fallback.len]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa1, 0xa2 }, bytes[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa8, 0xa9 }, bytes[8..10]);

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
}
