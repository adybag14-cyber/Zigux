const std = @import("std");
const atomic = @import("atomic");
const barrier = @import("barrier");
const mmio = @import("mmio");

test "phase3 low-level wrappers keep atomic ordering, barriers, and MMIO handoffs aligned" {
    var cell: u32 = 7;
    const previous = try atomic.compareExchangeStrong(u32, &cell, 7, 13, .acq_rel, .acquire);
    try std.testing.expectEqual(@as(?u32, null), previous);

    barrier.compiler();
    barrier.release();

    var register: u32 = 0;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    mmio.write(u32, register_ptr, cell);

    barrier.acquire();
    try std.testing.expectEqual(@as(u32, 13), mmio.read(u32, register_ptr));
}

test "phase3 low-level wrappers keep masked MMIO updates explicit after compare-exchange setup" {
    var state: u16 = 0x00F0;
    try std.testing.expectEqual(
        @as(?u16, null),
        try atomic.compareExchangeWeak(u16, &state, 0x00F0, 0x0FF0, .seq_cst, .acquire),
    );

    var register: u16 = state;
    const register_ptr: *volatile u16 = @ptrCast(&register);
    const updated = mmio.writeMasked(u16, register_ptr, 0x00F0, 0x0005);

    barrier.fullFence();
    try std.testing.expectEqual(@as(u16, 0x0F05), updated);
    try std.testing.expectEqual(updated, register);
    try std.testing.expectEqual(@as(?atomic.Ordering, .seq_cst), atomic.strongestAllowedFailureOrder(.seq_cst));
}

test "phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff" {
    var state: u32 = 0x0040_0004;
    try std.testing.expectEqual(
        @as(?u32, null),
        try atomic.compareExchangeStrong(u32, &state, 0x0040_0004, 0x00AA_5501, .acq_rel, .acquire),
    );

    barrier.release();

    var register: u32 = 0;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.writeInteropPolicyBytes(u32, 0, 0, register_ptr, state),
    );
    try std.testing.expectError(
        error.InvalidInteropPolicy,
        mmio.readInteropPolicyBytes(u32, 1, 1, const_register_ptr),
    );
    try std.testing.expectEqual(@as(u32, 0), register);

    try mmio.writeInteropPolicyBytes(u32, 1, 0, register_ptr, state);
    barrier.acquire();
    try std.testing.expectEqual(
        @as(u32, 0x00AA_5501),
        try mmio.readInteropPolicyBytes(u32, 1, 0, const_register_ptr),
    );

    const updated = try mmio.writeMaskedInteropPolicyBytes(
        u32,
        1,
        0,
        register_ptr,
        0x0000_FF00,
        0x0000_3300,
    );
    barrier.fullFence();
    try std.testing.expectEqual(@as(u32, 0x00AA_3301), updated);
    try std.testing.expectEqual(updated, register);
}

test "phase3 low-level wrappers keep MMIO byte-policy shorthand aligned with reserved-byte gates" {
    try std.testing.expect(mmio.allowsInteropPolicyByte(1));
    try std.testing.expect(mmio.allowsInteropPolicyBytes(1, 0));
    try mmio.requireInteropPolicyByte(1);
    try mmio.requireInteropPolicyBytes(1, 0);

    try std.testing.expect(!mmio.allowsInteropPolicyByte(0));
    try std.testing.expect(!mmio.allowsInteropPolicyBytes(0, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.requireInteropPolicyByte(0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.requireInteropPolicyBytes(0, 0));

    try std.testing.expect(!mmio.allowsInteropPolicyByte(2));
    try std.testing.expect(!mmio.allowsInteropPolicyBytes(2, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.requireInteropPolicyByte(2));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.requireInteropPolicyBytes(2, 0));

    try std.testing.expect(!mmio.allowsInteropPolicyBytes(1, 1));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.requireInteropPolicyBytes(1, 1));
}

test "phase3 low-level wrappers keep atomic load-store exchange and MMIO echo explicit" {
    var state: u8 = 0b1111_0000;

    try atomic.store(u8, &state, 0b1100_1100, .release);
    barrier.compiler();
    try std.testing.expectEqual(@as(u8, 0b1100_1100), try atomic.load(u8, &state, .acquire));

    try std.testing.expectEqual(@as(u8, 0b1100_1100), try atomic.exchange(u8, &state, 0b1010_1010, .acq_rel));
    try std.testing.expectEqual(@as(u8, 0b1010_1010), state);

    try std.testing.expectEqual(@as(u8, 0b1010_1010), try atomic.fetchNand(u8, &state, 0b1111_0000, .seq_cst));
    try std.testing.expectEqual(@as(u8, 0b0101_1111), state);

    var register: u8 = 0;
    const register_ptr: *volatile u8 = @ptrCast(&register);
    const const_register_ptr: *const volatile u8 = @ptrCast(&register);
    barrier.release();
    mmio.write(u8, register_ptr, state);
    barrier.acquire();
    try std.testing.expectEqual(@as(u8, 0b0101_1111), mmio.read(u8, const_register_ptr));
    try std.testing.expectEqual(@as(?atomic.Ordering, .monotonic), atomic.weakestAllowedFailureOrder(.seq_cst));
}

test "phase3 low-level wrappers keep exchange-style MMIO policy handoffs explicit" {
    var register: u16 = 0x55AA;
    const register_ptr: *volatile u16 = @ptrCast(&register);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.exchangeInteropPolicyBytes(u16, 0, 0, register_ptr, 0x0F0F),
    );
    try std.testing.expectEqual(
        @as(u16, 0x55AA),
        try mmio.exchangeInteropPolicyBytes(u16, 1, 0, register_ptr, 0x0F0F),
    );
    barrier.acquireRelease();
    try std.testing.expectEqual(@as(u16, 0x0F0F), register);
}
