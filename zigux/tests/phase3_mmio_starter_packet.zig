const std = @import("std");
const abi = @import("abi_bindings");
const mmio = @import("mmio");
const narrow = @import("narrow");
const unsafe_policy = @import("unsafe_policy");

fn mmioPolicy() abi.InteropPolicy {
    return .{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
}

fn safePolicy() abi.InteropPolicy {
    return .{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
}

fn rawPointerPolicy() abi.InteropPolicy {
    return .{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
}

fn reservedMmioPolicy() abi.InteropPolicy {
    return .{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };
}

test "phase3 mmio starter packet keeps typed scope gate and masked writes explicit" {
    var register: u32 = 0x0102_0304;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.readScoped(u32, .none, const_register_ptr));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.writeScoped(u32, .raw_pointer_bridge, register_ptr, 0xAAAA_5555),
    );
    try std.testing.expectEqual(@as(u32, 0x0102_0304), register);

    try std.testing.expectEqual(
        @as(u32, 0x0102_0304),
        try mmio.readScoped(u32, .volatile_mmio, const_register_ptr),
    );
    try mmio.writeScoped(u32, .volatile_mmio, register_ptr, 0x1234_5678);
    try std.testing.expectEqual(@as(u32, 0x1234_5678), register);

    try std.testing.expectEqual(
        @as(u32, 0x1234_5678),
        try mmio.exchangeScoped(u32, .volatile_mmio, register_ptr, 0xCAFE_BABE),
    );
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), register);

    try std.testing.expectEqual(
        @as(u32, 0xCA0E_B00E),
        try mmio.writeMaskedScoped(u32, .volatile_mmio, register_ptr, 0x00F0_0FF0, 0x000E_000E),
    );
    try std.testing.expectEqual(@as(u32, 0xCA0E_B00E), register);
}

test "phase3 mmio starter packet keeps byte-policy helpers aligned with unsafe policy relays" {
    const safe_scope = @intFromEnum(abi.UnsafeScope.none);
    const mmio_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio);
    const raw_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge);

    try std.testing.expect(unsafe_policy.permitsVolatileMmioInteropPolicy(mmioPolicy()));
    try std.testing.expect(!unsafe_policy.permitsVolatileMmioInteropPolicy(safePolicy()));
    try std.testing.expect(!unsafe_policy.permitsVolatileMmioInteropPolicy(rawPointerPolicy()));
    try std.testing.expect(!unsafe_policy.permitsVolatileMmioInteropPolicy(reservedMmioPolicy()));

    try std.testing.expect(mmio.allowsInteropPolicyByte(mmio_scope));
    try std.testing.expect(mmio.allowsInteropPolicyBytes(mmio_scope, 0));
    try std.testing.expect(!mmio.allowsInteropPolicyByte(safe_scope));
    try std.testing.expect(!mmio.allowsInteropPolicyByte(raw_scope));
    try std.testing.expect(!mmio.allowsInteropPolicyBytes(mmio_scope, 1));

    try mmio.requireInteropPolicyByte(mmio_scope);
    try mmio.requireInteropPolicyBytes(mmio_scope, 0);
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.requireInteropPolicyByte(safe_scope));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.requireInteropPolicyByte(raw_scope));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.requireInteropPolicyBytes(mmio_scope, 1));

    try std.testing.expect(narrow.permitsVolatileMmio(.volatile_mmio));
    try std.testing.expect(!narrow.permitsVolatileMmio(.none));
    try std.testing.expect(!narrow.permitsVolatileMmio(.raw_pointer_bridge));
}

test "phase3 mmio starter packet keeps whole-record policy writes side-effect free when denied" {
    var register: u32 = 0xABCD_0001;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.readInteropPolicy(u32, safePolicy(), const_register_ptr),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.writeInteropPolicy(u32, rawPointerPolicy(), register_ptr, 0x1234_5678),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        mmio.exchangeInteropPolicy(u32, reservedMmioPolicy(), register_ptr, 0xFFFF_00FF),
    );
    try std.testing.expectEqual(@as(u32, 0xABCD_0001), register);

    try std.testing.expectEqual(
        @as(u32, 0xABCD_0001),
        try mmio.readInteropPolicy(u32, mmioPolicy(), const_register_ptr),
    );
    try mmio.writeInteropPolicy(u32, mmioPolicy(), register_ptr, 0x1234_5678);
    try std.testing.expectEqual(@as(u32, 0x1234_5678), register);
    try std.testing.expectEqual(
        @as(u32, 0x1234_5678),
        try mmio.exchangeInteropPolicy(u32, mmioPolicy(), register_ptr, 0xFFFF_00FF),
    );
    try std.testing.expectEqual(@as(u32, 0xFFFF_00FF), register);
}

test "phase3 mmio starter packet keeps byte-policy shorthands and reserved bytes explicit" {
    var register: u16 = 0x0FF0;
    const register_ptr: *volatile u16 = @ptrCast(&register);
    const const_register_ptr: *const volatile u16 = @ptrCast(&register);
    const mmio_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio);

    try std.testing.expectEqual(
        @as(u16, 0x0FF0),
        try mmio.readInteropPolicyByte(u16, mmio_scope, const_register_ptr),
    );
    try std.testing.expectEqual(
        @as(u16, 0x0F05),
        try mmio.writeMaskedInteropPolicyByte(u16, mmio_scope, register_ptr, 0x00F0, 0x0005),
    );
    try std.testing.expectEqual(@as(u16, 0x0F05), register);

    try std.testing.expectEqual(
        @as(u16, 0x0F05),
        try mmio.exchangeInteropPolicyBytes(u16, mmio_scope, 0, register_ptr, 0x5500),
    );
    try std.testing.expectEqual(@as(u16, 0x5500), register);

    try std.testing.expectError(
        error.InvalidInteropPolicy,
        mmio.writeMaskedInteropPolicyBytes(u16, mmio_scope, 1, register_ptr, 0x0F00, 0x00A0),
    );
    try std.testing.expectEqual(@as(u16, 0x5500), register);
}
