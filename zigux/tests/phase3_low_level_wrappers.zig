const std = @import("std");
const atomic = @import("atomic");
const barrier = @import("barrier");
const layout_assert = @import("layout_assert");
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

test "phase3 low-level wrappers keep helper-local MMIO layout assertions explicit" {
    try layout_assert.assertMmioRangeLayout();
}

test "phase3 low-level wrappers keep masked MMIO updates explicit after compare-exchange setup" {
    var state: u16 = 0x00F0;
    try std.testing.expectEqual(@as(?u16, null), try atomic.compareExchangeWeak(u16, &state, 0x00F0, 0x0FF0, .seq_cst, .acquire));

    var register: u16 = state;
    const register_ptr: *volatile u16 = @ptrCast(&register);
    const updated = mmio.writeMasked(u16, register_ptr, 0x00F0, 0x0005);

    try std.testing.expect(barrier.fenceOrderAllowed(.seq_cst));
    try std.testing.expect(!barrier.fenceOrderAllowed(.monotonic));
    try barrier.fence(.seq_cst);
    try std.testing.expectError(error.InvalidFenceOrdering, barrier.fence(.monotonic));
    barrier.storeLoad();
    try std.testing.expectEqual(@as(u16, 0x0F05), updated);
    try std.testing.expectEqual(updated, register);
    try std.testing.expectEqual(@as(?atomic.Ordering, .seq_cst), atomic.strongestAllowedFailureOrder(.seq_cst));
}

test "phase3 low-level wrappers keep monotonic strong compare-exchange mismatch explicit before MMIO publish" {
    var state: u32 = 0x10;

    try std.testing.expectEqual(
        @as(?u32, null),
        try atomic.compareExchangeStrong(u32, &state, 0x10, 0x20, .monotonic, .monotonic),
    );
    try std.testing.expectEqual(@as(u32, 0x20), state);

    try std.testing.expectEqual(
        @as(?u32, 0x20),
        try atomic.compareExchangeStrong(u32, &state, 0x10, 0x30, .monotonic, .monotonic),
    );
    try std.testing.expectEqual(@as(u32, 0x20), state);

    try std.testing.expectEqual(@as(?atomic.Ordering, .monotonic), atomic.weakestAllowedFailureOrder(.monotonic));
    try std.testing.expectEqual(@as(?atomic.Ordering, .monotonic), atomic.strongestAllowedFailureOrder(.monotonic));

    var register: u32 = 0;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);

    barrier.release();
    mmio.write(u32, register_ptr, state);
    barrier.acquire();
    try std.testing.expectEqual(@as(u32, 0x20), mmio.read(u32, const_register_ptr));
}

test "phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff" {
    var state: u32 = 0x0040_0004;
    try std.testing.expectEqual(@as(?u32, null), try atomic.compareExchangeStrong(u32, &state, 0x0040_0004, 0x00AA_5501, .acq_rel, .acquire));

    barrier.release();

    var register: u32 = 0;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeInteropPolicyBytes(u32, 0, 0, register_ptr, state));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.readInteropPolicyBytes(u32, 1, 1, const_register_ptr));
    try std.testing.expectEqual(@as(u32, 0), register);

    try mmio.writeInteropPolicyBytes(u32, 1, 0, register_ptr, state);
    barrier.acquire();
    try std.testing.expectEqual(@as(u32, 0x00AA_5501), try mmio.readInteropPolicyBytes(u32, 1, 0, const_register_ptr));

    const updated = try mmio.writeMaskedInteropPolicyBytes(u32, 1, 0, register_ptr, 0x0000_FF00, 0x0000_3300);
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

