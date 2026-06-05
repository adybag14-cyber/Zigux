const std = @import("std");

const abi = @import("abi_bindings");
const mmio = @import("mmio_helpers");

fn mmioScopeByte() u8 {
    return @intFromEnum(abi.UnsafeScope.volatile_mmio);
}

fn noneScopeByte() u8 {
    return @intFromEnum(abi.UnsafeScope.none);
}

fn rawPointerScopeByte() u8 {
    return @intFromEnum(abi.UnsafeScope.raw_pointer_bridge);
}

test "phase3 mmio range contract keeps byte-policy construction fail closed" {
    var bytes: [16]u8 align(@alignOf(u32)) = @splat(0);
    const base_addr = @intFromPtr(&bytes[0]);

    const range = try mmio.rangeInteropPolicyByte(base_addr, bytes.len, 4, mmioScopeByte());
    try std.testing.expectEqual(base_addr, range.base_addr);
    try std.testing.expectEqual(@as(u32, bytes.len), range.length);
    try std.testing.expectEqual(@as(u32, 4), range.stride);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.rangeInteropPolicyByte(base_addr, bytes.len, 4, noneScopeByte()),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.rangeInteropPolicyByte(base_addr, bytes.len, 4, rawPointerScopeByte()),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        mmio.rangeInteropPolicyBytes(base_addr, bytes.len, 4, mmioScopeByte(), 1),
    );
}

test "phase3 mmio range contract keeps range-bound read write exchange and mask paths explicit" {
    var bytes: [16]u8 align(@alignOf(u32)) = @splat(0);
    const range = try mmio.rangeScoped(@intFromPtr(&bytes[0]), bytes.len, 4, .volatile_mmio);

    try mmio.writeAt(u32, range, 4, 0x1122_3344);
    try std.testing.expectEqual(@as(u32, 0x1122_3344), try mmio.readAt(u32, range, 4));

    try std.testing.expectEqual(@as(u32, 0x1122_3344), try mmio.exchangeAt(u32, range, 4, 0x5566_7788));
    try std.testing.expectEqual(@as(u32, 0x5566_7788), try mmio.readAt(u32, range, 4));

    try std.testing.expectEqual(
        @as(u32, 0x5500_0088),
        try mmio.writeMaskedAt(u32, range, 4, 0x00FF_FF00, 0x5500_0088),
    );
    try std.testing.expectEqual(@as(u32, 0x5500_0088), try mmio.readAt(u32, range, 4));

    try std.testing.expectError(error.InvalidInteropPolicy, mmio.readAt(u32, range, 2));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.writeAt(u32, range, 13, 1));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.exchangeAt(u32, range, 14, 1));
    try std.testing.expectEqual(@as(u32, 0x5500_0088), try mmio.readAt(u32, range, 4));
}

test "phase3 mmio range contract keeps byte-width helpers side effect free when denied" {
    var bytes: [16]u8 align(@alignOf(u64)) = @splat(0);
    const base_addr = @intFromPtr(&bytes[0]);
    const mmio_scope = mmioScopeByte();

    try mmio.write16InteropPolicyByte(base_addr, 2, 0xABCD, mmio_scope);
    try std.testing.expectEqual(@as(u16, 0xABCD), try mmio.read16InteropPolicyByte(base_addr, 2, mmio_scope));

    try mmio.write32InteropPolicyBytes(base_addr, 4, 0xC001_D00D, mmio_scope, 0);
    try std.testing.expectEqual(@as(u32, 0xC001_D00D), try mmio.read32InteropPolicyBytes(base_addr, 4, mmio_scope, 0));

    try mmio.write64InteropPolicyByte(base_addr, 8, 0x0123_4567_89AB_CDEF, mmio_scope);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89AB_CDEF), try mmio.read64InteropPolicyByte(base_addr, 8, mmio_scope));

    try std.testing.expectError(error.InvalidInteropPolicy, mmio.read16InteropPolicyBytes(base_addr, 3, mmio_scope, 0));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.read32InteropPolicyBytes(base_addr, 4, mmio_scope, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64InteropPolicyByte(base_addr, 8, 0, noneScopeByte()));
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89AB_CDEF), try mmio.read64InteropPolicyByte(base_addr, 8, mmio_scope));
}
