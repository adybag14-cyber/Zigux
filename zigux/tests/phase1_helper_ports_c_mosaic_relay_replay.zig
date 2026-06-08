const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const Packet = struct {
    code: u16,
    slots: [4]u8,
    ready: bool,
};

test "mosaic relay keeps slab windows and zalloc summaries isolated" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_bytes = slab.kmallocBytes(72, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(slab_bytes, 0xa5);
    const fallback_window = slab_bytes[7..56];
    const fallback = str_error_r.strErrorR(31337, fallback_window);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(31337, [buf], 49)=22", fallback);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_bytes[6]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[54]);
    try std.testing.expectEqual(@as(u8, 0xa5), slab_bytes[55]);

    var summary: ?[]u8 = try zalloc.zallocBytes(allocator, 40);
    defer zalloc.zfreeBytes(allocator, &summary);
    for (summary.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const summary_len = vsprintf.scnprintf(summary.?, "mosaic:{d}:{s}", .{ fallback.len, fallback[0..8] });
    try std.testing.expectEqual(@as(usize, 18), summary_len);
    try std.testing.expectEqualStrings("mosaic:47:INTERNAL", summary.?[0..summary_len]);
    try std.testing.expectEqual(@as(u8, 0), summary.?[summary_len]);

    @memset(slab_bytes[0..18], 0xc3);
    const padded_len = vsprintf.scnprintfPad(slab_bytes[2..17], 10, "z:{d}", .{summary_len});
    try std.testing.expect(padded_len == 10 or padded_len == 9);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xc3, 0xc3 }, slab_bytes[0..2]);
    try std.testing.expectEqualSlices(u8, "z:18      ", slab_bytes[2..12]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[12]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xc3, 0xc3, 0xc3, 0xc3 }, slab_bytes[13..17]);

    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);
    zalloc.zfreeBytes(allocator, &summary);
    try std.testing.expect(summary == null);

    try std.testing.expect(slab.kmallocBytes(8, 0) == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
}

test "mosaic relay reuses known errors through typed zalloc ownership" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_array = slab.kmallocArray(6, 6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_array) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memset(slab_array, 0xd4);
    const known = str_error_r.strErrorR(12, slab_array[4..28]);
    try std.testing.expectEqualStrings("Cannot allocate memory", known);
    try std.testing.expectEqual(@as(u8, 0xd4), slab_array[3]);
    try std.testing.expectEqual(@as(u8, 0), slab_array[26]);
    try std.testing.expectEqual(@as(u8, 0xd4), slab_array[27]);

    var packet: ?*Packet = try zalloc.zallocValue(allocator, Packet);
    defer zalloc.zfreeValue(allocator, Packet, &packet);
    try std.testing.expectEqual(@as(u16, 0), packet.?.code);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, &packet.?.slots);
    try std.testing.expectEqual(false, packet.?.ready);

    packet.?.code = 12;
    packet.?.slots = .{ known[0], known[1], known[known.len - 2], known[known.len - 1] };
    packet.?.ready = true;

    var record: [32]u8 = @splat(0xee);
    const record_len = vsprintf.scnprintf(&record, "pkt:{d}:{c}{c}{c}{c}", .{
        packet.?.code,
        packet.?.slots[0],
        packet.?.slots[1],
        packet.?.slots[2],
        packet.?.slots[3],
    });
    try std.testing.expectEqual(@as(usize, 11), record_len);
    try std.testing.expectEqualStrings("pkt:12:Cary", record[0..record_len]);
    try std.testing.expectEqual(@as(u8, 0), record[record_len]);
    try std.testing.expectEqual(@as(u8, 0xee), record[record_len + 1]);

    zalloc.zfreeValue(allocator, Packet, &packet);
    try std.testing.expect(packet == null);
    zalloc.zfreeValue(allocator, Packet, &packet);
    try std.testing.expect(packet == null);

    slab.kfree(slab_array);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
