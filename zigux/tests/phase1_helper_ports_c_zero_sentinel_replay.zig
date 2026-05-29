const std = @import("std");

const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "lane10 zero-sized slab allocations remain counted and freeable around formatting" {
    slab.kmalloc_nr_allocated = 0;

    const zero_bytes = slab.kmallocBytes(0, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(usize, 0), zero_bytes.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var formatted = [_]u8{0xa5} ** 5;
    const written = vsprintf.scnprintfPad(&formatted, 0, "allocs={d}", .{slab.kmalloc_nr_allocated});
    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0xa5, 0xa5, 0xa5, 0xa5 }, &formatted);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(zero_bytes);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "lane10 zero-length zalloc buffers are safe strerror destinations" {
    const allocator = std.testing.allocator;

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 0);
    defer zalloc.zfreeBytes(allocator, &bytes);

    const known = str_error_r.strErrorR(22, bytes.?);
    try std.testing.expectEqual(@as(usize, 0), known.len);

    const fallback = str_error_r.strErrorR(4096, bytes.?);
    try std.testing.expectEqual(@as(usize, 0), fallback.len);

    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);
}

test "lane10 zeroed value survives formatted and strerror truncation handoff" {
    const allocator = std.testing.allocator;
    const Packet = struct {
        code: u32,
        ready: bool,
        label: [6]u8,
    };

    var packet: ?*Packet = try zalloc.zallocValue(allocator, Packet);
    defer zalloc.zfreeValue(allocator, Packet, &packet);
    try std.testing.expectEqual(@as(u32, 0), packet.?.code);
    try std.testing.expectEqual(false, packet.?.ready);
    try std.testing.expectEqualSlices(u8, &[_]u8{0} ** 6, &packet.?.label);

    var format_buffer = [_]u8{0xcc} ** 7;
    const formatted = vsprintf.scnprintf(&format_buffer, "p={d}", .{packet.?.code});
    try std.testing.expectEqual(@as(usize, 3), formatted);
    try std.testing.expectEqualStrings("p=0", format_buffer[0..formatted]);
    try std.testing.expectEqual(@as(u8, 0), format_buffer[formatted]);

    var error_buffer = [_]u8{0xdd} ** 6;
    const rendered = str_error_r.strErrorR(12, &error_buffer);
    try std.testing.expectEqualStrings("Canno", rendered);
    try std.testing.expectEqual(@as(u8, 0), error_buffer[5]);
    try std.testing.expectEqual(@as(u32, 0), packet.?.code);
    try std.testing.expectEqual(false, packet.?.ready);
}

test "lane10 zero-count slab arrays and zalloc bytes release independently" {
    const allocator = std.testing.allocator;
    slab.kmalloc_nr_allocated = 0;

    const slab_zero = slab.kmallocArray(0, 8, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_zero);
    try std.testing.expectEqual(@as(usize, 0), slab_zero.len);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    var owned: ?[]u8 = try zalloc.zallocBytes(allocator, 4);
    defer zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0, 0, 0 }, owned.?);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    zalloc.zfreeBytes(allocator, &owned);
    try std.testing.expect(owned == null);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);

    slab.kfree(slab_zero);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}
