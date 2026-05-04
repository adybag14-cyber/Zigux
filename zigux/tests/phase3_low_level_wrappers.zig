const std = @import("std");
const abi = @import("abi_bindings");
const atomic = @import("atomic_helpers");
const barrier = @import("barrier_helpers");
const interop_policy = @import("interop_policy");
const layout_assert = @import("layout_assert");
const mmio = @import("mmio_helpers");
const narrow = @import("narrow_unsafe");

test "phase3 low-level wrappers stay inside the documented ABI surface" {
    var value: u32 = 5;
    try std.testing.expectEqual(@as(u32, 5), atomic.load(u32, &value, .seq_cst));
    atomic.store(u32, &value, 8, .seq_cst);
    try std.testing.expectEqual(@as(u32, 8), value);
    try std.testing.expectEqual(@as(u32, 8), atomic.exchange(u32, &value, 13, .seq_cst));
    try std.testing.expectEqual(@as(u32, 13), value);
    try std.testing.expectEqual(@as(u32, 13), atomic.fetchAdd(u32, &value, 2, .seq_cst));
    try std.testing.expectEqual(@as(u32, 15), value);
    try std.testing.expectEqual(@as(u32, 15), atomic.fetchSub(u32, &value, 4, .seq_cst));
    try std.testing.expectEqual(@as(u32, 11), value);
    try std.testing.expectEqual(@as(u32, 11), atomic.fetchOr(u32, &value, 0b1000, .seq_cst));
    try std.testing.expectEqual(@as(u32, 11), value);
    try std.testing.expectEqual(@as(u32, 11), atomic.fetchAnd(u32, &value, 0b0111, .seq_cst));
    try std.testing.expectEqual(@as(u32, 3), value);
    try std.testing.expectEqual(@as(u32, 3), atomic.fetchXor(u32, &value, 0b1111, .seq_cst));
    try std.testing.expectEqual(@as(u32, 12), value);
    try std.testing.expectEqual(@as(?u32, null), atomic.compareExchange(u32, &value, 12, 21, .seq_cst, .seq_cst));
    try std.testing.expectEqual(@as(u32, 21), value);
    const mismatch = atomic.compareExchange(u32, &value, 9, 19, .seq_cst, .seq_cst);
    try std.testing.expectEqual(@as(?u32, 21), mismatch);
    try std.testing.expectEqual(@as(u32, 21), value);
    try std.testing.expectEqual(@as(u32, 21), atomic.fetchMax(u32, &value, 29, .seq_cst));
    try std.testing.expectEqual(@as(u32, 29), value);
    try std.testing.expectEqual(@as(u32, 29), atomic.fetchMax(u32, &value, 25, .seq_cst));
    try std.testing.expectEqual(@as(u32, 29), value);
    try std.testing.expectEqual(@as(u32, 29), atomic.fetchMin(u32, &value, 17, .seq_cst));
    try std.testing.expectEqual(@as(u32, 17), value);
    try std.testing.expectEqual(@as(u32, 17), atomic.fetchMin(u32, &value, 19, .seq_cst));
    try std.testing.expectEqual(@as(u32, 17), value);

    var weak_value: u32 = 31;
    var attempts: usize = 0;
    while (true) {
        attempts += 1;
        if (atomic.compareExchangeWeak(u32, &weak_value, 31, 34, .seq_cst, .seq_cst) == null) break;
        try std.testing.expectEqual(@as(u32, 31), weak_value);
        try std.testing.expect(attempts < 8);
    }
    try std.testing.expect(attempts >= 1);
    try std.testing.expectEqual(@as(u32, 34), weak_value);
    const weak_mismatch = atomic.compareExchangeWeak(u32, &weak_value, 31, 55, .seq_cst, .seq_cst);
    try std.testing.expectEqual(@as(?u32, 34), weak_mismatch);
    try std.testing.expectEqual(@as(u32, 34), weak_value);

    barrier.acquire();
    barrier.release();
    barrier.acquireRelease();
    barrier.full();

    var regs = [_]u32{ 0, 0, 0 };
    const base = narrow.addressOf(&regs[0]);
    const desc = mmio.range(base, 12, 4);
    try std.testing.expectEqual(base, desc.base_addr);
    try std.testing.expectEqual(@as(u32, 12), desc.length);
    try std.testing.expectEqual(@as(u32, 4), desc.stride);
    mmio.write8(base, 1, 0x5a);
    try std.testing.expectEqual(@as(u8, 0x5a), mmio.read8(base, 1));
    mmio.write16(base, 2, 0xabcd);
    try std.testing.expectEqual(@as(u16, 0xabcd), mmio.read16(base, 2));
    mmio.write32(base, 8, 0x12345678);
    try std.testing.expectEqual(@as(u32, 0x12345678), mmio.read32(base, 8));
    try std.testing.expectEqual(@as(u32, 0x12345678), regs[2]);
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8Scoped(.none, base, 0, 0x99));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8Scoped(.raw_pointer_bridge, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Scoped(.none, base, 0, 0x99));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read16Scoped(.raw_pointer_bridge, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Scoped(.none, base, 0, 0x99));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Scoped(.raw_pointer_bridge, base, 0));
    try std.testing.expectError(error.MisalignedAccess, mmio.write16Scoped(.volatile_mmio, base, 1, 0x99));
    try std.testing.expectError(error.MisalignedAccess, mmio.read16Scoped(.volatile_mmio, base, 1));
    try std.testing.expectError(error.MisalignedAccess, mmio.write32Scoped(.volatile_mmio, base, 2, 0x99));
    try std.testing.expectError(error.MisalignedAccess, mmio.read32Scoped(.volatile_mmio, base, 2));
    try std.testing.expectError(error.AddressOverflow, mmio.write8Scoped(.volatile_mmio, std.math.maxInt(usize), 1, 0x99));
    try std.testing.expectError(error.AddressOverflow, mmio.read8Scoped(.volatile_mmio, std.math.maxInt(usize), 1));
    try std.testing.expectError(error.AddressOverflow, mmio.write16Scoped(.volatile_mmio, std.math.maxInt(usize), 1, 0x99));
    try std.testing.expectError(error.AddressOverflow, mmio.read16Scoped(.volatile_mmio, std.math.maxInt(usize), 1));
    try std.testing.expectError(error.AddressOverflow, mmio.write32Scoped(.volatile_mmio, std.math.maxInt(usize), 4, 0x99));
    try std.testing.expectError(error.AddressOverflow, mmio.read32Scoped(.volatile_mmio, std.math.maxInt(usize), 4));
    try mmio.write8Scoped(.volatile_mmio, base, 0, 0xbe);
    try std.testing.expectEqual(@as(u8, 0xbe), try mmio.read8Scoped(.volatile_mmio, base, 0));
    try mmio.write16Scoped(.volatile_mmio, base, 0, 0xbeef);
    try std.testing.expectEqual(@as(u16, 0xbeef), try mmio.read16Scoped(.volatile_mmio, base, 0));
    try mmio.write32Scoped(.volatile_mmio, base, 4, 0xaabbccdd);
    try std.testing.expectEqual(@as(u32, 0xaabbccdd), try mmio.read32Scoped(.volatile_mmio, base, 4));
    try std.testing.expectEqual(@as(u32, 0xaabbccdd), regs[1]);

    var regs64 = [_]u64{ 0, 0 };
    const base64 = narrow.addressOf(&regs64[0]);
    mmio.write64(base64, @sizeOf(u64), 0x0123_4567_89ab_cdef);
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), mmio.read64(base64, @sizeOf(u64)));
    try std.testing.expectEqual(@as(u64, 0x0123_4567_89ab_cdef), regs64[1]);
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Scoped(.none, base64, 0, 0x99));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read64Scoped(.raw_pointer_bridge, base64, 0));
    try std.testing.expectError(error.MisalignedAccess, mmio.write64Scoped(.volatile_mmio, base64, 4, 0x99));
    try std.testing.expectError(error.MisalignedAccess, mmio.read64Scoped(.volatile_mmio, base64, 4));
    try std.testing.expectError(error.AddressOverflow, mmio.write64Scoped(.volatile_mmio, std.math.maxInt(usize), 8, 0x99));
    try std.testing.expectError(error.AddressOverflow, mmio.read64Scoped(.volatile_mmio, std.math.maxInt(usize), 8));
    try mmio.write64Scoped(.volatile_mmio, base64, 0, 0xfedc_ba98_7654_3210);
    try std.testing.expectEqual(@as(u64, 0xfedc_ba98_7654_3210), try mmio.read64Scoped(.volatile_mmio, base64, 0));

    const mmio_policy = try interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    });
    const raw_pointer_policy = try interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    });
    const none_policy = try interop_policy.decode(.{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    });
    try mmio.write8Policy(mmio_policy, base, 0, 0x2a);
    try std.testing.expectEqual(@as(u8, 0x2a), try mmio.read8Policy(mmio_policy, base, 0));
    try mmio.write16Policy(mmio_policy, base, 2, 0x7bcd);
    try std.testing.expectEqual(@as(u16, 0x7bcd), try mmio.read16Policy(mmio_policy, base, 2));
    try mmio.write32Policy(mmio_policy, base, 8, 0xdecafbad);
    try std.testing.expectEqual(@as(u32, 0xdecafbad), regs[2]);
    try std.testing.expectEqual(@as(u32, 0xdecafbad), try mmio.read32Policy(mmio_policy, base, 8));
    try mmio.write64Policy(mmio_policy, base64, @sizeOf(u64), 0x1111_2222_3333_4444);
    try std.testing.expectEqual(@as(u64, 0x1111_2222_3333_4444), regs64[1]);
    try std.testing.expectEqual(@as(u64, 0x1111_2222_3333_4444), try mmio.read64Policy(mmio_policy, base64, @sizeOf(u64)));
    try mmio.writeScopedWithPolicy(u8, mmio_policy, base, 1, 0x3c);
    try std.testing.expectEqual(@as(u8, 0x3c), try mmio.readScopedWithPolicy(u8, mmio_policy, base, 1));
    try mmio.writeScopedWithPolicy(u16, mmio_policy, base, 0, 0x6bcd);
    try std.testing.expectEqual(@as(u16, 0x6bcd), try mmio.readScopedWithPolicy(u16, mmio_policy, base, 0));
    try mmio.writeScopedWithPolicy(u32, mmio_policy, base, 4, 0xcafe_babe);
    try std.testing.expectEqual(@as(u32, 0xcafe_babe), regs[1]);
    try std.testing.expectEqual(@as(u32, 0xcafe_babe), try mmio.readScopedWithPolicy(u32, mmio_policy, base, 4));
    try mmio.writeScopedWithPolicy(u64, mmio_policy, base64, 0, 0x5555_6666_7777_8888);
    try std.testing.expectEqual(@as(u64, 0x5555_6666_7777_8888), regs64[0]);
    try std.testing.expectEqual(@as(u64, 0x5555_6666_7777_8888), try mmio.readScopedWithPolicy(u64, mmio_policy, base64, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8Policy(raw_pointer_policy, base, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8Policy(raw_pointer_policy, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8Policy(none_policy, base, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8Policy(none_policy, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Policy(raw_pointer_policy, base, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read16Policy(raw_pointer_policy, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Policy(none_policy, base, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read16Policy(none_policy, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(raw_pointer_policy, base, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(raw_pointer_policy, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(none_policy, base, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(none_policy, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Policy(raw_pointer_policy, base64, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read64Policy(raw_pointer_policy, base64, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Policy(none_policy, base64, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.read64Policy(none_policy, base64, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeScopedWithPolicy(u8, raw_pointer_policy, base, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.readScopedWithPolicy(u8, raw_pointer_policy, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeScopedWithPolicy(u16, none_policy, base, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.readScopedWithPolicy(u16, none_policy, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeScopedWithPolicy(u32, raw_pointer_policy, base, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.readScopedWithPolicy(u32, raw_pointer_policy, base, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.writeScopedWithPolicy(u64, none_policy, base64, 0, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, mmio.readScopedWithPolicy(u64, none_policy, base64, 0));
}

test "phase3 low-level wrappers keep non-seq-cst atomic orderings reviewable" {
    var release_value: u32 = 0;
    atomic.store(u32, &release_value, 41, .release);
    try std.testing.expectEqual(@as(u32, 41), atomic.load(u32, &release_value, .acquire));

    var monotonic_value: u32 = 5;
    try std.testing.expectEqual(@as(?u32, null), atomic.compareExchange(u32, &monotonic_value, 5, 7, .monotonic, .monotonic));
    try std.testing.expectEqual(@as(u32, 7), monotonic_value);

    var acq_rel_value: u32 = 7;
    try std.testing.expectEqual(@as(?u32, null), atomic.compareExchange(u32, &acq_rel_value, 7, 11, .acq_rel, .acquire));
    try std.testing.expectEqual(@as(u32, 11), acq_rel_value);

    var weak_release_value: u32 = 13;
    var weak_release_attempts: usize = 0;
    while (true) {
        weak_release_attempts += 1;
        if (atomic.compareExchangeWeak(u32, &weak_release_value, 13, 19, .release, .monotonic) == null) break;
        try std.testing.expectEqual(@as(u32, 13), weak_release_value);
        try std.testing.expect(weak_release_attempts < 8);
    }
    try std.testing.expect(weak_release_attempts >= 1);
    try std.testing.expectEqual(@as(u32, 19), weak_release_value);
    const weak_release_mismatch = atomic.compareExchangeWeak(u32, &weak_release_value, 13, 23, .release, .monotonic);
    try std.testing.expectEqual(@as(?u32, 19), weak_release_mismatch);
    try std.testing.expectEqual(@as(u32, 19), weak_release_value);
}

test "phase3 low-level wrapper ABI range shape stays stable" {
    comptime {
        layout_assert.assertMmioRangeLayout();
    }
}

test "phase3 low-level wrappers keep the narrow unsafe scope contract explicit" {
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.none), @intFromEnum(narrow.UnsafeScopeTag.none));
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.volatile_mmio), @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio));
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge), @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge));

    try std.testing.expect(!narrow.permitsVolatileMmio(.none));
    try std.testing.expect(narrow.permitsVolatileMmio(.volatile_mmio));
    try std.testing.expect(!narrow.permitsVolatileMmio(.raw_pointer_bridge));

    try std.testing.expect(!narrow.permitsRawPointerBridge(.none));
    try std.testing.expect(!narrow.permitsRawPointerBridge(.volatile_mmio));
    try std.testing.expect(narrow.permitsRawPointerBridge(.raw_pointer_bridge));
    try std.testing.expectError(error.MisalignedAccess, narrow.scopedPointerAt(u32, .volatile_mmio, 1, 0));
    try std.testing.expectError(error.AddressOverflow, narrow.scopedPointerAt(u32, .volatile_mmio, std.math.maxInt(usize), 1));
}
