const std = @import("std");
const abi = @import("abi_bindings");

pub const AccessBoundary = enum {
    typed_safe,
    volatile_mmio_window,
    raw_pointer_bridge,
};

pub const UnsafeScopeError = error{UnsafeScopeDenied};

pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.UnsafeScope {
    if (reserved != 0) return null;
    return switch (mode) {
        @intFromEnum(abi.UnsafeScope.none) => .none,
        @intFromEnum(abi.UnsafeScope.volatile_mmio) => .volatile_mmio,
        @intFromEnum(abi.UnsafeScope.raw_pointer_bridge) => .raw_pointer_bridge,
        else => null,
    };
}

pub fn modeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.UnsafeScope {
    return modeFromInteropPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn modeFromByte(mode: u8) ?abi.UnsafeScope {
    return modeFromInteropPolicyBytes(mode, 0);
}

pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {
    return modeFromInteropPolicyBytes(scope, reserved);
}

pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.UnsafeScope {
    return modeFromInteropPolicy(policy);
}

pub fn scopeFromByte(scope: u8) ?abi.UnsafeScope {
    return modeFromByte(scope);
}

pub fn recognizesInteropPolicyBytes(mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(mode, reserved) != null;
}

pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {
    return modeFromInteropPolicy(policy) != null;
}

pub fn recognizesByte(mode: u8) bool {
    return recognizesInteropPolicyBytes(mode, 0);
}

pub fn accessBoundaryFor(mode: abi.UnsafeScope) AccessBoundary {
    return switch (mode) {
        .none => .typed_safe,
        .volatile_mmio => .volatile_mmio_window,
        .raw_pointer_bridge => .raw_pointer_bridge,
    };
}

pub fn accessBoundaryFromInteropPolicyBytes(scope: u8, reserved: u8) ?AccessBoundary {
    return accessBoundaryFor(scopeFromInteropPolicyBytes(scope, reserved) orelse return null);
}

pub fn accessBoundaryFromInteropPolicy(policy: abi.InteropPolicy) ?AccessBoundary {
    return accessBoundaryFromInteropPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn accessBoundaryFromByte(scope: u8) ?AccessBoundary {
    return accessBoundaryFromInteropPolicyBytes(scope, 0);
}

pub fn allowsTypedOnlyAccess(mode: abi.UnsafeScope) bool {
    return accessBoundaryFor(mode) == .typed_safe;
}

pub fn permitsNoUnsafe(mode: abi.UnsafeScope) bool {
    return allowsTypedOnlyAccess(mode);
}

pub fn requireNoUnsafe(mode: abi.UnsafeScope) UnsafeScopeError!void {
    if (!permitsNoUnsafe(mode)) return error.UnsafeScopeDenied;
}

pub fn isUnsafe(mode: abi.UnsafeScope) bool {
    return !allowsTypedOnlyAccess(mode);
}

pub fn isUnsafePolicyBytes(scope: u8, reserved: u8) bool {
    return isUnsafe(modeFromInteropPolicyBytes(scope, reserved) orelse return false);
}

pub fn isUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {
    return isUnsafePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn isUnsafeByte(scope: u8) bool {
    return isUnsafePolicyBytes(scope, 0);
}

pub fn requiresDedicatedAudit(mode: abi.UnsafeScope) bool {
    return isUnsafe(mode);
}

pub fn requiresVolatileMmioAccess(mode: abi.UnsafeScope) bool {
    return accessBoundaryFor(mode) == .volatile_mmio_window;
}

pub fn permitsVolatileMmio(mode: abi.UnsafeScope) bool {
    return requiresVolatileMmioAccess(mode);
}

pub fn requireVolatileMmio(mode: abi.UnsafeScope) UnsafeScopeError!void {
    if (!permitsVolatileMmio(mode)) return error.UnsafeScopeDenied;
}

pub fn requiresRawPointerBridge(mode: abi.UnsafeScope) bool {
    return accessBoundaryFor(mode) == .raw_pointer_bridge;
}

pub fn permitsRawPointerBridge(mode: abi.UnsafeScope) bool {
    return requiresRawPointerBridge(mode);
}

pub fn requireRawPointerBridge(mode: abi.UnsafeScope) UnsafeScopeError!void {
    if (!permitsRawPointerBridge(mode)) return error.UnsafeScopeDenied;
}

pub fn allowsTypedOnlyAccessPolicyBytes(mode: u8, reserved: u8) bool {
    return allowsTypedOnlyAccess(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn allowsTypedOnlyAccessInteropPolicy(policy: abi.InteropPolicy) bool {
    return allowsTypedOnlyAccessPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn allowsTypedOnlyAccessByte(mode: u8) bool {
    return allowsTypedOnlyAccessPolicyBytes(mode, 0);
}

pub fn permitsNoUnsafePolicyBytes(scope: u8, reserved: u8) bool {
    return allowsTypedOnlyAccessPolicyBytes(scope, reserved);
}

pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {
    return allowsTypedOnlyAccessInteropPolicy(policy);
}

pub fn permitsNoUnsafeByte(scope: u8) bool {
    return allowsTypedOnlyAccessByte(scope);
}

pub fn requireNoUnsafePolicyBytes(scope: u8, reserved: u8) UnsafeScopeError!void {
    return requireNoUnsafe(modeFromInteropPolicyBytes(scope, reserved) orelse return error.UnsafeScopeDenied);
}

pub fn requireNoUnsafeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return requireNoUnsafePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireNoUnsafeByte(scope: u8) UnsafeScopeError!void {
    return requireNoUnsafePolicyBytes(scope, 0);
}

pub fn requiresDedicatedAuditPolicyBytes(scope: u8, reserved: u8) bool {
    return requiresDedicatedAudit(modeFromInteropPolicyBytes(scope, reserved) orelse return false);
}

pub fn requiresDedicatedAuditInteropPolicy(policy: abi.InteropPolicy) bool {
    return requiresDedicatedAuditPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requiresDedicatedAuditByte(scope: u8) bool {
    return requiresDedicatedAuditPolicyBytes(scope, 0);
}

pub fn requiresVolatileMmioAccessPolicyBytes(mode: u8, reserved: u8) bool {
    return requiresVolatileMmioAccess(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn requiresVolatileMmioAccessInteropPolicy(policy: abi.InteropPolicy) bool {
    return requiresVolatileMmioAccessPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requiresVolatileMmioAccessByte(mode: u8) bool {
    return requiresVolatileMmioAccessPolicyBytes(mode, 0);
}

pub fn permitsVolatileMmioPolicyBytes(scope: u8, reserved: u8) bool {
    return requiresVolatileMmioAccessPolicyBytes(scope, reserved);
}

pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {
    return requiresVolatileMmioAccessInteropPolicy(policy);
}

pub fn permitsVolatileMmioByte(scope: u8) bool {
    return requiresVolatileMmioAccessByte(scope);
}

pub fn requireVolatileMmioPolicyBytes(scope: u8, reserved: u8) UnsafeScopeError!void {
    return requireVolatileMmio(modeFromInteropPolicyBytes(scope, reserved) orelse return error.UnsafeScopeDenied);
}

pub fn requireVolatileMmioInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return requireVolatileMmioPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireVolatileMmioByte(scope: u8) UnsafeScopeError!void {
    return requireVolatileMmioPolicyBytes(scope, 0);
}

pub fn requiresRawPointerBridgePolicyBytes(mode: u8, reserved: u8) bool {
    return requiresRawPointerBridge(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn requiresRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {
    return requiresRawPointerBridgePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requiresRawPointerBridgeByte(mode: u8) bool {
    return requiresRawPointerBridgePolicyBytes(mode, 0);
}

pub fn permitsRawPointerBridgePolicyBytes(scope: u8, reserved: u8) bool {
    return requiresRawPointerBridgePolicyBytes(scope, reserved);
}

pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {
    return requiresRawPointerBridgeInteropPolicy(policy);
}

pub fn permitsRawPointerBridgeByte(scope: u8) bool {
    return requiresRawPointerBridgeByte(scope);
}

pub fn requireRawPointerBridgePolicyBytes(scope: u8, reserved: u8) UnsafeScopeError!void {
    return requireRawPointerBridge(modeFromInteropPolicyBytes(scope, reserved) orelse return error.UnsafeScopeDenied);
}

pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return requireRawPointerBridgePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireRawPointerBridgeByte(scope: u8) UnsafeScopeError!void {
    return requireRawPointerBridgePolicyBytes(scope, 0);
}

test "phase3 unsafe policy keeps access boundaries explicit" {
    try std.testing.expectEqual(AccessBoundary.typed_safe, accessBoundaryFor(.none));
    try std.testing.expectEqual(AccessBoundary.volatile_mmio_window, accessBoundaryFor(.volatile_mmio));
    try std.testing.expectEqual(AccessBoundary.raw_pointer_bridge, accessBoundaryFor(.raw_pointer_bridge));

    try std.testing.expect(allowsTypedOnlyAccess(.none));
    try std.testing.expect(permitsNoUnsafe(.none));
    try requireNoUnsafe(.none);
    try std.testing.expect(!allowsTypedOnlyAccess(.volatile_mmio));
    try std.testing.expect(!permitsNoUnsafe(.volatile_mmio));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafe(.volatile_mmio));
    try std.testing.expect(!allowsTypedOnlyAccess(.raw_pointer_bridge));
    try std.testing.expect(!permitsNoUnsafe(.raw_pointer_bridge));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafe(.raw_pointer_bridge));

    try std.testing.expect(!isUnsafe(.none));
    try std.testing.expect(!requiresDedicatedAudit(.none));
    try std.testing.expect(isUnsafe(.volatile_mmio));
    try std.testing.expect(requiresDedicatedAudit(.volatile_mmio));
    try std.testing.expect(isUnsafe(.raw_pointer_bridge));
    try std.testing.expect(requiresDedicatedAudit(.raw_pointer_bridge));

    try std.testing.expect(!requiresVolatileMmioAccess(.none));
    try std.testing.expect(!permitsVolatileMmio(.none));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmio(.none));
    try std.testing.expect(requiresVolatileMmioAccess(.volatile_mmio));
    try std.testing.expect(permitsVolatileMmio(.volatile_mmio));
    try requireVolatileMmio(.volatile_mmio);
    try std.testing.expect(!requiresVolatileMmioAccess(.raw_pointer_bridge));
    try std.testing.expect(!permitsVolatileMmio(.raw_pointer_bridge));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmio(.raw_pointer_bridge));

    try std.testing.expect(!requiresRawPointerBridge(.none));
    try std.testing.expect(!permitsRawPointerBridge(.none));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridge(.none));
    try std.testing.expect(!requiresRawPointerBridge(.volatile_mmio));
    try std.testing.expect(!permitsRawPointerBridge(.volatile_mmio));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridge(.volatile_mmio));
    try std.testing.expect(requiresRawPointerBridge(.raw_pointer_bridge));
    try std.testing.expect(permitsRawPointerBridge(.raw_pointer_bridge));
    try requireRawPointerBridge(.raw_pointer_bridge);
}

test "phase3 unsafe policy stays explicit" {
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), modeFromByte(9));

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), scopeFromByte(0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), scopeFromByte(1));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), scopeFromByte(2));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), scopeFromByte(9));

    try std.testing.expectEqual(@as(?AccessBoundary, .typed_safe), accessBoundaryFromByte(0));
    try std.testing.expectEqual(@as(?AccessBoundary, .volatile_mmio_window), accessBoundaryFromByte(1));
    try std.testing.expectEqual(@as(?AccessBoundary, .raw_pointer_bridge), accessBoundaryFromByte(2));
    try std.testing.expectEqual(@as(?AccessBoundary, null), accessBoundaryFromByte(9));

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), modeFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), modeFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), modeFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), modeFromInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), modeFromInteropPolicyBytes(2, 1));

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), scopeFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), scopeFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), scopeFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), scopeFromInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), scopeFromInteropPolicyBytes(2, 1));

    try std.testing.expectEqual(@as(?AccessBoundary, .typed_safe), accessBoundaryFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?AccessBoundary, .volatile_mmio_window), accessBoundaryFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?AccessBoundary, .raw_pointer_bridge), accessBoundaryFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?AccessBoundary, null), accessBoundaryFromInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?AccessBoundary, null), accessBoundaryFromInteropPolicyBytes(2, 1));

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

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), modeFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), modeFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), modeFromInteropPolicy(raw_pointer_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), modeFromInteropPolicy(unknown_policy));

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), scopeFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), scopeFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), scopeFromInteropPolicy(raw_pointer_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), scopeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), scopeFromInteropPolicy(unknown_policy));

    try std.testing.expectEqual(@as(?AccessBoundary, .typed_safe), accessBoundaryFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?AccessBoundary, .volatile_mmio_window), accessBoundaryFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?AccessBoundary, .raw_pointer_bridge), accessBoundaryFromInteropPolicy(raw_pointer_policy));
    try std.testing.expectEqual(@as(?AccessBoundary, null), accessBoundaryFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?AccessBoundary, null), accessBoundaryFromInteropPolicy(unknown_policy));

    try std.testing.expect(recognizesInteropPolicy(safe_policy));
    try std.testing.expect(recognizesInteropPolicy(mmio_policy));
    try std.testing.expect(recognizesInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!recognizesInteropPolicy(reserved_policy));
    try std.testing.expect(!recognizesInteropPolicy(unknown_policy));

    try std.testing.expect(allowsTypedOnlyAccessByte(0));
    try std.testing.expect(permitsNoUnsafeByte(0));
    try std.testing.expect(!isUnsafeByte(0));
    try std.testing.expect(!isUnsafe(modeFromByte(0).?));
    try std.testing.expect(!requiresDedicatedAuditByte(0));
    try requireNoUnsafeByte(0);
    try std.testing.expect(!allowsTypedOnlyAccessByte(1));
    try std.testing.expect(!permitsNoUnsafeByte(1));
    try std.testing.expect(isUnsafeByte(1));
    try std.testing.expect(isUnsafe(modeFromByte(1).?));
    try std.testing.expect(requiresDedicatedAuditByte(1));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeByte(1));
    try std.testing.expect(!allowsTypedOnlyAccessByte(2));
    try std.testing.expect(!permitsNoUnsafeByte(2));
    try std.testing.expect(isUnsafeByte(2));
    try std.testing.expect(isUnsafe(modeFromByte(2).?));
    try std.testing.expect(requiresDedicatedAuditByte(2));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeByte(2));
    try std.testing.expect(!allowsTypedOnlyAccessByte(9));
    try std.testing.expect(!permitsNoUnsafeByte(9));
    try std.testing.expect(!isUnsafeByte(9));
    try std.testing.expect(!requiresDedicatedAuditByte(9));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeByte(9));
    try std.testing.expect(allowsTypedOnlyAccessPolicyBytes(0, 0));
    try std.testing.expect(permitsNoUnsafePolicyBytes(0, 0));
    try std.testing.expect(!isUnsafePolicyBytes(0, 0));
    try std.testing.expect(!requiresDedicatedAuditPolicyBytes(0, 0));
    try requireNoUnsafePolicyBytes(0, 0);
    try std.testing.expect(!allowsTypedOnlyAccessPolicyBytes(1, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(1, 0));
    try std.testing.expect(isUnsafePolicyBytes(1, 0));
    try std.testing.expect(requiresDedicatedAuditPolicyBytes(1, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafePolicyBytes(1, 0));
    try std.testing.expect(!allowsTypedOnlyAccessPolicyBytes(2, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(2, 0));
    try std.testing.expect(isUnsafePolicyBytes(2, 0));
    try std.testing.expect(requiresDedicatedAuditPolicyBytes(2, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafePolicyBytes(2, 0));
    try std.testing.expect(!allowsTypedOnlyAccessPolicyBytes(2, 1));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(2, 1));
    try std.testing.expect(!isUnsafePolicyBytes(2, 1));
    try std.testing.expect(!requiresDedicatedAuditPolicyBytes(2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafePolicyBytes(2, 1));
    try std.testing.expect(allowsTypedOnlyAccessInteropPolicy(safe_policy));
    try std.testing.expect(permitsNoUnsafeInteropPolicy(safe_policy));
    try std.testing.expect(!isUnsafeInteropPolicy(safe_policy));
    try std.testing.expect(!requiresDedicatedAuditInteropPolicy(safe_policy));
    try requireNoUnsafeInteropPolicy(safe_policy);
    try std.testing.expect(!allowsTypedOnlyAccessInteropPolicy(mmio_policy));
    try std.testing.expect(!permitsNoUnsafeInteropPolicy(mmio_policy));
    try std.testing.expect(isUnsafeInteropPolicy(mmio_policy));
    try std.testing.expect(requiresDedicatedAuditInteropPolicy(mmio_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeInteropPolicy(mmio_policy));
    try std.testing.expect(!allowsTypedOnlyAccessInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!permitsNoUnsafeInteropPolicy(raw_pointer_policy));
    try std.testing.expect(isUnsafeInteropPolicy(raw_pointer_policy));
    try std.testing.expect(requiresDedicatedAuditInteropPolicy(raw_pointer_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!allowsTypedOnlyAccessInteropPolicy(reserved_policy));
    try std.testing.expect(!permitsNoUnsafeInteropPolicy(reserved_policy));
    try std.testing.expect(!isUnsafeInteropPolicy(reserved_policy));
    try std.testing.expect(!requiresDedicatedAuditInteropPolicy(reserved_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeInteropPolicy(reserved_policy));
    try std.testing.expect(!allowsTypedOnlyAccessInteropPolicy(unknown_policy));
    try std.testing.expect(!permitsNoUnsafeInteropPolicy(unknown_policy));
    try std.testing.expect(!isUnsafeInteropPolicy(unknown_policy));
    try std.testing.expect(!requiresDedicatedAuditInteropPolicy(unknown_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeInteropPolicy(unknown_policy));

    try std.testing.expect(!requiresVolatileMmioAccessByte(0));
    try std.testing.expect(!permitsVolatileMmioByte(0));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioByte(0));
    try std.testing.expect(requiresVolatileMmioAccessByte(1));
    try std.testing.expect(permitsVolatileMmioByte(1));
    try requireVolatileMmioByte(1);
    try std.testing.expect(!requiresVolatileMmioAccessByte(2));
    try std.testing.expect(!permitsVolatileMmioByte(2));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioByte(2));
    try std.testing.expect(!requiresVolatileMmioAccessByte(9));
    try std.testing.expect(!permitsVolatileMmioByte(9));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioByte(9));
    try std.testing.expect(!requiresVolatileMmioAccessPolicyBytes(0, 0));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(0, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioPolicyBytes(0, 0));
    try std.testing.expect(requiresVolatileMmioAccessPolicyBytes(1, 0));
    try std.testing.expect(permitsVolatileMmioPolicyBytes(1, 0));
    try requireVolatileMmioPolicyBytes(1, 0);
    try std.testing.expect(!requiresVolatileMmioAccessPolicyBytes(2, 0));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(2, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioPolicyBytes(2, 0));
    try std.testing.expect(!requiresVolatileMmioAccessPolicyBytes(2, 1));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioPolicyBytes(2, 1));
    try std.testing.expect(!requiresVolatileMmioAccessInteropPolicy(safe_policy));
    try std.testing.expect(!permitsVolatileMmioInteropPolicy(safe_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioInteropPolicy(safe_policy));
    try std.testing.expect(requiresVolatileMmioAccessInteropPolicy(mmio_policy));
    try std.testing.expect(permitsVolatileMmioInteropPolicy(mmio_policy));
    try requireVolatileMmioInteropPolicy(mmio_policy);
    try std.testing.expect(!requiresVolatileMmioAccessInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!permitsVolatileMmioInteropPolicy(raw_pointer_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!requiresVolatileMmioAccessInteropPolicy(reserved_policy));
    try std.testing.expect(!permitsVolatileMmioInteropPolicy(reserved_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioInteropPolicy(reserved_policy));
    try std.testing.expect(!requiresVolatileMmioAccessInteropPolicy(unknown_policy));
    try std.testing.expect(!permitsVolatileMmioInteropPolicy(unknown_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioInteropPolicy(unknown_policy));

    try std.testing.expect(!requiresRawPointerBridgeByte(0));
    try std.testing.expect(!permitsRawPointerBridgeByte(0));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeByte(0));
    try std.testing.expect(!requiresRawPointerBridgeByte(1));
    try std.testing.expect(!permitsRawPointerBridgeByte(1));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeByte(1));
    try std.testing.expect(requiresRawPointerBridgeByte(2));
    try std.testing.expect(permitsRawPointerBridgeByte(2));
    try requireRawPointerBridgeByte(2);
    try std.testing.expect(!requiresRawPointerBridgeByte(9));
    try std.testing.expect(!permitsRawPointerBridgeByte(9));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeByte(9));
    try std.testing.expect(!requiresRawPointerBridgePolicyBytes(0, 0));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(0, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgePolicyBytes(0, 0));
    try std.testing.expect(!requiresRawPointerBridgePolicyBytes(1, 0));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(1, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgePolicyBytes(1, 0));
    try std.testing.expect(requiresRawPointerBridgePolicyBytes(2, 0));
    try std.testing.expect(permitsRawPointerBridgePolicyBytes(2, 0));
    try requireRawPointerBridgePolicyBytes(2, 0);
    try std.testing.expect(!requiresRawPointerBridgePolicyBytes(2, 1));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgePolicyBytes(2, 1));
    try std.testing.expect(!requiresRawPointerBridgeInteropPolicy(safe_policy));
    try std.testing.expect(!permitsRawPointerBridgeInteropPolicy(safe_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(safe_policy));
    try std.testing.expect(!requiresRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expect(!permitsRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expect(requiresRawPointerBridgeInteropPolicy(raw_pointer_policy));
    try std.testing.expect(permitsRawPointerBridgeInteropPolicy(raw_pointer_policy));
    try requireRawPointerBridgeInteropPolicy(raw_pointer_policy);
    try std.testing.expect(!requiresRawPointerBridgeInteropPolicy(reserved_policy));
    try std.testing.expect(!permitsRawPointerBridgeInteropPolicy(reserved_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(reserved_policy));
    try std.testing.expect(!requiresRawPointerBridgeInteropPolicy(unknown_policy));
    try std.testing.expect(!permitsRawPointerBridgeInteropPolicy(unknown_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(unknown_policy));
}
