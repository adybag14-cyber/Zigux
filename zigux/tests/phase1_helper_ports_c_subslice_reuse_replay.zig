const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C reuses offset caller slices without widening ownership" {
    slab.kmalloc_nr_allocated = 0;
    const left = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(left);
    var middle: ?[]u8 = slab.kmallocBytes(5, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(middle);
    const right = slab.kmallocBytes(3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(right);
    middle.?[0] = 0x41;
    middle.?[1] = 0x42;
    slab.kfree(middle);
    middle = slab.kmallocBytes(5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 3), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), left[0]);
    try std.testing.expectEqual(@as(u8, 0), right[0]);
    for (middle.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var message_backing = [_]u8{'?'} ** 18;
    const message_view = message_backing[4..12];
    try std.testing.expectEqualStrings("Permiss", str_error_r.strErrorR(13, message_view));
    try std.testing.expectEqual(@as(u8, 0), message_view[7]);
    try std.testing.expectEqual(@as(u8, '?'), message_backing[3]);
    try std.testing.expectEqual(@as(u8, '?'), message_backing[12]);
    try std.testing.expectEqualStrings("Success", str_error_r.strErrorR(0, message_view));
    try std.testing.expectEqual(@as(u8, 0), message_view[7]);
    try std.testing.expectEqual(@as(u8, '?'), message_backing[3]);
    try std.testing.expectEqual(@as(u8, '?'), message_backing[12]);

    var render_backing = [_]u8{'!'} ** 18;
    const render_view = render_backing[4..12];
    const truncated_written = vsprintf.scnprintf(render_view, "{s}", .{"alphabet"});
    try std.testing.expectEqual(@as(usize, 7), truncated_written);
    try std.testing.expectEqualStrings("alphabe", render_view[0..truncated_written]);
    try std.testing.expectEqual(@as(u8, 0), render_view[7]);
    const padded_written = vsprintf.scnprintfPad(render_view, 4, "{s}", .{"x"});
    try std.testing.expectEqual(@as(usize, 3), padded_written);
    try std.testing.expectEqualStrings("x   ", render_view[0..4]);
    try std.testing.expectEqual(@as(u8, 0), render_view[4]);
    try std.testing.expectEqual(@as(u8, '!'), render_backing[3]);
    try std.testing.expectEqual(@as(u8, '!'), render_backing[12]);

    const allocator = std.testing.allocator;
    const Value = struct { n: u16, flag: bool };
    var left_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &left_bytes);
    var middle_value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &middle_value);
    var right_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &right_bytes);
    left_bytes.?[0] = 0x33;
    right_bytes.?[0] = 0x44;
    zalloc.zfreeValue(allocator, Value, &middle_value);
    middle_value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expect(left_bytes != null);
    try std.testing.expect(right_bytes != null);
    try std.testing.expectEqual(@as(u8, 0x33), left_bytes.?[0]);
    try std.testing.expectEqual(@as(u8, 0x44), right_bytes.?[0]);
    try std.testing.expectEqual(@as(u16, 0), middle_value.?.n);
    try std.testing.expectEqual(false, middle_value.?.flag);
}
