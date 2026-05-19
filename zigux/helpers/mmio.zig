const std = @import("std");
const abi = @import("abi_bindings");
const unsafe_policy = @import("unsafe_policy");

pub const PolicyError = error{
    InvalidInteropPolicy,
    UnsafeScopeDenied,
};

fn scopeFromInteropPolicy(policy: abi.InteropPolicy) PolicyError!abi.UnsafeScope {
    return unsafe_policy.scopeFromInteropPolicy(policy) orelse error.InvalidInteropPolicy;
}

fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) PolicyError!abi.UnsafeScope {
    return unsafe_policy.scopeFromInteropPolicyBytes(scope, reserved) orelse error.InvalidInteropPolicy;
}

pub fn allowsVolatileMmioScope(scope: abi.UnsafeScope) bool {
    return unsafe_policy.permitsVolatileMmio(scope);
}

pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {
    const scope = scopeFromInteropPolicy(policy) catch return false;
    return allowsVolatileMmioScope(scope);
}

pub fn allowsInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {
    const scope = scopeFromInteropPolicyBytes(unsafe_scope, reserved) catch return false;
    return allowsVolatileMmioScope(scope);
}

pub fn allowsInteropPolicyByte(unsafe_scope: u8) bool {
    return allowsInteropPolicyBytes(unsafe_scope, 0);
}

pub fn requireVolatileMmioScope(scope: abi.UnsafeScope) PolicyError!void {
    if (!allowsVolatileMmioScope(scope)) {
        return error.UnsafeScopeDenied;
    }
}

pub fn requireInteropPolicy(policy: abi.InteropPolicy) PolicyError!void {
    try requireVolatileMmioScope(try scopeFromInteropPolicy(policy));
}

pub fn requireInteropPolicyBytes(unsafe_scope: u8, reserved: u8) PolicyError!void {
    try requireVolatileMmioScope(try scopeFromInteropPolicyBytes(unsafe_scope, reserved));
}

pub fn requireInteropPolicyByte(unsafe_scope: u8) PolicyError!void {
    try requireInteropPolicyBytes(unsafe_scope, 0);
}

pub fn read(comptime T: type, ptr: *const volatile T) T {
    return ptr.*;
}

pub fn write(comptime T: type, ptr: *volatile T, value: T) void {
    ptr.* = value;
}

pub fn exchange(comptime T: type, ptr: *volatile T, value: T) T {
    const before = read(T, @ptrCast(ptr));
    write(T, ptr, value);
    return before;
}

pub fn writeMasked(comptime T: type, ptr: *volatile T, clear_mask: T, set_mask: T) T {
    const before = read(T, @ptrCast(ptr));
    const after = (before & ~clear_mask) | set_mask;
    write(T, ptr, after);
    return after;
}

pub fn readScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *const volatile T) PolicyError!T {
    try requireVolatileMmioScope(scope);
    return read(T, ptr);
}

pub fn writeScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *volatile T, value: T) PolicyError!void {
    try requireVolatileMmioScope(scope);
    write(T, ptr, value);
}

pub fn exchangeScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *volatile T, value: T) PolicyError!T {
    try requireVolatileMmioScope(scope);
    return exchange(T, ptr, value);
}

pub fn writeMaskedScoped(
    comptime T: type,
    scope: abi.UnsafeScope,
    ptr: *volatile T,
    clear_mask: T,
    set_mask: T,
) PolicyError!T {
    try requireVolatileMmioScope(scope);
    return writeMasked(T, ptr, clear_mask, set_mask);
}

pub fn readInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *const volatile T) PolicyError!T {
    try requireInteropPolicy(policy);
    return read(T, ptr);
}

pub fn writeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!void {
    try requireInteropPolicy(policy);
    write(T, ptr, value);
}

pub fn exchangeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!T {
    try requireInteropPolicy(policy);
    return exchange(T, ptr, value);
}

pub fn writeMaskedInteropPolicy(
    comptime T: type,
    policy: abi.InteropPolicy,
    ptr: *volatile T,
    clear_mask: T,
    set_mask: T,
) PolicyError!T {
    try requireInteropPolicy(policy);
    return writeMasked(T, ptr, clear_mask, set_mask);
}

pub fn readInteropPolicyBytes(
    comptime T: type,
    unsafe_scope: u8,
    reserved: u8,
    ptr: *const volatile T,
) PolicyError!T {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return read(T, ptr);
}

pub fn writeInteropPolicyBytes(
    comptime T: type,
    unsafe_scope: u8,
    reserved: u8,
    ptr: *volatile T,
    value: T,
) PolicyError!void {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    write(T, ptr, value);
}

pub fn exchangeInteropPolicyBytes(
    comptime T: type,
    unsafe_scope: u8,
    reserved: u8,
    ptr: *volatile T,
    value: T,
) PolicyError!T {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return exchange(T, ptr, value);
}

