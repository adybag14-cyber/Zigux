const std = @import("std");
const abi = @import("abi_bindings");
const unsafe_policy = @import("unsafe_policy");

pub const MmioWindowError = unsafe_policy.UnsafeScopeError || error{
    AddressOverflow,
    ByteLengthTooSmall,
};

fn requireByteCoverage(comptime T: type, byte_len: usize) MmioWindowError!void {
    if (byte_len < @sizeOf(T)) return error.ByteLengthTooSmall;
}

fn requireAddressSpan(address: usize, byte_len: usize) MmioWindowError!void {
    _ = std.math.add(usize, address, byte_len) catch return error.AddressOverflow;
}

fn volatilePointer(comptime T: type, address: usize) *align(1) volatile T {
    return @ptrFromInt(address);
}

fn volatileConstPointer(comptime T: type, address: usize) *align(1) const volatile T {
    return @ptrFromInt(address);
}

pub fn pointerAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    byte_len: usize,
    unsafe_scope: u8,
    reserved: u8,
) MmioWindowError!*align(1) volatile T {
    try unsafe_policy.requireVolatileMmioPolicyBytes(unsafe_scope, reserved);
    try requireByteCoverage(T, byte_len);
    try requireAddressSpan(address, byte_len);
    return volatilePointer(T, address);
}

pub fn pointerAtInteropPolicy(
    comptime T: type,
    address: usize,
    byte_len: usize,
    policy: abi.InteropPolicy,
) MmioWindowError!*align(1) volatile T {
    return pointerAtInteropPolicyBytes(T, address, byte_len, policy.unsafe_scope, policy.reserved);
}

pub fn pointerAtByte(comptime T: type, address: usize, byte_len: usize, scope: u8) MmioWindowError!*align(1) volatile T {
    return pointerAtInteropPolicyBytes(T, address, byte_len, scope, 0);
}

pub fn constPointerAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    byte_len: usize,
    unsafe_scope: u8,
    reserved: u8,
) MmioWindowError!*align(1) const volatile T {
    try unsafe_policy.requireVolatileMmioPolicyBytes(unsafe_scope, reserved);
    try requireByteCoverage(T, byte_len);
    try requireAddressSpan(address, byte_len);
    return volatileConstPointer(T, address);
}

pub fn constPointerAtInteropPolicy(
    comptime T: type,
    address: usize,
    byte_len: usize,
    policy: abi.InteropPolicy,
) MmioWindowError!*align(1) const volatile T {
    return constPointerAtInteropPolicyBytes(T, address, byte_len, policy.unsafe_scope, policy.reserved);
}

pub fn constPointerAtByte(comptime T: type, address: usize, byte_len: usize, scope: u8) MmioWindowError!*align(1) const volatile T {
    return constPointerAtInteropPolicyBytes(T, address, byte_len, scope, 0);
}

pub fn readValueAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    byte_len: usize,
    unsafe_scope: u8,
    reserved: u8,
) MmioWindowError!T {
    return (try constPointerAtInteropPolicyBytes(T, address, byte_len, unsafe_scope, reserved)).*;
}

pub fn readValueAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, policy: abi.InteropPolicy) MmioWindowError!T {
    return readValueAtInteropPolicyBytes(T, address, byte_len, policy.unsafe_scope, policy.reserved);
}

pub fn readValueAtByte(comptime T: type, address: usize, byte_len: usize, scope: u8) MmioWindowError!T {
    return readValueAtInteropPolicyBytes(T, address, byte_len, scope, 0);
}

pub fn writeValueAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    byte_len: usize,
    value: T,
    unsafe_scope: u8,
    reserved: u8,
) MmioWindowError!void {
    const ptr = try pointerAtInteropPolicyBytes(T, address, byte_len, unsafe_scope, reserved);
    ptr.* = value;
}

pub fn writeValueAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, value: T, policy: abi.InteropPolicy) MmioWindowError!void {
    return writeValueAtInteropPolicyBytes(T, address, byte_len, value, policy.unsafe_scope, policy.reserved);
}

pub fn writeValueAtByte(comptime T: type, address: usize, byte_len: usize, value: T, scope: u8) MmioWindowError!void {
    return writeValueAtInteropPolicyBytes(T, address, byte_len, value, scope, 0);
}

pub fn exchangeValueAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    byte_len: usize,
    value: T,
    unsafe_scope: u8,
    reserved: u8,
) MmioWindowError!T {
    const ptr = try pointerAtInteropPolicyBytes(T, address, byte_len, unsafe_scope, reserved);
    const before = ptr.*;
    ptr.* = value;
    return before;
}

pub fn exchangeValueAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, value: T, policy: abi.InteropPolicy) MmioWindowError!T {
    return exchangeValueAtInteropPolicyBytes(T, address, byte_len, value, policy.unsafe_scope, policy.reserved);
}

pub fn exchangeValueAtByte(comptime T: type, address: usize, byte_len: usize, value: T, scope: u8) MmioWindowError!T {
    return exchangeValueAtInteropPolicyBytes(T, address, byte_len, value, scope, 0);
}

test "phase3 mmio window keeps volatile register windows explicit" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const denied_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    var register: u32 = 0x1234_5678;
    const register_addr = @intFromPtr(&register);

    const ptr = try pointerAtInteropPolicy(u32, register_addr, @sizeOf(u32), mmio_policy);
    try std.testing.expectEqual(@as(u32, 0x1234_5678), ptr.*);

    const const_ptr = try constPointerAtByte(u32, register_addr, @sizeOf(u32), @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(@as(u32, 0x1234_5678), const_ptr.*);

    try std.testing.expectEqual(@as(u32, 0x1234_5678), try readValueAtInteropPolicy(u32, register_addr, @sizeOf(u32), mmio_policy));
    try writeValueAtByte(u32, register_addr, @sizeOf(u32), 0xCAFE_BABE, @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), register);
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), try exchangeValueAtInteropPolicyBytes(u32, register_addr, @sizeOf(u32), 0x0BAD_C0DE, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0));
    try std.testing.expectEqual(@as(u32, 0x0BAD_C0DE), register);

    try std.testing.expectError(error.UnsafeScopeDenied, pointerAtInteropPolicy(u32, register_addr, @sizeOf(u32), denied_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, constPointerAtInteropPolicy(u32, register_addr, @sizeOf(u32), reserved_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, readValueAtByte(u32, register_addr, @sizeOf(u32), @intFromEnum(abi.UnsafeScope.raw_pointer_bridge)));
    try std.testing.expectError(error.ByteLengthTooSmall, pointerAtByte(u32, register_addr, @sizeOf(u16), @intFromEnum(abi.UnsafeScope.volatile_mmio)));
}

test "phase3 mmio window keeps odd-aligned volatile windows reviewable" {
    var bytes = [_]u8{ 0, 0x34, 0x12, 0, 0 };
    const mmio_addr = @intFromPtr(&bytes[1]);

    const ptr = try pointerAtByte(u16, mmio_addr, @sizeOf(u16), @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(@as(u16, 0x1234), ptr.*);

    try writeValueAtInteropPolicyBytes(u16, mmio_addr, @sizeOf(u16), 0xBEEF, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0);
    try std.testing.expectEqual(@as(u16, 0xBEEF), ptr.*);
}
