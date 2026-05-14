const std = @import("std");
const abi = @import("abi_bindings");

pub const UnsafeScopeTag = enum(u8) {
    none = 0,
    volatile_mmio = 1,
    raw_pointer_bridge = 2,
};

pub const UnsafeScopeError = error{UnsafeScopeDenied};

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

pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {
    if (reserved != 0) return null;
    return switch (unsafe_scope) {
        @intFromEnum(UnsafeScopeTag.none) => .none,
        @intFromEnum(UnsafeScopeTag.volatile_mmio) => .volatile_mmio,
        @intFromEnum(UnsafeScopeTag.raw_pointer_bridge) => .raw_pointer_bridge,
        else => null,
    };
}

pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?UnsafeScopeTag {
    return scopeFromInteropPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn scopeFromByte(unsafe_scope: u8) ?UnsafeScopeTag {
    return scopeFromInteropPolicyBytes(unsafe_scope, 0);
}

pub fn recognizesInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(unsafe_scope, reserved) != null;
}

pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {
    return scopeFromInteropPolicy(policy) != null;
}

pub fn recognizesByte(unsafe_scope: u8) bool {
    return recognizesInteropPolicyBytes(unsafe_scope, 0);
}

pub fn permitsNoUnsafe(scope: UnsafeScopeTag) bool {
    return scope == .none;
}

pub fn requireNoUnsafe(scope: UnsafeScopeTag) UnsafeScopeError!void {
    if (!permitsNoUnsafe(scope)) return error.UnsafeScopeDenied;
}

pub fn permitsNoUnsafePolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return permitsNoUnsafe(scopeFromInteropPolicyBytes(unsafe_scope, reserved) orelse return false);
}

pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {
    return permitsNoUnsafe(scopeFromInteropPolicy(policy) orelse return false);
}

pub fn permitsNoUnsafeByte(unsafe_scope: u8) bool {
    return permitsNoUnsafePolicyBytes(unsafe_scope, 0);
}

pub fn requireNoUnsafePolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {
    if (!permitsNoUnsafePolicyBytes(unsafe_scope, reserved)) return error.UnsafeScopeDenied;
}

pub fn requireNoUnsafeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return requireNoUnsafePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireNoUnsafeByte(unsafe_scope: u8) UnsafeScopeError!void {
    return requireNoUnsafePolicyBytes(unsafe_scope, 0);
}

pub fn permitsVolatileMmio(scope: UnsafeScopeTag) bool {
    return scope == .volatile_mmio;
}

pub fn requireVolatileMmio(scope: UnsafeScopeTag) UnsafeScopeError!void {
    if (!permitsVolatileMmio(scope)) return error.UnsafeScopeDenied;
}

pub fn permitsVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return permitsVolatileMmio(scopeFromInteropPolicyBytes(unsafe_scope, reserved) orelse return false);
}

pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {
    return permitsVolatileMmio(scopeFromInteropPolicy(policy) orelse return false);
}

pub fn permitsVolatileMmioByte(unsafe_scope: u8) bool {
    return permitsVolatileMmioPolicyBytes(unsafe_scope, 0);
}

pub fn requireVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {
    if (!permitsVolatileMmioPolicyBytes(unsafe_scope, reserved)) return error.UnsafeScopeDenied;
}

pub fn requireVolatileMmioInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return requireVolatileMmioPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireVolatileMmioByte(unsafe_scope: u8) UnsafeScopeError!void {
    return requireVolatileMmioPolicyBytes(unsafe_scope, 0);
}

pub fn permitsRawPointerBridge(scope: UnsafeScopeTag) bool {
    return scope == .raw_pointer_bridge;
}

pub fn requireRawPointerBridge(scope: UnsafeScopeTag) UnsafeScopeError!void {
    if (!permitsRawPointerBridge(scope)) return error.UnsafeScopeDenied;
}

pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return permitsRawPointerBridge(scopeFromInteropPolicyBytes(unsafe_scope, reserved) orelse return false);
}

pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {
    return permitsRawPointerBridge(scopeFromInteropPolicy(policy) orelse return false);
}

pub fn permitsRawPointerBridgeByte(unsafe_scope: u8) bool {
    return permitsRawPointerBridgePolicyBytes(unsafe_scope, 0);
}

pub fn requireRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {
    if (!permitsRawPointerBridgePolicyBytes(unsafe_scope, reserved)) return error.UnsafeScopeDenied;
}

pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return requireRawPointerBridgePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireRawPointerBridgeByte(unsafe_scope: u8) UnsafeScopeError!void {
    return requireRawPointerBridgePolicyBytes(unsafe_scope, 0);
}

pub fn pointerAtInteropPolicyBytes(
    comptime T: type,
    base: usize,
    offset: usize,
    unsafe_scope: u8,
    reserved: u8,
) UnsafeScopeError!*align(1) volatile T {
    try requireRawPointerBridgePolicyBytes(unsafe_scope, reserved);
    return pointerAt(T, base, offset);
}

pub fn pointerAtInteropPolicy(
    comptime T: type,
    base: usize,
    offset: usize,
    policy: abi.InteropPolicy,
) UnsafeScopeError!*align(1) volatile T {
    try requireRawPointerBridgeInteropPolicy(policy);
    return pointerAt(T, base, offset);
}

pub fn pointerAtByte(
    comptime T: type,
    base: usize,
    offset: usize,
    unsafe_scope: u8,
) UnsafeScopeError!*align(1) volatile T {
    try requireRawPointerBridgeByte(unsafe_scope);
    return pointerAt(T, base, offset);
}

pub fn sliceAtInteropPolicyBytes(
    comptime T: type,
    base: usize,
    len: usize,
    unsafe_scope: u8,
    reserved: u8,
) UnsafeScopeError![]align(1) T {
    try requireRawPointerBridgePolicyBytes(unsafe_scope, reserved);
    return sliceAt(T, base, len);
}

pub fn sliceAtInteropPolicy(
    comptime T: type,
    base: usize,
    len: usize,
    policy: abi.InteropPolicy,
) UnsafeScopeError![]align(1) T {
    try requireRawPointerBridgeInteropPolicy(policy);
    return sliceAt(T, base, len);
}

pub fn sliceAtByte(
    comptime T: type,
    base: usize,
    len: usize,
    unsafe_scope: u8,
) UnsafeScopeError![]align(1) T {
    try requireRawPointerBridgeByte(unsafe_scope);
    return sliceAt(T, base, len);
}

pub fn constSliceAtInteropPolicyBytes(
    comptime T: type,
    base: usize,
    len: usize,
    unsafe_scope: u8,
    reserved: u8,
) UnsafeScopeError![]align(1) const T {
    try requireRawPointerBridgePolicyBytes(unsafe_scope, reserved);
    return constSliceAt(T, base, len);
}

pub fn constSliceAtInteropPolicy(
    comptime T: type,
    base: usize,
    len: usize,
    policy: abi.InteropPolicy,
) UnsafeScopeError![]align(1) const T {
    try requireRawPointerBridgeInteropPolicy(policy);
    return constSliceAt(T, base, len);
}

pub fn constSliceAtByte(
    comptime T: type,
    base: usize,
    len: usize,
    unsafe_scope: u8,
) UnsafeScopeError![]align(1) const T {
    try requireRawPointerBridgeByte(unsafe_scope);
    return constSliceAt(T, base, len);
}

pub fn constPointerAtInteropPolicyBytes(
    comptime T: type,
    addr: usize,
    unsafe_scope: u8,
    reserved: u8,
) UnsafeScopeError!*align(1) const T {
    try requireRawPointerBridgePolicyBytes(unsafe_scope, reserved);
    return constPointerAt(T, addr);
}