pub fn writeMaskedInteropPolicyBytes(
    comptime T: type,
    unsafe_scope: u8,
    reserved: u8,
    ptr: *volatile T,
    clear_mask: T,
    set_mask: T,
) PolicyError!T {
    try requireInteropPolicyBytes(unsafe_scope, reserved);
    return writeMasked(T, ptr, clear_mask, set_mask);
}

test "phase3 mmio helper keeps volatile register reads and writes reviewable" {
    var register: u32 = 0x1234_5678;
    const register_ptr: *volatile u32 = @ptrCast(&register);

    try std.testing.expectEqual(@as(u32, 0x1234_5678), read(u32, register_ptr));
    write(u32, register_ptr, 0xCAFE_BABE);
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), register);
}

test "phase3 mmio helper keeps exchange-style register updates explicit" {
    var register: u16 = 0x1002;
    const register_ptr: *volatile u16 = @ptrCast(&register);

    try std.testing.expectEqual(@as(u16, 0x1002), exchange(u16, register_ptr, 0xBEEF));
    try std.testing.expectEqual(@as(u16, 0xBEEF), register);
}

test "phase3 mmio helper keeps masked register updates reviewable" {
    var register: u8 = 0b1011_0101;
    const register_ptr: *volatile u8 = @ptrCast(&register);

    try std.testing.expectEqual(
        @as(u8, 0b1001_0110),
        writeMasked(u8, register_ptr, 0b0011_0001, 0b0001_0010),
    );
    try std.testing.expectEqual(@as(u8, 0b1001_0110), register);
}

test "phase3 mmio helper keeps policy allowance predicates explicit" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const no_unsafe_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    try std.testing.expect(allowsVolatileMmioScope(.volatile_mmio));
    try std.testing.expect(!allowsVolatileMmioScope(.none));
    try std.testing.expect(!allowsVolatileMmioScope(.raw_pointer_bridge));

    try std.testing.expect(allowsInteropPolicy(mmio_policy));
    try std.testing.expect(!allowsInteropPolicy(no_unsafe_policy));
    try std.testing.expect(!allowsInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!allowsInteropPolicy(reserved_policy));

    try std.testing.expect(allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 0));
    try std.testing.expect(!allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.none), 0));
    try std.testing.expect(!allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge), 0));
    try std.testing.expect(!allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 1));

    try std.testing.expect(allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.volatile_mmio)));
    try std.testing.expect(!allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.none)));
    try std.testing.expect(!allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge)));
}

test "phase3 mmio helper keeps policy require helpers explicit" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const no_unsafe_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    try requireInteropPolicy(mmio_policy);
    try std.testing.expectError(error.UnsafeScopeDenied, requireInteropPolicy(no_unsafe_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, requireInteropPolicy(raw_pointer_policy));
    try std.testing.expectError(error.InvalidInteropPolicy, requireInteropPolicy(reserved_policy));

    try requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 0);
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.none), 0),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge), 0),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 1),
    );

    try requireInteropPolicyByte(@intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        requireInteropPolicyByte(@intFromEnum(abi.UnsafeScope.none)),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        requireInteropPolicyByte(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge)),
    );
}

test "phase3 mmio helper keeps typed scope require gate explicit" {
    try requireVolatileMmioScope(.volatile_mmio);
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioScope(.none));
    try std.testing.expectError(error.UnsafeScopeDenied, requireVolatileMmioScope(.raw_pointer_bridge));
}

test "phase3 mmio helper keeps 64-bit const reads and masked updates reviewable" {
    var register: u64 = 0x1234_5678_9ABC_DEF0;
    const register_ptr: *volatile u64 = @ptrCast(&register);
    const const_register_ptr: *const volatile u64 = @ptrCast(&register);

    try std.testing.expectEqual(@as(u64, 0x1234_5678_9ABC_DEF0), read(u64, const_register_ptr));
    try std.testing.expectEqual(@as(u64, 0x1234_5678_9ABC_DEF0), exchange(u64, register_ptr, 0x0F0E_0D0C_0B0A_0908));
    try std.testing.expectEqual(@as(u64, 0x0F0E_0D0C_0B0A_0908), register);

    write(u64, register_ptr, 0x1234_5678_9ABC_DEF0);
    try std.testing.expectEqual(
        @as(u64, 0x1255_5678_9A11_DEA0),
        writeMasked(u64, register_ptr, 0x00FF_0000_00FF_00F0, 0x0055_0000_0011_00A0),
    );
    try std.testing.expectEqual(@as(u64, 0x1255_5678_9A11_DEA0), register);
    try std.testing.expectEqual(@as(u64, 0x1255_5678_9A11_DEA0), read(u64, const_register_ptr));
}