test "phase3 low-level wrappers keep MMIO single-byte interop-policy shorthands explicit" {
    var register: u32 = 0x00AA_5500;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);

    try std.testing.expectEqual(@as(u32, 0x00AA_5500), try mmio.readInteropPolicyByte(u32, 1, const_register_ptr));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.readInteropPolicyByte(u32, 0, const_register_ptr));

    try mmio.writeInteropPolicyByte(u32, 1, register_ptr, 0x1234_5678);
    barrier.release();
    try std.testing.expectEqual(@as(u32, 0x1234_5678), register);
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeInteropPolicyByte(u32, 2, register_ptr, 0));

    try std.testing.expectEqual(@as(u32, 0x1234_5678), try mmio.exchangeInteropPolicyByte(u32, 1, register_ptr, 0xCAFE_BABE));
    barrier.acquireRelease();
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), register);
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.exchangeInteropPolicyByte(u32, 0, register_ptr, 0));

    const updated = try mmio.writeMaskedInteropPolicyByte(u32, 1, register_ptr, 0x00F0_0FF0, 0x000E_000E);
    barrier.fullFence();
    try std.testing.expectEqual(@as(u32, 0xCA0E_B00E), updated);
    try std.testing.expectEqual(updated, register);
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeMaskedInteropPolicyByte(u32, 2, register_ptr, 0xFFFF_0000, 0));
}

test "phase3 low-level wrappers keep whole-record MMIO interop-policy helpers explicit" {
    const InteropPolicy = @typeInfo(@TypeOf(mmio.readInteropPolicy)).@"fn".params[1].type.?;
    const mmio_policy = InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio),
        .reserved = 0,
    };
    const denied_policy = InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(narrow.UnsafeScopeTag.none),
        .reserved = 0,
    };

    try std.testing.expect(mmio.allowsInteropPolicy(mmio_policy));
    try std.testing.expect(!mmio.allowsInteropPolicy(denied_policy));

    var register: u32 = 0xABCD_0001;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.readInteropPolicy(u32, denied_policy, const_register_ptr));
    try std.testing.expectEqual(@as(u32, 0xABCD_0001), try mmio.readInteropPolicy(u32, mmio_policy, const_register_ptr));

    try mmio.writeInteropPolicy(u32, mmio_policy, register_ptr, 0x1234_5678);
    barrier.release();
    try std.testing.expectEqual(@as(u32, 0x1234_5678), register);

    try std.testing.expectEqual(@as(u32, 0x1234_5678), try mmio.exchangeInteropPolicy(u32, mmio_policy, register_ptr, 0xFFFF_00FF));
    barrier.acquireRelease();
    try std.testing.expectEqual(@as(u32, 0xFFFF_00FF), register);

    const updated = try mmio.writeMaskedInteropPolicy(u32, mmio_policy, register_ptr, 0x00FF_00FF, 0x0055_0033);
    barrier.fullFence();
    try std.testing.expectEqual(@as(u32, 0xFF55_0033), updated);
    try std.testing.expectEqual(updated, register);
}

test "phase3 low-level wrappers keep direct MMIO scope gates explicit" {
    const mmio_scope = narrow.UnsafeScopeTag.volatile_mmio;
    const none_scope = narrow.UnsafeScopeTag.none;
    const raw_scope = narrow.UnsafeScopeTag.raw_pointer_bridge;

    var register: u32 = 0x0102_0304;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.readScoped(u32, none_scope, const_register_ptr));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeScoped(u32, raw_scope, register_ptr, 0xAABB_CCDD));
    try std.testing.expectEqual(@as(u32, 0x0102_0304), register);

    try std.testing.expectEqual(@as(u32, 0x0102_0304), try mmio.readScoped(u32, mmio_scope, const_register_ptr));

    try mmio.writeScoped(u32, mmio_scope, register_ptr, 0xAABB_CCDD);
    barrier.release();
    try std.testing.expectEqual(@as(u32, 0xAABB_CCDD), register);

    try std.testing.expectEqual(@as(u32, 0xAABB_CCDD), try mmio.exchangeScoped(u32, mmio_scope, register_ptr, 0xFFFF_00FF));
    barrier.acquireRelease();
    try std.testing.expectEqual(@as(u32, 0xFFFF_00FF), register);

    const updated = try mmio.writeMaskedScoped(u32, mmio_scope, register_ptr, 0x00FF_0F0F, 0x0055_0033);
    barrier.fullFence();
    try std.testing.expectEqual(@as(u32, 0xFF55_00F3), updated);
    try std.testing.expectEqual(updated, register);
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
    try std.testing.expectEqual(@as(u8, 0b0101_1111), try atomic.fetchNand(u8, &state, 0b0000_1111, .monotonic));
    try std.testing.expectEqual(@as(u8, 0b1111_0000), state);

    var register: u8 = 0;
    const register_ptr: *volatile u8 = @ptrCast(&register);
    const const_register_ptr: *const volatile u8 = @ptrCast(&register);
    barrier.release();
    mmio.write(u8, register_ptr, state);
    barrier.acquire();
    try std.testing.expectEqual(@as(u8, 0b1111_0000), mmio.read(u8, const_register_ptr));
    try std.testing.expectEqual(@as(?atomic.Ordering, .monotonic), atomic.weakestAllowedFailureOrder(.seq_cst));
}

