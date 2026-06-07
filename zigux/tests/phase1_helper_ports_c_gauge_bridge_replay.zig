const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

fn expectAllEqual(bytes: []const u8, value: u8) !void {
    for (bytes) |item| {
        try std.testing.expectEqual(value, item);
    }
}

test "gauge bridge preserves slab windows through zalloc and formatter handoffs" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var slab_bytes = slab.kmallocBytes(72, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    try expectAllEqual(slab_bytes, 0);
    @memset(slab_bytes, 0xa5);

    const known_window = slab_bytes[6..28];
    const known = str_error_r.strErrorR(22, known_window);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try expectAllEqual(slab_bytes[0..6], 0xa5);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[6 + known.len]);
    try expectAllEqual(slab_bytes[29..], 0xa5);

    var zbytes: ?[]u8 = try zalloc.zallocBytes(allocator, 80);
    defer zalloc.zfreeBytes(allocator, &zbytes);
    try expectAllEqual(zbytes.?, 0);
    @memcpy(zbytes.?[4 .. 4 + known.len], known);
    try std.testing.expectEqualStrings("Invalid argument", zbytes.?[4 .. 4 + known.len]);

    const direct_len = vsprintf.scnprintf(zbytes.?[24..56], "gauge:{s}:{d}", .{ known[0..7], known.len });
    try std.testing.expectEqualStrings("gauge:Invalid:16", zbytes.?[24 .. 24 + direct_len]);
    try std.testing.expectEqual(@as(u8, 0), zbytes.?[24 + direct_len]);

    const slab_array = slab.kmallocArray(2, 18, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try expectAllEqual(slab_array, 0);
    @memset(slab_array, 0xc3);

    const pad_window = slab_array[5..18];
    const padded_len = vsprintf.scnprintfPad(pad_window, 10, "B:{d}:{s}", .{ known.len, "ok" });
    try std.testing.expect(padded_len == 9 or padded_len == 10);
    try std.testing.expectEqualStrings("B:16:ok   ", pad_window[0..10]);
    try std.testing.expectEqual(@as(u8, 0), pad_window[10]);
    try expectAllEqual(slab_array[0..5], 0xc3);
    try expectAllEqual(slab_array[18..], 0xc3);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &zbytes);
    try std.testing.expect(zbytes == null);
    slab.kfree(slab_array);
    slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "gauge bridge resets zalloc owners around fallback strerror windows" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    try expectAllEqual(owner.?, 0);

    const fallback = str_error_r.strErrorR(9009, owner.?[3..31]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r", fallback[0..26]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[3 + fallback.len]);
    try expectAllEqual(owner.?[0..3], 0);
    try expectAllEqual(owner.?[32..], 0);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);

    owner = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &owner);
    try expectAllEqual(owner.?, 0);

    const Gauge = struct {
        seen: u32,
        active: bool,
        label: [6]u8,
    };

    var value: ?*Gauge = try zalloc.zallocValue(allocator, Gauge);
    defer zalloc.zfreeValue(allocator, Gauge, &value);
    try std.testing.expectEqual(@as(u32, 0), value.?.seen);
    try std.testing.expectEqual(false, value.?.active);
    try expectAllEqual(value.?.label[0..], 0);

    value.?.seen = 28;
    value.?.active = true;
    @memcpy(value.?.label[0..5], "gauge");

    const summary_len = vsprintf.vscnprintf(owner.?[8..34], "reset:{s}:{d}:{any}", .{
        value.?.label[0..5],
        value.?.seen,
        value.?.active,
    });
    try std.testing.expectEqualStrings("reset:gauge:28:true", owner.?[8 .. 8 + summary_len]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[8 + summary_len]);

    zalloc.zfreeValue(allocator, Gauge, &value);
    try std.testing.expect(value == null);
}
