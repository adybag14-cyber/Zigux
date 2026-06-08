const std = @import("std");
const abi = @import("abi_bindings");
const mmio = @import("mmio_helpers");

fn mmioPolicy() abi.InteropPolicy {
    return .{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
}

test "policy-gated exchange reports old value and replaces register" {
    var register: u32 = 0x1020_3040;
    const register_ptr: *volatile u32 = @ptrCast(&register);

    try std.testing.expectEqual(
        @as(u32, 0x1020_3040),
        try mmio.exchangeInteropPolicy(u32, mmioPolicy(), register_ptr, 0xA0B0_C0D0),
    );
    try std.testing.expectEqual(@as(u32, 0xA0B0_C0D0), register);

    try std.testing.expectEqual(
        @as(u32, 0xA0B0_C0D0),
        try mmio.exchangeInteropPolicyBytes(
            u32,
            @intFromEnum(abi.UnsafeScope.volatile_mmio),
            0,
            register_ptr,
            0x0102_0304,
        ),
    );
    try std.testing.expectEqual(@as(u32, 0x0102_0304), register);

    try std.testing.expectEqual(
        @as(u32, 0x0102_0304),
        try mmio.exchangeInteropPolicyByte(
            u32,
            @intFromEnum(abi.UnsafeScope.volatile_mmio),
            register_ptr,
            0x5566_7788,
        ),
    );
    try std.testing.expectEqual(@as(u32, 0x5566_7788), register);
}

test "policy-gated masked writes clear then set selected lanes" {
    var register: u16 = 0b1011_0110_1100_0011;
    const register_ptr: *volatile u16 = @ptrCast(&register);

    try std.testing.expectEqual(
        @as(u16, 0b1011_1000_1111_0011),
        try mmio.writeMaskedInteropPolicy(
            u16,
            mmioPolicy(),
            register_ptr,
            0b0000_1111_0011_0000,
            0b0000_1000_0011_0000,
        ),
    );
    try std.testing.expectEqual(@as(u16, 0b1011_1000_1111_0011), register);

    try std.testing.expectEqual(
        @as(u16, 0b1011_0011_1111_0011),
        try mmio.writeMaskedInteropPolicyBytes(
            u16,
            @intFromEnum(abi.UnsafeScope.volatile_mmio),
            0,
            register_ptr,
            0b0000_1100_0000_0000,
            0b0000_0011_0000_0000,
        ),
    );
    try std.testing.expectEqual(@as(u16, 0b1011_0011_1111_0011), register);

    try std.testing.expectEqual(
        @as(u16, 0b0000_0011_1111_0011),
        try mmio.writeMaskedInteropPolicyByte(
            u16,
            @intFromEnum(abi.UnsafeScope.volatile_mmio),
            register_ptr,
            0b1111_0000_0000_0000,
            0,
        ),
    );
    try std.testing.expectEqual(@as(u16, 0b0000_0011_1111_0011), register);
}

test "reserved policy bytes reject updates before volatile access" {
    var exchange_register: u8 = 0x44;
    const exchange_ptr: *volatile u8 = @ptrCast(&exchange_register);
    var masked_register: u8 = 0b1111_0000;
    const masked_ptr: *volatile u8 = @ptrCast(&masked_register);

    try std.testing.expectError(
        error.InvalidInteropPolicy,
        mmio.exchangeInteropPolicyBytes(
            u8,
            @intFromEnum(abi.UnsafeScope.volatile_mmio),
            1,
            exchange_ptr,
            0x88,
        ),
    );
    try std.testing.expectEqual(@as(u8, 0x44), exchange_register);

    try std.testing.expectError(
        error.InvalidInteropPolicy,
        mmio.writeMaskedInteropPolicyBytes(
            u8,
            @intFromEnum(abi.UnsafeScope.volatile_mmio),
            1,
            masked_ptr,
            0b1111_0000,
            0b0000_1111,
        ),
    );
    try std.testing.expectEqual(@as(u8, 0b1111_0000), masked_register);
}

test "non-MMIO unsafe scopes reject direct policy updates without mutation" {
    const denied_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };

    var exchange_register: u32 = 0xAAAA_5555;
    const exchange_ptr: *volatile u32 = @ptrCast(&exchange_register);
    var masked_register: u32 = 0xFFFF_0000;
    const masked_ptr: *volatile u32 = @ptrCast(&masked_register);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.exchangeInteropPolicy(u32, denied_policy, exchange_ptr, 0),
    );
    try std.testing.expectEqual(@as(u32, 0xAAAA_5555), exchange_register);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.exchangeInteropPolicyByte(
            u32,
            @intFromEnum(abi.UnsafeScope.none),
            exchange_ptr,
            0x1111_2222,
        ),
    );
    try std.testing.expectEqual(@as(u32, 0xAAAA_5555), exchange_register);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.writeMaskedInteropPolicy(u32, denied_policy, masked_ptr, 0xFFFF_0000, 0x1234_0000),
    );
    try std.testing.expectEqual(@as(u32, 0xFFFF_0000), masked_register);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.writeMaskedInteropPolicyByte(
            u32,
            @intFromEnum(abi.UnsafeScope.none),
            masked_ptr,
            0xFFFF_0000,
            0x1234_0000,
        ),
    );
    try std.testing.expectEqual(@as(u32, 0xFFFF_0000), masked_register);
}
