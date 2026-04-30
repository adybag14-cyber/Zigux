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

pub fn read8Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u8 {
    const ptr = try narrow.scopedPointerAt(u8, scope, base_addr, offset);
    return ptr.*;
}

pub fn write8Scoped(
    scope: narrow.UnsafeScopeTag,
    base_addr: usize,
    offset: usize,
    value: u8,
) narrow.ScopeError!void {
    const ptr = try narrow.scopedPointerAt(u8, scope, base_addr, offset);
    ptr.* = value;
}

pub fn read16Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u16 {
    const ptr = try narrow.scopedPointerAt(u16, scope, base_addr, offset);
    return ptr.*;
}

pub fn write16Scoped(
    scope: narrow.UnsafeScopeTag,
    base_addr: usize,
    offset: usize,
    value: u16,
) narrow.ScopeError!void {
    const ptr = try narrow.scopedPointerAt(u16, scope, base_addr, offset);
    ptr.* = value;
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

pub fn read8(base_addr: usize, offset: usize) u8 {
    return read8Scoped(.volatile_mmio, base_addr, offset) catch unreachable;
}

pub fn write8(base_addr: usize, offset: usize, value: u8) void {
    write8Scoped(.volatile_mmio, base_addr, offset, value) catch unreachable;
}

pub fn read16(base_addr: usize, offset: usize) u16 {
    return read16Scoped(.volatile_mmio, base_addr, offset) catch unreachable;
}

pub fn write16(base_addr: usize, offset: usize, value: u16) void {
    write16Scoped(.volatile_mmio, base_addr, offset, value) catch unreachable;
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
    write8(base, 1, 0x5a);
    try std.testing.expectEqual(@as(u8, 0x5a), read8(base, 1));
    write16(base, 0, 0xbeef);
    try std.testing.expectEqual(@as(u16, 0xbeef), read16(base, 0));

    write32(base, @sizeOf(u32), 0xfeedbeef);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), regs[1]);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), read32(base, @sizeOf(u32)));

    const desc = range(base, 8, 4);
    try std.testing.expectEqual(base, desc.base_addr);
    try std.testing.expectEqual(@as(u32, 8), desc.length);
    try std.testing.expectEqual(@as(u32, 4), desc.stride);
}

test "phase3 mmio wrapper keeps declared scope explicit across widths" {
    var regs = [_]u32{ 0, 0 };
    const base = narrow.addressOf(&regs[0]);

    try std.testing.expectError(error.UnsafeScopeDenied, write8Scoped(.none, base, 0, 0xab));
    try std.testing.expectError(error.UnsafeScopeDenied, read8Scoped(.raw_pointer_bridge, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, write16Scoped(.none, base, 0, 0xabcd));
    try std.testing.expectError(error.UnsafeScopeDenied, read16Scoped(.raw_pointer_bridge, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, write32Scoped(.none, base, 0, 0x12345678));
    try std.testing.expectError(error.UnsafeScopeDenied, read32Scoped(.raw_pointer_bridge, base, 0));

    try write8Scoped(.volatile_mmio, base, 1, 0xab);
    try std.testing.expectEqual(@as(u8, 0xab), try read8Scoped(.volatile_mmio, base, 1));
    try write16Scoped(.volatile_mmio, base, 0, 0xabcd);
    try std.testing.expectEqual(@as(u16, 0xabcd), try read16Scoped(.volatile_mmio, base, 0));

    try write32Scoped(.volatile_mmio, base, @sizeOf(u32), 0xaabbccdd);
    try std.testing.expectEqual(@as(u32, 0xaabbccdd), regs[1]);
    try std.testing.expectEqual(@as(u32, 0xaabbccdd), try read32Scoped(.volatile_mmio, base, @sizeOf(u32)));
}

test "phase3 mmio wrapper rejects misaligned scoped accesses" {
    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = narrow.addressOf(&bytes[0]);

    try std.testing.expectError(error.MisalignedAccess, write16Scoped(.volatile_mmio, base, 1, 0xabcd));
    try std.testing.expectError(error.MisalignedAccess, read16Scoped(.volatile_mmio, base, 1));
    try std.testing.expectError(error.MisalignedAccess, write32Scoped(.volatile_mmio, base, 2, 0x12345678));
    try std.testing.expectError(error.MisalignedAccess, read32Scoped(.volatile_mmio, base, 2));
}

test "phase3 mmio wrapper rejects overflowed scoped accesses" {
    const max = std.math.maxInt(usize);

    try std.testing.expectError(error.AddressOverflow, write8Scoped(.volatile_mmio, max, 1, 0xab));
    try std.testing.expectError(error.AddressOverflow, read8Scoped(.volatile_mmio, max, 1));
    try std.testing.expectError(error.AddressOverflow, write16Scoped(.volatile_mmio, max, 1, 0xabcd));
    try std.testing.expectError(error.AddressOverflow, read16Scoped(.volatile_mmio, max, 1));
    try std.testing.expectError(error.AddressOverflow, write32Scoped(.volatile_mmio, max, 4, 0x12345678));
    try std.testing.expectError(error.AddressOverflow, read32Scoped(.volatile_mmio, max, 4));
}
