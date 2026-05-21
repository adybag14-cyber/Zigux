const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "phase1 helper ports C rebound caller windows stay bounded across reuse" {
    slab.kmalloc_nr_allocated = 0;

    var anchor: ?[]u8 = slab.kmallocBytes(6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(anchor);
    const neighbor = slab.kmallocArray(2, 3, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(neighbor);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expect(slab.kmallocBytes(6, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    neighbor[0] = 0x6a;
    slab.kfree(anchor);
    anchor = slab.kmallocBytes(6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (anchor.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    try std.testing.expectEqual(@as(u8, 0x6a), neighbor[0]);

    var message_backing = [_]u8{'%'} ** 18;
    const message_view = message_backing[4..12];
    try std.testing.expectEqualStrings("Success", str_error_r.strErrorR(0, message_view));
    try std.testing.expectEqual(@as(u8, 0), message_view[7]);
    try std.testing.expectEqual(@as(u8, '%'), message_backing[3]);
    try std.testing.expectEqual(@as(u8, '%'), message_backing[12]);
    try std.testing.expectEqualStrings("INTERNA", str_error_r.strErrorR(4096, message_view));
    try std.testing.expectEqual(@as(u8, 0), message_view[7]);
    try std.testing.expectEqual(@as(u8, '%'), message_backing[3]);
    try std.testing.expectEqual(@as(u8, '%'), message_backing[12]);
    try std.testing.expectEqualStrings("Success", str_error_r.strErrorR(0, message_view));
    try std.testing.expectEqual(@as(u8, 0), message_view[7]);
    try std.testing.expectEqual(@as(u8, '%'), message_backing[3]);
    try std.testing.expectEqual(@as(u8, '%'), message_backing[12]);

    var render_backing = [_]u8{'!'} ** 18;
    const render_view = render_backing[4..12];
    const long_written = vsprintf.scnprintf(render_view, "{s}", .{"alphabet"});
    try std.testing.expectEqual(@as(usize, 7), long_written);
    try std.testing.expectEqualStrings("alphabe", render_view[0..long_written]);
    try std.testing.expectEqual(@as(u8, 0), render_view[7]);
    const padded_written = vsprintf.scnprintfPad(render_view, 5, "{s}", .{"z"});
    try std.testing.expectEqual(@as(usize, 4), padded_written);
    try std.testing.expectEqualStrings("z    ", render_view[0..5]);
    try std.testing.expectEqual(@as(u8, 0), render_view[5]);
    const rebound_written = vsprintf.scnprintf(render_view, "{s}", .{"ok"});
    try std.testing.expectEqual(@as(usize, 2), rebound_written);
    try std.testing.expectEqualStrings("ok", render_view[0..rebound_written]);
    try std.testing.expectEqual(@as(u8, 0), render_view[2]);
    try std.testing.expectEqual(@as(u8, '!'), render_backing[3]);
    try std.testing.expectEqual(@as(u8, '!'), render_backing[12]);

    const allocator = std.testing.allocator;
    const Value = struct {
        bytes_seen: u16,
        dirty: bool,
    };

    var survivor: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &survivor);
    var rebound_value: ?*Value = try zalloc.zallocValue(allocator, Value);
    defer zalloc.zfreeValue(allocator, Value, &rebound_value);
    survivor.?[0] = 0x44;
    rebound_value.?.bytes_seen = 9;
    rebound_value.?.dirty = true;
    zalloc.zfreeValue(allocator, Value, &rebound_value);
    try std.testing.expect(rebound_value == null);
    rebound_value = try zalloc.zallocValue(allocator, Value);
    try std.testing.expectEqual(@as(u8, 0x44), survivor.?[0]);
    try std.testing.expectEqual(@as(u16, 0), rebound_value.?.bytes_seen);
    try std.testing.expectEqual(false, rebound_value.?.dirty);

    var rebound_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &rebound_bytes);
    rebound_bytes.?[0] = 0xaa;
    zalloc.zfreeBytes(allocator, &rebound_bytes);
    try std.testing.expect(rebound_bytes == null);
    rebound_bytes = try zalloc.zallocBytes(allocator, 4);
    for (rebound_bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    try std.testing.expectEqual(@as(u8, 0x44), survivor.?[0]);
}
