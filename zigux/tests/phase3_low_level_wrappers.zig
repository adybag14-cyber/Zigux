const std = @import("std");
const atomic = @import("atomic");
const barrier = @import("barrier");
const mmio = @import("mmio");
const unsafe_policy = @import("unsafe_policy");
const narrow = @import("narrow");

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

test "phase3 low-level wrappers keep raw-pointer bridge scope gates explicit beside MMIO policy gates" {
    const raw_scope = @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge);
    const mmio_scope = @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio);

    try std.testing.expect(unsafe_policy.permitsRawPointerBridgeByte(raw_scope));
    try std.testing.expect(!unsafe_policy.permitsRawPointerBridgeByte(mmio_scope));
    try std.testing.expect(narrow.permitsRawPointerBridge(.raw_pointer_bridge));
    try std.testing.expect(!narrow.permitsRawPointerBridge(.volatile_mmio));

    var bridge_words = [_]u32{ 0x1122_3344, 0x5566_7788 };
    const bridge_addr = @intFromPtr(&bridge_words[0]);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.pointerAtByte(u32, bridge_addr, @sizeOf(u32), mmio_scope),
    );

    const bridge_ptr = try narrow.pointerAtByte(u32, bridge_addr, @sizeOf(u32), raw_scope);
    barrier.release();
    bridge_ptr.* = 0xAABB_CCDD;
    barrier.acquire();
    try std.testing.expectEqual(@as(u32, 0xAABB_CCDD), bridge_words[0]);

    const bridge_slice = try narrow.constSliceAtByte(u32, bridge_addr, bridge_words.len, raw_scope);
    try std.testing.expectEqual(@as(u32, 0x5566_7788), bridge_slice[1]);
}

test "phase3 low-level wrappers keep raw-pointer bridge byte coverage explicit" {
    const raw_scope = @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge);
    const safe_scope = @intFromEnum(narrow.UnsafeScopeTag.none);

    var bridge_word: u32 = 0xDEAD_BEEF;
    const bridge_addr = @intFromPtr(&bridge_word);

    try std.testing.expectError(
        error.ByteLengthTooSmall,
        narrow.pointerAtByte(u32, bridge_addr, @sizeOf(u16), raw_scope),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.writeValueAtByte(u32, bridge_addr, 0xCAFE_BABE, safe_scope),
    );

    try narrow.writeValueAtByte(u32, bridge_addr, 0xCAFE_BABE, raw_scope);
    barrier.fullFence();
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), bridge_word);
}
