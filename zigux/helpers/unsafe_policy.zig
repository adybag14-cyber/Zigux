const std = @import("std");
const abi = @import("abi_bindings");

pub const AccessBoundary = enum {
    typed_safe,
    volatile_mmio_window,
    raw_pointer_bridge,
};

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

pub fn allowsTypedOnlyAccess(mode: abi.UnsafeScope) bool {
    return accessBoundaryFor(mode) == .typed_safe;
}

pub fn requiresVolatileMmioAccess(mode: abi.UnsafeScope) bool {
    return accessBoundaryFor(mode) == .volatile_mmio_window;
}

pub fn requiresRawPointerBridge(mode: abi.UnsafeScope) bool {
    return accessBoundaryFor(mode) == .raw_pointer_bridge;
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

pub fn requiresVolatileMmioAccessPolicyBytes(mode: u8, reserved: u8) bool {
    return requiresVolatileMmioAccess(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn requiresVolatileMmioAccessInteropPolicy(policy: abi.InteropPolicy) bool {
    return requiresVolatileMmioAccessPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requiresVolatileMmioAccessByte(mode: u8) bool {
    return requiresVolatileMmioAccessPolicyBytes(mode, 0);
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

test "phase3 unsafe policy keeps access boundaries explicit" {
    try std.testing.expectEqual(AccessBoundary.typed_safe, accessBoundaryFor(.none));
    try std.testing.expectEqual(AccessBoundary.volatile_mmio_window, accessBoundaryFor(.volatile_mmio));
    try std.testing.expectEqual(AccessBoundary.raw_pointer_bridge, accessBoundaryFor(.raw_pointer_bridge));

    try std.testing.expect(allowsTypedOnlyAccess(.none));
    try std.testing.expect(!allowsTypedOnlyAccess(.volatile_mmio));
    try std.testing.expect(!allowsTypedOnlyAccess(.raw_pointer_bridge));

    try std.testing.expect(!requiresVolatileMmioAccess(.none));
    try std.testing.expect(requiresVolatileMmioAccess(.volatile_mmio));
    try std.testing.expect(!requiresVolatileMmioAccess(.raw_pointer_bridge));

    try std.testing.expect(!requiresRawPointerBridge(.none));
    try std.testing.expect(!requiresRawPointerBridge(.volatile_mmio));
    try std.testing.expect(requiresRawPointerBridge(.raw_pointer_bridge));
}

test "phase3 unsafe policy stays explicit" {
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), modeFromByte(9));

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), modeFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), modeFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), modeFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), modeFromInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), modeFromInteropPolicyBytes(2, 1));

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

    try std.testing.expect(recognizesInteropPolicy(safe_policy));
    try std.testing.expect(recognizesInteropPolicy(mmio_policy));
    try std.testing.expect(recognizesInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!recognizesInteropPolicy(reserved_policy));
    try std.testing.expect(!recognizesInteropPolicy(unknown_policy));

    try std.testing.expect(allowsTypedOnlyAccessByte(0));
    try std.testing.expect(!allowsTypedOnlyAccessByte(1));
    try std.testing.expect(!allowsTypedOnlyAccessByte(2));
    try std.testing.expect(!allowsTypedOnlyAccessByte(9));
    try std.testing.expect(allowsTypedOnlyAccessPolicyBytes(0, 0));
    try std.testing.expect(!allowsTypedOnlyAccessPolicyBytes(1, 0));
    try std.testing.expect(!allowsTypedOnlyAccessPolicyBytes(2, 0));
    try std.testing.expect(!allowsTypedOnlyAccessPolicyBytes(2, 1));
    try std.testing.expect(allowsTypedOnlyAccessInteropPolicy(safe_policy));
    try std.testing.expect(!allowsTypedOnlyAccessInteropPolicy(mmio_policy));
    try std.testing.expect(!allowsTypedOnlyAccessInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!allowsTypedOnlyAccessInteropPolicy(reserved_policy));
    try std.testing.expect(!allowsTypedOnlyAccessInteropPolicy(unknown_policy));

    try std.testing.expect(!requiresVolatileMmioAccessByte(0));
    try std.testing.expect(requiresVolatileMmioAccessByte(1));
    try std.testing.expect(!requiresVolatileMmioAccessByte(2));
    try std.testing.expect(!requiresVolatileMmioAccessByte(9));
    try std.testing.expect(!requiresVolatileMmioAccessPolicyBytes(0, 0));
    try std.testing.expect(requiresVolatileMmioAccessPolicyBytes(1, 0));
    try std.testing.expect(!requiresVolatileMmioAccessPolicyBytes(2, 0));
    try std.testing.expect(!requiresVolatileMmioAccessPolicyBytes(2, 1));
    try std.testing.expect(!requiresVolatileMmioAccessInteropPolicy(safe_policy));
    try std.testing.expect(requiresVolatileMmioAccessInteropPolicy(mmio_policy));
    try std.testing.expect(!requiresVolatileMmioAccessInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!requiresVolatileMmioAccessInteropPolicy(reserved_policy));
    try std.testing.expect(!requiresVolatileMmioAccessInteropPolicy(unknown_policy));

    try std.testing.expect(!requiresRawPointerBridgeByte(0));
    try std.testing.expect(!requiresRawPointerBridgeByte(1));
    try std.testing.expect(requiresRawPointerBridgeByte(2));
    try std.testing.expect(!requiresRawPointerBridgeByte(9));
    try std.testing.expect(!requiresRawPointerBridgePolicyBytes(0, 0));
    try std.testing.expect(!requiresRawPointerBridgePolicyBytes(1, 0));
    try std.testing.expect(requiresRawPointerBridgePolicyBytes(2, 0));
    try std.testing.expect(!requiresRawPointerBridgePolicyBytes(2, 1));
    try std.testing.expect(!requiresRawPointerBridgeInteropPolicy(safe_policy));
    try std.testing.expect(!requiresRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expect(requiresRawPointerBridgeInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!requiresRawPointerBridgeInteropPolicy(reserved_policy));
    try std.testing.expect(!requiresRawPointerBridgeInteropPolicy(unknown_policy));
}
