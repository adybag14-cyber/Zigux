const std = @import("std");
const abi = @import("abi_bindings");
const narrow = @import("narrow_unsafe");

pub fn range(base_addr: usize, length: u32, stride: u32) abi.MmioRange {
    return .{
        .base_addr = base_addr,
        .length = length,
        .stride = stride,
    };
}

pub fn read8(base_addr: usize, offset: usize) u8 {
    const ptr = narrow.pointerAt(u8, base_addr, offset);
    return ptr.*;
}

pub fn write8(base_addr: usize, offset: usize, value: u8) void {
    const ptr = narrow.pointerAt(u8, base_addr, offset);
    ptr.* = value;
}

pub fn read16(base_addr: usize, offset: usize) u16 {
    const ptr = narrow.pointerAt(u16, base_addr, offset);
    return ptr.*;
}

pub fn write16(base_addr: usize, offset: usize, value: u16) void {
    const ptr = narrow.pointerAt(u16, base_addr, offset);
    ptr.* = value;
}

pub fn read32(base_addr: usize, offset: usize) u32 {
    const ptr = narrow.pointerAt(u32, base_addr, offset);
    return ptr.*;
}

pub fn write32(base_addr: usize, offset: usize, value: u32) void {
    const ptr = narrow.pointerAt(u32, base_addr, offset);
    ptr.* = value;
}

test "phase3 mmio wrapper uses bounded volatile access" {
    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = narrow.addressOf(&bytes[0]);

    write8(base, 1, 0x5a);
    try std.testing.expectEqual(@as(u8, 0x5a), bytes[1]);
    try std.testing.expectEqual(@as(u8, 0x5a), read8(base, 1));

    const halfwords: *align(1) [4]u16 = @ptrCast(&bytes);
    write16(base, 2, 0xbeef);
    try std.testing.expectEqual(@as(u16, 0xbeef), halfwords[1]);
    try std.testing.expectEqual(@as(u16, 0xbeef), read16(base, 2));

    const regs: *align(1) [2]u32 = @ptrCast(&bytes);
    write32(base, @sizeOf(u32), 0xfeedbeef);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), regs[1]);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), read32(base, @sizeOf(u32)));

    const desc = range(base, 8, 1);
    try std.testing.expectEqual(base, desc.base_addr);
    try std.testing.expectEqual(@as(u32, 8), desc.length);
    try std.testing.expectEqual(@as(u32, 1), desc.stride);
}
