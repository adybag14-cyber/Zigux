const std = @import("std");
const abi = @import("abi_bindings");
const narrow = @import("narrow_unsafe");

pub const UnsafeScopeError = narrow.UnsafeScopeError;

pub fn requireNoUnsafe(scope: narrow.UnsafeScopeTag) UnsafeScopeError!void {
    if (!narrow.permitsNoUnsafe(scope)) return error.UnsafeScopeDenied;
}

pub fn requireNoUnsafePolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {
    if (!narrow.permitsNoUnsafePolicyBytes(unsafe_scope, reserved)) return error.UnsafeScopeDenied;
}

pub fn requireNoUnsafeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return requireNoUnsafePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireNoUnsafeByte(unsafe_scope: u8) UnsafeScopeError!void {
    return requireNoUnsafePolicyBytes(unsafe_scope, 0);
}

pub fn requireVolatileMmio(scope: narrow.UnsafeScopeTag) UnsafeScopeError!void {
    if (!narrow.permitsVolatileMmio(scope)) return error.UnsafeScopeDenied;
}

pub fn requireVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {
    if (!narrow.permitsVolatileMmioPolicyBytes(unsafe_scope, reserved)) return error.UnsafeScopeDenied;
}

pub fn requireVolatileMmioInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return requireVolatileMmioPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireVolatileMmioByte(unsafe_scope: u8) UnsafeScopeError!void {
    return requireVolatileMmioPolicyBytes(unsafe_scope, 0);
}

pub fn requireRawPointerBridge(scope: narrow.UnsafeScopeTag) UnsafeScopeError!void {
    if (!narrow.permitsRawPointerBridge(scope)) return error.UnsafeScopeDenied;
}

pub fn requireRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {
    return narrow.requireRawPointerBridgePolicyBytes(unsafe_scope, reserved);
}

pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return narrow.requireRawPointerBridgeInteropPolicy(policy);
}

pub fn requireRawPointerBridgeByte(unsafe_scope: u8) UnsafeScopeError!void {
    return requireRawPointerBridgePolicyBytes(unsafe_scope, 0);
}

test "phase3 scope require helper fail-closes by scope family" {
    try requireNoUnsafe(.none);
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafe(.volatile_mmio));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafe(.raw_pointer_bridge));

    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmio(.none));
    try requireVolatileMmio(.volatile_mmio);
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmio(.raw_pointer_bridge));

    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridge(.none));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridge(.volatile_mmio));
    try requireRawPointerBridge(.raw_pointer_bridge);
}

test "phase3 scope require helper fail-closes by interop policy bytes" {
    try requireNoUnsafeByte(0);
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeByte(1));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeByte(2));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeByte(9));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafePolicyBytes(0, 1));

    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioByte(0));
    try requireVolatileMmioByte(1);
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioByte(2));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioByte(9));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioPolicyBytes(1, 1));

    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeByte(0));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeByte(1));
    try requireRawPointerBridgeByte(2);
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeByte(9));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgePolicyBytes(2, 1));
}

test "phase3 scope require helper fail-closes by typed interop policy" {
    const none_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = 0,
        .reserved = 0,
    };
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 1,
        .allocator_mode = 1,
        .unsafe_scope = 1,
        .reserved = 0,
    };
    const raw_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 2,
        .unsafe_scope = 2,
        .reserved = 0,
    };
    const unknown_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = 9,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 2,
        .unsafe_scope = 2,
        .reserved = 1,
    };

    try requireNoUnsafeInteropPolicy(none_policy);
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeInteropPolicy(mmio_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeInteropPolicy(raw_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeInteropPolicy(unknown_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeInteropPolicy(reserved_policy));

    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioInteropPolicy(none_policy));
    try requireVolatileMmioInteropPolicy(mmio_policy);
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioInteropPolicy(raw_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioInteropPolicy(unknown_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioInteropPolicy(reserved_policy));

    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(none_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(mmio_policy));
    try requireRawPointerBridgeInteropPolicy(raw_policy);
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(unknown_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(reserved_policy));
}
