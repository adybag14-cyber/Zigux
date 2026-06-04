const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "helper ports C preserve subview sentinels and reset allocation owners" {
    slab.kmalloc_nr_allocated = 0;

    const slab_window = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_window) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    slab.kfree(slab_window);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    var backing = [_]u8{
        0xa0, 0xa1, 0xa2, 0xa3,
        0xa4, 0xa5, 0xa6, 0xa7,
        0xa8, 0xa9, 0xaa, 0xab,
    };
    const rendered = str_error_r.strErrorR(22, backing[3..12]);
    try std.testing.expectEqualStrings("Invalid ", rendered);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa0, 0xa1, 0xa2 }, backing[0..3]);
    try std.testing.expectEqual(@as(u8, 0), backing[11]);

    var formatted = [_]u8{
        0xb0, 0xb1, 0xb2, 0xb3,
        0xb4, 0xb5, 0xb6, 0xb7,
        0xb8, 0xb9, 0xba, 0xbb,
    };
    const written = vsprintf.scnprintf(formatted[2..9], "{s}:{d}", .{ "c", 10 });
    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xb0, 0xb1 }, formatted[0..2]);
    try std.testing.expectEqualStrings("c:10", formatted[2..6]);
    try std.testing.expectEqual(@as(u8, 0), formatted[6]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xb7, 0xb8, 0xb9, 0xba, 0xbb }, formatted[7..12]);

    const allocator = std.testing.allocator;
    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
}

test "helper ports C keep truncated render contracts aligned" {
    var err_buf: [8]u8 = @splat(0xcc);
    const err = str_error_r.strErrorR(4096, &err_buf);
    try std.testing.expectEqualStrings("INTERNA", err);
    try std.testing.expectEqual(@as(u8, 0), err_buf[7]);

    var pad_buf: [7]u8 = @splat(0xdd);
    const pad_written = vsprintf.scnprintfPad(&pad_buf, 6, "{s}", .{"xy"});
    try std.testing.expectEqual(@as(usize, 6), pad_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', ' ', ' ', ' ', ' ', 0 }, &pad_buf);

    const allocator = std.testing.allocator;
    const Value = struct {
        count: u32,
        enabled: bool,
        marker: u8,
    };
    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u32, 0), value.?.count);
    try std.testing.expectEqual(false, value.?.enabled);
    try std.testing.expectEqual(@as(u8, 0), value.?.marker);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);

    try std.testing.expect(slab.kmallocBytes(3, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.slabIsAvailable());
}
