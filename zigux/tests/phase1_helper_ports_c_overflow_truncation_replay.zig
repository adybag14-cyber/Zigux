const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab rejects overflowed arrays without moving allocation counters" {
    slab.kmalloc_nr_allocated = 0;

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL | slab.__GFP_ZERO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const one = slab.kmallocArray(1, 1, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(one);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), one[0]);
}

test "strErrorR and vsprintf keep terminators on narrow caller buffers" {
    var one_byte_error = [_]u8{0xaa};
    const empty_error = str_error_r.strErrorR(4096, &one_byte_error);
    try std.testing.expectEqual(@as(usize, 0), empty_error.len);
    try std.testing.expectEqual(@as(u8, 0), one_byte_error[0]);

    var tiny_error = [_]u8{ 0xbb, 0xbb, 0xbb, 0xbb };
    const tiny_rendered = str_error_r.strErrorR(22, &tiny_error);
    try std.testing.expectEqualStrings("Inv", tiny_rendered);
    try std.testing.expectEqual(@as(u8, 0), tiny_error[3]);

    var formatted = [_]u8{ 0xcc, 0xcc, 0xcc, 0xcc, 0xcc };
    const written = vsprintf.scnprintf(&formatted, "{s}:{d}", .{ "overflow", 99 });
    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualStrings("over", formatted[0..written]);
    try std.testing.expectEqual(@as(u8, 0), formatted[written]);
}

test "vsprintf padding clamps logical size before zalloc frees reset optionals" {
    var padded = [_]u8{ 0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd };
    const padded_len = vsprintf.scnprintfPad(&padded, 128, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 5), padded_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', ' ', 0 }, &padded);

    const allocator = std.testing.allocator;
    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0 }, bytes.?);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    const Packed = struct {
        count: u16,
        flag: bool,
        tag: u8,
    };
    var value: ?*Packed = try zalloc.zallocValue(allocator, Packed);
    try std.testing.expectEqual(@as(u16, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.flag);
    try std.testing.expectEqual(@as(u8, 0), value.?.tag);
    zalloc.zfreeValue(allocator, Packed, &value);
    try std.testing.expect(value == null);
}
