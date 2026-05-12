const std = @import("std");
const abi = @import("abi_bindings");
const narrow = @import("narrow_unsafe");

pub const MmioError = narrow.UnsafeScopeError;

pub const Range = struct {
    base_addr: usize,
    length: u32,
    stride: u32,
};

fn pointerAt(comptime T: type, base_addr: usize, offset: usize) *align(1) volatile T {
    return narrow.pointerAt(T, base_addr, offset);
}

fn readValue(comptime T: type, base_addr: usize, offset: usize) T {
    return pointerAt(T, base_addr, offset).*;
}

fn writeValue(comptime T: type, base_addr: usize, offset: usize, value: T) void {
    pointerAt(T, base_addr, offset).* = value;
}

pub fn requireInteropPolicyBytes(unsafe_scope: u8, reserved: u8) MmioError!void {
    try narrow.requireVolatileMmioPolicyBytes(unsafe_scope, reserved);
}

fn readInteropPolicyBytes(
    comptime T: type,
    base_addr: usize,
    offset: usize,
    unsafe_scope: u8,
    reserved: u8,
) MmioError!T {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return readValue(T, base_addr, offset);
}

fn writeInteropPolicyBytes(
    comptime T: type,
    base_addr: usize,
    offset: usize,
    value: T,
    unsafe_scope: u8,
    reserved: u8,
) MmioError!void {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    writeValue(T, base_addr, offset, value);
}

pub fn range(base_addr: usize, length: u32, stride: u32) Range {
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

pub fn allowsInteropPolicyByte(unsafe_scope: u8) bool {
    return allowsInteropPolicyBytes(unsafe_scope, 0);
}

pub fn requireInteropPolicy(policy: abi.InteropPolicy) MmioError!void {
    try narrow.requireVolatileMmioInteropPolicy(policy);
}

pub fn requireInteropPolicyByte(unsafe_scope: u8) MmioError!void {
    try requireInteropPolicyBytes(unsafe_scope, 0);
}

pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) MmioError!Range {
    try requireInteropPolicy(policy);
    return range(base_addr, length, stride);
}

pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) MmioError!Range {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return range(base_addr, length, stride);
}

pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) MmioError!Range {
    return rangeInteropPolicyBytes(base_addr, length, stride, unsafe_scope, 0);
}

pub fn read8(base_addr: usize, offset: usize) u8 {
    return readValue(u8, base_addr, offset);
}

pub fn read16(base_addr: usize, offset: usize) u16 {
    return readValue(u16, base_addr, offset);
}

pub fn read32(base_addr: usize, offset: usize) u32 {
    return readValue(u32, base_addr, offset);
}

pub fn read64(base_addr: usize, offset: usize) u64 {
    return readValue(u64, base_addr, offset);
}

pub fn write8(base_addr: usize, offset: usize, value: u8) void {
    writeValue(u8, base_addr, offset, value);
}

pub fn write16(base_addr: usize, offset: usize, value: u16) void {
    writeValue(u16, base_addr, offset, value);
}

pub fn write32(base_addr: usize, offset: usize, value: u32) void {
    writeValue(u32, base_addr, offset, value);
}

pub fn write64(base_addr: usize, offset: usize, value: u64) void {
    writeValue(u64, base_addr, offset, value);
}

pub fn read8InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u8 {
    return readInteropPolicyBytes(u8, base_addr, offset, policy.unsafe_scope, policy.reserved);
}

pub fn read16InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u16 {
    return readInteropPolicyBytes(u16, base_addr, offset, policy.unsafe_scope, policy.reserved);
}

pub fn read32InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u32 {
    return readInteropPolicyBytes(u32, base_addr, offset, policy.unsafe_scope, policy.reserved);
}

pub fn read64InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!u64 {
    return readInteropPolicyBytes(u64, base_addr, offset, policy.unsafe_scope, policy.reserved);
}

