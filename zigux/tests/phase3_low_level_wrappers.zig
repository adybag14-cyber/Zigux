const std = @import("std");
const abi = @import("abi_bindings");
const atomic = @import("atomic_helpers");
const barrier = @import("barrier_helpers");
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

    barrier.acquire();
    barrier.release();
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
