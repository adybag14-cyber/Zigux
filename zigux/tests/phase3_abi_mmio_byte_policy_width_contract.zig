const std = @import("std");

const abi = @import("abi_bindings");
const mmio = @import("mmio_helpers");

fn mmioScope() u8 {
    return @intFromEnum(abi.UnsafeScope.volatile_mmio);
}

fn noUnsafeScope() u8 {
    return @intFromEnum(abi.UnsafeScope.none);
}

fn rawPointerScope() u8 {
    return @intFromEnum(abi.UnsafeScope.raw_pointer_bridge);
}

test "phase3 mmio byte-policy width aliases keep denied writes side-effect free" {
    var bytes: [16]u8 align(@alignOf(u64)) = @splat(0);
    const base_addr = @intFromPtr(&bytes[0]);
    const scope = mmioScope();

    try mmio.write8InteropPolicyByte(base_addr, 0, 0x11, scope);
    try mmio.write16InteropPolicyByte(base_addr, 2, 0x2233, scope);
    try mmio.write32InteropPolicyByte(base_addr, 4, 0x4455_6677, scope);
    try mmio.write64InteropPolicyByte(base_addr, 8, 0x8899_AABB_CCDD_EEFF, scope);

    const before = bytes;

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8InteropPolicyByte(base_addr, 0, 0xAA, noUnsafeScope()));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16InteropPolicyByte(base_addr, 2, 0xAAAA, rawPointerScope()));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.write32InteropPolicyBytes(base_addr, 4, 0xAAAA_AAAA, scope, 1));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.write64InteropPolicyBytes(base_addr, 8, 0xAAAA_AAAA_AAAA_AAAA, scope, 1));

    try std.testing.expectEqualSlices(u8, &before, &bytes);
}

test "phase3 mmio byte-policy width aliases keep denied exchanges side-effect free" {
    var register: u64 = 0x0123_4567_89AB_CDEF;
    const base_addr = @intFromPtr(&register);
    const scope = mmioScope();

    try std.testing.expectEqual(@as(u64, 0x0123_4567_89AB_CDEF), try mmio.read64InteropPolicyByte(base_addr, 0, scope));

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.exchangeInteropPolicyByte(u64, noUnsafeScope(), @ptrCast(&register), 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.exchangeInteropPolicyBytes(u64, rawPointerScope(), 0, @ptrCast(&register), 0));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.exchangeInteropPolicyBytes(u64, scope, 1, @ptrCast(&register), 0));

    try std.testing.expectEqual(@as(u64, 0x0123_4567_89AB_CDEF), register);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89AB_CDEF), try mmio.exchangeInteropPolicyByte(u64, scope, @ptrCast(&register), 0x0FED_CBA9_8765_4321));
    try std.testing.expectEqual(@as(u64, 0x0FED_CBA9_8765_4321), register);
}

test "phase3 mmio byte-policy width aliases enforce alignment before volatile reads" {
    var bytes: [16]u8 align(@alignOf(u64)) = @splat(0);
    const base_addr = @intFromPtr(&bytes[0]);
    const scope = mmioScope();

    try mmio.write16InteropPolicyByte(base_addr, 2, 0x1020, scope);
    try mmio.write32InteropPolicyByte(base_addr, 4, 0x3040_5060, scope);
    try mmio.write64InteropPolicyByte(base_addr, 8, 0x7080_90A0_B0C0_D0E0, scope);

    try std.testing.expectEqual(@as(u16, 0x1020), try mmio.read16InteropPolicyByte(base_addr, 2, scope));
    try std.testing.expectEqual(@as(u32, 0x3040_5060), try mmio.read32InteropPolicyByte(base_addr, 4, scope));
    try std.testing.expectEqual(@as(u64, 0x7080_90A0_B0C0_D0E0), try mmio.read64InteropPolicyByte(base_addr, 8, scope));

    try std.testing.expectError(error.InvalidInteropPolicy, mmio.read16InteropPolicyByte(base_addr, 1, scope));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.read32InteropPolicyByte(base_addr, 2, scope));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.read64InteropPolicyByte(base_addr, 4, scope));
}

test "phase3 mmio byte-policy width aliases keep masked writes gated" {
    var register: u32 = 0xFF00_00FF;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const scope = mmioScope();

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.writeMaskedInteropPolicyByte(u32, noUnsafeScope(), register_ptr, 0x00FF_0000, 0x0055_0000),
    );
    try std.testing.expectEqual(@as(u32, 0xFF00_00FF), register);

    try std.testing.expectError(
        error.InvalidInteropPolicy,
        mmio.writeMaskedInteropPolicyBytes(u32, scope, 1, register_ptr, 0x00FF_0000, 0x0055_0000),
    );
    try std.testing.expectEqual(@as(u32, 0xFF00_00FF), register);

    try std.testing.expectEqual(
        @as(u32, 0xFF55_00FF),
        try mmio.writeMaskedInteropPolicyByte(u32, scope, register_ptr, 0x00FF_0000, 0x0055_0000),
    );
    try std.testing.expectEqual(@as(u32, 0xFF55_00FF), register);
}
