const std = @import("std");
const abi = @import("abi_bindings");
const atomic = @import("atomic_helpers");
const barrier = @import("barrier_helpers");
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
    try std.testing.expectEqual(@as(?u32, null), atomic.compareExchange(u32, &value, 15, 21, .seq_cst, .seq_cst));
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
    mmio.write32(base, 8, 0x12345678);
    try std.testing.expectEqual(@as(u32, 0x12345678), mmio.read32(base, 8));
    try std.testing.expectEqual(@as(u32, 0x12345678), regs[2]);
}

test "phase3 low-level wrapper ABI range shape stays stable" {
    comptime {
        if (@sizeOf(abi.MmioRange) != @sizeOf(usize) + 8) {
            @compileError("MmioRange size drifted");
        }
        if (@offsetOf(abi.MmioRange, "length") != @sizeOf(usize)) {
            @compileError("MmioRange.length offset drifted");
        }
        if (@offsetOf(abi.MmioRange, "stride") != @sizeOf(usize) + 4) {
            @compileError("MmioRange.stride offset drifted");
        }
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
}

test "phase3 low-level wrappers decode interop policy unsafe scope explicitly" {
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const raw_pointer_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const invalid_scope_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = 9,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 1,
    };

    try std.testing.expectEqual(narrow.UnsafeScopeTag.volatile_mmio, narrow.scopeFromInteropPolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved).?);
    try std.testing.expect(narrow.recognizesInteropPolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved));
    try std.testing.expect(narrow.permitsVolatileMmioPolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved));
    try std.testing.expect(!narrow.permitsRawPointerBridgePolicyBytes(mmio_policy.unsafe_scope, mmio_policy.reserved));

    try std.testing.expectEqual(narrow.UnsafeScopeTag.raw_pointer_bridge, narrow.scopeFromInteropPolicyBytes(raw_pointer_policy.unsafe_scope, raw_pointer_policy.reserved).?);
    try std.testing.expect(narrow.recognizesInteropPolicyBytes(raw_pointer_policy.unsafe_scope, raw_pointer_policy.reserved));
    try std.testing.expect(!narrow.permitsVolatileMmioPolicyBytes(raw_pointer_policy.unsafe_scope, raw_pointer_policy.reserved));
    try std.testing.expect(narrow.permitsRawPointerBridgePolicyBytes(raw_pointer_policy.unsafe_scope, raw_pointer_policy.reserved));

    try std.testing.expectEqual(@as(?narrow.UnsafeScopeTag, null), narrow.scopeFromInteropPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));
    try std.testing.expect(!narrow.recognizesInteropPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));
    try std.testing.expect(!narrow.permitsVolatileMmioPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));
    try std.testing.expect(!narrow.permitsRawPointerBridgePolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));

    try std.testing.expectEqual(@as(?narrow.UnsafeScopeTag, null), narrow.scopeFromInteropPolicyBytes(reserved_policy.unsafe_scope, reserved_policy.reserved));
    try std.testing.expect(!narrow.recognizesInteropPolicyBytes(reserved_policy.unsafe_scope, reserved_policy.reserved));
}
