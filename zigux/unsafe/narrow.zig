const std = @import("std");
const abi = @import("abi_bindings");

pub const UnsafeScopeTag = enum(u8) {
    none = 0,
    volatile_mmio = 1,
    raw_pointer_bridge = 2,
};

pub fn addressOf(ptr: anytype) usize {
    return @intFromPtr(ptr);
}

pub fn byteOffset(base: usize, offset: usize) usize {
    return std.math.add(usize, base, offset) catch @panic("phase3 narrow unsafe byte offset overflow");
}

pub fn pointerAt(comptime T: type, base: usize, offset: usize) *align(1) volatile T {
    return @ptrFromInt(byteOffset(base, offset));
}

pub fn constSliceAt(comptime T: type, base: usize, len: usize) []const T {
    const ptr: [*]const T = @ptrFromInt(base);
    return ptr[0..len];
}

pub fn constPointerAt(comptime T: type, addr: usize) *const T {
    return @ptrFromInt(addr);
}

pub fn writeValueAt(comptime T: type, addr: usize, value: T) void {
    const ptr: *T = @ptrFromInt(addr);
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

pub fn permitsNoUnsafePolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(unsafe_scope, reserved) == .none;
}

pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {
    return scopeFromInteropPolicy(policy) == .none;
}

pub fn permitsNoUnsafeByte(unsafe_scope: u8) bool {
    return permitsNoUnsafePolicyBytes(unsafe_scope, 0);
}

pub fn permitsVolatileMmioPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(unsafe_scope, reserved) == .volatile_mmio;
}

pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {
    return scopeFromInteropPolicy(policy) == .volatile_mmio;
}

pub fn permitsVolatileMmioByte(unsafe_scope: u8) bool {
    return permitsVolatileMmioPolicyBytes(unsafe_scope, 0);
}

pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    return scopeFromInteropPolicyBytes(unsafe_scope, reserved) == .raw_pointer_bridge;
}

pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {
    return scopeFromInteropPolicy(policy) == .raw_pointer_bridge;
}

pub fn permitsRawPointerBridgeByte(unsafe_scope: u8) bool {
    return permitsRawPointerBridgePolicyBytes(unsafe_scope, 0);
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
    const odd_ptr = pointerAt(u16, addressOf(&odd_bytes[0]), 1);
    odd_ptr.* = 0x1234;
    const odd_confirm: *align(1) const u16 = @ptrCast(&odd_bytes[1]);
    try std.testing.expectEqual(@as(u16, 0x1234), odd_confirm.*);

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

    try std.testing.expect(recognizesByte(0));
    try std.testing.expect(recognizesByte(1));
    try std.testing.expect(recognizesByte(2));
    try std.testing.expect(!recognizesByte(9));

    try std.testing.expect(recognizesInteropPolicyBytes(0, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(1, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(2, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(9, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(1, 1));

    try std.testing.expect(permitsNoUnsafeByte(0));
    try std.testing.expect(!permitsNoUnsafeByte(1));
    try std.testing.expect(!permitsNoUnsafeByte(2));
    try std.testing.expect(!permitsNoUnsafeByte(9));

    try std.testing.expect(permitsNoUnsafePolicyBytes(0, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(1, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(2, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(9, 0));
    try std.testing.expect(!permitsNoUnsafePolicyBytes(0, 1));

    try std.testing.expect(!permitsVolatileMmioByte(0));
    try std.testing.expect(permitsVolatileMmioByte(1));
    try std.testing.expect(!permitsVolatileMmioByte(2));
    try std.testing.expect(!permitsVolatileMmioByte(9));

    try std.testing.expect(!permitsVolatileMmioPolicyBytes(0, 0));
    try std.testing.expect(permitsVolatileMmioPolicyBytes(1, 0));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(2, 0));
    try std.testing.expect(!permitsVolatileMmioPolicyBytes(9, 0));

    try std.testing.expect(!permitsRawPointerBridgeByte(0));
    try std.testing.expect(!permitsRawPointerBridgeByte(1));
    try std.testing.expect(permitsRawPointerBridgeByte(2));
    try std.testing.expect(!permitsRawPointerBridgeByte(9));

    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(0, 0));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(1, 0));
    try std.testing.expect(permitsRawPointerBridgePolicyBytes(2, 0));
    try std.testing.expect(!permitsRawPointerBridgePolicyBytes(2, 1));

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
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 2,
        .unsafe_scope = 2,
        .reserved = 1,
    };

    try std.testing.expectEqual(@as(?UnsafeScopeTag, .none), scopeFromInteropPolicy(none_policy));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, .volatile_mmio), scopeFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, .raw_pointer_bridge), scopeFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?UnsafeScopeTag, null), scopeFromInteropPolicy(reserved_policy));

    try std.testing.expect(recognizesInteropPolicy(none_policy));
    try std.testing.expect(recognizesInteropPolicy(mmio_policy));
    try std.testing.expect(recognizesInteropPolicy(raw_policy));
    try std.testing.expect(!recognizesInteropPolicy(reserved_policy));

    try std.testing.expect(permitsNoUnsafeInteropPolicy(none_policy));
    try std.testing.expect(!permitsNoUnsafeInteropPolicy(mmio_policy));
    try std.testing.expect(!permitsNoUnsafeInteropPolicy(raw_policy));
    try std.testing.expect(!permitsNoUnsafeInteropPolicy(reserved_policy));

    try std.testing.expect(!permitsVolatileMmioInteropPolicy(none_policy));
    try std.testing.expect(permitsVolatileMmioInteropPolicy(mmio_policy));
    try std.testing.expect(!permitsVolatileMmioInteropPolicy(raw_policy));
    try std.testing.expect(!permitsVolatileMmioInteropPolicy(reserved_policy));

    try std.testing.expect(!permitsRawPointerBridgeInteropPolicy(none_policy));
    try std.testing.expect(!permitsRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expect(permitsRawPointerBridgeInteropPolicy(raw_policy));
    try std.testing.expect(!permitsRawPointerBridgeInteropPolicy(reserved_policy));
}
