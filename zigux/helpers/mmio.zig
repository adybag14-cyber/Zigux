const std = @import("std");
const abi = @import("abi_bindings");
const narrow = @import("narrow_unsafe");

pub const PolicyError = error{UnsafeScopeDenied};

pub fn range(base_addr: usize, length: u32, stride: u32) abi.MmioRange {
    return .{
        .base_addr = base_addr,
        .length = length,
        .stride = stride,
    };
}

pub fn allowsInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return narrow.permitsVolatileMmioPolicyBytes(unsafe_scope, reserved);
}

pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.permitsVolatileMmioInteropPolicy(policy);
}

pub fn requireInteropPolicyBytes(unsafe_scope: u8, reserved: u8) PolicyError!void {
    return narrow.requireVolatileMmioPolicyBytes(unsafe_scope, reserved);
}

pub fn requireInteropPolicy(policy: abi.InteropPolicy) PolicyError!void {
    return narrow.requireVolatileMmioInteropPolicy(policy);
}

pub fn rangeInteropPolicyBytes(
    base_addr: usize,
    length: u32,
    stride: u32,
    unsafe_scope: u8,
    reserved: u8,
) PolicyError!abi.MmioRange {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return range(base_addr, length, stride);
}

pub fn rangeInteropPolicy(
    base_addr: usize,
    length: u32,
    stride: u32,
    policy: abi.InteropPolicy,
) PolicyError!abi.MmioRange {
    try requireInteropPolicy(policy);
    return range(base_addr, length, stride);
}

pub fn rangeInteropPolicyByte(
    base_addr: usize,
    length: u32,
    stride: u32,
    unsafe_scope: u8,
) PolicyError!abi.MmioRange {
    try requireInteropPolicyBytes(unsafe_scope, 0);
    return range(base_addr, length, stride);
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

pub fn read64(base_addr: usize, offset: usize) u64 {
    const ptr = narrow.pointerAt(u64, base_addr, offset);
    return ptr.*;
}

pub fn write64(base_addr: usize, offset: usize, value: u64) void {
    const ptr = narrow.pointerAt(u64, base_addr, offset);
    ptr.* = value;
}

pub fn read8InteropPolicyBytes(
    base_addr: usize,
    offset: usize,
    unsafe_scope: u8,
    reserved: u8,
) PolicyError!u8 {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return read8(base_addr, offset);
}

pub fn read8InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) PolicyError!u8 {
    try requireInteropPolicy(policy);
    return read8(base_addr, offset);
}

pub fn read8InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) PolicyError!u8 {
    try requireInteropPolicyBytes(unsafe_scope, 0);
    return read8(base_addr, offset);
}

pub fn write8InteropPolicyBytes(
    base_addr: usize,
    offset: usize,
    value: u8,
    unsafe_scope: u8,
    reserved: u8,
) PolicyError!void {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    write8(base_addr, offset, value);
}

pub fn write8InteropPolicy(
    base_addr: usize,
    offset: usize,
    value: u8,
    policy: abi.InteropPolicy,
) PolicyError!void {
    try requireInteropPolicy(policy);
    write8(base_addr, offset, value);
}

pub fn write8InteropPolicyByte(base_addr: usize, offset: usize, value: u8, unsafe_scope: u8) PolicyError!void {
    try requireInteropPolicyBytes(unsafe_scope, 0);
    write8(base_addr, offset, value);
}

pub fn read16InteropPolicyBytes(
    base_addr: usize,
    offset: usize,
    unsafe_scope: u8,
    reserved: u8,
) PolicyError!u16 {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return read16(base_addr, offset);
}

pub fn read16InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) PolicyError!u16 {
    try requireInteropPolicy(policy);
    return read16(base_addr, offset);
}

pub fn read16InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) PolicyError!u16 {
    try requireInteropPolicyBytes(unsafe_scope, 0);
    return read16(base_addr, offset);
}

pub fn write16InteropPolicyBytes(
    base_addr: usize,
    offset: usize,
    value: u16,
    unsafe_scope: u8,
    reserved: u8,
) PolicyError!void {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    write16(base_addr, offset, value);
}

pub fn write16InteropPolicy(
    base_addr: usize,
    offset: usize,
    value: u16,
    policy: abi.InteropPolicy,
) PolicyError!void {
    try requireInteropPolicy(policy);
    write16(base_addr, offset, value);
}

pub fn write16InteropPolicyByte(base_addr: usize, offset: usize, value: u16, unsafe_scope: u8) PolicyError!void {
    try requireInteropPolicyBytes(unsafe_scope, 0);
    write16(base_addr, offset, value);
}

pub fn read32InteropPolicyBytes(
    base_addr: usize,
    offset: usize,
    unsafe_scope: u8,
    reserved: u8,
) PolicyError!u32 {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return read32(base_addr, offset);
}

