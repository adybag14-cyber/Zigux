const std = @import("std");
const abi = @import("abi_bindings");

pub const Surface = enum {
    safe_only,
    mmio_only,
    raw_pointer_bridge_only,
};

pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {
    if (reserved != 0) return null;
    return switch (scope) {
        @intFromEnum(abi.UnsafeScope.none) => .none,
        @intFromEnum(abi.UnsafeScope.volatile_mmio) => .volatile_mmio,
        @intFromEnum(abi.UnsafeScope.raw_pointer_bridge) => .raw_pointer_bridge,
        else => null,
    };
}

pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.UnsafeScope {
    return scopeFromInteropPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn scopeFromByte(scope: u8) ?abi.UnsafeScope {
    return scopeFromInteropPolicyBytes(scope, 0);
}

pub fn recognizesInteropPolicyBytes(scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(scope, reserved) != null;
}

pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {
    return scopeFromInteropPolicy(policy) != null;
}

pub fn recognizesByte(scope: u8) bool {
    return recognizesInteropPolicyBytes(scope, 0);
}

pub fn surfaceFor(scope: abi.UnsafeScope) Surface {
    return switch (scope) {
        .none => .safe_only,
        .volatile_mmio => .mmio_only,
        .raw_pointer_bridge => .raw_pointer_bridge_only,
    };
}

pub fn isUnsafe(scope: abi.UnsafeScope) bool {
    return scope != .none;
}

pub fn allowsVolatileMmio(scope: abi.UnsafeScope) bool {
    return scope == .volatile_mmio;
}

pub fn allowsRawPointerBridge(scope: abi.UnsafeScope) bool {
    return scope == .raw_pointer_bridge;
}

pub fn requiresDedicatedAudit(scope: abi.UnsafeScope) bool {
    return isUnsafe(scope);
}

pub fn requiresDedicatedAuditPolicyBytes(scope: u8, reserved: u8) bool {
    return requiresDedicatedAudit(scopeFromInteropPolicyBytes(scope, reserved) orelse return false);
}

pub fn requiresDedicatedAuditInteropPolicy(policy: abi.InteropPolicy) bool {
    return requiresDedicatedAuditPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requiresDedicatedAuditByte(scope: u8) bool {
    return requiresDedicatedAuditPolicyBytes(scope, 0);
}

pub fn allowsVolatileMmioPolicyBytes(scope: u8, reserved: u8) bool {
    return allowsVolatileMmio(scopeFromInteropPolicyBytes(scope, reserved) orelse return false);
}

pub fn allowsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {
    return allowsVolatileMmioPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn allowsVolatileMmioByte(scope: u8) bool {
    return allowsVolatileMmioPolicyBytes(scope, 0);
}

pub fn allowsRawPointerBridgePolicyBytes(scope: u8, reserved: u8) bool {
    return allowsRawPointerBridge(scopeFromInteropPolicyBytes(scope, reserved) orelse return false);
}

pub fn allowsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {
    return allowsRawPointerBridgePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn allowsRawPointerBridgeByte(scope: u8) bool {
    return allowsRawPointerBridgePolicyBytes(scope, 0);
}

test "phase3 narrow unsafe surface keeps the capability split explicit" {
    try std.testing.expectEqual(Surface.safe_only, surfaceFor(.none));
    try std.testing.expectEqual(Surface.mmio_only, surfaceFor(.volatile_mmio));
    try std.testing.expectEqual(Surface.raw_pointer_bridge_only, surfaceFor(.raw_pointer_bridge));

    try std.testing.expect(!isUnsafe(.none));
    try std.testing.expect(isUnsafe(.volatile_mmio));
    try std.testing.expect(isUnsafe(.raw_pointer_bridge));

    try std.testing.expect(!allowsVolatileMmio(.none));
    try std.testing.expect(allowsVolatileMmio(.volatile_mmio));
    try std.testing.expect(!allowsVolatileMmio(.raw_pointer_bridge));

    try std.testing.expect(!allowsRawPointerBridge(.none));
    try std.testing.expect(!allowsRawPointerBridge(.volatile_mmio));
    try std.testing.expect(allowsRawPointerBridge(.raw_pointer_bridge));

    try std.testing.expect(!requiresDedicatedAudit(.none));
    try std.testing.expect(requiresDedicatedAudit(.volatile_mmio));
    try std.testing.expect(requiresDedicatedAudit(.raw_pointer_bridge));
}

test "phase3 narrow unsafe surface stays explicit" {
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), scopeFromByte(0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), scopeFromByte(1));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), scopeFromByte(2));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), scopeFromByte(9));

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), scopeFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), scopeFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), scopeFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), scopeFromInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), scopeFromInteropPolicyBytes(2, 1));

    try std.testing.expect(recognizesInteropPolicyBytes(0, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(1, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(2, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(9, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(2, 1));

    try std.testing.expect(recognizesByte(0));
    try std.testing.expect(recognizesByte(1));
    try std.testing.expect(recognizesByte(2));
    try std.testing.expect(!recognizesByte(9));

    const safe_policy = abi.InteropPolicy{
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
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 2,
        .unsafe_scope = 2,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = 2,
        .reserved = 1,
    };
    const unknown_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = 9,
        .reserved = 0,
    };

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), scopeFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), scopeFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), scopeFromInteropPolicy(raw_pointer_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), scopeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), scopeFromInteropPolicy(unknown_policy));

    try std.testing.expect(recognizesInteropPolicy(safe_policy));
    try std.testing.expect(recognizesInteropPolicy(mmio_policy));
    try std.testing.expect(recognizesInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!recognizesInteropPolicy(reserved_policy));
    try std.testing.expect(!recognizesInteropPolicy(unknown_policy));

    try std.testing.expect(!requiresDedicatedAuditByte(0));
    try std.testing.expect(requiresDedicatedAuditByte(1));
    try std.testing.expect(requiresDedicatedAuditByte(2));
    try std.testing.expect(!requiresDedicatedAuditByte(9));

    try std.testing.expect(!requiresDedicatedAuditPolicyBytes(0, 0));
    try std.testing.expect(requiresDedicatedAuditPolicyBytes(1, 0));
    try std.testing.expect(requiresDedicatedAuditPolicyBytes(2, 0));
    try std.testing.expect(!requiresDedicatedAuditPolicyBytes(2, 1));

    try std.testing.expect(!requiresDedicatedAuditInteropPolicy(safe_policy));
    try std.testing.expect(requiresDedicatedAuditInteropPolicy(mmio_policy));
    try std.testing.expect(requiresDedicatedAuditInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!requiresDedicatedAuditInteropPolicy(reserved_policy));
    try std.testing.expect(!requiresDedicatedAuditInteropPolicy(unknown_policy));

    try std.testing.expect(!allowsVolatileMmioByte(0));
    try std.testing.expect(allowsVolatileMmioByte(1));
    try std.testing.expect(!allowsVolatileMmioByte(2));
    try std.testing.expect(!allowsVolatileMmioByte(9));

    try std.testing.expect(!allowsVolatileMmioPolicyBytes(0, 0));
    try std.testing.expect(allowsVolatileMmioPolicyBytes(1, 0));
    try std.testing.expect(!allowsVolatileMmioPolicyBytes(2, 0));
    try std.testing.expect(!allowsVolatileMmioPolicyBytes(2, 1));

    try std.testing.expect(!allowsVolatileMmioInteropPolicy(safe_policy));
    try std.testing.expect(allowsVolatileMmioInteropPolicy(mmio_policy));
    try std.testing.expect(!allowsVolatileMmioInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!allowsVolatileMmioInteropPolicy(reserved_policy));
    try std.testing.expect(!allowsVolatileMmioInteropPolicy(unknown_policy));

    try std.testing.expect(!allowsRawPointerBridgeByte(0));
    try std.testing.expect(!allowsRawPointerBridgeByte(1));
    try std.testing.expect(allowsRawPointerBridgeByte(2));
    try std.testing.expect(!allowsRawPointerBridgeByte(9));

    try std.testing.expect(!allowsRawPointerBridgePolicyBytes(0, 0));
    try std.testing.expect(!allowsRawPointerBridgePolicyBytes(1, 0));
    try std.testing.expect(allowsRawPointerBridgePolicyBytes(2, 0));
    try std.testing.expect(!allowsRawPointerBridgePolicyBytes(2, 1));

    try std.testing.expect(!allowsRawPointerBridgeInteropPolicy(safe_policy));
    try std.testing.expect(!allowsRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expect(allowsRawPointerBridgeInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!allowsRawPointerBridgeInteropPolicy(reserved_policy));
    try std.testing.expect(!allowsRawPointerBridgeInteropPolicy(unknown_policy));
}
