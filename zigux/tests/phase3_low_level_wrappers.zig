const std = @import("std");
const abi = @import("abi_bindings");

const atomic = @import("atomic_helpers");
const barrier = @import("barrier_helpers");
const mmio = @import("mmio_helpers");
const narrow = @import("narrow_unsafe");
const allocator_policy = @import("allocator_policy_helpers");
const panic_policy = @import("panic_policy_helpers");

test "phase3 low-level wrappers cover the shipped helper surface directly" {
    var value: u32 = 5;

    try std.testing.expectEqual(@as(u32, 5), atomic.load(u32, &value, .seq_cst));
    atomic.store(u32, &value, 8, .seq_cst);
    try std.testing.expectEqual(@as(u32, 8), value);
    try std.testing.expectEqual(@as(u32, 8), atomic.exchange(u32, &value, 13, .seq_cst));
    try std.testing.expectEqual(@as(u32, 13), value);
    try std.testing.expectEqual(@as(u32, 13), atomic.fetchAdd(u32, &value, 4, .seq_cst));
    try std.testing.expectEqual(@as(u32, 17), value);
    try std.testing.expectEqual(@as(u32, 17), atomic.fetchSub(u32, &value, 3, .seq_cst));
    try std.testing.expectEqual(@as(u32, 14), value);
    try std.testing.expectEqual(@as(u32, 14), atomic.fetchAnd(u32, &value, 12, .seq_cst));
    try std.testing.expectEqual(@as(u32, 12), value);
    try std.testing.expectEqual(@as(u32, 12), atomic.fetchOr(u32, &value, 3, .seq_cst));
    try std.testing.expectEqual(@as(u32, 15), value);
    try std.testing.expectEqual(@as(u32, 15), atomic.fetchXor(u32, &value, 6, .seq_cst));
    try std.testing.expectEqual(@as(u32, 9), value);

    try std.testing.expectEqual(@as(u32, 9), atomic.fetchNand(u32, &value, 10, .seq_cst));
    try std.testing.expectEqual(@as(u32, 0xffff_fff7), value);
    try std.testing.expectEqual(@as(u32, 0xffff_fff7), atomic.fetchMin(u32, &value, 4, .seq_cst));
    try std.testing.expectEqual(@as(u32, 4), value);
    try std.testing.expectEqual(@as(u32, 4), atomic.fetchMax(u32, &value, 19, .seq_cst));
    try std.testing.expectEqual(@as(u32, 19), value);

    value = 13;
    const seq_cst_swap = atomic.compareExchange(u32, &value, 13, 21, .seq_cst, .seq_cst);
    try std.testing.expectEqual(@as(?u32, null), seq_cst_swap);
    try std.testing.expectEqual(@as(u32, 21), value);

    const mismatch = atomic.compareExchange(u32, &value, 9, 19, .seq_cst, .seq_cst);
    try std.testing.expectEqual(@as(?u32, 21), mismatch);
    try std.testing.expectEqual(@as(u32, 21), value);

    var weak_value: u32 = 21;
    var attempts: usize = 0;
    while (true) {
        attempts += 1;
        if (atomic.compareExchangeWeak(u32, &weak_value, 21, 34, .seq_cst, .seq_cst) == null) break;
        try std.testing.expectEqual(@as(u32, 21), weak_value);
        try std.testing.expect(attempts < 16);
    }
    try std.testing.expectEqual(@as(u32, 34), weak_value);

    barrier.acquire();
    barrier.release();
    barrier.full();
    barrier.acquireRelease();

    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = narrow.addressOf(&bytes[0]);
    const aligned_halfword: *align(1) const u16 = @ptrCast(&bytes[2]);
    const aligned_word: *align(1) const u32 = @ptrCast(&bytes[@sizeOf(u32)]);
    const aligned_doubleword: *align(1) const u64 = @ptrCast(&bytes[@sizeOf(u64)]);
    const byte_desc = mmio.range(base, 24, 1);
    const halfword_desc = mmio.range(base, 24, 2);
    const word_desc = mmio.range(base, 24, 4);
    const dword_desc = mmio.range(base, 24, 8);

    try std.testing.expectEqual(base, byte_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 24), byte_desc.length);
    try std.testing.expectEqual(@as(u32, 1), byte_desc.stride);
    try std.testing.expectEqual(base, halfword_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 24), halfword_desc.length);
    try std.testing.expectEqual(@as(u32, 2), halfword_desc.stride);
    try std.testing.expectEqual(base, word_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 24), word_desc.length);
    try std.testing.expectEqual(@as(u32, 4), word_desc.stride);
    try std.testing.expectEqual(base, dword_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 24), dword_desc.length);
    try std.testing.expectEqual(@as(u32, 8), dword_desc.stride);

    mmio.write8(base, 1, 0x5a);
    try std.testing.expectEqual(@as(u8, 0x5a), bytes[1]);
    try std.testing.expectEqual(@as(u8, 0x5a), mmio.read8(base, 1));

    mmio.write16(base, 2, 0xbeef);
    try std.testing.expectEqual(@as(u16, 0xbeef), aligned_halfword.*);
    try std.testing.expectEqual(@as(u16, 0xbeef), mmio.read16(base, 2));

    mmio.write32(base, @sizeOf(u32), 0xfeedbeef);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), aligned_word.*);
    try std.testing.expectEqual(@as(u32, 0xfeedbeef), mmio.read32(base, @sizeOf(u32)));

    mmio.write64(base, @sizeOf(u64), 0x0123_4567_89ab_cdef);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), aligned_doubleword.*);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), mmio.read64(base, @sizeOf(u64)));

    const odd_halfword: *align(1) const u16 = @ptrCast(&bytes[1]);
    mmio.write16(base, 1, 0x1234);
    try std.testing.expectEqual(@as(u16, 0x1234), odd_halfword.*);
    try std.testing.expectEqual(@as(u16, 0x1234), mmio.read16(base, 1));

    const odd_word: *align(1) const u32 = @ptrCast(&bytes[3]);
    mmio.write32(base, 3, 0x89abcdef);
    try std.testing.expectEqual(@as(u32, 0x89abcdef), odd_word.*);
    try std.testing.expectEqual(@as(u32, 0x89abcdef), mmio.read32(base, 3));

    const odd_doubleword: *align(1) const u64 = @ptrCast(&bytes[5]);
    mmio.write64(base, 5, 0xfedc_ba98_7654_3210);
    try std.testing.expectEqual(@as(u64, 0xfedc_ba98_7654_3210), odd_doubleword.*);
    try std.testing.expectEqual(@as(u64, 0xfedc_ba98_7654_3210), mmio.read64(base, 5));
}

