const std = @import("std");

const abi = @import("abi_bindings");
const mmio_helpers = @import("mmio_helpers");

fn policy(scope: abi.UnsafeScope, reserved: u8) abi.InteropPolicy {
    return .{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(scope),
        .reserved = reserved,
    };
}

test "phase3 mmio denied interop policies leave registers untouched" {
    const allowed = policy(.volatile_mmio, 0);
    const no_unsafe = policy(.none, 0);
    const raw_pointer = policy(.raw_pointer_bridge, 0);
    const reserved = policy(.volatile_mmio, 1);

    var register: u32 = 0x1234_5678;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);

    try std.testing.expectError(error.UnsafeScopeDenied, mmio_helpers.writeInteropPolicy(u32, no_unsafe, register_ptr, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio_helpers.exchangeInteropPolicy(u32, raw_pointer, register_ptr, 0));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio_helpers.writeInteropPolicy(u32, reserved, register_ptr, 0));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio_helpers.readInteropPolicy(u32, reserved, const_register_ptr));
    try std.testing.expectEqual(@as(u32, 0x1234_5678), register);

    try mmio_helpers.writeInteropPolicy(u32, allowed, register_ptr, 0xCAFE_BABE);
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), register);
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), try mmio_helpers.exchangeInteropPolicy(u32, allowed, register_ptr, 0x0BAD_C0DE));
    try std.testing.expectEqual(@as(u32, 0x0BAD_C0DE), register);
}

test "phase3 mmio denied byte policies leave masked writes untouched" {
    const mmio_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio);
    const no_unsafe_scope = @intFromEnum(abi.UnsafeScope.none);
    const raw_pointer_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge);

    var register: u16 = 0x5AA5;
    const register_ptr: *volatile u16 = @ptrCast(&register);
    const const_register_ptr: *const volatile u16 = @ptrCast(&register);

    try std.testing.expectError(error.UnsafeScopeDenied, mmio_helpers.writeInteropPolicyByte(u16, no_unsafe_scope, register_ptr, 0x1111));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio_helpers.exchangeInteropPolicyByte(u16, raw_pointer_scope, register_ptr, 0x2222));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio_helpers.writeMaskedInteropPolicyBytes(u16, mmio_scope, 1, register_ptr, 0x00FF, 0x0033));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio_helpers.readInteropPolicyBytes(u16, mmio_scope, 1, const_register_ptr));
    try std.testing.expectEqual(@as(u16, 0x5AA5), register);

    try std.testing.expectEqual(@as(u16, 0x5A33), try mmio_helpers.writeMaskedInteropPolicyByte(u16, mmio_scope, register_ptr, 0x00FF, 0x0033));
    try std.testing.expectEqual(@as(u16, 0x5A33), register);
    try std.testing.expectEqual(@as(u16, 0x5A33), try mmio_helpers.exchangeInteropPolicyBytes(u16, mmio_scope, 0, register_ptr, 0xBEEF));
    try std.testing.expectEqual(@as(u16, 0xBEEF), register);
}

test "phase3 mmio denied scoped access leaves raw storage unchanged" {
    var register: u8 = 0xA5;
    const register_ptr: *volatile u8 = @ptrCast(&register);
    const const_register_ptr: *const volatile u8 = @ptrCast(&register);

    try std.testing.expectError(error.UnsafeScopeDenied, mmio_helpers.readScoped(u8, .none, const_register_ptr));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio_helpers.writeScoped(u8, .raw_pointer_bridge, register_ptr, 0x11));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio_helpers.writeMaskedScoped(u8, .none, register_ptr, 0xF0, 0x03));
    try std.testing.expectEqual(@as(u8, 0xA5), register);

    try mmio_helpers.writeScoped(u8, .volatile_mmio, register_ptr, 0x3C);
    try std.testing.expectEqual(@as(u8, 0x3C), try mmio_helpers.readScoped(u8, .volatile_mmio, const_register_ptr));
    try std.testing.expectEqual(@as(u8, 0x35), try mmio_helpers.writeMaskedScoped(u8, .volatile_mmio, register_ptr, 0x0F, 0x05));
    try std.testing.expectEqual(@as(u8, 0x35), register);
}
