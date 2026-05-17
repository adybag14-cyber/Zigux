const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const atomic_helper = @import("atomic_helper");
const barrier_helper = @import("barrier_helper");
const mmio_helper = @import("mmio_helper");
const narrow_unsafe = @import("narrow_unsafe");

test "phase3 low-level wrapper replay keeps compare-exchange ordering explicit" {
    try testing.expect(atomic_helper.compareExchangeFailureOrderAllowed(.acq_rel, .acquire));
    try testing.expectEqual(
        @as(?atomic_helper.Ordering, .acquire),
        atomic_helper.strongestAllowedFailureOrder(.acq_rel),
    );
    try testing.expectEqual(
        @as(?atomic_helper.Ordering, .monotonic),
        atomic_helper.weakestAllowedFailureOrder(.acq_rel),
    );
    try testing.expect(!atomic_helper.compareExchangeFailureOrderAllowed(.release, .acquire));
    try testing.expect(!atomic_helper.compareExchangeFailureOrderAllowed(.seq_cst, .release));

    var value: u32 = 7;
    try testing.expectEqual(
        @as(?u32, null),
        try atomic_helper.compareExchangeStrong(u32, &value, 7, 9, .acq_rel, .acquire),
    );
    try testing.expectEqual(@as(u32, 9), value);
    try testing.expectError(
        error.InvalidFailureOrdering,
        atomic_helper.compareExchangeWeak(u32, &value, 9, 11, .seq_cst, .release),
    );
    try testing.expectEqual(@as(u32, 9), value);
}

test "phase3 low-level wrapper replay keeps barrier handoff reviewable" {
    const Packet = struct {
        ready: bool,
        value: u32,
        mirror: u32,
    };

    var packet = Packet{
        .ready = false,
        .value = 41,
        .mirror = 0,
    };

    barrier_helper.compiler();
    barrier_helper.release();
    packet.ready = true;

    barrier_helper.acquire();
    try testing.expect(packet.ready);
    try testing.expectEqual(@as(u32, 41), packet.value);

    barrier_helper.full();
    barrier_helper.compiler();
    packet.mirror = packet.value;
    barrier_helper.acquireRelease();
    barrier_helper.fullFence();

    try testing.expectEqual(@as(u32, 41), packet.mirror);
}

test "phase3 low-level wrapper replay keeps mmio register updates reviewable" {
    var register: u32 = 0x1234_5678;
    const register_ptr: *volatile u32 = @ptrCast(&register);

    try testing.expectEqual(@as(u32, 0x1234_5678), mmio_helper.read(u32, register_ptr));
    mmio_helper.write(u32, register_ptr, 0xCAFE_BABE);
    try testing.expectEqual(@as(u32, 0xCAFE_BABE), register);

    try testing.expectEqual(@as(u32, 0xCAFE_BABE), mmio_helper.exchange(u32, register_ptr, 0xDEAD_BEEF));
    try testing.expectEqual(@as(u32, 0xDEAD_BEEF), register);

    try testing.expectEqual(
        @as(u32, 0xD0AD_BE0F),
        mmio_helper.writeMasked(u32, register_ptr, 0x0F00_00F0, 0x0000_0A00),
    );
    try testing.expectEqual(@as(u32, 0xD0AD_BE0F), register);
}

test "phase3 low-level wrapper replay keeps unsafe scope decoding explicit" {
    const safe_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 1,
    };

    try testing.expectEqual(@as(?abi.UnsafeScope, .none), narrow_unsafe.scopeFromInteropPolicy(safe_policy));
    try testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), narrow_unsafe.scopeFromInteropPolicy(mmio_policy));
    try testing.expectEqual(
        @as(?abi.UnsafeScope, .raw_pointer_bridge),
        narrow_unsafe.scopeFromInteropPolicy(raw_pointer_policy),
    );
    try testing.expectEqual(@as(?abi.UnsafeScope, null), narrow_unsafe.scopeFromInteropPolicy(reserved_policy));

    try testing.expectEqual(narrow_unsafe.Surface.safe_only, narrow_unsafe.surfaceFor(.none));
    try testing.expectEqual(narrow_unsafe.Surface.mmio_only, narrow_unsafe.surfaceFor(.volatile_mmio));
    try testing.expectEqual(
        narrow_unsafe.Surface.raw_pointer_bridge_only,
        narrow_unsafe.surfaceFor(.raw_pointer_bridge),
    );

    try testing.expect(!narrow_unsafe.requiresDedicatedAuditInteropPolicy(safe_policy));
    try testing.expect(narrow_unsafe.allowsVolatileMmioInteropPolicy(mmio_policy));
    try testing.expect(!narrow_unsafe.allowsRawPointerBridgeInteropPolicy(mmio_policy));
    try testing.expect(!narrow_unsafe.allowsVolatileMmioInteropPolicy(raw_pointer_policy));
    try testing.expect(narrow_unsafe.allowsRawPointerBridgeInteropPolicy(raw_pointer_policy));
    try testing.expect(!narrow_unsafe.recognizesInteropPolicy(reserved_policy));
}
