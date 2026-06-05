const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "caller windows survive slab and zalloc reset cycles" {
    slab.kmalloc_nr_allocated = 0;
    const allocator = std.testing.allocator;

    const slab_bytes = slab.kmallocArray(3, 6, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    for (slab_bytes) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const formatted = vsprintf.scnprintf(slab_bytes[2..12], "lane10:{d}", .{42});
    try std.testing.expectEqual(@as(usize, 9), formatted);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, slab_bytes[0..2]);
    try std.testing.expectEqualStrings("lane10:42", slab_bytes[2 .. 2 + formatted]);
    try std.testing.expectEqual(@as(u8, 0), slab_bytes[11]);
    for (slab_bytes[12..]) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 18);
    defer zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner != null);
    for (owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    @memcpy(owner.?[4 .. 4 + formatted], slab_bytes[2 .. 2 + formatted]);
    try std.testing.expectEqualStrings("lane10:42", owner.?[4 .. 4 + formatted]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[3]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[13]);

    const fallback = str_error_r.strErrorR(4096, owner.?[1..13]);
    try std.testing.expectEqualStrings("INTERNAL ER", fallback);
    try std.testing.expectEqual(@as(u8, 0), owner.?[12]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[0]);
    for (owner.?[13..]) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);

    owner = try zalloc.zallocBytes(allocator, 18);
    for (owner.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    const padded = vsprintf.scnprintfPad(owner.?[2..14], 7, "{s}", .{"ok"});
    try std.testing.expect(padded == 6 or padded == 7);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0 }, owner.?[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', ' ', ' ', ' ', ' ', ' ', 0 }, owner.?[2..10]);
    for (owner.?[10..]) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);

    slab.kfree(slab_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "zeroed value owners can be reacquired after helper writes" {
    const allocator = std.testing.allocator;
    const Packet = struct {
        len: usize,
        tag: [12]u8,
        errno_len: usize,
    };

    var packet: ?*Packet = try zalloc.zallocValue(allocator, Packet);
    defer zalloc.zfreeValue(allocator, Packet, &packet);
    try std.testing.expectEqual(@as(usize, 0), packet.?.len);
    try std.testing.expectEqual(@as(usize, 0), packet.?.errno_len);
    try std.testing.expectEqualSlices(u8, &([_]u8{0} ** 12), &packet.?.tag);

    packet.?.len = vsprintf.vscnprintf(&packet.?.tag, "{s}", .{"phase1"});
    try std.testing.expectEqual(@as(usize, 6), packet.?.len);
    try std.testing.expectEqualStrings("phase1", packet.?.tag[0..packet.?.len]);
    try std.testing.expectEqual(@as(u8, 0), packet.?.tag[packet.?.len]);

    packet.?.errno_len = str_error_r.strErrorR(13, packet.?.tag[1..9]).len;
    try std.testing.expectEqual(@as(usize, 7), packet.?.errno_len);
    try std.testing.expectEqualStrings("Permiss", packet.?.tag[1..8]);
    try std.testing.expectEqual(@as(u8, 0), packet.?.tag[8]);

    zalloc.zfreeValue(allocator, Packet, &packet);
    try std.testing.expect(packet == null);

    packet = try zalloc.zallocValue(allocator, Packet);
    try std.testing.expectEqual(@as(usize, 0), packet.?.len);
    try std.testing.expectEqual(@as(usize, 0), packet.?.errno_len);
    try std.testing.expectEqualSlices(u8, &([_]u8{0} ** 12), &packet.?.tag);
}

test "failed slab allocation does not disturb owned caller buffers" {
    slab.kmalloc_nr_allocated = 0;
    const allocator = std.testing.allocator;

    var owner: ?[]u8 = try zalloc.zallocBytes(allocator, 16);
    defer zalloc.zfreeBytes(allocator, &owner);
    @memset(owner.?, 0x7a);

    try std.testing.expect(slab.kmallocBytes(16, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const written = str_error_r.strErrorR(22, owner.?[3..16]);
    try std.testing.expectEqualStrings("Invalid argu", written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0x7a, 0x7a, 0x7a }, owner.?[0..3]);
    try std.testing.expectEqual(@as(u8, 0), owner.?[15]);

    zalloc.zfreeBytes(allocator, &owner);
    try std.testing.expect(owner == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