pub fn read32InteropPolicyByte(
    base_addr: usize,
    offset: usize,
    unsafe_scope: u8,
) PolicyError!u32 {
    try requireInteropPolicyBytes(unsafe_scope, 0);
    return read32(base_addr, offset);
}

pub fn read32InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) PolicyError!u32 {
    try requireInteropPolicy(policy);
    return read32(base_addr, offset);
}

pub fn write32InteropPolicyBytes(
    base_addr: usize,
    offset: usize,
    value: u32,
    unsafe_scope: u8,
    reserved: u8,
) PolicyError!void {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    write32(base_addr, offset, value);
}

pub fn write32InteropPolicyByte(
    base_addr: usize,
    offset: usize,
    value: u32,
    unsafe_scope: u8,
) PolicyError!void {
    try requireInteropPolicyBytes(unsafe_scope, 0);
    write32(base_addr, offset, value);
}

pub fn write32InteropPolicy(
    base_addr: usize,
    offset: usize,
    value: u32,
    policy: abi.InteropPolicy,
) PolicyError!void {
    try requireInteropPolicy(policy);
    write32(base_addr, offset, value);
}

pub fn read64InteropPolicyBytes(
    base_addr: usize,
    offset: usize,
    unsafe_scope: u8,
    reserved: u8,
) PolicyError!u64 {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return read64(base_addr, offset);
}

pub fn read64InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) PolicyError!u64 {
    try requireInteropPolicy(policy);
    return read64(base_addr, offset);
}

pub fn read64InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) PolicyError!u64 {
    try requireInteropPolicyBytes(unsafe_scope, 0);
    return read64(base_addr, offset);
}

pub fn write64InteropPolicyBytes(
    base_addr: usize,
    offset: usize,
    value: u64,
    unsafe_scope: u8,
    reserved: u8,
) PolicyError!void {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    write64(base_addr, offset, value);
}

pub fn write64InteropPolicy(
    base_addr: usize,
    offset: usize,
    value: u64,
    policy: abi.InteropPolicy,
) PolicyError!void {
    try requireInteropPolicy(policy);
    write64(base_addr, offset, value);
}

pub fn write64InteropPolicyByte(base_addr: usize, offset: usize, value: u64, unsafe_scope: u8) PolicyError!void {
    try requireInteropPolicyBytes(unsafe_scope, 0);
    write64(base_addr, offset, value);
}

test "phase3 mmio wrapper uses bounded volatile access" {
    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = narrow.addressOf(&bytes[0]);

    write8(base, 0, 0x5a);
    try std.testing.expectEqual(@as(u8, 0x5a), bytes[0]);
    try std.testing.expectEqual(@as(u8, 0x5a), read8(base, 0));

    const unaligned_halfword: *align(1) const u16 = @ptrCast(&bytes[1]);
    write16(base, 1, 0xbeef);
    try std.testing.expectEqual(@as(u16, 0xbeef), unaligned_halfword.*);
    try std.testing.expectEqual(@as(u16, 0xbeef), read16(base, 1));

    const unaligned_word: *align(1) const u32 = @ptrCast(&bytes[3]);
    write32(base, 3, 0xfeedbeef);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), unaligned_word.*);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), read32(base, 3));

    const aligned_doubleword: *align(1) const u64 = @ptrCast(&bytes[8]);
    write64(base, 8, 0x0123_4567_89ab_cdef);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), aligned_doubleword.*);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), read64(base, 8));

    const unaligned_doubleword: *align(1) const u64 = @ptrCast(&bytes[5]);
    write64(base, 5, 0xfedc_ba98_7654_3210);
    try std.testing.expectEqual(@as(u64, 0xfedc_ba98_7654_3210), unaligned_doubleword.*);
    try std.testing.expectEqual(@as(u64, 0xfedc_ba98_7654_3210), read64(base, 5));

    const desc = range(base, 24, 1);
    try std.testing.expectEqual(base, desc.base_addr);
    try std.testing.expectEqual(@as(u32, 24), desc.length);
    try std.testing.expectEqual(@as(u32, 1), desc.stride);

    const halfword_desc = range(base, 24, 2);
    try std.testing.expectEqual(base, halfword_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 24), halfword_desc.length);
    try std.testing.expectEqual(@as(u32, 2), halfword_desc.stride);

    const word_desc = range(base, 24, 4);
    try std.testing.expectEqual(base, word_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 24), word_desc.length);
    try std.testing.expectEqual(@as(u32, 4), word_desc.stride);

    const dword_desc = range(base, 24, 8);
    try std.testing.expectEqual(base, dword_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 24), dword_desc.length);
    try std.testing.expectEqual(@as(u32, 8), dword_desc.stride);
}

