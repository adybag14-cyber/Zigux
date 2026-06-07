const std = @import("std");
const mmio = @import("mmio_helper");
const abi = @import("abi_bindings");

const mmio_scope = 1;
const no_unsafe_scope = 0;
const raw_pointer_scope = 2;

const mmio_policy = abi.InteropPolicy{
    .panic_mode = 0,
    .allocator_mode = 0,
    .unsafe_scope = mmio_scope,
    .reserved = 0,
};

test "range view records policy-gated base length and stride" {
    var bytes: [32]u8 align(@alignOf(u64)) = @splat(0);
    const base_addr = @intFromPtr(&bytes[0]);

    const scoped = try mmio.rangeScoped(base_addr, 24, 4, .volatile_mmio);
    try std.testing.expectEqual(base_addr, scoped.base_addr);
    try std.testing.expectEqual(@as(u32, 24), scoped.length);
    try std.testing.expectEqual(@as(u32, 4), scoped.stride);

    const from_policy = try mmio.rangeInteropPolicy(base_addr + 4, 16, 8, mmio_policy);
    try std.testing.expectEqual(base_addr + 4, from_policy.base_addr);
    try std.testing.expectEqual(@as(u32, 16), from_policy.length);
    try std.testing.expectEqual(@as(u32, 8), from_policy.stride);

    const from_bytes = try mmio.rangeInteropPolicyBytes(base_addr + 8, 12, 0, mmio_scope, 0);
    try std.testing.expectEqual(base_addr + 8, from_bytes.base_addr);
    try std.testing.expectEqual(@as(u32, 12), from_bytes.length);
    try std.testing.expectEqual(@as(u32, 0), from_bytes.stride);

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeScoped(base_addr, 8, 4, .none));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeScoped(base_addr, 8, 4, .raw_pointer_bridge));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicyBytes(base_addr, 8, 4, no_unsafe_scope, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicyBytes(base_addr, 8, 4, raw_pointer_scope, 0));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.rangeInteropPolicyBytes(base_addr, 8, 4, mmio_scope, 1));
}

test "range view accessors enforce stride width and bounds before touching storage" {
    var bytes: [24]u8 align(@alignOf(u64)) = @splat(0);
    const base_addr = @intFromPtr(&bytes[0]);
    const range = try mmio.rangeInteropPolicyByte(base_addr, 24, 4, mmio_scope);

    try mmio.writeAt(u32, range, 4, 0x1122_3344);
    try std.testing.expectEqual(@as(u32, 0x1122_3344), try mmio.readAt(u32, range, 4));
    try std.testing.expectEqual(@as(u32, 0x1122_3344), try mmio.exchangeAt(u32, range, 4, 0x5566_7788));
    try std.testing.expectEqual(@as(u32, 0x5566_7788), try mmio.readAt(u32, range, 4));

    try std.testing.expectEqual(
        @as(u32, 0x5500_0088),
        try mmio.writeMaskedAt(u32, range, 4, 0x00FF_FF00, 0x5500_0088),
    );
    try std.testing.expectEqual(@as(u32, 0x5500_0088), try mmio.readAt(u32, range, 4));

    const direct_ptr = try mmio.pointerAt(u32, range, 8);
    direct_ptr.* = 0xCAFE_BABE;
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), try mmio.readAt(u32, range, 8));

    try std.testing.expectError(error.InvalidInteropPolicy, mmio.constPointerAt(u16, range, 2));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.writeAt(u32, range, 2, 1));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.exchangeAt(u32, range, 22, 1));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.writeMaskedAt(u32, range, 21, 0, 1));
    try std.testing.expectEqual(@as(u32, 0x5500_0088), try mmio.readAt(u32, range, 4));
}

test "range view accepts tight zero-stride windows while preserving alignment and length checks" {
    var bytes: [16]u8 align(@alignOf(u64)) = @splat(0);
    const range = try mmio.rangeScoped(@intFromPtr(&bytes[0]), 16, 0, .volatile_mmio);

    try mmio.writeAt(u16, range, 2, 0xABCD);
    try mmio.writeAt(u16, range, 6, 0x1357);
    try std.testing.expectEqual(@as(u16, 0xABCD), try mmio.readAt(u16, range, 2));
    try std.testing.expectEqual(@as(u16, 0x1357), try mmio.readAt(u16, range, 6));

    try mmio.writeAt(u64, range, 8, 0x0123_4567_89AB_CDEF);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89AB_CDEF), try mmio.readAt(u64, range, 8));

    try std.testing.expectError(error.InvalidInteropPolicy, mmio.readAt(u16, range, 15));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.writeAt(u32, range, 14, 0xCAFE));
}

test "range view rejects overflowing windows before blessing MMIO access" {
    const near_end = std.math.maxInt(usize) - 3;

    const bounded = try mmio.rangeScoped(near_end, 4, 1, .volatile_mmio);
    try std.testing.expectEqual(near_end, bounded.base_addr);
    try std.testing.expectEqual(@as(u32, 4), bounded.length);
    try std.testing.expectEqual(@as(u32, 1), bounded.stride);

    try std.testing.expectError(error.InvalidInteropPolicy, mmio.rangeScoped(near_end, 5, 1, .volatile_mmio));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.rangeInteropPolicy(near_end, 5, 1, mmio_policy));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.rangeInteropPolicyBytes(near_end, 5, 1, mmio_scope, 0));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.rangeInteropPolicyByte(near_end, 5, 1, mmio_scope));

    const empty = try mmio.rangeInteropPolicyByte(std.math.maxInt(usize), 0, 0, mmio_scope);
    try std.testing.expectEqual(std.math.maxInt(usize), empty.base_addr);
    try std.testing.expectEqual(@as(u32, 0), empty.length);
    try std.testing.expectEqual(@as(u32, 0), empty.stride);
}