test "phase3 low-level wrappers keep additive and bitwise atomic updates explicit before MMIO publish" {
    var state: u8 = 0x30;

    try std.testing.expectEqual(@as(u8, 0x30), try atomic.fetchAdd(u8, &state, 0x05, .release));
    try std.testing.expectEqual(@as(u8, 0x35), state);

    try std.testing.expectEqual(@as(u8, 0x35), try atomic.fetchOr(u8, &state, 0xC0, .acq_rel));
    try std.testing.expectEqual(@as(u8, 0xF5), state);

    try std.testing.expectEqual(@as(u8, 0xF5), try atomic.fetchAnd(u8, &state, 0xD5, .acquire));
    try std.testing.expectEqual(@as(u8, 0xD5), state);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchAdd(u8, &state, 0x01, .unordered));
    try std.testing.expectEqual(@as(u8, 0xD5), state);

    var register: u8 = 0;
    const register_ptr: *volatile u8 = @ptrCast(&register);
    const const_register_ptr: *const volatile u8 = @ptrCast(&register);

    barrier.release();
    mmio.write(u8, register_ptr, state);
    barrier.acquire();
    try std.testing.expectEqual(@as(u8, 0xD5), mmio.read(u8, const_register_ptr));
}

test "phase3 low-level wrappers keep subtractive, xor, and clamp-style atomic updates explicit before MMIO publish" {
    var state: u16 = 0x0040;

    try std.testing.expectEqual(@as(u16, 0x0040), try atomic.fetchSub(u16, &state, 0x0005, .release));
    try std.testing.expectEqual(@as(u16, 0x003B), state);

    try std.testing.expectEqual(@as(u16, 0x003B), try atomic.fetchXor(u16, &state, 0x00F0, .acq_rel));
    try std.testing.expectEqual(@as(u16, 0x00CB), state);

    try std.testing.expectEqual(@as(u16, 0x00CB), try atomic.fetchMin(u16, &state, 0x0044, .acquire));
    try std.testing.expectEqual(@as(u16, 0x0044), state);

    try std.testing.expectEqual(@as(u16, 0x0044), try atomic.fetchMax(u16, &state, 0x0088, .seq_cst));
    try std.testing.expectEqual(@as(u16, 0x0088), state);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchXor(u16, &state, 0x0001, .unordered));
    try std.testing.expectEqual(@as(u16, 0x0088), state);

    var register: u16 = 0;
    const register_ptr: *volatile u16 = @ptrCast(&register);
    const const_register_ptr: *const volatile u16 = @ptrCast(&register);

    barrier.release();
    mmio.write(u16, register_ptr, state);
    barrier.acquire();
    try std.testing.expectEqual(@as(u16, 0x0088), mmio.read(u16, const_register_ptr));
}

