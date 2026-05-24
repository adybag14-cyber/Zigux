const std = @import("std");

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const panic_policy = @import("panic_policy");
const unsafe_policy = @import("unsafe_policy");

test "phase3 abi keeps policy helper decoding aligned with interop policy bytes" {
    const safe_policy = abi.defaultInteropPolicy();
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
    const raw_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 1,
    };
    const unknown_policy = abi.InteropPolicy{
        .panic_mode = 9,
        .allocator_mode = 9,
        .unsafe_scope = 9,
        .reserved = 0,
    };

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .kernel_bug), panic_policy.escalationFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .warning_only), panic_policy.escalationFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved_policy));
    try std.testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(unknown_policy));
    try std.testing.expect(panic_policy.causesImmediateHaltInteropPolicy(safe_policy));
    try std.testing.expect(panic_policy.causesImmediateHaltInteropPolicy(mmio_policy));
    try std.testing.expect(!panic_policy.causesImmediateHaltInteropPolicy(raw_policy));
    try std.testing.expect(!panic_policy.recognizesInteropPolicy(reserved_policy));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromInteropPolicy(safe_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromInteropPolicy(mmio_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(raw_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(unknown_policy));
    try std.testing.expect(allocator_policy.requiresExplicitCallerInteropPolicy(safe_policy));
    try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(mmio_policy));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(mmio_policy));
    try std.testing.expect(allocator_policy.requiresResetOnInitInteropPolicy(raw_policy));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicy(reserved_policy));

    try std.testing.expect(unsafe_policy.permitsNoUnsafeInteropPolicy(safe_policy));
    try std.testing.expect(!unsafe_policy.permitsNoUnsafeInteropPolicy(mmio_policy));
    try std.testing.expect(unsafe_policy.permitsVolatileMmioInteropPolicy(mmio_policy));
    try std.testing.expect(!unsafe_policy.permitsVolatileMmioInteropPolicy(raw_policy));
    try std.testing.expect(unsafe_policy.permitsRawPointerBridgeInteropPolicy(raw_policy));
    try std.testing.expect(unsafe_policy.requiresDedicatedAuditInteropPolicy(raw_policy));
    try std.testing.expect(!unsafe_policy.recognizesInteropPolicy(reserved_policy));
    try std.testing.expect(!unsafe_policy.recognizesInteropPolicy(unknown_policy));
}

test "phase3 abi keeps byte-level policy relays aligned with published ABI constants" {
    const safe_policy = abi.defaultInteropPolicy();

    try std.testing.expectEqual(@as(u8, abi.PANIC_ABORT), safe_policy.panic_mode);
    try std.testing.expectEqual(@as(u8, abi.ALLOC_CALLER_PROVIDED), safe_policy.allocator_mode);
    try std.testing.expectEqual(@as(u8, abi.UNSAFE_NONE), safe_policy.unsafe_scope);
    try std.testing.expectEqual(@as(u8, 0), safe_policy.reserved);

    try std.testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromByte(abi.PANIC_ABORT));
    try std.testing.expectEqual(@as(?panic_policy.Escalation, .kernel_bug), panic_policy.escalationFromByte(abi.PANIC_BUG));
    try std.testing.expect(panic_policy.causesImmediateHaltByte(abi.PANIC_BUG));
    try std.testing.expect(panic_policy.permitsWarningOnlyContinuationByte(abi.PANIC_WARN));
    try std.testing.expect(!panic_policy.recognizesInteropPolicyBytes(abi.PANIC_WARN, 1));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expect(allocator_policy.requiresExplicitCallerByte(abi.ALLOC_CALLER_PROVIDED));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackByte(abi.ALLOC_KERNEL_HEAP));
    try std.testing.expect(allocator_policy.initializesOwnedStateByte(abi.ALLOC_ARENA));
    try std.testing.expect(allocator_policy.requiresResetOnInitByte(abi.ALLOC_ARENA));
    try std.testing.expect(!allocator_policy.recognizesInteropPolicyBytes(abi.ALLOC_ARENA, 1));

    try std.testing.expectEqual(@as(?abi.UnsafeScope, .none), unsafe_policy.modeFromByte(abi.UNSAFE_NONE));
    try std.testing.expectEqual(
        @as(?unsafe_policy.AccessBoundary, .typed_safe),
        unsafe_policy.accessBoundaryFromByte(abi.UNSAFE_NONE),
    );
    try std.testing.expectEqual(
        @as(?unsafe_policy.AccessBoundary, .volatile_mmio_window),
        unsafe_policy.accessBoundaryFromByte(abi.UNSAFE_VOLATILE_MMIO),
    );
    try std.testing.expectEqual(
        @as(?unsafe_policy.AccessBoundary, .raw_pointer_bridge),
        unsafe_policy.accessBoundaryFromByte(abi.UNSAFE_RAW_POINTER_BRIDGE),
    );
    try std.testing.expect(unsafe_policy.permitsVolatileMmioByte(abi.UNSAFE_VOLATILE_MMIO));
    try std.testing.expect(unsafe_policy.permitsRawPointerBridgeByte(abi.UNSAFE_RAW_POINTER_BRIDGE));
    try std.testing.expect(!unsafe_policy.recognizesInteropPolicyBytes(abi.UNSAFE_RAW_POINTER_BRIDGE, 1));
}
