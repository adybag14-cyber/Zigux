const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C preserves caller ownership across adjacent state" {
    slab.kmalloc_nr_allocated = 0;
    var first: ?[]u8 = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(first);
    const second = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(second);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), first.?[0]);
    second[0] = 0x7b;
    slab.kfree(first);
    first = null;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0x7b), second[0]);

    var known_backing = [_]u8{'^'} ** 28;
    const known_view = known_backing[5..23];
    try std.testing.expectEqualStrings("Permission denied", str_error_r.strErrorR(13, known_view));
    try std.testing.expectEqual(@as(u8, '^'), known_backing[4]);
    try std.testing.expectEqual(@as(u8, '^'), known_backing[23]);

    var unknown_backing = [_]u8{'~'} ** 20;
    const unknown_view = unknown_backing[6..14];
    try std.testing.expectEqualStrings("INTERNA", str_error_r.strErrorR(4096, unknown_view));
    try std.testing.expectEqual(@as(u8, '~'), unknown_backing[5]);
    try std.testing.expectEqual(@as(u8, '~'), unknown_backing[14]);

    var render_backing = [_]u8{'!'} ** 16;
    const render_view = render_backing[3..11];
    const first_written = vsprintf.scnprintf(render_view, "{s}", .{"alpha"});
    try std.testing.expectEqual(@as(usize, 5), first_written);
    try std.testing.expectEqualStrings("alpha", render_view[0..first_written]);
    try std.testing.expectEqual(@as(u8, '!'), render_backing[2]);
    try std.testing.expectEqual(@as(u8, '!'), render_backing[11]);

    const padded_written = vsprintf.scnprintfPad(render_view, 6, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 5), padded_written);
    try std.testing.expectEqualStrings("id    ", render_view[0..6]);
    try std.testing.expectEqual(@as(u8, 0), render_view[6]);
    try std.testing.expectEqual(@as(u8, '!'), render_backing[2]);
    try std.testing.expectEqual(@as(u8, '!'), render_backing[11]);

    const allocator = std.testing.allocator;
    var left_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &left_bytes);
    var right_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &right_bytes);
    right_bytes.?[0] = 0x55;
    zalloc.zfreeBytes(allocator, &left_bytes);
    try std.testing.expect(left_bytes == null);
    try std.testing.expect(right_bytes != null);
    try std.testing.expectEqual(@as(u8, 0x55), right_bytes.?[0]);

    const Value = struct {
        x: u16,
        y: bool,
    };
    var left_value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &left_value);
    var right_value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &right_value);
    try std.testing.expectEqual(@as(u16, 0), right_value.?.x);
    try std.testing.expectEqual(false, right_value.?.y);
    right_value.?.x = 9;
    zalloc.zfreeValue(allocator, Value, &left_value);
    try std.testing.expect(left_value == null);
    try std.testing.expect(right_value != null);
    try std.testing.expectEqual(@as(u16, 9), right_value.?.x);
}