test "phase3 low-level wrappers keep exchange-style MMIO policy handoffs explicit" {
    var register: u16 = 0x55AA;
    const register_ptr: *volatile u16 = @ptrCast(&register);

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.exchangeInteropPolicyBytes(u16, 0, 0, register_ptr, 0x0F0F));
    try std.testing.expectEqual(@as(u16, 0x55AA), try mmio.exchangeInteropPolicyBytes(u16, 1, 0, register_ptr, 0x0F0F));
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

    try std.testing.expectError(error.UnsafeScopeDenied, narrow.pointerAtByte(u32, bridge_addr, @sizeOf(u32), mmio_scope));

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

    try std.testing.expectError(error.ByteLengthTooSmall, narrow.pointerAtByte(u32, bridge_addr, @sizeOf(u16), raw_scope));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.writeValueAtByte(u32, bridge_addr, 0xCAFE_BABE, safe_scope));

    try narrow.writeValueAtByte(u32, bridge_addr, 0xCAFE_BABE, raw_scope);
    barrier.fullFence();
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), bridge_word);
}

test "phase3 low-level wrappers keep raw-pointer bridge interop-policy helpers explicit" {
    const InteropPolicy = @typeInfo(@TypeOf(mmio.readInteropPolicy)).@"fn".params[1].type.?;
    const raw_policy = InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge),
        .reserved = 0,
    };
    const denied_policy = InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(narrow.UnsafeScopeTag.none),
        .reserved = 0,
    };
    const reserved_policy = InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge),
        .reserved = 1,
    };

    var bridge_words = [_]u32{ 0x0102_0304, 0x0506_0708, 73 };
    const bridge_addr = @intFromPtr(&bridge_words[0]);
    const second_addr = @intFromPtr(&bridge_words[1]);

    const direct_ptr = try narrow.pointerAtInteropPolicyBytes(
        u32,
        bridge_addr,
        @sizeOf(u32),
        raw_policy.unsafe_scope,
        raw_policy.reserved,
    );
    try std.testing.expectEqual(@as(u32, 0x0102_0304), direct_ptr.*);

    const direct_const_ptr = try narrow.constPointerAtInteropPolicyBytes(
        u32,
        bridge_addr,
        raw_policy.unsafe_scope,
        raw_policy.reserved,
    );
    try std.testing.expectEqual(@as(u32, 0x0102_0304), direct_const_ptr.*);

    const policy_slice = try narrow.sliceAtInteropPolicy(u32, bridge_addr, bridge_words.len, raw_policy);
    policy_slice[0] = 0x1122_3344;
    barrier.release();
    try std.testing.expectEqual(@as(u32, 0x1122_3344), bridge_words[0]);

    const const_policy_slice = try narrow.constSliceAtInteropPolicyBytes(
        u32,
        bridge_addr,
        bridge_words.len,
        raw_policy.unsafe_scope,
        raw_policy.reserved,
    );
    try std.testing.expectEqual(@as(u32, 0x0506_0708), const_policy_slice[1]);

    try narrow.writeValueAtInteropPolicyBytes(
        u32,
        bridge_addr,
        0xFACE_CAFE,
        raw_policy.unsafe_scope,
        raw_policy.reserved,
    );
    try narrow.writeValueAtInteropPolicy(u32, second_addr, 0x0BAD_F00D, raw_policy);
    barrier.fullFence();
    try std.testing.expectEqual(@as(u32, 0xFACE_CAFE), bridge_words[0]);
    try std.testing.expectEqual(@as(u32, 0x0BAD_F00D), bridge_words[1]);

    try std.testing.expectEqual(
        @as(u32, 0x0BAD_F00D),
        (try narrow.constPointerAtInteropPolicy(u32, second_addr, raw_policy)).*,
    );

    bridge_words[1] = 47;
    const third_addr = @intFromPtr(&bridge_words[2]);
    try std.testing.expectEqual(@as(u32, 73), try narrow.exchangeValueAtInteropPolicyBytes(u32, third_addr, @sizeOf(u32), 79, 2, 0));
    try std.testing.expectEqual(@as(u32, 79), bridge_words[2]);
    try std.testing.expectEqual(@as(u32, 47), try narrow.exchangeValueAtInteropPolicy(u32, second_addr, @sizeOf(u32), 61, raw_policy));
    try std.testing.expectEqual(@as(u32, 61), bridge_words[1]);
    try std.testing.expectEqual(@as(u32, 61), try narrow.exchangeValueAtByte(u32, second_addr, @sizeOf(u32), 47, 2));
    try std.testing.expectEqual(@as(u32, 47), bridge_words[1]);

    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.pointerAtInteropPolicy(u32, bridge_addr, @sizeOf(u32), denied_policy),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.constPointerAtInteropPolicy(u32, bridge_addr, reserved_policy),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        narrow.sliceAtInteropPolicy(u32, bridge_addr, bridge_words.len, reserved_policy),
    );
    try std.testing.expectError(
        error.ByteLengthTooSmall,
        narrow.pointerAtInteropPolicyBytes(
            u32,
            bridge_addr,
            @sizeOf(u16),
            raw_policy.unsafe_scope,
            raw_policy.reserved,
        ),
    );
}

