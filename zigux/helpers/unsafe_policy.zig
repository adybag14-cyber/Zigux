const std = @import("std");
const abi = @import("abi_bindings");
const narrow = @import("narrow");

pub const AccessBoundary = enum {
    typed_safe,
    volatile_mmio_window,
    raw_pointer_bridge,
};

pub const Surface = narrow.Surface;
pub const UnsafeScopeError = narrow.UnsafeScopeError;

fn fromNarrowAccessBoundary(boundary: narrow.AccessBoundary) AccessBoundary {
    return switch (boundary) {
        .typed_safe => .typed_safe,
        .volatile_mmio_window => .volatile_mmio_window,
        .raw_pointer_bridge => .raw_pointer_bridge,
    };
}

pub fn modeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {
    return scopeFromInteropPolicyBytes(scope, reserved);
}

pub fn modeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.UnsafeScope {
    return scopeFromInteropPolicy(policy);
}

pub fn modeFromByte(scope: u8) ?abi.UnsafeScope {
    return scopeFromByte(scope);
}

pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {
    return narrow.scopeFromInteropPolicyBytes(scope, reserved);
}

pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.UnsafeScope {
    return narrow.scopeFromInteropPolicy(policy);
}

pub fn scopeFromByte(scope: u8) ?abi.UnsafeScope {
    return narrow.scopeFromByte(scope);
}

pub fn recognizesInteropPolicyBytes(scope: u8, reserved: u8) bool {
    return narrow.recognizesInteropPolicyBytes(scope, reserved);
}

pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.recognizesInteropPolicy(policy);
}

pub fn recognizesByte(scope: u8) bool {
    return narrow.recognizesByte(scope);
}

pub fn accessBoundaryFor(scope: abi.UnsafeScope) AccessBoundary {
    return fromNarrowAccessBoundary(narrow.accessBoundaryFor(scope));
}

pub fn accessBoundaryFromInteropPolicyBytes(scope: u8, reserved: u8) ?AccessBoundary {
    return fromNarrowAccessBoundary(
        narrow.accessBoundaryFromInteropPolicyBytes(scope, reserved) orelse return null,
    );
}

pub fn accessBoundaryFromInteropPolicy(policy: abi.InteropPolicy) ?AccessBoundary {
    return accessBoundaryFromInteropPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn accessBoundaryFromByte(scope: u8) ?AccessBoundary {
    return accessBoundaryFromInteropPolicyBytes(scope, 0);
}

pub fn allowsTypedOnlyAccess(scope: abi.UnsafeScope) bool {
    return narrow.allowsTypedOnlyAccess(scope);
}

pub fn permitsNoUnsafe(scope: abi.UnsafeScope) bool {
    return narrow.permitsNoUnsafe(scope);
}

pub fn requiresVolatileMmioAccess(scope: abi.UnsafeScope) bool {
    return narrow.permitsVolatileMmio(scope);
}

pub fn permitsVolatileMmio(scope: abi.UnsafeScope) bool {
    return narrow.permitsVolatileMmio(scope);
}

pub fn requiresRawPointerBridge(scope: abi.UnsafeScope) bool {
    return narrow.permitsRawPointerBridge(scope);
}

pub fn permitsRawPointerBridge(scope: abi.UnsafeScope) bool {
    return narrow.permitsRawPointerBridge(scope);
}

pub fn permitsNoUnsafePolicyBytes(scope: u8, reserved: u8) bool {
    return narrow.permitsNoUnsafePolicyBytes(scope, reserved);
}

pub fn permitsVolatileMmioPolicyBytes(scope: u8, reserved: u8) bool {
    return narrow.permitsVolatileMmioPolicyBytes(scope, reserved);
}

pub fn requiresVolatileMmioAccessPolicyBytes(scope: u8, reserved: u8) bool {
    return permitsVolatileMmioPolicyBytes(scope, reserved);
}

pub fn permitsRawPointerBridgePolicyBytes(scope: u8, reserved: u8) bool {
    return narrow.permitsRawPointerBridgePolicyBytes(scope, reserved);
}

pub fn requiresRawPointerBridgePolicyBytes(scope: u8, reserved: u8) bool {
    return permitsRawPointerBridgePolicyBytes(scope, reserved);
}

pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.permitsNoUnsafeInteropPolicy(policy);
}

pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.permitsVolatileMmioInteropPolicy(policy);
}

pub fn requiresVolatileMmioAccessInteropPolicy(policy: abi.InteropPolicy) bool {
    return permitsVolatileMmioInteropPolicy(policy);
}

pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.permitsRawPointerBridgeInteropPolicy(policy);
}

pub fn requiresRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {
    return permitsRawPointerBridgeInteropPolicy(policy);
}

pub fn permitsNoUnsafeByte(scope: u8) bool {
    return narrow.permitsNoUnsafeByte(scope);
}

pub fn permitsVolatileMmioByte(scope: u8) bool {
    return narrow.permitsVolatileMmioByte(scope);
}

pub fn requiresVolatileMmioAccessByte(scope: u8) bool {
    return permitsVolatileMmioByte(scope);
}

pub fn permitsRawPointerBridgeByte(scope: u8) bool {
    return narrow.permitsRawPointerBridgeByte(scope);
}

pub fn requiresRawPointerBridgeByte(scope: u8) bool {
    return permitsRawPointerBridgeByte(scope);
}

pub fn allowsTypedOnlyAccessPolicyBytes(scope: u8, reserved: u8) bool {
    return narrow.allowsTypedOnlyAccessPolicyBytes(scope, reserved);
}

pub fn allowsTypedOnlyAccessInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.allowsTypedOnlyAccessInteropPolicy(policy);
}

pub fn allowsTypedOnlyAccessByte(scope: u8) bool {
    return narrow.allowsTypedOnlyAccessByte(scope);
}

pub fn requireNoUnsafePolicyBytes(scope: u8, reserved: u8) UnsafeScopeError!void {
    return narrow.requireNoUnsafePolicyBytes(scope, reserved);
}

pub fn requireVolatileMmioPolicyBytes(scope: u8, reserved: u8) UnsafeScopeError!void {
    return narrow.requireVolatileMmioPolicyBytes(scope, reserved);
}

pub fn requireRawPointerBridgePolicyBytes(scope: u8, reserved: u8) UnsafeScopeError!void {
    return narrow.requireRawPointerBridgePolicyBytes(scope, reserved);
}

pub fn requireNoUnsafeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return narrow.requireNoUnsafeInteropPolicy(policy);
}

pub fn requireVolatileMmioInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return narrow.requireVolatileMmioInteropPolicy(policy);
}

pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return narrow.requireRawPointerBridgeInteropPolicy(policy);
}

pub fn requireNoUnsafeByte(scope: u8) UnsafeScopeError!void {
    return narrow.requireNoUnsafeByte(scope);
}

pub fn requireVolatileMmioByte(scope: u8) UnsafeScopeError!void {
    return narrow.requireVolatileMmioByte(scope);
}

pub fn requireRawPointerBridgeByte(scope: u8) UnsafeScopeError!void {
    return narrow.requireRawPointerBridgeByte(scope);
}

pub fn allowsVolatileMmio(scope: abi.UnsafeScope) bool {
    return narrow.allowsVolatileMmio(scope);
}

pub fn allowsVolatileMmioPolicyBytes(scope: u8, reserved: u8) bool {
    return narrow.allowsVolatileMmioPolicyBytes(scope, reserved);
}

pub fn allowsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.allowsVolatileMmioInteropPolicy(policy);
}

pub fn allowsVolatileMmioByte(scope: u8) bool {
    return narrow.allowsVolatileMmioByte(scope);
}

pub fn allowsRawPointerBridge(scope: abi.UnsafeScope) bool {
    return narrow.allowsRawPointerBridge(scope);
}

pub fn allowsRawPointerBridgePolicyBytes(scope: u8, reserved: u8) bool {
    return narrow.allowsRawPointerBridgePolicyBytes(scope, reserved);
}

pub fn allowsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.allowsRawPointerBridgeInteropPolicy(policy);
}

pub fn allowsRawPointerBridgeByte(scope: u8) bool {
    return narrow.allowsRawPointerBridgeByte(scope);
}

pub fn isUnsafe(scope: abi.UnsafeScope) bool {
    return narrow.isUnsafe(scope);
}

pub fn isUnsafePolicyBytes(scope: u8, reserved: u8) bool {
    return narrow.isUnsafePolicyBytes(scope, reserved);
}

pub fn isUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.isUnsafeInteropPolicy(policy);
}

pub fn isUnsafeByte(scope: u8) bool {
    return narrow.isUnsafeByte(scope);
}

pub fn surfaceFor(scope: abi.UnsafeScope) Surface {
    return narrow.surfaceFor(scope);
}

pub fn surfaceFromInteropPolicyBytes(scope: u8, reserved: u8) ?Surface {
    return narrow.surfaceFromInteropPolicyBytes(scope, reserved);
}