pub fn constPointerAtInteropPolicy(
    comptime T: type,
    addr: usize,
    policy: abi.InteropPolicy,
) UnsafeScopeError!*align(1) const T {
    try requireRawPointerBridgeInteropPolicy(policy);
    return constPointerAt(T, addr);
}

pub fn constPointerAtByte(
    comptime T: type,
    addr: usize,
    unsafe_scope: u8,
) UnsafeScopeError!*align(1) const T {
    try requireRawPointerBridgeByte(unsafe_scope);
    return constPointerAt(T, addr);
}

pub fn writeValueAtInteropPolicyBytes(
    comptime T: type,
    addr: usize,
    value: T,
    unsafe_scope: u8,
    reserved: u8,
) UnsafeScopeError!void {
    try requireRawPointerBridgePolicyBytes(unsafe_scope, reserved);
    writeValueAt(T, addr, value);
}

pub fn writeValueAtInteropPolicy(
    comptime T: type,
    addr: usize,
    value: T,
    policy: abi.InteropPolicy,
) UnsafeScopeError!void {
    try requireRawPointerBridgeInteropPolicy(policy);
    writeValueAt(T, addr, value);
}

pub fn writeValueAtByte(
    comptime T: type,
    addr: usize,
    value: T,
    unsafe_scope: u8,
) UnsafeScopeError!void {
    try requireRawPointerBridgeByte(unsafe_scope);
    writeValueAt(T, addr, value);
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

    var slice_values = [_]u32{ 1, 2, 3 };
    const mutable_slice = sliceAt(u32, addressOf(&slice_values[0]), slice_values.len);
    mutable_slice[1] = 7;
    try std.testing.expectEqual(@as(u32, 7), slice_values[1]);

    const slice = constSliceAt(u32, base, 1);
    try std.testing.expectEqual(@as(u32, 11), slice[0]);

    const const_ptr = constPointerAt(u32, base);
    try std.testing.expectEqual(@as(u32, 11), const_ptr.*);

    writeValueAt(u32, base, 19);
    try std.testing.expectEqual(@as(u32, 19), value);
}

