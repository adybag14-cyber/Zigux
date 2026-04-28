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

pub fn read32Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u32 {
    const ptr = try narrow.scopedPointerAt(u32, scope, base_addr, offset);
    return ptr.*;
}

pub fn write32Scoped(
    scope: narrow.UnsafeScopeTag,
    base_addr: usize,
    offset: usize,
    value: u32,
) narrow.ScopeError!void {
    const ptr = try narrow.scopedPointerAt(u32, scope, base_addr, offset);
    ptr.* = value;
}

pub fn read32(base_addr: usize, offset: usize) u32 {
    return read32Scoped(.volatile_mmio, base_addr, offset) catch unreachable;
}

pub fn write32(base_addr: usize, offset: usize, value: u32) void {
    write32Scoped(.volatile_mmio, base_addr, offset, value) catch unreachable;
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

test "phase3 mmio wrapper keeps declared scope explicit" {
    var regs = [_]u32{ 0, 0 };
    const base = narrow.addressOf(&regs[0]);

    try std.testing.expectError(error.UnsafeScopeDenied, write32Scoped(.none, base, 0, 0x12345678));
    try std.testing.expectError(error.UnsafeScopeDenied, read32Scoped(.raw_pointer_bridge, base, 0));

    try write32Scoped(.volatile_mmio, base, @sizeOf(u32), 0xaabbccdd);
    try std.testing.expectEqual(@as(u32, 0xaabbccdd), regs[1]);
    try std.testing.expectEqual(@as(u32, 0xaabbccdd), try read32Scoped(.volatile_mmio, base, @sizeOf(u32)));
}