test "phase3 mmio interop policy gates stay explicit" {
    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = narrow.addressOf(&bytes[0]);

    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const no_unsafe_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };
    const volatile_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio);

    try std.testing.expect(allowsInteropPolicy(mmio_policy));
    try std.testing.expect(allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 0));
    try std.testing.expect(!allowsInteropPolicy(no_unsafe_policy));
    try std.testing.expect(!allowsInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!allowsInteropPolicy(reserved_policy));
    try std.testing.expect(!allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 1));

    try std.testing.expectError(error.UnsafeScopeDenied, narrow.requireVolatileMmioInteropPolicy(no_unsafe_policy));
    try narrow.requireVolatileMmioInteropPolicy(mmio_policy);
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.requireVolatileMmioInteropPolicy(raw_pointer_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.requireVolatileMmioInteropPolicy(reserved_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.requireVolatileMmioByte(0));
    try narrow.requireVolatileMmioByte(1);
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.requireVolatileMmioByte(2));

    const scoped_desc = try rangeInteropPolicy(base, 16, 4, mmio_policy);
    try std.testing.expectEqual(base, scoped_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 16), scoped_desc.length);
    try std.testing.expectEqual(@as(u32, 4), scoped_desc.stride);
    const byte_scoped_desc = try rangeInteropPolicyByte(base, 12, 2, @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(base, byte_scoped_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 12), byte_scoped_desc.length);
    try std.testing.expectEqual(@as(u32, 2), byte_scoped_desc.stride);
    try std.testing.expectError(error.UnsafeScopeDenied, rangeInteropPolicy(base, 16, 4, no_unsafe_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, rangeInteropPolicy(base, 16, 4, raw_pointer_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, rangeInteropPolicy(base, 16, 4, reserved_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, rangeInteropPolicyByte(base, 12, 2, @intFromEnum(abi.UnsafeScope.none)));
    try std.testing.expectError(error.UnsafeScopeDenied, rangeInteropPolicyByte(base, 12, 2, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge)));

    try write8InteropPolicy(base, 0, 0x33, mmio_policy);
    try std.testing.expectEqual(@as(u8, 0x33), try read8InteropPolicy(base, 0, mmio_policy));
    try write8InteropPolicyByte(base, 1, 0x44, volatile_scope);
    try std.testing.expectEqual(@as(u8, 0x44), try read8InteropPolicyByte(base, 1, volatile_scope));
    try write16InteropPolicy(base, 2, 0x1234, mmio_policy);
    try std.testing.expectEqual(@as(u16, 0x1234), try read16InteropPolicy(base, 2, mmio_policy));
    try write16InteropPolicyByte(base, 4, 0x5678, volatile_scope);
    try std.testing.expectEqual(@as(u16, 0x5678), try read16InteropPolicyByte(base, 4, volatile_scope));
    try write32InteropPolicy(base, 4, 0xfeed_beef, mmio_policy);
    try std.testing.expectEqual(@as(u32, 0xfeed_beef), try read32InteropPolicy(base, 4, mmio_policy));
    try write32InteropPolicyByte(base, 6, 0x89ab_cdef, volatile_scope);
    try std.testing.expectEqual(@as(u32, 0x89ab_cdef), try read32InteropPolicyByte(base, 6, volatile_scope));
    try write64InteropPolicy(base, 8, 0x0123_4567_89ab_cdef, mmio_policy);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), try read64InteropPolicy(base, 8, mmio_policy));
    try write64InteropPolicyByte(base, 8, 0xfedc_ba98_7654_3210, volatile_scope);
    try std.testing.expectEqual(@as(u64, 0xfedc_ba98_7654_3210), try read64InteropPolicyByte(base, 8, volatile_scope));

    try write8InteropPolicyBytes(base, 1, 0x44, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0);
    try std.testing.expectEqual(
        @as(u8, 0x44),
        try read8InteropPolicyBytes(base, 1, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0),
    );

    try std.testing.expectError(error.UnsafeScopeDenied, requireInteropPolicy(no_unsafe_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireInteropPolicy(raw_pointer_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireInteropPolicy(reserved_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, read32InteropPolicy(base, 4, no_unsafe_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, write16InteropPolicy(base, 2, 0x7777, raw_pointer_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, read8InteropPolicyBytes(base, 1, 1, 1));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        read16InteropPolicyByte(base, 4, @intFromEnum(abi.UnsafeScope.none)),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        write32InteropPolicyByte(base, 6, 0, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge)),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        read64InteropPolicyByte(base, 8, @intFromEnum(abi.UnsafeScope.none)),
    );
    try std.testing.expectError(error.UnsafeScopeDenied, write64InteropPolicyBytes(base, 8, 0, 0, 0));
}