test "phase3 narrow unsafe scope bytes stay explicit" {
    try std.testing.expectEqual(@as(?UnsafeScopeTag, .none), scopeFromByte(0));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, .volatile_mmio), scopeFromByte(1));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, .raw_pointer_bridge), scopeFromByte(2));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, null), scopeFromByte(9));

    try std.testing.expectEqual(@as(?UnsafeScopeTag, .none), scopeFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, .volatile_mmio), scopeFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, .raw_pointer_bridge), scopeFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, null), scopeFromInteropPolicyBytes(9, 0));

    try std.testing.expect(recognizesByte(0));
    try std.testing.expect(recognizesByte(1));
    try std.testing.expect(recognizesByte(2));
    try std.testing.expect(!recognizesByte(9));

    try std.testing.expect(recognizesInteropPolicyBytes(0, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(1, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(2, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(9, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(1, 1));

    try std.testing.expect(permitsNoUnsafe(.none));
    try std.testing.expect(!permitsNoUnsafe(.volatile_mmio));
    try std.testing.expect(!permitsNoUnsafe(.raw_pointer_bridge));
    try requireNoUnsafe(.none);
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafe(.volatile_mmio));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafe(.raw_pointer_bridge));
    try std.testing.expect(permitsNoUnsafeByte(0));
    try std.testing.expect(!permitsNoUnsafeByte(1));
    try std.testing.expect(!permitsNoUnsafeByte(2));
    try std.testing.expect(!permitsNoUnsafeByte(9));

    try std.testing.expect(permitsNoUnsafePolicyBytes(0, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(1, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(2, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(9, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(0, 1));

    try requireNoUnsafeByte(0);
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeByte(1));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeByte(2));
    try std.testing.expectError(error.UnsafeScopeDenied, requireNoUnsafeByte(9));

    try std.testing.expect(!permitsVolatileMmio(.none));
    try std.testing.expect(permitsVolatileMmio(.volatile_mmio));
    try std.testing.expect(!permitsVolatileMmio(.raw_pointer_bridge));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmio(.none));
    try requireVolatileMmio(.volatile_mmio);
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmio(.raw_pointer_bridge));
    try std.testing.expect(!permitsVolatileMmioByte(0));
    try std.testing.expect(permitsVolatileMmioByte(1));
    try std.testing.expect(!permitsVolatileMmioByte(2));
    try std.testing.expect(!permitsVolatileMmioByte(9));

    try std.testing.expect(!permitsVolatileMmioPolicyBytes(0, 0));
    try std.testing.expect(permitsVolatileMmioPolicyBytes(1, 0));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(2, 0));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(9, 0));

    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioByte(0));
    try requireVolatileMmioByte(1);
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioByte(2));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioByte(9));

    try std.testing.expect(!permitsRawPointerBridge(.none));
    try std.testing.expect(!permitsRawPointerBridge(.volatile_mmio));
    try std.testing.expect(permitsRawPointerBridge(.raw_pointer_bridge));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridge(.none));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridge(.volatile_mmio));
    try requireRawPointerBridge(.raw_pointer_bridge);
    try std.testing.expect(!permitsRawPointerBridgeByte(0));
    try std.testing.expect(!permitsRawPointerBridgeByte(1));
    try std.testing.expect(permitsRawPointerBridgeByte(2));
    try std.testing.expect(!permitsRawPointerBridgeByte(9));

    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(0, 0));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(1, 0));
    try std.testing.expect(permitsRawPointerBridgePolicyBytes(2, 0));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(9, 0));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(2, 1));

    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeByte(0));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeByte(1));
    try requireRawPointerBridgeByte(2);
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeByte(9));

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

    try std.testing.expectEqual(@as(?UnsafeScopeTag, .none), scopeFromInteropPolicy(none_policy));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, .volatile_mmio), scopeFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, .raw_pointer_bridge), scopeFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, null), scopeFromInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, null), scopeFromInteropPolicy(reserved_policy));

    try std.testing.expect(recognizesInteropPolicy(none_policy));
    try std.testing.expect(recognizesInteropPolicy(mmio_policy));
    try std.testing.expect(recognizesInteropPolicy(raw_policy));
    try std.testing.expect(!recognizesInteropPolicy(unknown_policy));
    try std.testing.expect(!recognizesInteropPolicy(reserved_policy));

    try std.testing.expect(permitsNoUnsafeInteropPolicy(none_policy));
    try std.testing.expect(!permitsNoUnsafeInteropPolicy(mmio_policy));
    try std.testing.expect(!permitsNoUnsafeInteropPolicy(raw_policy));
    try std.testing.expect(!permitsNoUnsafeInteropPolicy(unknown_policy));
    try std.testing.expect(!permitsNoUnsafeInteropPolicy(reserved_policy));

    try std.testing.expect(!permitsVolatileMmioInteropPolicy(none_policy));
    try std.testing.expect(permitsVolatileMmioInteropPolicy(mmio_policy));
    try std.testing.expect(!permitsVolatileMmioInteropPolicy(raw_policy));
    try std.testing.expect(!permitsVolatileMmioInteropPolicy(unknown_policy));
    try std.testing.expect(!permitsVolatileMmioInteropPolicy(reserved_policy));

    try std.testing.expect(!permitsRawPointerBridgeInteropPolicy(none_policy));
    try std.testing.expect(!permitsRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expect(permitsRawPointerBridgeInteropPolicy(raw_policy));
    try std.testing.expect(!permitsRawPointerBridgeInteropPolicy(unknown_policy));
    try std.testing.expect(!permitsRawPointerBridgeInteropPolicy(reserved_policy));

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
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(unknown_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(reserved_policy));

    var bridge_values = [_]u32{ 27, 31, 35 };
    const bridge_addr = addressOf(&bridge_values[0]);
    const second_addr = byteOffset(bridge_addr, @sizeOf(u32));
    const third_addr = byteOffset(bridge_addr, @sizeOf(u32) * 2);

    const scoped_mut_slice = try sliceAtInteropPolicy(u32, bridge_addr, bridge_values.len, raw_policy);
    scoped_mut_slice[0] = 39;
    try std.testing.expectEqual(@as(u32, 39), bridge_values[0]);

    const scoped_mut_slice_bytes = try sliceAtInteropPolicyBytes(u32, bridge_addr, bridge_values.len, 2, 0);
    scoped_mut_slice_bytes[1] = 41;
    try std.testing.expectEqual(@as(u32, 41), bridge_values[1]);

    const scoped_direct_mut_slice = try sliceAtByte(u32, bridge_addr, bridge_values.len, 2);
    scoped_direct_mut_slice[2] = 43;
    try std.testing.expectEqual(@as(u32, 43), bridge_values[2]);

    const scoped_mut_ptr = try pointerAtInteropPolicy(u32, bridge_addr, @sizeOf(u32), raw_policy);
    scoped_mut_ptr.* = 47;
    try std.testing.expectEqual(@as(u32, 47), bridge_values[1]);

    const scoped_mut_byte_ptr = try pointerAtInteropPolicyBytes(u32, bridge_addr, @sizeOf(u32) * 2, 2, 0);
    scoped_mut_byte_ptr.* = 49;
    try std.testing.expectEqual(@as(u32, 49), bridge_values[2]);

    const scoped_direct_byte_ptr = try pointerAtByte(u32, bridge_addr, 0, 2);
    scoped_direct_byte_ptr.* = 51;
    try std.testing.expectEqual(@as(u32, 51), bridge_values[0]);

    const scoped_ptr = try constPointerAtInteropPolicy(u32, bridge_addr, raw_policy);
    try std.testing.expectEqual(@as(u32, 51), scoped_ptr.*);

    const scoped_byte_ptr = try constPointerAtInteropPolicyBytes(u32, third_addr, 2, 0);
    try std.testing.expectEqual(@as(u32, 49), scoped_byte_ptr.*);

    const scoped_direct_const_byte_ptr = try constPointerAtByte(u32, second_addr, 2);
    try std.testing.expectEqual(@as(u32, 47), scoped_direct_const_byte_ptr.*);

    const scoped_slice = try constSliceAtInteropPolicyBytes(u32, bridge_addr, bridge_values.len, 2, 0);
    try std.testing.expectEqual(@as(u32, 51), scoped_slice[0]);
    try std.testing.expectEqual(@as(u32, 47), scoped_slice[1]);
    try std.testing.expectEqual(@as(u32, 49), scoped_slice[2]);

    const scoped_direct_slice = try constSliceAtByte(u32, bridge_addr, bridge_values.len, 2);
    try std.testing.expectEqual(@as(u32, 51), scoped_direct_slice[0]);
    try std.testing.expectEqual(@as(u32, 47), scoped_direct_slice[1]);
    try std.testing.expectEqual(@as(u32, 49), scoped_direct_slice[2]);

    try writeValueAtInteropPolicy(u32, bridge_addr, 65, raw_policy);
    try std.testing.expectEqual(@as(u32, 65), bridge_values[0]);

    try writeValueAtInteropPolicyBytes(u32, third_addr, 71, 2, 0);
    try std.testing.expectEqual(@as(u32, 71), bridge_values[2]);

    try writeValueAtByte(u32, second_addr, 73, 2);
    try std.testing.expectEqual(@as(u32, 73), bridge_values[1]);

    var odd_bridge_bytes = [_]u8{ 0, 0, 0, 0, 0 };
    const odd_bridge_addr = addressOf(&odd_bridge_bytes[0]) + 1;

    try writeValueAtInteropPolicy(u16, odd_bridge_addr, 0xabcd, raw_policy);

    const scoped_odd_ptr = try constPointerAtInteropPolicy(u16, odd_bridge_addr, raw_policy);
    try std.testing.expectEqual(@as(u16, 0xabcd), scoped_odd_ptr.*);

    const scoped_odd_byte_ptr = try constPointerAtInteropPolicyBytes(u16, odd_bridge_addr, 2, 0);
    try std.testing.expectEqual(@as(u16, 0xabcd), scoped_odd_byte_ptr.*);

    const scoped_odd_direct_ptr = try constPointerAtByte(u16, odd_bridge_addr, 2);
    try std.testing.expectEqual(@as(u16, 0xabcd), scoped_odd_direct_ptr.*);

    const scoped_odd_slice = try constSliceAtInteropPolicy(u16, odd_bridge_addr, 1, raw_policy);
    try std.testing.expectEqual(@as(u16, 0xabcd), scoped_odd_slice[0]);

    const scoped_odd_slice_bytes = try constSliceAtInteropPolicyBytes(u16, odd_bridge_addr, 1, 2, 0);
    try std.testing.expectEqual(@as(u16, 0xabcd), scoped_odd_slice_bytes[0]);

    const scoped_odd_slice_byte = try constSliceAtByte(u16, odd_bridge_addr, 1, 2);
    try std.testing.expectEqual(@as(u16, 0xabcd), scoped_odd_slice_byte[0]);

    const scoped_odd_mut_slice = try sliceAtInteropPolicy(u16, odd_bridge_addr, 1, raw_policy);
    scoped_odd_mut_slice[0] = 0xbcde;
    try std.testing.expectEqual(@as(u16, 0xbcde), scoped_odd_ptr.*);

    const scoped_odd_mut_slice_bytes = try sliceAtInteropPolicyBytes(u16, odd_bridge_addr, 1, 2, 0);
    scoped_odd_mut_slice_bytes[0] = 0xcdef;
    try std.testing.expectEqual(@as(u16, 0xcdef), scoped_odd_ptr.*);

    const scoped_odd_mut_slice_byte = try sliceAtByte(u16, odd_bridge_addr, 1, 2);
    scoped_odd_mut_slice_byte[0] = 0xdef0;
    try std.testing.expectEqual(@as(u16, 0xdef0), scoped_odd_ptr.*);

    try writeValueAtInteropPolicyBytes(u16, odd_bridge_addr, 0x2468, 2, 0);
    try std.testing.expectEqual(@as(u16, 0x2468), scoped_odd_ptr.*);

    try writeValueAtByte(u16, odd_bridge_addr, 0x1357, 2);
    try std.testing.expectEqual(@as(u16, 0x1357), scoped_odd_ptr.*);

    try std.testing.expectError(error.UnsafeScopeDenied, sliceAtInteropPolicy(u32, bridge_addr, bridge_values.len, none_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, sliceAtInteropPolicyBytes(u32, bridge_addr, bridge_values.len, 2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, sliceAtByte(u32, bridge_addr, bridge_values.len, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, pointerAtInteropPolicy(u32, bridge_addr, 0, none_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, pointerAtInteropPolicyBytes(u32, bridge_addr, 0, 2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, pointerAtByte(u32, bridge_addr, 0, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, constPointerAtInteropPolicy(u32, bridge_addr, none_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, constPointerAtByte(u32, bridge_addr, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, constSliceAtInteropPolicy(u32, bridge_addr, bridge_values.len, mmio_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, constSliceAtInteropPolicyBytes(u32, bridge_addr, bridge_values.len, 2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, constSliceAtByte(u32, bridge_addr, bridge_values.len, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, writeValueAtInteropPolicy(u32, bridge_addr, 79, mmio_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, writeValueAtInteropPolicyBytes(u32, bridge_addr, 81, 0, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, writeValueAtByte(u32, bridge_addr, 83, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, constPointerAtInteropPolicy(u32, bridge_addr, unknown_policy));
}