test "phase3 low-level wrappers keep atomic order-gate failures explicit before MMIO publish" {
    var state: u32 = 0x10;

    try atomic.validateLoadOrder(.acquire);
    try std.testing.expectError(error.InvalidLoadOrdering, atomic.validateLoadOrder(.release));
    try std.testing.expectError(error.InvalidLoadOrdering, atomic.load(u32, &state, .release));
    try std.testing.expectEqual(@as(u32, 0x10), state);

    try atomic.validateStoreOrder(.release);
    try std.testing.expectError(error.InvalidStoreOrdering, atomic.validateStoreOrder(.acquire));
    try std.testing.expectError(error.InvalidStoreOrdering, atomic.store(u32, &state, 0x20, .acquire));
    try std.testing.expectEqual(@as(u32, 0x10), state);

    try atomic.validateRmwOrder(.acq_rel);
    try std.testing.expectError(error.InvalidRmwOrdering, atomic.validateRmwOrder(.unordered));
    try std.testing.expectError(error.InvalidRmwOrdering, atomic.exchange(u32, &state, 0x20, .unordered));
    try std.testing.expectEqual(@as(u32, 0x10), state);

    try atomic.store(u32, &state, 0x30, .release);

    var register: u32 = 0;
    const register_ptr: *volatile u32 = @ptrCast(&register);
    const const_register_ptr: *const volatile u32 = @ptrCast(&register);

    barrier.release();
    mmio.write(u32, register_ptr, try atomic.load(u32, &state, .acquire));
    barrier.acquire();
    try std.testing.expectEqual(@as(u32, 0x30), mmio.read(u32, const_register_ptr));
}

