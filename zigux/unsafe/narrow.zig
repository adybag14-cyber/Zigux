const std = @import("std");
const abi = @import("abi_bindings");

pub const Surface = enum {
    safe_only,
    mmio_only,
    raw_pointer_bridge_only,
};

pub const ScopeError = error{UnsafeScopeDenied};

pub fn addressOf(ptr: anytype) usize {
    return @intFromPtr(ptr);
}

pub fn byteOffset(base: usize, offset: usize) usize {
    return std.math.add(usize, base, offset) catch @panic("phase3 narrow unsafe byte offset overflow");
}

pub fn pointerAt(comptime T: type, base: usize, offset: usize) *align(1) volatile T {
    return @ptrFromInt(byteOffset(base, offset));
}

pub fn sliceAt(comptime T: type, base: usize, len: usize) []align(1) T {
    const ptr: [*]align(1) T = @ptrFromInt(base);
    return ptr[0..len];
}

pub fn constSliceAt(comptime T: type, base: usize, len: usize) []align(1) const T {
    const ptr: [*]align(1) const T = @ptrFromInt(base);
    return ptr[0..len];
}

pub fn constPointerAt(comptime T: type, addr: usize) *align(1) const T {
    return @ptrFromInt(addr);
}

pub fn writeValueAt(comptime T: type, addr: usize, value: T) void {
    const ptr: *align(1) T = @ptrFromInt(addr);
    ptr.* = value;
}

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