pub fn write8InteropPolicy(base_addr: usize, offset: usize, value: u8, policy: abi.InteropPolicy) MmioError!void {
    try writeInteropPolicyBytes(u8, base_addr, offset, value, policy.unsafe_scope, policy.reserved);
}

pub fn write16InteropPolicy(base_addr: usize, offset: usize, value: u16, policy: abi.InteropPolicy) MmioError!void {
    try writeInteropPolicyBytes(u16, base_addr, offset, value, policy.unsafe_scope, policy.reserved);
}

pub fn write32InteropPolicy(base_addr: usize, offset: usize, value: u32, policy: abi.InteropPolicy) MmioError!void {
    try writeInteropPolicyBytes(u32, base_addr, offset, value, policy.unsafe_scope, policy.reserved);
}

pub fn write64InteropPolicy(base_addr: usize, offset: usize, value: u64, policy: abi.InteropPolicy) MmioError!void {
    try writeInteropPolicyBytes(u64, base_addr, offset, value, policy.unsafe_scope, policy.reserved);
}

pub fn read8InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) MmioError!u8 {
    return readInteropPolicyBytes(u8, base_addr, offset, unsafe_scope, reserved);
}

pub fn read16InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) MmioError!u16 {
    return readInteropPolicyBytes(u16, base_addr, offset, unsafe_scope, reserved);
}

pub fn read32InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) MmioError!u32 {
    return readInteropPolicyBytes(u32, base_addr, offset, unsafe_scope, reserved);
}

pub fn read64InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) MmioError!u64 {
    return readInteropPolicyBytes(u64, base_addr, offset, unsafe_scope, reserved);
}

pub fn write8InteropPolicyBytes(base_addr: usize, offset: usize, value: u8, unsafe_scope: u8, reserved: u8) MmioError!void {
    try writeInteropPolicyBytes(u8, base_addr, offset, value, unsafe_scope, reserved);
}

pub fn write16InteropPolicyBytes(base_addr: usize, offset: usize, value: u16, unsafe_scope: u8, reserved: u8) MmioError!void {
    try writeInteropPolicyBytes(u16, base_addr, offset, value, unsafe_scope, reserved);
}

pub fn write32InteropPolicyBytes(base_addr: usize, offset: usize, value: u32, unsafe_scope: u8, reserved: u8) MmioError!void {
    try writeInteropPolicyBytes(u32, base_addr, offset, value, unsafe_scope, reserved);
}

pub fn write64InteropPolicyBytes(base_addr: usize, offset: usize, value: u64, unsafe_scope: u8, reserved: u8) MmioError!void {
    try writeInteropPolicyBytes(u64, base_addr, offset, value, unsafe_scope, reserved);
}

pub fn read8InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) MmioError!u8 {
    return read8InteropPolicyBytes(base_addr, offset, unsafe_scope, 0);
}

pub fn read16InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) MmioError!u16 {
    return read16InteropPolicyBytes(base_addr, offset, unsafe_scope, 0);
}

pub fn read32InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) MmioError!u32 {
    return read32InteropPolicyBytes(base_addr, offset, unsafe_scope, 0);
}

pub fn read64InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) MmioError!u64 {
    return read64InteropPolicyBytes(base_addr, offset, unsafe_scope, 0);
}

pub fn write8InteropPolicyByte(base_addr: usize, offset: usize, value: u8, unsafe_scope: u8) MmioError!void {
    try write8InteropPolicyBytes(base_addr, offset, value, unsafe_scope, 0);
}

pub fn write16InteropPolicyByte(base_addr: usize, offset: usize, value: u16, unsafe_scope: u8) MmioError!void {
    try write16InteropPolicyBytes(base_addr, offset, value, unsafe_scope, 0);
}

pub fn write32InteropPolicyByte(base_addr: usize, offset: usize, value: u32, unsafe_scope: u8) MmioError!void {
    try write32InteropPolicyBytes(base_addr, offset, value, unsafe_scope, 0);
}

