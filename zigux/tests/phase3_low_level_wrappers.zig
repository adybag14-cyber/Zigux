const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const atomic_helper = @import("atomic_helper");
const narrow_unsafe = @import("narrow_unsafe");

test "phase3 low-level wrappers keep compare-exchange failure ordering explicit" {
    try testing.expect(atomic_helper.compareExchangeFailureOrderAllowed(.acq_rel, .acquire));
    try testing.expectEqual(@as(?atomic_helper.Ordering, .acquire), atomic_helper.strongestAllowedFailureOrder(.acq_rel));
    try testing.expectEqual(@as(?atomic_helper.Ordering, .monotonic), atomic_helper.weakestAllowedFailureOrder(.acq_rel));

    try testing.expect(!atomic_helper.compareExchangeFailureOrderAllowed(.release, .acquire));
    try testing.expect(!atomic_helper.compareExchangeFailureOrderAllowed(.seq_cst, .release));

    var value: u32 = 7;
    try testing.expectEqual(@as(?u32, null), try atomic_helper.compareExchangeStrong(u32, &value, 7, 9, .acq_rel, .acquire));
    try testing.expectEqual(@as(u32, 9), value);
    try testing.expectError(
        error.InvalidFailureOrdering,
        atomic_helper.compareExchangeWeak(u32, &value, 9, 11, .seq_cst, .release),
    );
    try testing.expectEqual(@as(u32, 9), value);
}

test "phase3 low-level wrappers decode shared unsafe scopes without widening access" {
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
    const bridge_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 1,
    };

    try testing.expectEqual(@as(?abi.UnsafeScope, .none), narrow_unsafe.scopeFromInteropPolicy(safe_policy));
    try testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), narrow_unsafe.scopeFromInteropPolicy(mmio_policy));
    try testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), narrow_unsafe.scopeFromInteropPolicy(bridge_policy));
    try testing.expectEqual(@as(?abi.UnsafeScope, null), narrow_unsafe.scopeFromInteropPolicy(reserved_policy));

    try testing.expectEqual(narrow_unsafe.Surface.safe_only, narrow_unsafe.surfaceFor(.none));
    try testing.expectEqual(narrow_unsafe.Surface.mmio_only, narrow_unsafe.surfaceFor(.volatile_mmio));
    try testing.expectEqual(narrow_unsafe.Surface.raw_pointer_bridge_only, narrow_unsafe.surfaceFor(.raw_pointer_bridge));

    try testing.expect(!narrow_unsafe.requiresDedicatedAuditInteropPolicy(safe_policy));
    try testing.expect(narrow_unsafe.requiresDedicatedAuditInteropPolicy(mmio_policy));
    try testing.expect(narrow_unsafe.requiresDedicatedAuditInteropPolicy(bridge_policy));
    try testing.expect(!narrow_unsafe.requiresDedicatedAuditInteropPolicy(reserved_policy));
}

test "phase3 low-level wrappers keep the current atomic-plus-unsafe packet coherent" {
    const success = atomic_helper.strongestAllowedFailureOrder(.acquire) orelse unreachable;
    const typed_scope = narrow_unsafe.scopeFromByte(@intFromEnum(abi.UnsafeScope.none)) orelse unreachable;
    const raw_scope = narrow_unsafe.scopeFromByte(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge)) orelse unreachable;

    try testing.expectEqual(atomic_helper.Ordering.acquire, success);
    try testing.expect(atomic_helper.compareExchangeFailureOrderAllowed(.acquire, success));
    try testing.expectEqual(narrow_unsafe.Surface.safe_only, narrow_unsafe.surfaceFor(typed_scope));
    try testing.expectEqual(narrow_unsafe.Surface.raw_pointer_bridge_only, narrow_unsafe.surfaceFor(raw_scope));
    try testing.expect(!narrow_unsafe.allowsVolatileMmio(raw_scope));
    try testing.expect(narrow_unsafe.allowsRawPointerBridge(raw_scope));
}
