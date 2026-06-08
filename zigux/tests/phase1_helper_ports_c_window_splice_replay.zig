const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const Packet = struct {
    code: u16,
    span: usize,
    tag: [4]u8,
    ready: bool,
};

test "window splice keeps slab sentinels around zalloc summaries" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kmallocBytes(80, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(slab_bytes, 0x51);
    const fallback_window = slab_bytes[5..54];
    const fallback = str_error_r.strErrorR(7001, fallback_window);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(7001, [buf], 49)=22", fallback);
    try std.testing.expectEqual(@as(u8, 0x51), slab_bytes[4]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[51]);
    try std.testing.expectEqual(@as(u8, 0x51), slab_bytes[52]);
    try std.testing.expectEqual(@as(u8, 0x51), slab_bytes[54]);

    var summary: ?[]u8 = try zalloc.zallocBytes(allocator, 48);
    defer zalloc.zfreeBytes(allocator, &summary);
    for (summary.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const summary_len = vsprintf.scnprintf(summary.?, "splice:{d}:{s}", .{ fallback.len, fallback[0..8] });
    try std.testing.expectEqual(@as(usize, 18), summary_len);
    try std.testing.expectEqualStrings("splice:46:INTERNAL", summary.?[0..summary_len]);
    try std.testing.expectEqual(@as(u8, 0), summary.?[summary_len]);

    const padded_len = vsprintf.scnprintfPad(slab_bytes[58..74], 12, "sum={d}", .{summary_len});
    try std.testing.expect(padded_len == 12 or padded_len == 11);
    try std.testing.expectEqual(@as(u8, 0x51), slab_bytes[57]);
    try std.testing.expectEqualSlices(u8, "sum=18      ", slab_bytes[58..70]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[70]);
    try std.testing.expectEqual(@as(u8, 0x51), slab_bytes[71]);
    try std.testing.expectEqual(@as(u8, 0x51), slab_bytes[74]);

    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);
    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "window splice carries known errors through typed zalloc state" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_array = slab.kmallocArray(7, 5, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_array);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_array) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(slab_array, 0x62);
    const known_window = slab_array[3..21];
    const known = str_error_r.strErrorR(22, known_window);
    try std.testing.expectEqualStrings("Invalid argument", known);
    try std.testing.expectEqual(@as(u8, 0x62), slab_array[2]);
    try std.testing.expectEqual(@as(u8, 0), slab_array[19]);
    try std.testing.expectEqual(@as(u8, 0x62), slab_array[20]);

    var packet: ?*Packet = try zalloc.zallocValue(allocator, Packet);
    defer zalloc.zfreeValue(allocator, Packet, &packet);
    try std.testing.expectEqual(@as(u16, 0), packet.?.code);
    try std.testing.expectEqual(@as(usize, 0), packet.?.span);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &packet.?.tag);
    try std.testing.expectEqual(false, packet.?.ready);

    var record: ?[]u8 = try zalloc.zallocBytes(allocator, 32);
    defer zalloc.zfreeBytes(allocator, &record);
    const record_len = vsprintf.vscnprintf(record.?, "known:{s}:{d}", .{ known[0..7], known.len });
    try std.testing.expectEqual(@as(usize, 16), record_len);
    try std.testing.expectEqualStrings("known:Invalid:16", record.?[0..record_len]);

    packet.?.code = @intCast(known.len);
    packet.?.span = record_len;
    @memcpy(&packet.?.tag, record.?[0..4]);
    packet.?.ready = true;
    try std.testing.expectEqual(@as(u16, 16), packet.?.code);
    try std.testing.expectEqual(@as(usize, 16), packet.?.span);
    try std.testing.expectEqualSlices(u8, "know", &packet.?.tag);
    try std.testing.expect(packet.?.ready);

    const tail_len = vsprintf.scnprintf(slab_array[22..34], "p:{d}:{d}", .{ packet.?.code, packet.?.span });
    try std.testing.expectEqual(@as(usize, 7), tail_len);
    try std.testing.expectEqualStrings("p:16:16", slab_array[22 .. 22 + tail_len]);
    try std.testing.expectEqual(@as(u8, 0), slab_array[22 + tail_len]);
    try std.testing.expectEqual(@as(u8, 0x62), slab_array[34]);

    zalloc.zfreeValue(allocator, Packet, &packet);
    try std.testing.expect(packet == null);
    zalloc.zfreeValue(allocator, Packet, &packet);
    try std.testing.expect(packet == null);
    zalloc.zfreeBytes(allocator, &record);
    try std.testing.expect(record == null);

    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}