test "phase3 mmio helper gates volatile access through typed unsafe scope" {
    var register: u32 = 0xAABB_CCDD;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);

    try std.testing.expectError(error.UnsafeScopeDenied, readScoped(u32, .none, const_register_ptr));
    try std.testing.expectError(error.UnsafeScopeDenied, writeScoped(u32, .raw_pointer_bridge, register_ptr, 0x1111_2222));
    try std.testing.expectEqual(@as(u32, 0xAABB_CCDD), try readScoped(u32, .volatile_mmio, const_register_ptr));
    try writeScoped(u32, .volatile_mmio, register_ptr, 0x1234_5678);
    try std.testing.expectEqual(@as(u32, 0x1234_5678), register);
    try std.testing.expectEqual(@as(u32, 0x1234_5678), try exchangeScoped(u32, .volatile_mmio, register_ptr, 0xCAFE_BABE));
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), register);
}

test "phase3 mmio helper gates volatile access through interop policy records" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    var register: u16 = 0x0F00;
    const register_ptr: *volatile u16 = @ptrCast(&register);
    const const_register_ptr: *const volatile u16 = @ptrCast(&register);

    try std.testing.expectError(error.InvalidInteropPolicy, readInteropPolicy(u16, reserved_policy, const_register_ptr));
    try std.testing.expectError(error.UnsafeScopeDenied, readInteropPolicy(u16, raw_pointer_policy, const_register_ptr));

    try std.testing.expectEqual(@as(u16, 0x0F00), try readInteropPolicy(u16, mmio_policy, const_register_ptr));
    try writeInteropPolicy(u16, mmio_policy, register_ptr, 0x00F0);
    try std.testing.expectEqual(@as(u16, 0x00F0), register);
    try std.testing.expectEqual(@as(u16, 0x00F0), try exchangeInteropPolicy(u16, mmio_policy, register_ptr, 0xF000));
    try std.testing.expectEqual(@as(u16, 0xF000), register);

    try std.testing.expectError(error.InvalidInteropPolicy, readInteropPolicyBytes(u16, @intFromEnum(abi.UnsafeScope.volatile_mmio), 1, const_register_ptr));
    try std.testing.expectError(error.UnsafeScopeDenied, writeInteropPolicyBytes(u16, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge), 0, register_ptr, 0xAAAA));
    try std.testing.expectEqual(
        @as(u16, 0xF00F),
        try writeMaskedInteropPolicyBytes(
            u16,
            @intFromEnum(abi.UnsafeScope.volatile_mmio),
            0,
            register_ptr,
            0x00F0,
            0x000F,
        ),
    );
    try std.testing.expectEqual(@as(u16, 0xF00F), register);
}

test "phase3 mmio helper keeps scoped masked writes and byte-policy exchanges explicit" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    var register: u16 = 0x0FF0;
    const register_ptr: *volatile u16 = @ptrCast(&register);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        writeMaskedScoped(u16, .raw_pointer_bridge, register_ptr, 0x00F0, 0x0005),
    );
    try std.testing.expectEqual(@as(u16, 0x0FF0), register);

    try std.testing.expectEqual(
        @as(u16, 0x0F05),
        try writeMaskedScoped(u16, .volatile_mmio, register_ptr, 0x00F0, 0x0005),
    );
    try std.testing.expectEqual(@as(u16, 0x0F05), register);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        exchangeInteropPolicyBytes(u16, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge), 0, register_ptr, 0x5500),
    );
    try std.testing.expectEqual(@as(u16, 0x0F05), register);

    try std.testing.expectEqual(
        @as(u16, 0x0F05),
        try exchangeInteropPolicyBytes(u16, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0, register_ptr, 0x5500),
    );
    try std.testing.expectEqual(@as(u16, 0x5500), register);

    try std.testing.expectError(
        error.InvalidInteropPolicy,
        writeMaskedInteropPolicy(u16, reserved_policy, register_ptr, 0x0F00, 0x00A0),
    );
    try std.testing.expectEqual(@as(u16, 0x5500), register);

    try std.testing.expectEqual(
        @as(u16, 0x50A0),
        try writeMaskedInteropPolicy(u16, mmio_policy, register_ptr, 0x0F00, 0x00A0),
    );
    try std.testing.expectEqual(@as(u16, 0x50A0), register);
}

test "phase3 mmio helper keeps interop-policy reads and writes routed through require helpers" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    var register: u16 = 0x0F00;
    const register_ptr: *volatile u16 = @ptrCast(&register);
    const const_register_ptr: *const volatile u16 = @ptrCast(&register);

    try std.testing.expectEqual(@as(u16, 0x0F00), try readInteropPolicy(u16, mmio_policy, const_register_ptr));
    try writeInteropPolicy(u16, mmio_policy, register_ptr, 0x00F0);
    try std.testing.expectEqual(@as(u16, 0x00F0), register);
    try std.testing.expectEqual(@as(u16, 0x00F0), try exchangeInteropPolicyBytes(
        u16,
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        0,
        register_ptr,
        0xF000,
    ));
    try std.testing.expectEqual(@as(u16, 0xF000), register);

    try std.testing.expectError(error.InvalidInteropPolicy, readInteropPolicy(u16, reserved_policy, const_register_ptr));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        writeInteropPolicyBytes(u16, @intFromEnum(abi.UnsafeScope.none), 0, register_ptr, 0xAAAA),
    );
}