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
pub const RawPointerBridgeError = narrow.RawPointerBridgeError;

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

pub fn pointerAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    byte_len: usize,
    scope: u8,
    reserved: u8,
) RawPointerBridgeError!*align(1) T {
    return narrow.pointerAtInteropPolicyBytes(T, address, byte_len, scope, reserved);
}

pub fn pointerAtInteropPolicy(
    comptime T: type,
    address: usize,
    byte_len: usize,
    policy: abi.InteropPolicy,
) RawPointerBridgeError!*align(1) T {
    return narrow.pointerAtInteropPolicy(T, address, byte_len, policy);
}

pub fn pointerAtByte(
    comptime T: type,
    address: usize,
    byte_len: usize,
    scope: u8,
) RawPointerBridgeError!*align(1) T {
    return narrow.pointerAtByte(T, address, byte_len, scope);
}

pub fn constPointerAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    scope: u8,
    reserved: u8,
) RawPointerBridgeError!*align(1) const T {
    return narrow.constPointerAtInteropPolicyBytes(T, address, scope, reserved);
}

pub fn constPointerAtInteropPolicy(
    comptime T: type,
    address: usize,
    policy: abi.InteropPolicy,
) RawPointerBridgeError!*align(1) const T {
    return narrow.constPointerAtInteropPolicy(T, address, policy);
}

pub fn constPointerAtByte(
    comptime T: type,
    address: usize,
    scope: u8,
) RawPointerBridgeError!*align(1) const T {
    return narrow.constPointerAtByte(T, address, scope);
}

pub fn sliceAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    len: usize,
    scope: u8,
    reserved: u8,
) RawPointerBridgeError![]align(1) T {
    return narrow.sliceAtInteropPolicyBytes(T, address, len, scope, reserved);
}

pub fn sliceAtInteropPolicy(
    comptime T: type,
    address: usize,
    len: usize,
    policy: abi.InteropPolicy,
) RawPointerBridgeError![]align(1) T {
    return narrow.sliceAtInteropPolicy(T, address, len, policy);
}

pub fn sliceAtByte(
    comptime T: type,
    address: usize,
    len: usize,
    scope: u8,
) RawPointerBridgeError![]align(1) T {
    return narrow.sliceAtByte(T, address, len, scope);
}

pub fn constSliceAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    len: usize,
    scope: u8,
    reserved: u8,
) RawPointerBridgeError![]align(1) const T {
    return narrow.constSliceAtInteropPolicyBytes(T, address, len, scope, reserved);
}

pub fn constSliceAtInteropPolicy(
    comptime T: type,
    address: usize,
    len: usize,
    policy: abi.InteropPolicy,
) RawPointerBridgeError![]align(1) const T {
    return narrow.constSliceAtInteropPolicy(T, address, len, policy);
}

pub fn constSliceAtByte(
    comptime T: type,
    address: usize,
    len: usize,
    scope: u8,
) RawPointerBridgeError![]align(1) const T {
    return narrow.constSliceAtByte(T, address, len, scope);
}

pub fn readValueAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    byte_len: usize,
    scope: u8,
    reserved: u8,
) RawPointerBridgeError!T {
    return narrow.readValueAtInteropPolicyBytes(T, address, byte_len, scope, reserved);
}

pub fn readValueAtInteropPolicy(
    comptime T: type,
    address: usize,
    byte_len: usize,
    policy: abi.InteropPolicy,
) RawPointerBridgeError!T {
    return narrow.readValueAtInteropPolicy(T, address, byte_len, policy);
}

pub fn readValueAtByte(
    comptime T: type,
    address: usize,
    byte_len: usize,
    scope: u8,
) RawPointerBridgeError!T {
    return narrow.readValueAtByte(T, address, byte_len, scope);
}

pub fn exchangeValueAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    byte_len: usize,
    value: T,
    scope: u8,
    reserved: u8,
) RawPointerBridgeError!T {
    return narrow.exchangeValueAtInteropPolicyBytes(T, address, byte_len, value, scope, reserved);
}

pub fn exchangeValueAtInteropPolicy(
    comptime T: type,
    address: usize,
    byte_len: usize,
    value: T,
    policy: abi.InteropPolicy,
) RawPointerBridgeError!T {
    return narrow.exchangeValueAtInteropPolicy(T, address, byte_len, value, policy);
}

pub fn exchangeValueAtByte(
    comptime T: type,
    address: usize,
    byte_len: usize,
    value: T,
    scope: u8,
) RawPointerBridgeError!T {
    return narrow.exchangeValueAtByte(T, address, byte_len, value, scope);
}

