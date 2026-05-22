const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C preserve sentinels across shifted handoff windows" {
    slab.kmalloc_nr_allocated = 0;

    const left = slab.kmallocBytes(2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(left);
    var center: ?[]u8 = slab.kmallocArray(3, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(center);
    const right = slab.kmallocBytes(2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(right);
    try std.testing.expectEqual(@as(isize, 3), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocArray(3, 2, 0) == null);
    try std.testing.expectEqual(@as(isize, 3), slab.kmalloc_nr_allocated);

    right[0] = 0x7c;
    center.?[0] = 0xaa;
    center.?[5] = 0xbb;
    slab.kfree(center);
    center = slab.kmallocArray(3, 2, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 3), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(u8, 0), left[0]);
    try std.testing.expectEqual(@as(u8, 0), left[1]);
    try std.testing.expectEqual(@as(u8, 0x7c), right[0]);
    for (center.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var message_backing = [_]u8{'#'} ** 20;
    const first_view = message_backing[2..10];
    const second_view = message_backing[10..18];
    try std.testing.expectEqualStrings("Success", str_error_r.strErrorR(0, first_view));
    try std.testing.expectEqual(@as(u8, 0), first_view[7]);
    try std.testing.expectEqualStrings("Permiss", str_error_r.strErrorR(13, second_view));
    try std.testing.expectEqual(@as(u8, 0), second_view[7]);
    try std.testing.expectEqual(@as(u8, '#'), message_backing[1]);
    try std.testing.expectEqual(@as(u8, '#'), message_backing[18]);
    try std.testing.expectEqualStrings("INTERNA", str_error_r.strErrorR(4096, first_view));
    try std.testing.expectEqual(@as(u8, 0), first_view[7]);
    try std.testing.expectEqual(@as(u8, '#'), message_backing[1]);
    try std.testing.expectEqual(@as(u8, '#'), message_backing[18]);

    var render_backing = [_]u8{'!'} ** 22;
    const padded_view = render_backing[3..11];
    const rebound_view = render_backing[11..19];
    const padded_written = vsprintf.scnprintfPad(padded_view, 6, "{s}", .{"go"});
    try std.testing.expectEqual(@as(usize, 5), padded_written);
    try std.testing.expectEqualStrings("go    ", padded_view[0..6]);
    try std.testing.expectEqual(@as(u8, 0), padded_view[6]);
    const rebound_written = vsprintf.scnprintf(rebound_view, "{s}:{d}", .{ "zig", 42 });
    try std.testing.expectEqual(@as(usize, 6), rebound_written);
    try std.testing.expectEqualStrings("zig:42", rebound_view[0..rebound_written]);
    try std.testing.expectEqual(@as(u8, 0), rebound_view[6]);
    try std.testing.expectEqual(@as(u8, '!'), render_backing[2]);
    try std.testing.expectEqual(@as(u8, '!'), render_backing[19]);

    const allocator = std.testing.allocator;
    const Value = struct {
        bytes_seen: u16,
        dirty: bool,
    };

    var sentinel_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 3);
    defer zalloc.zfreeBytes(allocator, &sentinel_bytes);
    var bytes_view: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &bytes_view);
    var value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &value);

    sentinel_bytes.?[0] = 0x5a;
    bytes_view.?[0] = 0x44;
    value.?.bytes_seen = 9;
    value.?.dirty = true;
    zalloc.zfreeBytes(allocator, &bytes_view);
    try std.testing.expect(bytes_view == null);
    bytes_view = try zalloc.zallocBytes(allocator, 5);
    for (bytes_view.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    try std.testing.expectEqual(@as(u8, 0x5a), sentinel_bytes.?[0]);
    zalloc.zfreeValue(allocator, Value, &value);
    try std.testing.expect(value == null);
    value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u16, 0), value.?.bytes_seen);
    try std.testing.expectEqual(false, value.?.dirty);
    try std.testing.expectEqual(@as(u8, 0x5a), sentinel_bytes.?[0]);
}
