const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "helper ports C keep allocation failure and zeroing boundaries visible" {
    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.slabIsAvailable());

    try std.testing.expect(slab.kmallocBytes(16, slab.__GFP_IO) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const plain = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(plain);
    @memset(plain, 0xa5);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    const zeroed = slab.kmallocArray(3, 4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(@as(usize, 12), zeroed.len);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    try std.testing.expect(slab.kmallocArray(std.math.maxInt(usize), 2, slab.GFP_KERNEL) == null);
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
}

test "helper ports C keep strerror and formatting truncation NUL terminated" {
    var err_buffer: [12]u8 = @splat(0xaa);
    const known = str_error_r.strErrorR(22, &err_buffer);
    try std.testing.expectEqualStrings("Invalid arg", known);
    try std.testing.expectEqual(@as(u8, 0), err_buffer[known.len]);

    var fallback_buffer: [16]u8 = @splat(0xbb);
    const fallback = str_error_r.strErrorR(9001, &fallback_buffer);
    try std.testing.expectEqualStrings("INTERNAL ERROR:", fallback);
    try std.testing.expectEqual(@as(u8, 0), fallback_buffer[fallback.len]);

    var formatted: [7]u8 = @splat(0xcc);
    const written = vsprintf.scnprintf(&formatted, "err={d}:{s}", .{ 22, "invalid" });
    try std.testing.expectEqual(@as(usize, 6), written);
    try std.testing.expectEqualStrings("err=22", formatted[0..written]);
    try std.testing.expectEqual(@as(u8, 0), formatted[written]);

    var padded: [10]u8 = @splat(0xdd);
    const padded_written = vsprintf.scnprintfPad(&padded, padded.len - 1, "z={d}", .{0});
    try std.testing.expectEqual(@as(usize, 8), padded_written);
    try std.testing.expectEqualStrings("z=0      ", padded[0 .. padded.len - 1]);
    try std.testing.expectEqual(@as(u8, 0), padded[padded.len - 1]);
}

test "helper ports C zalloc free helpers reset optionals and tolerate repeats" {
    const allocator = std.testing.allocator;
    const Packet = struct {
        id: u32,
        active: bool,
        payload: [5]u8,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 9);
    try std.testing.expect(bytes != null);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    var packet: ?*Packet = try zalloc.zallocValue(allocator, Packet);
    try std.testing.expect(packet != null);
    try std.testing.expectEqual(@as(u32, 0), packet.?.id);
    try std.testing.expectEqual(false, packet.?.active);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0, 0 }, &packet.?.payload);
    zalloc.zfreeValue(allocator, Packet, &packet);
    try std.testing.expect(packet == null);
    zalloc.zfreeValue(allocator, Packet, &packet);
    try std.testing.expect(packet == null);
}