pub fn surfaceFromInteropPolicy(policy: abi.InteropPolicy) ?Surface {
    return narrow.surfaceFromInteropPolicy(policy);
}

pub fn surfaceFromByte(scope: u8) ?Surface {
    return narrow.surfaceFromByte(scope);
}

pub fn requiresDedicatedAudit(scope: abi.UnsafeScope) bool {
    return narrow.requiresDedicatedAudit(scope);
}

pub fn requiresDedicatedAuditPolicyBytes(scope: u8, reserved: u8) bool {
    return narrow.requiresDedicatedAuditPolicyBytes(scope, reserved);
}

pub fn requiresDedicatedAuditInteropPolicy(policy: abi.InteropPolicy) bool {
    return narrow.requiresDedicatedAuditInteropPolicy(policy);
}

pub fn requiresDedicatedAuditByte(scope: u8) bool {
    return narrow.requiresDedicatedAuditByte(scope);
}

test "phase3 unsafe policy keeps scope decoding and boundary relays explicit" {
    const safe = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 };
    const mmio = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 1, .reserved = 0 };
    const raw = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 2, .reserved = 0 };
    const reserved = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 2, .reserved = 1 };

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), modeFromInteropPolicy(safe));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), modeFromInteropPolicy(mmio));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), modeFromInteropPolicy(raw));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), modeFromInteropPolicy(reserved));

    try std.testing.expectEqual(@as(?AccessBoundary, .typed_safe), accessBoundaryFromInteropPolicy(safe));
    try std.testing.expectEqual(@as(?AccessBoundary, .volatile_mmio_window), accessBoundaryFromInteropPolicy(mmio));
    try std.testing.expectEqual(@as(?AccessBoundary, .raw_pointer_bridge), accessBoundaryFromInteropPolicy(raw));
    try std.testing.expectEqual(@as(?AccessBoundary, null), accessBoundaryFromInteropPolicy(reserved));
    try std.testing.expectEqual(AccessBoundary.typed_safe, accessBoundaryFor(.none));
    try std.testing.expectEqual(AccessBoundary.volatile_mmio_window, accessBoundaryFor(.volatile_mmio));
    try std.testing.expectEqual(AccessBoundary.raw_pointer_bridge, accessBoundaryFor(.raw_pointer_bridge));
}

test "phase3 unsafe policy keeps allow, permit, and require helpers aligned" {
    const safe = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 };
    const mmio = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 1, .reserved = 0 };
    const raw = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 2, .reserved = 0 };
    const reserved = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 2, .reserved = 1 };

    try std.testing.expect(allowsTypedOnlyAccess(.none));
    try std.testing.expect(permitsNoUnsafeInteropPolicy(safe));
    try requireNoUnsafeInteropPolicy(safe);
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeInteropPolicy(mmio));

    try std.testing.expect(requiresVolatileMmioAccess(.volatile_mmio));
    try std.testing.expect(permitsVolatileMmioInteropPolicy(mmio));
    try std.testing.expect(allowsVolatileMmioInteropPolicy(mmio));
    try requireVolatileMmioInteropPolicy(mmio);
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioInteropPolicy(raw));

    try std.testing.expect(requiresRawPointerBridge(.raw_pointer_bridge));
    try std.testing.expect(permitsRawPointerBridgeInteropPolicy(raw));
    try std.testing.expect(allowsRawPointerBridgeInteropPolicy(raw));
    try requireRawPointerBridgeInteropPolicy(raw);
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(safe));

    try std.testing.expect(!recognizesInteropPolicy(reserved));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(1, 1));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(2, 1));
}

test "phase3 unsafe policy keeps unsafe and audit routing explicit" {
    const safe = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 };
    const mmio = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 1, .reserved = 0 };
    const raw = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 2, .reserved = 0 };

    try std.testing.expectEqual(Surface.safe_only, surfaceFor(.none));
    try std.testing.expectEqual(Surface.mmio_only, surfaceFor(.volatile_mmio));
    try std.testing.expectEqual(Surface.raw_pointer_bridge_only, surfaceFor(.raw_pointer_bridge));

    try std.testing.expect(!isUnsafeInteropPolicy(safe));
    try std.testing.expect(isUnsafeInteropPolicy(mmio));
    try std.testing.expect(isUnsafeInteropPolicy(raw));
    try std.testing.expect(!requiresDedicatedAuditInteropPolicy(safe));
    try std.testing.expect(requiresDedicatedAuditInteropPolicy(mmio));
    try std.testing.expect(requiresDedicatedAuditInteropPolicy(raw));
}