pub fn write64InteropPolicyByte(base_addr: usize, offset: usize, value: u64, unsafe_scope: u8) MmioError!void {
    try write64InteropPolicyBytes(base_addr, offset, value, unsafe_scope, 0);
}

test "phase3 mmio wrappers keep direct reads and writes reviewable" {
    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = narrow.addressOf(&bytes[0]);
    const aligned_halfword: *align(1) const u16 = @ptrCast(&bytes[2]);
    const aligned_word: *align(1) const u32 = @ptrCast(&bytes[4]);
    const aligned_doubleword: *align(1) const u64 = @ptrCast(&bytes[8]);

    const desc = range(base, 16, 4);
    try std.testing.expectEqual(base, desc.base_addr);
    try std.testing.expectEqual(@as(u32, 16), desc.length);
    try std.testing.expectEqual(@as(u32, 4), desc.stride);

    write8(base, 1, 0x5a);
    try std.testing.expectEqual(@as(u8, 0x5a), read8(base, 1));

    write16(base, 2, 0xbeef);
    try std.testing.expectEqual(@as(u16, 0xbeef), aligned_halfword.*);
    try std.testing.expectEqual(@as(u16, 0xbeef), read16(base, 2));

    write32(base, 4, 0xfeed_beef);
    try std.testing.expectEqual(@as(u32, 0xfeed_beef), aligned_word.*);
    try std.testing.expectEqual(@as(u32, 0xfeed_beef), read32(base, 4));

    write64(base, 8, 0x0123_4567_89ab_cdef);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), aligned_doubleword.*);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), read64(base, 8));
}

test "phase3 mmio wrappers keep volatile-mmio policy gates reviewable" {
    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = narrow.addressOf(&bytes[0]);

    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const none_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const raw_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };

    try std.testing.expect(allowsInteropPolicy(mmio_policy));
    try std.testing.expect(allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 0));
    try std.testing.expect(allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.volatile_mmio)));
    try std.testing.expect(!allowsInteropPolicy(none_policy));
    try std.testing.expect(!allowsInteropPolicy(raw_policy));
    try std.testing.expect(!allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.none)));
    try std.testing.expect(!allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge)));
    try std.testing.expect(!allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 1));

    try requireInteropPolicy(mmio_policy);
    try requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 0);
    try requireInteropPolicyByte(@intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 1),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        requireInteropPolicyByte(@intFromEnum(abi.UnsafeScope.none)),
    );

    const desc = try rangeInteropPolicy(base, 16, 8, mmio_policy);
    try std.testing.expectEqual(@as(u32, 8), desc.stride);
    try std.testing.expectEqual(base, (try rangeInteropPolicyByte(base, 16, 4, @intFromEnum(abi.UnsafeScope.volatile_mmio))).base_addr);
    try std.testing.expectError(error.UnsafeScopeDenied, rangeInteropPolicy(base, 16, 4, none_policy));

    try write16InteropPolicy(base, 2, 0x1234, mmio_policy);
    try std.testing.expectEqual(@as(u16, 0x1234), try read16InteropPolicy(base, 2, mmio_policy));

    try write32InteropPolicyByte(base, 4, 0xc001_d00d, @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(
        @as(u32, 0xc001_d00d),
        try read32InteropPolicyByte(base, 4, @intFromEnum(abi.UnsafeScope.volatile_mmio)),
    );

    try write64InteropPolicyBytes(
        base,
        8,
        0x0bad_f00d_dead_beef,
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        0,
    );
    try std.testing.expectEqual(
        @as(u64, 0x0bad_f00d_dead_beef),
        try read64InteropPolicyBytes(base, 8, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0),
    );

    try std.testing.expectError(error.UnsafeScopeDenied, read8InteropPolicy(base, 0, none_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, write8InteropPolicy(base, 0, 0x44, raw_policy));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        read16InteropPolicyBytes(base, 2, @intFromEnum(abi.UnsafeScope.volatile_mmio), 1),
    );
}