test "phase3 low-level wrappers keep mmio range boundaries reviewable" {
    const desc = mmio.range(0x1000, 32, 8);
    const empty = mmio.range(0x2000, 0, 4);

    try std.testing.expect(mmio.containsOffset(desc, 0));
    try std.testing.expect(mmio.containsOffset(desc, 31));
    try std.testing.expect(!mmio.containsOffset(desc, 32));

    try std.testing.expect(mmio.containsAccess(desc, 0, 1));
    try std.testing.expect(mmio.containsAccess(desc, 24, @sizeOf(u64)));
    try std.testing.expect(!mmio.containsAccess(desc, 25, @sizeOf(u64)));
    try std.testing.expect(!mmio.containsAccess(desc, 32, 1));
    try std.testing.expect(!mmio.containsAccess(desc, 0, 33));
    try std.testing.expect(!mmio.containsAccess(desc, 0, 0));

    try std.testing.expectEqual(@as(?usize, 0), mmio.offsetForIndex(desc, 0));
    try std.testing.expectEqual(@as(?usize, 8), mmio.offsetForIndex(desc, 1));
    try std.testing.expectEqual(@as(?usize, 24), mmio.offsetForIndex(desc, 3));
    try std.testing.expectEqual(@as(?usize, null), mmio.offsetForIndex(desc, 4));
    try std.testing.expectEqual(@as(?usize, null), mmio.offsetForIndex(empty, 0));

    try std.testing.expectEqual(@as(?usize, 0), mmio.typedOffsetForIndex(desc, u32, 0));
    try std.testing.expectEqual(@as(?usize, 8), mmio.typedOffsetForIndex(desc, u32, 1));
    try std.testing.expectEqual(@as(?usize, 24), mmio.typedOffsetForIndex(desc, u64, 3));
    try std.testing.expectEqual(@as(?usize, null), mmio.typedOffsetForIndex(desc, u16, 4));
    try std.testing.expectEqual(@as(?usize, null), mmio.typedOffsetForIndex(desc, u64, std.math.maxInt(usize)));
    try std.testing.expectEqual(@as(?usize, null), mmio.typedOffsetForIndex(empty, u8, 0));
}

