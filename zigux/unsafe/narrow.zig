const std = @import("std");
const abi = @import("abi_bindings");

pub const UnsafeScopeTag = abi.UnsafeScope;

pub const Surface = enum {
    safe_only,
    mmio_only,
    raw_pointer_bridge_only,
};

pub const UnsafeScopeError = error{UnsafeScopeDenied};
pub const RawPointerBridgeError = UnsafeScopeError || error{
    AddressOverflow,
    ByteLengthTooSmall,
    LengthOverflow,
};

pub fn scopeFromByte(scope: u8) ?UnsafeScopeTag {
    return switch (scope) {
        @intFromEnum(UnsafeScopeTag.none) => .none,
        @intFromEnum(UnsafeScopeTag.volatile_mmio) => .volatile_mmio,
        @intFromEnum(UnsafeScopeTag.raw_pointer_bridge) => .raw_pointer_bridge,
        else => null,
    };
}

pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {
    if (reserved != 0) return null;
    return scopeFromByte(unsafe_scope);
}

pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?UnsafeScopeTag {
    return scopeFromInteropPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {
    return scopeFromInteropPolicy(policy) != null;
}

pub fn permitsNoUnsafe(scope: UnsafeScopeTag) bool {
    return scope == .none;
}

pub fn permitsVolatileMmio(scope: UnsafeScopeTag) bool {
    return scope == .volatile_mmio;
}

pub fn permitsRawPointerBridge(scope: UnsafeScopeTag) bool {
    return scope == .raw_pointer_bridge;
}

pub fn permitsNoUnsafePolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(unsafe_scope, reserved) == .none;
}

pub fn permitsVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(unsafe_scope, reserved) == .volatile_mmio;
}

pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(unsafe_scope, reserved) == .raw_pointer_bridge;
}

pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {
    return scopeFromInteropPolicy(policy) == .none;
}

pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {
    return scopeFromInteropPolicy(policy) == .volatile_mmio;
}

pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {
    return scopeFromInteropPolicy(policy) == .raw_pointer_bridge;
}

pub fn permitsNoUnsafeByte(scope: u8) bool {
    return scopeFromByte(scope) == .none;
}

pub fn permitsVolatileMmioByte(scope: u8) bool {
    return scopeFromByte(scope) == .volatile_mmio;
}

pub fn permitsRawPointerBridgeByte(scope: u8) bool {
    return scopeFromByte(scope) == .raw_pointer_bridge;
}

pub fn requireNoUnsafePolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {
    if (!permitsNoUnsafePolicyBytes(unsafe_scope, reserved)) return error.UnsafeScopeDenied;
}

pub fn requireVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {
    if (!permitsVolatileMmioPolicyBytes(unsafe_scope, reserved)) return error.UnsafeScopeDenied;
}

pub fn requireRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {
    if (!permitsRawPointerBridgePolicyBytes(unsafe_scope, reserved)) return error.UnsafeScopeDenied;
}

pub fn requireNoUnsafeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return requireNoUnsafePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireVolatileMmioInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return requireVolatileMmioPolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {
    return requireRawPointerBridgePolicyBytes(policy.unsafe_scope, policy.reserved);
}

pub fn requireNoUnsafeByte(scope: u8) UnsafeScopeError!void {
    if (!permitsNoUnsafeByte(scope)) return error.UnsafeScopeDenied;
}

pub fn requireVolatileMmioByte(scope: u8) UnsafeScopeError!void {
    if (!permitsVolatileMmioByte(scope)) return error.UnsafeScopeDenied;
}

pub fn requireRawPointerBridgeByte(scope: u8) UnsafeScopeError!void {
    if (!permitsRawPointerBridgeByte(scope)) return error.UnsafeScopeDenied;
}

pub fn allowsVolatileMmio(scope: UnsafeScopeTag) bool {
    return permitsVolatileMmio(scope);
}

pub fn allowsVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return permitsVolatileMmioPolicyBytes(unsafe_scope, reserved);
}

pub fn allowsRawPointerBridge(scope: UnsafeScopeTag) bool {
    return permitsRawPointerBridge(scope);
}

pub fn allowsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return permitsRawPointerBridgePolicyBytes(unsafe_scope, reserved);
}

pub fn isUnsafe(scope: UnsafeScopeTag) bool {
    return scope != .none;
}

