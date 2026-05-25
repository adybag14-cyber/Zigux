const std = @import("std");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

test "slab pulses between failed, plain, and zeroed allocations without counter drift" {
    slab.kmalloc_nr_allocated = 0;
    try std.testing.expect(slab.kmallocBytes(2, 0) == null);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);

    const plain = slab.kmallocBytes(4, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    @memset(plain, 0x5a);

    const zeroed = slab.kmallocArray(2, 3, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(isize, 2), slab.kmalloc_nr_allocated);
    for (zeroed) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    slab.kfree(zeroed);
    try std.testing.expectEqual(@as(isize, 1), slab.kmalloc_nr_allocated);
    slab.kfree(plain);
    try std.testing.expectEqual(@as(isize, 0), slab.kmalloc_nr_allocated);
}

test "strErrorR pulses exact, one-byte, and empty windows without touching neighbors" {
    var backing = [_]u8{0xaa} ** 20;

    const exact = str_error_r.strErrorR(12, backing[2..9]);
    try std.testing.expectEqualStrings("Cannot", exact);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[1]);
    try std.testing.expectEqual(@as(u8, 0), backing[8]);
    try std.testing.expectEqual(@as(u8, 0xaa), backing[9]);

    @memset(backing[0..], 0xbb);
    const one_byte = str_error_r.strErrorR(0, backing[10..11]);
    try std.testing.expectEqualStrings("", one_byte);
    try std.testing.expectEqual(@as(u8, 0xbb), backing[9]);
    try std.testing.expectEqual(@as(u8, 0), backing[10]);
    try std.testing.expectEqual(@as(u8, 0xbb), backing[11]);

    @memset(backing[0..], 0xcc);
    const empty = str_error_r.strErrorR(13, backing[6..6]);
    try std.testing.expectEqualStrings("", empty);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[5]);
    try std.testing.expectEqual(@as(u8, 0xcc), backing[6]);
}

test "vsprintf pulses truncated and padded windows while preserving sentinels" {
    var trunc_backing = [_]u8{0xdd} ** 12;
    const trunc_written = vsprintf.vscnprintf(trunc_backing[1..6], "{s}", .{"pulse"});
    try std.testing.expectEqual(@as(usize, 4), trunc_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'p', 'u', 'l', 's', 0 }, trunc_backing[1..6]);
    try std.testing.expectEqual(@as(u8, 0xdd), trunc_backing[0]);
    try std.testing.expectEqual(@as(u8, 0xdd), trunc_backing[6]);

    var pad_backing = [_]u8{0xee} ** 10;
    const pad_written = vsprintf.scnprintfPad(pad_backing[2..8], 3, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, 2), pad_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'd', ' ', 0, 0xee, 0xee }, pad_backing[2..8]);
    try std.testing.expectEqual(@as(u8, 0xee), pad_backing[1]);
    try std.testing.expectEqual(@as(u8, 0xee), pad_backing[8]);
}

test "zalloc pulses byte and value ownership back to clean zero state" {
    const allocator = std.testing.allocator;
    const Pulse = struct {
        code: u16,
        armed: bool,
    };

    var bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 5);
    defer zalloc.zfreeBytes(allocator, &bytes);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    bytes.?[4] = 0x7f;
    zalloc.zfreeBytes(allocator, &bytes);
    try std.testing.expect(bytes == null);

    bytes = try zalloc.zallocBytes(allocator, 5);
    for (bytes.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }

    var pulse: ?*Pulse = try zalloc.zallocValue(allocator, Pulse);
    defer zalloc.zfreeValue(allocator, Pulse, &pulse);
    try std.testing.expectEqual(@as(u16, 0), pulse.?.code);
    try std.testing.expectEqual(false, pulse.?.armed);
    pulse.?.* = .{ .code = 9, .armed = true };
    zalloc.zfreeValue(allocator, Pulse, &pulse);
    try std.testing.expect(pulse == null);

    pulse = try zalloc.zallocValue(allocator, Pulse);
    try std.testing.expectEqual(@as(u16, 0), pulse.?.code);
    try std.testing.expectEqual(false, pulse.?.armed);
}