test "phase3 low-level wrappers keep mmio interop policy gates reviewable" {
    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const base = narrow.addressOf(&bytes[0]);

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

    try std.testing.expect(mmio.allowsInteropPolicy(mmio_policy));
    try std.testing.expect(mmio.allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 0));
    try std.testing.expect(!mmio.allowsInteropPolicy(no_unsafe_policy));
    try std.testing.expect(!mmio.allowsInteropPolicy(raw_pointer_policy));
    try std.testing.expect(!mmio.allowsInteropPolicy(reserved_policy));
    try std.testing.expect(!mmio.allowsInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 1));

    const scoped_desc = try mmio.rangeInteropPolicy(base, 16, 4, mmio_policy);
    try std.testing.expectEqual(base, scoped_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 16), scoped_desc.length);
    try std.testing.expectEqual(@as(u32, 4), scoped_desc.stride);
    const byte_scoped_desc = try mmio.rangeInteropPolicyByte(base, 12, 2, @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(base, byte_scoped_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 12), byte_scoped_desc.length);
    try std.testing.expectEqual(@as(u32, 2), byte_scoped_desc.stride);
    const bytes_scoped_desc = try mmio.rangeInteropPolicyBytes(
        base,
        10,
        1,
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        0,
    );
    try std.testing.expectEqual(base, bytes_scoped_desc.base_addr);
    try std.testing.expectEqual(@as(u32, 10), bytes_scoped_desc.length);
    try std.testing.expectEqual(@as(u32, 1), bytes_scoped_desc.stride);
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicy(base, 16, 4, no_unsafe_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicy(base, 16, 4, raw_pointer_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicy(base, 16, 4, reserved_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicyByte(base, 12, 2, @intFromEnum(abi.UnsafeScope.none)));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicyByte(base, 12, 2, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge)));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.rangeInteropPolicyBytes(base, 10, 1, @intFromEnum(abi.UnsafeScope.volatile_mmio), 1),
    );

    try mmio.write8InteropPolicy(base, 0, 0x33, mmio_policy);
    try std.testing.expectEqual(@as(u8, 0x33), try mmio.read8InteropPolicy(base, 0, mmio_policy));
    try mmio.write8InteropPolicyByte(base, 3, 0x7e, @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(
        @as(u8, 0x7e),
        try mmio.read8InteropPolicyByte(base, 3, @intFromEnum(abi.UnsafeScope.volatile_mmio)),
    );
    try mmio.write16InteropPolicy(base, 2, 0x1234, mmio_policy);
    try std.testing.expectEqual(@as(u16, 0x1234), try mmio.read16InteropPolicy(base, 2, mmio_policy));
    try mmio.write16InteropPolicyByte(base, 4, 0x5678, @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(
        @as(u16, 0x5678),
        try mmio.read16InteropPolicyByte(base, 4, @intFromEnum(abi.UnsafeScope.volatile_mmio)),
    );
    try mmio.write32InteropPolicy(base, 4, 0xfeed_beef, mmio_policy);
    try std.testing.expectEqual(@as(u32, 0xfeed_beef), try mmio.read32InteropPolicy(base, 4, mmio_policy));
    try mmio.write64InteropPolicy(base, 8, 0x0123_4567_89ab_cdef, mmio_policy);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), try mmio.read64InteropPolicy(base, 8, mmio_policy));

    try mmio.write8InteropPolicyBytes(base, 1, 0x44, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0);
    try std.testing.expectEqual(
        @as(u8, 0x44),
        try mmio.read8InteropPolicyBytes(base, 1, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0),
    );
    try mmio.write64InteropPolicyBytes(
        base,
        8,
        0x0bad_f00d_dead_beef,
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        0,
    );
    try std.testing.expectEqual(
        @as(u64, 0x0bad_f00d_dead_beef),
        try mmio.read64InteropPolicyBytes(base, 8, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0),
    );

    try mmio.write32InteropPolicyByte(base, 4, 0xc001_d00d, @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(
        @as(u32, 0xc001_d00d),
        try mmio.read32InteropPolicyByte(base, 4, @intFromEnum(abi.UnsafeScope.volatile_mmio)),
    );
    try mmio.write64InteropPolicyByte(base, 8, 0xfedc_ba98_7654_3210, @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(
        @as(u64, 0xfedc_ba98_7654_3210),
        try mmio.read64InteropPolicyByte(base, 8, @intFromEnum(abi.UnsafeScope.volatile_mmio)),
    );

    try std.testing.expectError(error.UnsafeScopeDenied, mmio.requireInteropPolicy(no_unsafe_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.requireInteropPolicy(raw_pointer_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.requireInteropPolicy(reserved_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32InteropPolicy(base, 4, no_unsafe_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16InteropPolicy(base, 2, 0x7777, raw_pointer_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8InteropPolicyBytes(base, 1, 1, 1));
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.read16InteropPolicyByte(base, 4, @intFromEnum(abi.UnsafeScope.none)),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.read32InteropPolicyByte(base, 4, @intFromEnum(abi.UnsafeScope.none)),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.write32InteropPolicyByte(base, 4, 0, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge)),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.read64InteropPolicyByte(base, 8, @intFromEnum(abi.UnsafeScope.none)),
    );
    try std.testing.expectError(
        error.UnsafeScopeDenied,
        mmio.read64InteropPolicyBytes(base, 8, @intFromEnum(abi.UnsafeScope.volatile_mmio), 1),
    );
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64InteropPolicyBytes(base, 8, 0, 0, 0));
}

test "phase3 low-level wrappers keep raw pointer bridge policy gates reviewable" {
    var values = [_]u32{ 11, 22, 33 };
    const base = narrow.addressOf(&values[0]);
    const third_addr = narrow.byteOffset(base, @sizeOf(u32) * 2);

    const raw_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
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
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 1,
    };

    try std.testing.expect(narrow.permitsRawPointerBridgeInteropPolicy(raw_policy));
    try std.testing.expect(!narrow.permitsRawPointerBridgeInteropPolicy(mmio_policy));
    try std.testing.expect(!narrow.permitsRawPointerBridgeInteropPolicy(no_unsafe_policy));
    try std.testing.expect(!narrow.permitsRawPointerBridgeInteropPolicy(reserved_policy));

    const scoped_ptr = try narrow.pointerAtInteropPolicy(u32, base, @sizeOf(u32), raw_policy);
    scoped_ptr.* = 44;
    try std.testing.expectEqual(@as(u32, 44), values[1]);

    const scoped_mut_slice = try narrow.sliceAtInteropPolicy(u32, base, values.len, raw_policy);
    scoped_mut_slice[0] = 77;
    try std.testing.expectEqual(@as(u32, 77), values[0]);

    const scoped_mut_slice_bytes = try narrow.sliceAtInteropPolicyBytes(u32, base, values.len, 2, 0);
    scoped_mut_slice_bytes[1] = 88;
    try std.testing.expectEqual(@as(u32, 88), values[1]);

    const scoped_mut_slice_byte = try narrow.sliceAtByte(u32, base, values.len, 2);
    scoped_mut_slice_byte[2] = 99;
    try std.testing.expectEqual(@as(u32, 99), values[2]);

    const scoped_slice = try narrow.constSliceAtInteropPolicy(u32, base, values.len, raw_policy);
    try std.testing.expectEqual(@as(u32, 77), scoped_slice[0]);
    try std.testing.expectEqual(@as(u32, 88), scoped_slice[1]);
    try std.testing.expectEqual(@as(u32, 99), scoped_slice[2]);

    const scoped_const_ptr = try narrow.constPointerAtInteropPolicyBytes(u32, third_addr, 2, 0);
    try std.testing.expectEqual(@as(u32, 99), scoped_const_ptr.*);

    try narrow.writeValueAtInteropPolicy(u32, base, 111, raw_policy);
    try std.testing.expectEqual(@as(u32, 111), values[0]);
    try narrow.writeValueAtInteropPolicyBytes(u32, third_addr, 122, 2, 0);
    try std.testing.expectEqual(@as(u32, 122), values[2]);

    try std.testing.expectError(error.UnsafeScopeDenied, narrow.pointerAtInteropPolicy(u32, base, 0, mmio_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.constSliceAtInteropPolicy(u32, base, values.len, no_unsafe_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.constPointerAtInteropPolicyBytes(u32, third_addr, 2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.writeValueAtInteropPolicy(u32, base, 77, reserved_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.sliceAtInteropPolicy(u32, base, values.len, no_unsafe_policy));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.sliceAtInteropPolicyBytes(u32, base, values.len, 2, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, narrow.sliceAtByte(u32, base, values.len, 1));
}

test "phase3 low-level wrappers keep non-seq-cst orderings and signed atomic edges reviewable" {
    var handoff_value: u32 = 0;
    atomic.store(u32, &handoff_value, 41, .release);
    try std.testing.expectEqual(@as(u32, 41), atomic.load(u32, &handoff_value, .acquire));

    var signed_value: i32 = 4;
    try std.testing.expectEqual(@as(i32, 4), atomic.fetchMin(i32, &signed_value, -3, .seq_cst));
    try std.testing.expectEqual(@as(i32, -3), signed_value);
    try std.testing.expectEqual(@as(i32, -3), atomic.fetchMax(i32, &signed_value, 6, .seq_cst));
    try std.testing.expectEqual(@as(i32, 6), signed_value);

    var signed_arithmetic_value: i32 = -2;
    try std.testing.expectEqual(@as(i32, -2), atomic.fetchAdd(i32, &signed_arithmetic_value, 5, .seq_cst));
    try std.testing.expectEqual(@as(i32, 3), signed_arithmetic_value);
    try std.testing.expectEqual(@as(i32, 3), atomic.fetchSub(i32, &signed_arithmetic_value, 7, .seq_cst));
    try std.testing.expectEqual(@as(i32, -4), signed_arithmetic_value);

    var ordered_fetch_value: i32 = -4;
    try std.testing.expectEqual(@as(i32, -4), atomic.fetchAdd(i32, &ordered_fetch_value, 6, .monotonic));
    try std.testing.expectEqual(@as(i32, 2), ordered_fetch_value);
    try std.testing.expectEqual(@as(i32, 2), atomic.fetchSub(i32, &ordered_fetch_value, 3, .release));
    try std.testing.expectEqual(@as(i32, -1), ordered_fetch_value);
    try std.testing.expectEqual(@as(i32, -1), atomic.fetchMin(i32, &ordered_fetch_value, -7, .acquire));
    try std.testing.expectEqual(@as(i32, -7), ordered_fetch_value);
    try std.testing.expectEqual(@as(i32, -7), atomic.fetchMax(i32, &ordered_fetch_value, 5, .acq_rel));
    try std.testing.expectEqual(@as(i32, 5), ordered_fetch_value);

    var monotonic_value: u32 = 5;
    try std.testing.expectEqual(
        @as(?u32, null),
        atomic.compareExchange(u32, &monotonic_value, 5, 7, .monotonic, .monotonic),
    );
    try std.testing.expectEqual(@as(u32, 7), monotonic_value);
    const monotonic_mismatch = atomic.compareExchange(
        u32,
        &monotonic_value,
        5,
        9,
        .monotonic,
        .monotonic,
    );
    try std.testing.expectEqual(@as(?u32, 7), monotonic_mismatch);
    try std.testing.expectEqual(@as(u32, 7), monotonic_value);

    var monotonic_nand_value: u32 = 0x0000_00ff;
    try std.testing.expectEqual(@as(u32, 0x0000_00ff), atomic.fetchNand(u32, &monotonic_nand_value, 0x0000_0f0f, .monotonic));
    try std.testing.expectEqual(@as(u32, 0xffff_fff0), monotonic_nand_value);

    var acq_rel_value: u32 = 7;
    try std.testing.expectEqual(
        @as(?u32, null),
        atomic.compareExchange(u32, &acq_rel_value, 7, 11, .acq_rel, .acquire),
    );
    try std.testing.expectEqual(@as(u32, 11), acq_rel_value);
    const acq_rel_mismatch = atomic.compareExchange(
        u32,
        &acq_rel_value,
        7,
        15,
        .acq_rel,
        .acquire,
    );
    try std.testing.expectEqual(@as(?u32, 11), acq_rel_mismatch);
    try std.testing.expectEqual(@as(u32, 11), acq_rel_value);

    var weak_release_value: u32 = 13;
    var attempts: usize = 0;
    while (true) {
        attempts += 1;
        if (atomic.compareExchangeWeak(u32, &weak_release_value, 13, 19, .release, .monotonic) == null) break;
        try std.testing.expectEqual(@as(u32, 13), weak_release_value);
        try std.testing.expect(attempts < 16);
    }
    try std.testing.expectEqual(@as(u32, 19), weak_release_value);

    const weak_release_mismatch = atomic.compareExchangeWeak(
        u32,
        &weak_release_value,
        13,
        23,
        .release,
        .monotonic,
    );
    try std.testing.expectEqual(@as(?u32, 19), weak_release_mismatch);
    try std.testing.expectEqual(@as(u32, 19), weak_release_value);
}

test "phase3 low-level wrappers keep barrier locality reviewable" {
    var left: u8 = 7;
    var right: u8 = 19;
    const before_left = left;
    const before_right = right;

    barrier.acquire();
    barrier.release();
    barrier.full();
    barrier.acquireRelease();

    try std.testing.expectEqual(before_left, left);
    try std.testing.expectEqual(before_right, right);

    left +%= 1;
    right +%= 2;
    barrier.acquireRelease();

    try std.testing.expectEqual(@as(u8, 8), left);
    try std.testing.expectEqual(@as(u8, 21), right);
}

test "phase3 low-level wrappers keep barrier handoff reviewable" {
    const Packet = struct {
        ready: bool,
        value: u32,
        mirror: u32,
    };

    var packet = Packet{
        .ready = false,
        .value = 0,
        .mirror = 0,
    };

    packet.value = 41;
    barrier.release();
    packet.ready = true;

    barrier.acquire();
    try std.testing.expect(packet.ready);
    try std.testing.expectEqual(@as(u32, 41), packet.value);

    barrier.full();
    packet.mirror = packet.value;
    barrier.acquireRelease();

    try std.testing.expectEqual(@as(u32, 41), packet.mirror);

    packet.value = 73;
    barrier.release();
    packet.ready = false;
    barrier.acquire();
    try std.testing.expect(!packet.ready);
    try std.testing.expectEqual(@as(u32, 73), packet.value);
}

test "phase3 low-level wrappers keep allocator and panic policy helpers reviewable" {
    const caller_abort_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = 0,
        .reserved = 0,
    };
    const heap_bug_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = 0,
        .reserved = 0,
    };
    const arena_warn_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = 0,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = 0,
        .reserved = 1,
    };

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromInteropPolicy(caller_abort_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromInteropPolicy(heap_bug_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(arena_warn_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromByte(9));
    try std.testing.expect(allocator_policy.recognizesInteropPolicyBytes(@intFromEnum(abi.AllocatorMode.arena), 0));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicyBytes(@intFromEnum(abi.AllocatorMode.arena), 1));
    try std.testing.expect(allocator_policy.recognizesByte(0));
    try std.testing.expect(allocator_policy.recognizesByte(1));
    try std.testing.expect(allocator_policy.recognizesByte(2));
    try std.testing.expect(!allocator_policy.recognizesByte(9));
    try std.testing.expect(allocator_policy.requiresExplicitCallerInteropPolicy(caller_abort_policy));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(heap_bug_policy));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(arena_warn_policy));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(reserved_policy));
    try std.testing.expect(allocator_policy.requiresExplicitCallerByte(0));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerByte(1));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerByte(2));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerByte(9));
    try std.testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(caller_abort_policy));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(heap_bug_policy));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(arena_warn_policy));
    try std.testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(reserved_policy));
    try std.testing.expect(!allocator_policy.permitsGlobalFallbackByte(0));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackByte(1));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackByte(2));
    try std.testing.expect(!allocator_policy.permitsGlobalFallbackByte(9));

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromInteropPolicy(caller_abort_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromInteropPolicy(heap_bug_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromInteropPolicy(arena_warn_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromByte(9));
    try std.testing.expect(panic_policy.recognizesInteropPolicyBytes(@intFromEnum(abi.PanicMode.warn), 0));
    try std.testing.expect(!panic_policy.recognizesInteropPolicyBytes(@intFromEnum(abi.PanicMode.warn), 1));
    try std.testing.expect(panic_policy.recognizesByte(0));
    try std.testing.expect(panic_policy.recognizesByte(1));
    try std.testing.expect(panic_policy.recognizesByte(2));
    try std.testing.expect(!panic_policy.recognizesByte(9));
    try std.testing.expectEqual(@as(?panic_policy.Action, .abort_now), panic_policy.actionForInteropPolicy(caller_abort_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, .bug_check), panic_policy.actionForInteropPolicy(heap_bug_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, .warn_and_return), panic_policy.actionForInteropPolicy(arena_warn_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?panic_policy.Action, .abort_now), panic_policy.actionForByte(0));
    try std.testing.expectEqual(@as(?panic_policy.Action, .bug_check), panic_policy.actionForByte(1));
    try std.testing.expectEqual(@as(?panic_policy.Action, .warn_and_return), panic_policy.actionForByte(2));
    try std.testing.expectEqual(@as(?panic_policy.Action, null), panic_policy.actionForByte(9));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(caller_abort_policy));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(heap_bug_policy));
    try std.testing.expect(panic_policy.canReturnInteropPolicy(arena_warn_policy));
    try std.testing.expect(!panic_policy.canReturnInteropPolicy(reserved_policy));
    try std.testing.expect(panic_policy.mustAbortByte(0));
    try std.testing.expect(!panic_policy.mustAbortByte(1));
    try std.testing.expect(!panic_policy.mustAbortByte(9));
    try std.testing.expect(!panic_policy.mustBugCheckByte(0));
    try std.testing.expect(panic_policy.mustBugCheckByte(1));
    try std.testing.expect(!panic_policy.mustBugCheckByte(9));
    try std.testing.expect(!panic_policy.canReturnByte(0));
    try std.testing.expect(!panic_policy.canReturnByte(1));
    try std.testing.expect(panic_policy.canReturnByte(2));
    try std.testing.expect(!panic_policy.canReturnByte(9));
}