pub fn surfaceFor(scope: UnsafeScopeTag) Surface {
    return switch (scope) {
        .none => .safe_only,
        .volatile_mmio => .mmio_only,
        .raw_pointer_bridge => .raw_pointer_bridge_only,
    };
}

pub fn requiresDedicatedAudit(scope: UnsafeScopeTag) bool {
    return isUnsafe(scope);
}

fn requireByteCoverage(comptime T: type, byte_len: usize) RawPointerBridgeError!void {
    if (byte_len < @sizeOf(T)) return error.ByteLengthTooSmall;
}

fn requireAddressSpan(address: usize, byte_len: usize) RawPointerBridgeError!void {
    _ = std.math.add(usize, address, byte_len) catch return error.AddressOverflow;
}

fn requireElementSpan(comptime T: type, address: usize, len: usize) RawPointerBridgeError!usize {
    const byte_len = std.math.mul(usize, len, @sizeOf(T)) catch return error.LengthOverflow;
    try requireAddressSpan(address, byte_len);
    return byte_len;
}

fn rawPointer(comptime T: type, address: usize) *align(1) T {
    return @ptrFromInt(address);
}

fn rawConstPointer(comptime T: type, address: usize) *align(1) const T {
    return @ptrFromInt(address);
}

fn rawSlice(comptime T: type, address: usize, len: usize) []align(1) T {
    const base: [*]align(1) T = @ptrFromInt(address);
    return base[0..len];
}

fn rawConstSlice(comptime T: type, address: usize, len: usize) []align(1) const T {
    const base: [*]align(1) const T = @ptrFromInt(address);
    return base[0..len];
}

pub fn pointerAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) T {
    try requireRawPointerBridgePolicyBytes(unsafe_scope, reserved);
    try requireByteCoverage(T, byte_len);
    try requireAddressSpan(address, byte_len);
    return rawPointer(T, address);
}

pub fn pointerAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, policy: abi.InteropPolicy) RawPointerBridgeError!*align(1) T {
    return pointerAtInteropPolicyBytes(T, address, byte_len, policy.unsafe_scope, policy.reserved);
}

pub fn pointerAtByte(comptime T: type, address: usize, byte_len: usize, scope: u8) RawPointerBridgeError!*align(1) T {
    return pointerAtInteropPolicyBytes(T, address, byte_len, scope, 0);
}

pub fn constPointerAtInteropPolicyBytes(comptime T: type, address: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) const T {
    try requireRawPointerBridgePolicyBytes(unsafe_scope, reserved);
    try requireAddressSpan(address, @sizeOf(T));
    return rawConstPointer(T, address);
}

pub fn constPointerAtInteropPolicy(comptime T: type, address: usize, policy: abi.InteropPolicy) RawPointerBridgeError!*align(1) const T {
    return constPointerAtInteropPolicyBytes(T, address, policy.unsafe_scope, policy.reserved);
}

pub fn constPointerAtByte(comptime T: type, address: usize, scope: u8) RawPointerBridgeError!*align(1) const T {
    return constPointerAtInteropPolicyBytes(T, address, scope, 0);
}

pub fn sliceAtInteropPolicyBytes(comptime T: type, address: usize, len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError![]align(1) T {
    try requireRawPointerBridgePolicyBytes(unsafe_scope, reserved);
    _ = try requireElementSpan(T, address, len);
    return rawSlice(T, address, len);
}

pub fn sliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) T {
    return sliceAtInteropPolicyBytes(T, address, len, policy.unsafe_scope, policy.reserved);
}

pub fn sliceAtByte(comptime T: type, address: usize, len: usize, scope: u8) RawPointerBridgeError![]align(1) T {
    return sliceAtInteropPolicyBytes(T, address, len, scope, 0);
}

pub fn constSliceAtInteropPolicyBytes(comptime T: type, address: usize, len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError![]align(1) const T {
    try requireRawPointerBridgePolicyBytes(unsafe_scope, reserved);
    _ = try requireElementSpan(T, address, len);
    return rawConstSlice(T, address, len);
}

pub fn constSliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) const T {
    return constSliceAtInteropPolicyBytes(T, address, len, policy.unsafe_scope, policy.reserved);
}