pub fn writeValueAtInteropPolicyBytes(
    comptime T: type,
    address: usize,
    value: T,
    scope: u8,
    reserved: u8,
) RawPointerBridgeError!void {
    return narrow.writeValueAtInteropPolicyBytes(T, address, value, scope, reserved);
}

pub fn writeValueAtInteropPolicy(
    comptime T: type,
    address: usize,
    value: T,
    policy: abi.InteropPolicy,
) RawPointerBridgeError!void {
    return narrow.writeValueAtInteropPolicy(T, address, value, policy);
}

pub fn writeValueAtByte(
    comptime T: type,
    address: usize,
    value: T,
    scope: u8,
) RawPointerBridgeError!void {
    return narrow.writeValueAtByte(T, address, value, scope);
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

test "phase3 unsafe policy keeps byte and reserved shorthands aligned with helper aliases" {
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), modeFromByte(9));
    try std.testing.expectEqual(@as(?abi.UnsafeScope, null), modeFromInteropPolicyBytes(2, 1));

    try std.testing.expect(recognizesByte(0));
    try std.testing.expect(recognizesByte(1));
    try std.testing.expect(recognizesByte(2));
    try std.testing.expect(!recognizesByte(9));
    try std.testing.expect(!recognizesInteropPolicyBytes(2, 1));

    try std.testing.expectEqual(@as(?Surface, .safe_only), surfaceFromByte(0));
    try std.testing.expectEqual(@as(?Surface, .mmio_only), surfaceFromByte(1));
    try std.testing.expectEqual(@as(?Surface, .raw_pointer_bridge_only), surfaceFromByte(2));
    try std.testing.expectEqual(@as(?Surface, null), surfaceFromByte(9));
    try std.testing.expectEqual(@as(?Surface, null), surfaceFromInteropPolicyBytes(2, 1));

    try std.testing.expectEqual(@as(?AccessBoundary, .typed_safe), accessBoundaryFromByte(0));
    try std.testing.expectEqual(@as(?AccessBoundary, .volatile_mmio_window), accessBoundaryFromByte(1));
    try std.testing.expectEqual(@as(?AccessBoundary, .raw_pointer_bridge), accessBoundaryFromByte(2));
    try std.testing.expectEqual(@as(?AccessBoundary, null), accessBoundaryFromInteropPolicyBytes(2, 1));

    try std.testing.expect(permitsNoUnsafeByte(0));
    try std.testing.expect(!permitsNoUnsafeByte(1));
    try std.testing.expect(permitsVolatileMmioByte(1));
    try std.testing.expect(!permitsVolatileMmioByte(2));
    try std.testing.expect(permitsRawPointerBridgeByte(2));
    try std.testing.expect(!permitsRawPointerBridgeByte(1));

    try std.testing.expect(permitsNoUnsafePolicyBytes(0, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(0, 1));
    try std.testing.expect(permitsVolatileMmioPolicyBytes(1, 0));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(1, 1));
    try std.testing.expect(requiresVolatileMmioAccessPolicyBytes(1, 0));
    try std.testing.expect(!requiresVolatileMmioAccessPolicyBytes(1, 1));
    try std.testing.expect(permitsRawPointerBridgePolicyBytes(2, 0));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(2, 1));
    try std.testing.expect(requiresRawPointerBridgePolicyBytes(2, 0));
    try std.testing.expect(!requiresRawPointerBridgePolicyBytes(2, 1));

    try std.testing.expect(allowsTypedOnlyAccessByte(0));
    try std.testing.expect(!allowsTypedOnlyAccessByte(1));
    try std.testing.expect(allowsTypedOnlyAccessPolicyBytes(0, 0));
    try std.testing.expect(!allowsTypedOnlyAccessPolicyBytes(0, 1));
    try std.testing.expect(allowsVolatileMmioByte(1));
    try std.testing.expect(!allowsVolatileMmioByte(2));
    try std.testing.expect(allowsVolatileMmioPolicyBytes(1, 0));
    try std.testing.expect(!allowsVolatileMmioPolicyBytes(1, 1));
    try std.testing.expect(allowsRawPointerBridgeByte(2));
    try std.testing.expect(!allowsRawPointerBridgeByte(1));
    try std.testing.expect(allowsRawPointerBridgePolicyBytes(2, 0));
    try std.testing.expect(!allowsRawPointerBridgePolicyBytes(2, 1));

    try std.testing.expect(!isUnsafeByte(0));
    try std.testing.expect(isUnsafeByte(1));
    try std.testing.expect(isUnsafeByte(2));
    try std.testing.expect(!isUnsafePolicyBytes(2, 1));
    try std.testing.expect(!requiresDedicatedAuditByte(0));
    try std.testing.expect(requiresDedicatedAuditByte(1));
    try std.testing.expect(requiresDedicatedAuditByte(2));
    try std.testing.expect(!requiresDedicatedAuditPolicyBytes(2, 1));

    try requireNoUnsafeByte(0);
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeByte(1));
    try requireVolatileMmioByte(1);
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioByte(2));
    try requireRawPointerBridgeByte(2);
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeByte(1));

    try requireNoUnsafePolicyBytes(0, 0);
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafePolicyBytes(0, 1));
    try requireVolatileMmioPolicyBytes(1, 0);
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioPolicyBytes(1, 1));
    try requireRawPointerBridgePolicyBytes(2, 0);
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgePolicyBytes(2, 1));
}

