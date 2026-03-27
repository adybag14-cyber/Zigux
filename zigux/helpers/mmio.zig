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

pub fn read32(base_addr: usize, offset: usize) u32 {
    const ptr = narrow.pointerAt(u32, base_addr, offset);
    return ptr.*;
}

pub fn write32(base_addr: usize, offset: usize, value: u32) void {
    const ptr = narrow.pointerAt(u32, base_addr, offset);
    ptr.* = value;
}

test "phase3 mmio wrapper uses bounded volatile access" {
    var regs = [_]u32{ 0, 0 };
    const base = narrow.addressOf(&regs[0]);
    write32(base, @sizeOf(u32), 0xfeedbeef);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), regs[1]);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), read32(base, @sizeOf(u32)));

    const desc = range(base, 8, 4);
    try std.testing.expectEqual(base, desc.base_addr);
    try std.testing.expectEqual(@as(u32, 8), desc.length);
    try std.testing.expectEqual(@as(u32, 4), desc.stride);
}
