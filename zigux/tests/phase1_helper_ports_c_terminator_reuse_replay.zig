const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 replay keeps tiny helper windows reusable" {
    slab.kmalloc_nr_allocated = 0;

    const zero = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zero);
    try std.testing.expectEqual(@as(usize, 0), zero.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var tiny_known: [1]u8 = [_]u8{0xaa};
    const known = str_error_r.strErrorR(13, &tiny_known);
    try std.testing.expectEqual(@as(usize, 0), known.len);
    try std.testing.expectEqual(@as(u8, 0), tiny_known[0]);

    var tiny_unknown: [1]u8 = [_]u8{0xbb};
    const unknown = str_error_r.strErrorR(4096, &tiny_unknown);
    try std.testing.expectEqual(@as(usize, 0), unknown.len);
    try std.testing.expectEqual(@as(u8, 0), tiny_unknown[0]);

    var padded: [6]u8 = [_]u8{ '!', '!', '!', '!', '!', '!' };
    const padded_written = vsprintf.scnprintfPad(&padded, 99, "{s}", .{"x"});
    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqualStrings("x    ", padded[0..5]);
    try std.testing.expectEqual(@as(u8, 0), padded[5]);

    const reset_written = vsprintf.scnprintfPad(&padded, 0, "{s}", .{"reset"});
    try std.testing.expectEqual(@as(usize, 0), reset_written);
    try std.testing.expectEqual(@as(u8, 0), padded[0]);

    const allocator = std.testing.allocator;
    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    try std.testing.expect(bytes != null);
    try std.testing.expectEqual(@as(usize, 0), bytes.?.len);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const Pair = struct {
        count: u16,
        ready: bool,
    };
    var value: ?*Pair = try zalloc.zallocValue(allocator, Pair);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.ready);
    zalloc.zfreeValue(allocator, Pair, &value);
    try std.testing.expect(value == null);
}