test "phase3 low-level wrappers keep MMIO range helpers and width aliases explicit beside raw bridge gates" {
    const InteropPolicy = @typeInfo(@TypeOf(mmio.readInteropPolicy)).@"fn".params[1].type.?;
    const mmio_policy = InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio),
        .reserved = 0,
    };
    const raw_policy = InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge),
        .reserved = 0,
    };
    const mmio_scope = @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio);
    const raw_scope = @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge);

    var bytes = [_]u8{0} ** 16;
    const base_addr = @intFromPtr(&bytes[0]);

    const scoped_range = try mmio.rangeScoped(base_addr, 16, 4, .volatile_mmio);
    try std.testing.expectEqual(base_addr, scoped_range.base_addr);
    try std.testing.expectEqual(@as(u32, 16), scoped_range.length);
    try std.testing.expectEqual(@as(u32, 4), scoped_range.stride);

    const direct_const_ptr = try mmio.constPointerAt(u32, scoped_range, 4);
    try std.testing.expectEqual(@as(*const volatile u32, @ptrFromInt(base_addr + 4)), direct_const_ptr);
    try mmio.writeAt(u32, scoped_range, 4, 0x1122_3344);
    try std.testing.expectEqual(@as(u32, 0x1122_3344), try mmio.readAt(u32, scoped_range, 4));
    try std.testing.expectEqual(@as(u32, 0x1122_3344), try mmio.exchangeAt(u32, scoped_range, 4, 0x5566_7788));
    try std.testing.expectEqual(@as(u32, 0x5533_4488), try mmio.writeMaskedAt(u32, scoped_range, 4, 0x00FF_FF00, 0x0033_4400));
    const direct_ptr = try mmio.pointerAt(u32, scoped_range, 4);
    direct_ptr.* = 0xCAFE_BABE;
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), try mmio.readAt(u32, scoped_range, 4));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.constPointerAt(u16, scoped_range, 2));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.writeAt(u32, scoped_range, 2, 1));

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicy(base_addr, 16, 4, raw_policy));
    const policy_range = try mmio.rangeInteropPolicy(base_addr, 16, 4, mmio_policy);
    try std.testing.expectEqual(scoped_range.base_addr, policy_range.base_addr);
    try std.testing.expectEqual(scoped_range.length, policy_range.length);
    try std.testing.expectEqual(scoped_range.stride, policy_range.stride);

    const bytes_range = try mmio.rangeInteropPolicyBytes(base_addr, 16, 4, mmio_scope, 0);
    try std.testing.expectEqual(policy_range.base_addr, bytes_range.base_addr);
    try std.testing.expectEqual(policy_range.length, bytes_range.length);
    try std.testing.expectEqual(policy_range.stride, bytes_range.stride);

    const byte_range = try mmio.rangeInteropPolicyByte(base_addr, 16, 4, mmio_scope);
    try std.testing.expectEqual(policy_range.base_addr, byte_range.base_addr);
    try std.testing.expectEqual(policy_range.length, byte_range.length);
    try std.testing.expectEqual(policy_range.stride, byte_range.stride);

    try mmio.write8InteropPolicyBytes(base_addr, 1, 0x44, mmio_scope, 0);
    try std.testing.expectEqual(@as(u8, 0x44), try mmio.read8InteropPolicyBytes(base_addr, 1, mmio_scope, 0));

    try mmio.write16InteropPolicyBytes(base_addr, 2, 0xBEEF, mmio_scope, 0);
    try std.testing.expectEqual(@as(u16, 0xBEEF), try mmio.read16InteropPolicyBytes(base_addr, 2, mmio_scope, 0));
    try std.testing.expectError(error.InvalidInteropPolicy, mmio.read16InteropPolicyBytes(base_addr, 3, mmio_scope, 0));

    try mmio.write32InteropPolicyByte(base_addr, 4, 0xCAFE_BABE, mmio_scope);
    barrier.release();
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), try mmio.read32InteropPolicyByte(base_addr, 4, mmio_scope));

    try mmio.write64InteropPolicyBytes(base_addr, 8, 0x0123_4567_89AB_CDEF, mmio_scope, 0);
    barrier.acquire();
    try std.testing.expectEqual(
        @as(u64, 0x0123_4567_89AB_CDEF),
        try mmio.read64InteropPolicyBytes(base_addr, 8, mmio_scope, 0),
    );

    try std.testing.expectEqual(@as(u16, 0xBEEF), (try narrow.constPointerAtByte(u16, base_addr + 2, raw_scope)).*);
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), (try narrow.constPointerAtByte(u32, base_addr + 4, raw_scope)).*);
    try std.testing.expectEqual(
        @as(u64, 0x0123_4567_89AB_CDEF),
        try narrow.readValueAtInteropPolicyBytes(u64, base_addr + 8, @sizeOf(u64), raw_scope, 0),
    );
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.constPointerAtByte(u32, base_addr + 4, mmio_scope));
}