pub fn permitsNoUnsafe(scope: abi.UnsafeScope) bool {
    return scope == .none;
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

pub fn requireNoUnsafe(scope: abi.UnsafeScope) ScopeError!void {
    if (!permitsNoUnsafe(scope)) return error.UnsafeScopeDenied;
}

pub fn requireVolatileMmio(scope: abi.UnsafeScope) ScopeError!void {
    if (!allowsVolatileMmio(scope)) return error.UnsafeScopeDenied;
}

pub fn requireRawPointerBridge(scope: abi.UnsafeScope) ScopeError!void {
    if (!allowsRawPointerBridge(scope)) return error.UnsafeScopeDenied;
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

pub fn permitsNoUnsafePolicyBytes(scope: u8, reserved: u8) bool {
    return permitsNoUnsafe(scopeFromInteropPolicyBytes(scope, reserved) orelse return false);
}

pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {
    return permitsNoUnsafePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn permitsNoUnsafeByte(scope: u8) bool {
    return permitsNoUnsafePolicyBytes(scope, 0);
}

pub fn requireNoUnsafePolicyBytes(scope: u8, reserved: u8) ScopeError!void {
    try requireNoUnsafe(scopeFromInteropPolicyBytes(scope, reserved) orelse return error.UnsafeScopeDenied);
}

pub fn requireNoUnsafeInteropPolicy(policy: abi.InteropPolicy) ScopeError!void {
    return requireNoUnsafePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireNoUnsafeByte(scope: u8) ScopeError!void {
    return requireNoUnsafePolicyBytes(scope, 0);
}

pub fn requireVolatileMmioPolicyBytes(scope: u8, reserved: u8) ScopeError!void {
    try requireVolatileMmio(scopeFromInteropPolicyBytes(scope, reserved) orelse return error.UnsafeScopeDenied);
}

pub fn requireVolatileMmioInteropPolicy(policy: abi.InteropPolicy) ScopeError!void {
    return requireVolatileMmioPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireVolatileMmioByte(scope: u8) ScopeError!void {
    return requireVolatileMmioPolicyBytes(scope, 0);
}

pub fn requireRawPointerBridgePolicyBytes(scope: u8, reserved: u8) ScopeError!void {
    try requireRawPointerBridge(scopeFromInteropPolicyBytes(scope, reserved) orelse return error.UnsafeScopeDenied);
}

pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) ScopeError!void {
    return requireRawPointerBridgePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireRawPointerBridgeByte(scope: u8) ScopeError!void {
    return requireRawPointerBridgePolicyBytes(scope, 0);
}

pub fn pointerAtInteropPolicyBytes(
    comptime T: type,
    base: usize,
    offset: usize,
    scope: u8,
    reserved: u8,
) ScopeError!*align(1) volatile T {
    try requireRawPointerBridgePolicyBytes(scope, reserved);
    return pointerAt(T, base, offset);
}

pub fn pointerAtInteropPolicy(
    comptime T: type,
    base: usize,
    offset: usize,
    policy: abi.InteropPolicy,
) ScopeError!*align(1) volatile T {
    try requireRawPointerBridgeInteropPolicy(policy);
    return pointerAt(T, base, offset);
}

pub fn pointerAtByte(
    comptime T: type,
    base: usize,
    offset: usize,
    scope: u8,
) ScopeError!*align(1) volatile T {
    try requireRawPointerBridgeByte(scope);
    return pointerAt(T, base, offset);
}

pub fn sliceAtInteropPolicyBytes(
    comptime T: type,
    base: usize,
    len: usize,
    scope: u8,
    reserved: u8,
) ScopeError![]align(1) T {
    try requireRawPointerBridgePolicyBytes(scope, reserved);
    return sliceAt(T, base, len);
}

pub fn sliceAtInteropPolicy(
    comptime T: type,
    base: usize,
    len: usize,
    policy: abi.InteropPolicy,
) ScopeError![]align(1) T {
    try requireRawPointerBridgeInteropPolicy(policy);
    return sliceAt(T, base, len);
}

pub fn sliceAtByte(
    comptime T: type,
    base: usize,
    len: usize,
    scope: u8,
) ScopeError![]align(1) T {
    try requireRawPointerBridgeByte(scope);
    return sliceAt(T, base, len);
}

pub fn constPointerAtInteropPolicyBytes(
    comptime T: type,
    addr: usize,
    scope: u8,
    reserved: u8,
) ScopeError!*align(1) const T {
    try requireRawPointerBridgePolicyBytes(scope, reserved);
    return constPointerAt(T, addr);
}

pub fn constPointerAtInteropPolicy(
    comptime T: type,
    addr: usize,
    policy: abi.InteropPolicy,
) ScopeError!*align(1) const T {
    try requireRawPointerBridgeInteropPolicy(policy);
    return constPointerAt(T, addr);
}

pub fn constPointerAtByte(
    comptime T: type,
    addr: usize,
    scope: u8,
) ScopeError!*align(1) const T {
    try requireRawPointerBridgeByte(scope);
    return constPointerAt(T, addr);
}

pub fn constSliceAtInteropPolicyBytes(
    comptime T: type,
    base: usize,
    len: usize,
    scope: u8,
    reserved: u8,
) ScopeError![]align(1) const T {
    try requireRawPointerBridgePolicyBytes(scope, reserved);
    return constSliceAt(T, base, len);
}

pub fn constSliceAtInteropPolicy(
    comptime T: type,
    base: usize,
    len: usize,
    policy: abi.InteropPolicy,
) ScopeError![]align(1) const T {
    try requireRawPointerBridgeInteropPolicy(policy);
    return constSliceAt(T, base, len);
}

pub fn constSliceAtByte(
    comptime T: type,
    base: usize,
    len: usize,
    scope: u8,
) ScopeError![]align(1) const T {
    try requireRawPointerBridgeByte(scope);
    return constSliceAt(T, base, len);
}

pub fn writeValueAtInteropPolicyBytes(
    comptime T: type,
    addr: usize,
    value: T,
    scope: u8,
    reserved: u8,
) ScopeError!void {
    try requireRawPointerBridgePolicyBytes(scope, reserved);
    writeValueAt(T, addr, value);
}

pub fn writeValueAtInteropPolicy(
    comptime T: type,
    addr: usize,
    value: T,
    policy: abi.InteropPolicy,
) ScopeError!void {
    try requireRawPointerBridgeInteropPolicy(policy);
    writeValueAt(T, addr, value);
}

pub fn writeValueAtByte(
    comptime T: type,
    addr: usize,
    value: T,
    scope: u8,
) ScopeError!void {
    try requireRawPointerBridgeByte(scope);
    writeValueAt(T, addr, value);
}

test "phase3 narrow unsafe surface keeps the capability split explicit" {
    try std.testing.expectEqual(Surface.safe_only, surfaceFor(.none));
    try std.testing.expectEqual(Surface.mmio_only, surfaceFor(.volatile_mmio));
    try std.testing.expectEqual(Surface.raw_pointer_bridge_only, surfaceFor(.raw_pointer_bridge));

    try std.testing.expect(permitsNoUnsafe(.none));
    try std.testing.expect(!permitsNoUnsafe(.volatile_mmio));
    try std.testing.expect(!permitsNoUnsafe(.raw_pointer_bridge));

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
}

test "phase3 narrow unsafe wrappers stay bounded" {
    try std.testing.expectEqual(@as(usize, 12), byteOffset(9, 3));
    try std.testing.expectEqual(std.math.maxInt(usize), byteOffset(std.math.maxInt(usize) - 4, 4));

    var value: u32 = 0;
    const base = addressOf(&value);
    const ptr = pointerAt(u32, base, 0);
    ptr.* = 11;
    try std.testing.expectEqual(@as(u32, 11), value);

    var odd_bytes = [_]u8{ 0, 0, 0, 0 };
    const odd_addr = addressOf(&odd_bytes[0]) + 1;
    const odd_ptr = pointerAt(u16, addressOf(&odd_bytes[0]), 1);
    odd_ptr.* = 0x1234;
    const odd_confirm: *align(1) const u16 = @ptrCast(&odd_bytes[1]);
    try std.testing.expectEqual(@as(u16, 0x1234), odd_confirm.*);

    const odd_const_ptr = constPointerAt(u16, odd_addr);
    try std.testing.expectEqual(@as(u16, 0x1234), odd_const_ptr.*);

    const odd_const_slice = constSliceAt(u16, odd_addr, 1);
    try std.testing.expectEqual(@as(u16, 0x1234), odd_const_slice[0]);

    const odd_mut_slice = sliceAt(u16, odd_addr, 1);
    odd_mut_slice[0] = 0x5678;
    try std.testing.expectEqual(@as(u16, 0x5678), odd_const_ptr.*);

    writeValueAt(u16, odd_addr, 0x9abc);
    try std.testing.expectEqual(@as(u16, 0x9abc), odd_const_ptr.*);
}

test "phase3 narrow raw pointer bridge gating stays explicit" {
    const none_policy = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 };
    const mmio_policy = abi.InteropPolicy{ .panic_mode = 1, .allocator_mode = 1, .unsafe_scope = 1, .reserved = 0 };
    const raw_policy = abi.InteropPolicy{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 0 };
    const reserved_policy = abi.InteropPolicy{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 1 };
    const unknown_policy = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 9, .reserved = 0 };

    try requireNoUnsafe(.none);
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafe(.volatile_mmio));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafe(.raw_pointer_bridge));

    try std.testing.expect(permitsNoUnsafeByte(0));
    try std.testing.expect(!permitsNoUnsafeByte(2));
    try std.testing.expect(!permitsNoUnsafeByte(9));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeByte(2));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeInteropPolicy(raw_policy));

    try std.testing.expect(!allowsVolatileMmioByte(0));
    try std.testing.expect(allowsVolatileMmioByte(1));
    try std.testing.expect(!allowsVolatileMmioByte(2));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmio(.none));
    try requireVolatileMmio(.volatile_mmio);
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmio(.raw_pointer_bridge));

    try std.testing.expect(!allowsRawPointerBridgeByte(0));
    try std.testing.expect(!allowsRawPointerBridgeByte(1));
    try std.testing.expect(allowsRawPointerBridgeByte(2));
    try std.testing.expect(!allowsRawPointerBridgeByte(9));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeByte(1));
    try requireRawPointerBridgeInteropPolicy(raw_policy);
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(reserved_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(unknown_policy));

    var bridge_values = [_]u32{ 27, 31, 35 };
    const bridge_addr = addressOf(&bridge_values[0]);
    const second_addr = byteOffset(bridge_addr, @sizeOf(u32));

    const mut_slice = try sliceAtInteropPolicy(u32, bridge_addr, bridge_values.len, raw_policy);
    mut_slice[0] = 39;
    try std.testing.expectEqual(@as(u32, 39), bridge_values[0]);

    const ptr = try pointerAtByte(u32, bridge_addr, @sizeOf(u32), 2);
    ptr.* = 47;
    try std.testing.expectEqual(@as(u32, 47), bridge_values[1]);

    const const_ptr = try constPointerAtInteropPolicy(u32, second_addr, raw_policy);
    try std.testing.expectEqual(@as(u32, 47), const_ptr.*);

    const const_slice = try constSliceAtInteropPolicyBytes(u32, bridge_addr, bridge_values.len, 2, 0);
    try std.testing.expectEqual(@as(u32, 39), const_slice[0]);
    try std.testing.expectEqual(@as(u32, 47), const_slice[1]);
    try std.testing.expectEqual(@as(u32, 35), const_slice[2]);

    try writeValueAtInteropPolicy(u32, bridge_addr, 65, raw_policy);
    try std.testing.expectEqual(@as(u32, 65), bridge_values[0]);

    try std.testing.expectError(error.UnsafeScopeDenied, sliceAtInteropPolicy(u32, bridge_addr, bridge_values.len, none_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, pointerAtInteropPolicy(u32, bridge_addr, 0, mmio_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, constSliceAtByte(u32, bridge_addr, bridge_values.len, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, writeValueAtByte(u32, bridge_addr, 79, 1));
}
