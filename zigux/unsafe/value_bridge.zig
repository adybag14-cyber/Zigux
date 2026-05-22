const std = @import("std");
const abi = @import("abi_bindings");
const narrow = @import("narrow");

pub fn readValueAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    unsafe_scope: u8,
    reserved: u8,
) narrow.RawPointerBridgeError!T {
    return (try narrow.constPointerAtInteropPolicyBytes(T, address, unsafe_scope, reserved)).*;
}

pub fn readValueAtInteropPolicy(
    comptime T: type,
    address: usize,
    policy: abi.InteropPolicy,
) narrow.RawPointerBridgeError!T {
    return readValueAtInteropPolicyBytes(T, address, policy.unsafe_scope, policy.reserved);
}

pub fn readValueAtByte(
    comptime T: type,
    address: usize,
    scope: u8,
) narrow.RawPointerBridgeError!T {
    return readValueAtInteropPolicyBytes(T, address, scope, 0);
}

test "phase3 value bridge keeps raw-pointer-bridge reads typed and explicit" {
    const raw_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge);
    const raw_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = raw_scope,
        .reserved = 0,
    };

    var values = [_]u32{ 0x0102_0304, 0x5566_7788 };
    const first_addr = @intFromPtr(&values[0]);
    const second_addr = @intFromPtr(&values[1]);
    var odd_storage = [_]u8{ 0, 0xcd, 0xab, 0, 0 };
    const odd_addr = @intFromPtr(&odd_storage[1]);

    try std.testing.expectEqual(@as(u32, 0x0102_0304), try readValueAtByte(u32, first_addr, raw_scope));
    try std.testing.expectEqual(@as(u32, 0x5566_7788), try readValueAtInteropPolicy(u32, second_addr, raw_policy));
    try std.testing.expectEqual(
        @as(u16, 0xabcd),
        try readValueAtInteropPolicyBytes(u16, odd_addr, raw_scope, 0),
    );
}

test "phase3 value bridge rejects non-raw or malformed policy bytes" {
    const raw_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge);
    const none_scope = @intFromEnum(abi.UnsafeScope.none);
    const mmio_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio);
    const denied_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = none_scope,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = raw_scope,
        .reserved = 1,
    };
    var value: u32 = 0xCAFE_BABE;
    const addr = @intFromPtr(&value);

    try std.testing.expectError(error.UnsafeScopeDenied, readValueAtByte(u32, addr, none_scope));
    try std.testing.expectError(error.UnsafeScopeDenied, readValueAtByte(u32, addr, mmio_scope));
    try std.testing.expectError(error.UnsafeScopeDenied, readValueAtInteropPolicy(u32, addr, denied_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, readValueAtInteropPolicy(u32, addr, reserved_policy));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        readValueAtInteropPolicyBytes(u32, addr, raw_scope, 1),
    );
}

test "phase3 value bridge reports address overflow before reading" {
    const raw_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge);

    try std.testing.expectError(
        error.AddressOverflow,
        readValueAtByte(u32, std.math.maxInt(usize), raw_scope),
    );
}