test "phase3 unsafe policy keeps raw-pointer bridge relays helper-local" {
    const raw = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 2, .reserved = 0 };
    const reserved = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 2, .reserved = 1 };
    const safe = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 };

    var bridge_words = [_]u32{ 31, 47 };
    const first_addr = @intFromPtr(&bridge_words[0]);
    const second_addr = @intFromPtr(&bridge_words[1]);

    const ptr = try pointerAtInteropPolicy(u32, first_addr, @sizeOf(u32), raw);
    try std.testing.expectEqual(@as(u32, 31), ptr.*);

    const byte_ptr = try pointerAtByte(u32, second_addr, @sizeOf(u32), 2);
    try std.testing.expectEqual(@as(u32, 47), byte_ptr.*);

    const const_ptr = try constPointerAtInteropPolicy(u32, second_addr, raw);
    try std.testing.expectEqual(@as(u32, 47), const_ptr.*);

    const const_slice = try constSliceAtInteropPolicy(u32, first_addr, bridge_words.len, raw);
    try std.testing.expectEqual(@as(usize, bridge_words.len), const_slice.len);
    try std.testing.expectEqual(@as(u32, 31), const_slice[0]);
    try std.testing.expectEqual(@as(u32, 47), const_slice[1]);

    const mutable_slice = try sliceAtInteropPolicy(u32, first_addr, bridge_words.len, raw);
    mutable_slice[0] = 61;
    try std.testing.expectEqual(@as(u32, 61), bridge_words[0]);

    const mutable_bytes_slice = try sliceAtInteropPolicyBytes(u32, first_addr, bridge_words.len, 2, 0);
    mutable_bytes_slice[1] = 83;
    try std.testing.expectEqual(@as(u32, 83), bridge_words[1]);

    const mutable_byte_slice = try sliceAtByte(u32, first_addr, bridge_words.len, 2);
    try std.testing.expectEqual(@as(u32, 61), mutable_byte_slice[0]);
    try std.testing.expectEqual(@as(u32, 83), mutable_byte_slice[1]);

    try std.testing.expectEqual(
        @as(u32, 61),
        try readValueAtInteropPolicy(u32, first_addr, @sizeOf(u32), raw),
    );
    try std.testing.expectEqual(
        @as(u32, 83),
        try readValueAtInteropPolicyBytes(u32, second_addr, @sizeOf(u32), 2, 0),
    );
    try std.testing.expectEqual(@as(u32, 83), try readValueAtByte(u32, second_addr, @sizeOf(u32), 2));

    try std.testing.expectEqual(
        @as(u32, 83),
        try exchangeValueAtInteropPolicyBytes(u32, second_addr, @sizeOf(u32), 73, 2, 0),
    );
    try std.testing.expectEqual(@as(u32, 73), bridge_words[1]);

    try std.testing.expectEqual(
        @as(u32, 73),
        try exchangeValueAtInteropPolicy(u32, second_addr, @sizeOf(u32), 79, raw),
    );
    try std.testing.expectEqual(@as(u32, 79), bridge_words[1]);

    try std.testing.expectEqual(
        @as(u32, 79),
        try exchangeValueAtByte(u32, second_addr, @sizeOf(u32), 71, 2),
    );
    try std.testing.expectEqual(@as(u32, 71), bridge_words[1]);

    try writeValueAtInteropPolicy(u32, second_addr, 73, raw);
    try std.testing.expectEqual(@as(u32, 73), bridge_words[1]);

    const const_byte_slice = try constSliceAtByte(u32, first_addr, bridge_words.len, 2);
    try std.testing.expectEqual(@as(usize, bridge_words.len), const_byte_slice.len);
    try std.testing.expectEqual(@as(u32, 61), const_byte_slice[0]);
    try std.testing.expectEqual(@as(u32, 73), const_byte_slice[1]);

    try writeValueAtInteropPolicyBytes(u32, second_addr, 79, 2, 0);
    try std.testing.expectEqual(@as(u32, 79), bridge_words[1]);

    try std.testing.expectError(error.UnsafeScopeDenied, pointerAtInteropPolicy(u32, first_addr, @sizeOf(u32), safe));
    try std.testing.expectError(error.UnsafeScopeDenied, sliceAtInteropPolicy(u32, first_addr, bridge_words.len, safe));
    try std.testing.expectError(error.UnsafeScopeDenied, pointerAtInteropPolicyBytes(u32, first_addr, @sizeOf(u32), 2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, sliceAtInteropPolicyBytes(u32, first_addr, bridge_words.len, 2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, constPointerAtInteropPolicy(u32, second_addr, reserved));
    try std.testing.expectError(error.UnsafeScopeDenied, constSliceAtInteropPolicyBytes(u32, first_addr, bridge_words.len, 2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, sliceAtByte(u32, first_addr, bridge_words.len, 0));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        readValueAtInteropPolicy(u32, first_addr, @sizeOf(u32), safe),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        readValueAtInteropPolicyBytes(u32, first_addr, @sizeOf(u32), 2, 1),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        exchangeValueAtInteropPolicy(u32, second_addr, @sizeOf(u32), 83, safe),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        exchangeValueAtByte(u32, second_addr, @sizeOf(u32), 83, 0),
    );
    try std.testing.expectError(error.UnsafeScopeDenied, writeValueAtByte(u32, second_addr, 83, 0));
}

pub const RawPointerWindow = struct {
    base_addr: usize,
    byte_len: usize,
};

pub const RawPointerWindowError = RawPointerBridgeError || error{
    OffsetOverflow,
    AccessOutsideWindow,
};

fn rawPointerBridgeScopeByte() u8 {
    return @intFromEnum(abi.UnsafeScope.raw_pointer_bridge);
}

fn requireWindowAddress(window: RawPointerWindow, byte_offset: usize, access_len: usize) RawPointerWindowError!usize {
    const end_offset = std.math.add(usize, byte_offset, access_len) catch return error.OffsetOverflow;
    if (end_offset > window.byte_len) return error.AccessOutsideWindow;
    return std.math.add(usize, window.base_addr, byte_offset) catch return error.AddressOverflow;
}

pub fn windowInteropPolicyBytes(
    base_addr: usize,
    byte_len: usize,
    scope: u8,
    reserved: u8,
) RawPointerWindowError!RawPointerWindow {
    try requireRawPointerBridgePolicyBytes(scope, reserved);
    _ = std.math.add(usize, base_addr, byte_len) catch return error.AddressOverflow;
    return .{ .base_addr = base_addr, .byte_len = byte_len };
}

pub fn windowInteropPolicy(
    base_addr: usize,
    byte_len: usize,
    policy: abi.InteropPolicy,
) RawPointerWindowError!RawPointerWindow {
    return windowInteropPolicyBytes(base_addr, byte_len, policy.unsafe_scope, policy.reserved);
}

pub fn windowByte(base_addr: usize, byte_len: usize, scope: u8) RawPointerWindowError!RawPointerWindow {
    return windowInteropPolicyBytes(base_addr, byte_len, scope, 0);
}

pub fn pointerAtWindow(
    comptime T: type,
    window: RawPointerWindow,
    byte_offset: usize,
) RawPointerWindowError!*align(1) T {
    const address = try requireWindowAddress(window, byte_offset, @sizeOf(T));
    return narrow.pointerAtByte(T, address, @sizeOf(T), rawPointerBridgeScopeByte());
}

pub fn constPointerAtWindow(
    comptime T: type,
    window: RawPointerWindow,
    byte_offset: usize,
) RawPointerWindowError!*align(1) const T {
    const address = try requireWindowAddress(window, byte_offset, @sizeOf(T));
    return narrow.constPointerAtByte(T, address, rawPointerBridgeScopeByte());
}

pub fn sliceAtWindow(
    comptime T: type,
    window: RawPointerWindow,
    byte_offset: usize,
    len: usize,
) RawPointerWindowError![]align(1) T {
    const access_len = std.math.mul(usize, len, @sizeOf(T)) catch return error.LengthOverflow;
    const address = try requireWindowAddress(window, byte_offset, access_len);
    return narrow.sliceAtByte(T, address, len, rawPointerBridgeScopeByte());
}

pub fn constSliceAtWindow(
    comptime T: type,
    window: RawPointerWindow,
    byte_offset: usize,
    len: usize,
) RawPointerWindowError![]align(1) const T {
    const access_len = std.math.mul(usize, len, @sizeOf(T)) catch return error.LengthOverflow;
    const address = try requireWindowAddress(window, byte_offset, access_len);
    return narrow.constSliceAtByte(T, address, len, rawPointerBridgeScopeByte());
}

pub fn readValueAtWindow(
    comptime T: type,
    window: RawPointerWindow,
    byte_offset: usize,
) RawPointerWindowError!T {
    const address = try requireWindowAddress(window, byte_offset, @sizeOf(T));
    return narrow.readValueAtByte(T, address, @sizeOf(T), rawPointerBridgeScopeByte());
}

pub fn writeValueAtWindow(
    comptime T: type,
    window: RawPointerWindow,
    byte_offset: usize,
    value: T,
) RawPointerWindowError!void {
    const address = try requireWindowAddress(window, byte_offset, @sizeOf(T));
    return narrow.writeValueAtByte(T, address, value, rawPointerBridgeScopeByte());
}

pub fn exchangeValueAtWindow(
    comptime T: type,
    window: RawPointerWindow,
    byte_offset: usize,
    value: T,
) RawPointerWindowError!T {
    const address = try requireWindowAddress(window, byte_offset, @sizeOf(T));
    return narrow.exchangeValueAtByte(T, address, @sizeOf(T), value, rawPointerBridgeScopeByte());
}

test "phase3 unsafe policy keeps raw-pointer bridge windows bounded" {
    const raw = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 2, .reserved = 0 };
    const safe = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 };
    const reserved = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 2, .reserved = 1 };

    var bridge_words = [_]u32{ 31, 47, 59 };
    const base_addr = @intFromPtr(&bridge_words[0]);
    const byte_len = @sizeOf(@TypeOf(bridge_words));

    const window = try windowInteropPolicy(base_addr, byte_len, raw);
    try std.testing.expectEqual(base_addr, window.base_addr);
    try std.testing.expectEqual(byte_len, window.byte_len);
    try std.testing.expectEqual(window, try windowByte(base_addr, byte_len, 2));

    const first = try pointerAtWindow(u32, window, 0);
    try std.testing.expectEqual(@as(u32, 31), first.*);

    const second = try constPointerAtWindow(u32, window, @sizeOf(u32));
    try std.testing.expectEqual(@as(u32, 47), second.*);

    const mutable_slice = try sliceAtWindow(u32, window, 0, bridge_words.len);
    mutable_slice[2] = 71;
    try std.testing.expectEqual(@as(u32, 71), bridge_words[2]);

    const replay_slice = try constSliceAtWindow(u32, window, 0, bridge_words.len);
    try std.testing.expectEqual(@as(usize, bridge_words.len), replay_slice.len);
    try std.testing.expectEqual(@as(u32, 71), replay_slice[2]);

    try std.testing.expectEqual(@as(u32, 47), try readValueAtWindow(u32, window, @sizeOf(u32)));

    try writeValueAtWindow(u32, window, @sizeOf(u32) * 2, 73);
    try std.testing.expectEqual(@as(u32, 73), bridge_words[2]);

    try std.testing.expectEqual(
        @as(u32, 73),
        try exchangeValueAtWindow(u32, window, @sizeOf(u32) * 2, 79),
    );
    try std.testing.expectEqual(@as(u32, 79), bridge_words[2]);

    try std.testing.expectError(error.UnsafeScopeDenied, windowInteropPolicy(base_addr, byte_len, safe));
    try std.testing.expectError(error.UnsafeScopeDenied, windowInteropPolicy(base_addr, byte_len, reserved));
    try std.testing.expectError(error.AccessOutsideWindow, pointerAtWindow(u32, window, byte_len));
    try std.testing.expectError(
        error.AccessOutsideWindow,
        sliceAtWindow(u32, window, @sizeOf(u32), bridge_words.len),
    );
    try std.testing.expectError(error.OffsetOverflow, readValueAtWindow(u32, window, std.math.maxInt(usize)));
}