pub fn constSliceAtByte(comptime T: type, address: usize, len: usize, scope: u8) RawPointerBridgeError![]align(1) const T {
    return constSliceAtInteropPolicyBytes(T, address, len, scope, 0);
}

pub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!void {
    const ptr = try pointerAtInteropPolicyBytes(T, address, @sizeOf(T), unsafe_scope, reserved);
    ptr.* = value;
}

pub fn writeValueAtInteropPolicy(comptime T: type, address: usize, value: T, policy: abi.InteropPolicy) RawPointerBridgeError!void {
    return writeValueAtInteropPolicyBytes(T, address, value, policy.unsafe_scope, policy.reserved);
}

pub fn writeValueAtByte(comptime T: type, address: usize, value: T, scope: u8) RawPointerBridgeError!void {
    return writeValueAtInteropPolicyBytes(T, address, value, scope, 0);
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
    try std.testing.expectEqual(@as(?UnsafeScopeTag, null), scopeFromInteropPolicyBytes(2, 1));

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
    try requireRawPointerBridgeInteropPolicy(raw_policy);
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(unknown_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireRawPointerBridgeInteropPolicy(reserved_policy));

    var bridge_values = [_]u32{ 31, 47, 59 };
    const bridge_addr = @intFromPtr(&bridge_values[0]);
    const second_addr = @intFromPtr(&bridge_values[1]);
    const third_addr = @intFromPtr(&bridge_values[2]);
    var odd_bridge_storage = [_]u8{ 0, 0xcd, 0xab, 0, 0 };
    const odd_bridge_addr = @intFromPtr(&odd_bridge_storage[1]);

    const scoped_mut_ptr = try pointerAtInteropPolicy(u32, bridge_addr, @sizeOf(u32), raw_policy);
    try std.testing.expectEqual(@as(u32, 31), scoped_mut_ptr.*);

    const scoped_mut_slice = try sliceAtInteropPolicy(u32, bridge_addr, bridge_values.len, raw_policy);
    try std.testing.expectEqual(@as(usize, bridge_values.len), scoped_mut_slice.len);
    try std.testing.expectEqual(@as(u32, 47), scoped_mut_slice[1]);

    const scoped_direct_mut_slice = try sliceAtByte(u32, bridge_addr, bridge_values.len, 2);
    scoped_direct_mut_slice[1] = 47;
    try std.testing.expectEqual(@as(u32, 47), bridge_values[1]);

    const scoped_const_slice = try constSliceAtInteropPolicyBytes(u32, bridge_addr, bridge_values.len, 2, 0);
    try std.testing.expectEqual(@as(u32, 31), scoped_const_slice[0]);

    const scoped_const_policy_slice = try constSliceAtInteropPolicy(u32, bridge_addr, bridge_values.len, raw_policy);
    try std.testing.expectEqual(@as(u32, 59), scoped_const_policy_slice[2]);

    const scoped_direct_const_slice = try constSliceAtByte(u32, bridge_addr, bridge_values.len, 2);
    try std.testing.expectEqual(@as(u32, 47), scoped_direct_const_slice[1]);

    const scoped_const_ptr = try constPointerAtInteropPolicyBytes(u32, third_addr, 2, 0);
    try std.testing.expectEqual(@as(u32, 59), scoped_const_ptr.*);

    const scoped_direct_const_ptr = try constPointerAtInteropPolicy(u32, second_addr, raw_policy);
    try std.testing.expectEqual(@as(u32, 47), scoped_direct_const_ptr.*);

    const scoped_direct_const_byte_ptr = try constPointerAtByte(u32, second_addr, 2);
    try std.testing.expectEqual(@as(u32, 47), scoped_direct_const_byte_ptr.*);

    try writeValueAtInteropPolicyBytes(u32, third_addr, 66, 2, 0);
    try std.testing.expectEqual(@as(u32, 66), bridge_values[2]);

    try writeValueAtInteropPolicy(u32, third_addr, 71, raw_policy);
    try std.testing.expectEqual(@as(u32, 71), bridge_values[2]);

    try writeValueAtByte(u32, third_addr, 73, 2);
    try std.testing.expectEqual(@as(u32, 73), bridge_values[2]);

    const scoped_odd_ptr = try pointerAtByte(u16, odd_bridge_addr, @sizeOf(u16), 2);
    try std.testing.expectEqual(@as(u16, 0xabcd), scoped_odd_ptr.*);

    const scoped_odd_const_ptr = try constPointerAtByte(u16, odd_bridge_addr, 2);
    try std.testing.expectEqual(@as(u16, 0xabcd), scoped_odd_const_ptr.*);

    const scoped_odd_slice = try constSliceAtInteropPolicy(u16, odd_bridge_addr, 1, raw_policy);
    try std.testing.expectEqual(@as(u16, 0xabcd), scoped_odd_slice[0]);

    try writeValueAtByte(u16, odd_bridge_addr, 0x1357, 2);
    try std.testing.expectEqual(@as(u16, 0x1357), scoped_odd_ptr.*);

    try std.testing.expectError(error.UnsafeScopeDenied, sliceAtInteropPolicy(u32, bridge_addr, bridge_values.len, none_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, sliceAtInteropPolicyBytes(u32, bridge_addr, bridge_values.len, 2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, sliceAtByte(u32, bridge_addr, bridge_values.len, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, pointerAtInteropPolicy(u32, bridge_addr, 0, none_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, pointerAtInteropPolicy(u32, bridge_addr, 0, mmio_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, pointerAtInteropPolicy(u32, bridge_addr, 0, unknown_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, pointerAtInteropPolicyBytes(u32, bridge_addr, 0, 2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, pointerAtByte(u32, bridge_addr, 0, 0));
}

test "phase3 narrow raw-pointer bridge rejects undersized and overflowing windows" {
    var bridge_values = [_]u32{ 11, 22, 33 };
    const bridge_addr = @intFromPtr(&bridge_values[0]);
    const last_u32_addr = std.math.maxInt(usize) - @sizeOf(u32);
    const overflowing_addr = std.math.maxInt(usize) - (@sizeOf(u32) - 2);
    const overflowing_slice_addr = std.math.maxInt(usize) - 1;

    try std.testing.expectError(
        error.ByteLengthTooSmall,
        pointerAtByte(u32, bridge_addr, @sizeOf(u16), 2),
    );
    try std.testing.expectError(
        error.ByteLengthTooSmall,
        pointerAtInteropPolicyBytes(u32, bridge_addr, @sizeOf(u16), 2, 0),
    );

    const edge_const_ptr = try constPointerAtByte(u32, last_u32_addr, 2);
    try std.testing.expectEqual(last_u32_addr, @intFromPtr(edge_const_ptr));

    try std.testing.expectError(
        error.AddressOverflow,
        constPointerAtByte(u32, overflowing_addr, 2),
    );
    try std.testing.expectError(
        error.AddressOverflow,
        pointerAtByte(u32, overflowing_addr, @sizeOf(u32), 2),
    );
    try std.testing.expectError(
        error.AddressOverflow,
        pointerAtInteropPolicyBytes(u32, overflowing_addr, @sizeOf(u32), 2, 0),
    );
    try std.testing.expectError(
        error.AddressOverflow,
        writeValueAtByte(u32, overflowing_addr, 99, 2),
    );
    try std.testing.expectError(
        error.AddressOverflow,
        sliceAtByte(u32, overflowing_slice_addr, 1, 2),
    );
    try std.testing.expectError(
        error.AddressOverflow,
        constSliceAtByte(u32, overflowing_slice_addr, 1, 2),
    );
}

test "phase3 narrow raw-pointer bridge rejects overflowing element counts" {
    var bridge_values = [_]u16{ 1, 2 };
    const bridge_addr = @intFromPtr(&bridge_values[0]);
    const overflowing_len = (std.math.maxInt(usize) / @sizeOf(u16)) + 1;

    try std.testing.expectError(
        error.LengthOverflow,
        sliceAtByte(u16, bridge_addr, overflowing_len, 2),
    );
    try std.testing.expectError(
        error.LengthOverflow,
        constSliceAtByte(u16, bridge_addr, overflowing_len, 2),
    );
    try std.testing.expectError(
        error.LengthOverflow,
        sliceAtInteropPolicyBytes(u16, bridge_addr, overflowing_len, 2, 0),
    );
    try std.testing.expectError(
        error.LengthOverflow,
        constSliceAtInteropPolicyBytes(u16, bridge_addr, overflowing_len, 2, 0),
    );
}
