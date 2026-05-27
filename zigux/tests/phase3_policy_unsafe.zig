const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const panic_policy = @import("panic_policy");
const unsafe_policy = @import("unsafe_policy");
const narrow = @import("narrow");

fn safePolicy() abi.InteropPolicy {
    return .{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
}

fn mmioPolicy() abi.InteropPolicy {
    return .{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.volatile_mmio),
        .reserved = 0,
    };
}

fn rawPolicy() abi.InteropPolicy {
    return .{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
}

test "phase3 policy unsafe replay decodes shared policy records" {
    try testing.expectEqual(@as(?abi.PanicMode, .abort), panic_policy.modeFromInteropPolicy(safePolicy()));
    try testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromInteropPolicy(mmioPolicy()));
    try testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromInteropPolicy(rawPolicy()));

    try testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), allocator_policy.modeFromInteropPolicy(safePolicy()));
    try testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromInteropPolicy(mmioPolicy()));
    try testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(rawPolicy()));

    try testing.expectEqual(@as(?abi.UnsafeScope, .none), unsafe_policy.scopeFromInteropPolicy(safePolicy()));
    try testing.expectEqual(@as(?abi.UnsafeScope, .volatile_mmio), unsafe_policy.scopeFromInteropPolicy(mmioPolicy()));
    try testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), unsafe_policy.scopeFromInteropPolicy(rawPolicy()));
}

test "phase3 policy unsafe replay keeps ABI recognition aligned with helper decoders" {
    const cases = [_]abi.InteropPolicy{
        safePolicy(),
        mmioPolicy(),
        rawPolicy(),
        .{ .panic_mode = 9, .allocator_mode = abi.ALLOC_CALLER_PROVIDED, .unsafe_scope = abi.UNSAFE_NONE, .reserved = 0 },
        .{ .panic_mode = abi.PANIC_ABORT, .allocator_mode = 9, .unsafe_scope = abi.UNSAFE_NONE, .reserved = 0 },
        .{ .panic_mode = abi.PANIC_ABORT, .allocator_mode = abi.ALLOC_CALLER_PROVIDED, .unsafe_scope = 9, .reserved = 0 },
        .{ .panic_mode = abi.PANIC_WARN, .allocator_mode = abi.ALLOC_ARENA, .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE, .reserved = 1 },
    };

    for (cases) |policy| {
        const panic_known = panic_policy.modeFromInteropPolicy(policy) != null;
        const allocator_known = allocator_policy.modeFromInteropPolicy(policy) != null;
        const unsafe_known = unsafe_policy.scopeFromInteropPolicy(policy) != null;

        try testing.expectEqual(abi.panicModeFromInteropPolicy(policy), panic_policy.modeFromInteropPolicy(policy));
        try testing.expectEqual(abi.allocatorModeFromInteropPolicy(policy), allocator_policy.modeFromInteropPolicy(policy));
        try testing.expectEqual(abi.unsafeScopeFromInteropPolicy(policy), unsafe_policy.scopeFromInteropPolicy(policy));
        try testing.expectEqual(abi.interopPolicyIsRecognized(policy), panic_known and allocator_known and unsafe_known);
        try testing.expectEqual(unsafe_policy.recognizesInteropPolicy(policy), narrow.recognizesInteropPolicy(policy));
    }
}

test "phase3 policy unsafe replay keeps reserved-byte failures closed across helpers" {
    const reserved_mmio = abi.InteropPolicy{
        .panic_mode = abi.PANIC_BUG,
        .allocator_mode = abi.ALLOC_KERNEL_HEAP,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 1,
    };

    try testing.expect(!abi.interopPolicyReservedClear(reserved_mmio));
    try testing.expectEqual(@as(?abi.PanicMode, null), abi.panicModeFromInteropPolicy(reserved_mmio));
    try testing.expectEqual(@as(?abi.AllocatorMode, null), abi.allocatorModeFromInteropPolicy(reserved_mmio));
    try testing.expectEqual(@as(?abi.UnsafeScope, null), abi.unsafeScopeFromInteropPolicy(reserved_mmio));
    try testing.expect(!abi.interopPolicyIsRecognized(reserved_mmio));

    try testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved_mmio));
    try testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved_mmio));
    try testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.scopeFromInteropPolicy(reserved_mmio));
    try testing.expectEqual(@as(?unsafe_policy.AccessBoundary, null), unsafe_policy.accessBoundaryFromInteropPolicy(reserved_mmio));
    try testing.expectEqual(@as(?narrow.Surface, null), narrow.surfaceFromInteropPolicy(reserved_mmio));
    try testing.expect(!panic_policy.recognizesInteropPolicy(reserved_mmio));
    try testing.expect(!allocator_policy.recognizesInteropPolicy(reserved_mmio));
    try testing.expect(!unsafe_policy.recognizesInteropPolicy(reserved_mmio));
    try testing.expect(!narrow.recognizesInteropPolicy(reserved_mmio));
}

test "phase3 policy unsafe replay keeps helper and narrow gates aligned" {
    const cases = [_]abi.InteropPolicy{
        safePolicy(),
        mmioPolicy(),
        rawPolicy(),
        .{ .panic_mode = 9, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 },
        .{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 1 },
    };

    for (cases) |policy| {
        try testing.expectEqual(unsafe_policy.permitsNoUnsafeInteropPolicy(policy), narrow.permitsNoUnsafeInteropPolicy(policy));
        try testing.expectEqual(unsafe_policy.permitsVolatileMmioInteropPolicy(policy), narrow.permitsVolatileMmioInteropPolicy(policy));
        try testing.expectEqual(unsafe_policy.permitsRawPointerBridgeInteropPolicy(policy), narrow.permitsRawPointerBridgeInteropPolicy(policy));
        try testing.expectEqual(unsafe_policy.allowsTypedOnlyAccessInteropPolicy(policy), narrow.permitsNoUnsafeInteropPolicy(policy));
        try testing.expectEqual(unsafe_policy.allowsVolatileMmioInteropPolicy(policy), narrow.permitsVolatileMmioInteropPolicy(policy));
        try testing.expectEqual(unsafe_policy.allowsRawPointerBridgeInteropPolicy(policy), narrow.permitsRawPointerBridgeInteropPolicy(policy));
        try testing.expectEqual(
            unsafe_policy.accessBoundaryFromInteropPolicy(policy) != null,
            narrow.accessBoundaryFromInteropPolicy(policy) != null,
        );
        try testing.expectEqual(
            unsafe_policy.scopeFromInteropPolicy(policy) != null,
            narrow.surfaceFromInteropPolicy(policy) != null,
        );
    }
}

test "phase3 policy unsafe replay keeps require gates fail closed" {
    try unsafe_policy.requireNoUnsafeInteropPolicy(safePolicy());
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireVolatileMmioInteropPolicy(safePolicy()));
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgeInteropPolicy(safePolicy()));

    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireNoUnsafeInteropPolicy(mmioPolicy()));
    try unsafe_policy.requireVolatileMmioInteropPolicy(mmioPolicy());
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgeInteropPolicy(mmioPolicy()));

    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireNoUnsafeInteropPolicy(rawPolicy()));
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireVolatileMmioInteropPolicy(rawPolicy()));
    try unsafe_policy.requireRawPointerBridgeInteropPolicy(rawPolicy());
}

test "phase3 policy unsafe replay keeps policy consequences explicit" {
    try testing.expect(panic_policy.causesImmediateHaltInteropPolicy(mmioPolicy()));
    try testing.expect(panic_policy.emitsKernelBugInteropPolicy(mmioPolicy()));
    try testing.expectEqual(@as(?panic_policy.Action, .bug_check), panic_policy.actionForInteropPolicy(mmioPolicy()));

    try testing.expect(!panic_policy.causesImmediateHaltInteropPolicy(rawPolicy()));
    try testing.expect(panic_policy.canReturnInteropPolicy(rawPolicy()));
    try testing.expectEqual(@as(?panic_policy.Action, .warn_and_return), panic_policy.actionForInteropPolicy(rawPolicy()));

    try allocator_policy.requireInitFlowInteropPolicy(safePolicy(), .caller_prepared);
    try allocator_policy.requireInitFlowInteropPolicy(mmioPolicy(), .helper_owned);
    try allocator_policy.requireInitFlowInteropPolicy(rawPolicy(), .helper_owned_with_reset);
    try testing.expect(allocator_policy.requiresExplicitCallerInteropPolicy(safePolicy()));
    try testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(mmioPolicy()));
    try testing.expect(allocator_policy.requiresResetOnInitInteropPolicy(rawPolicy()));

    try testing.expectEqual(@as(?narrow.Surface, .safe_only), narrow.surfaceFromInteropPolicy(safePolicy()));
    try testing.expectEqual(@as(?narrow.Surface, .mmio_only), narrow.surfaceFromInteropPolicy(mmioPolicy()));
    try testing.expectEqual(@as(?narrow.Surface, .raw_pointer_bridge_only), narrow.surfaceFromInteropPolicy(rawPolicy()));
    try testing.expect(!narrow.requiresDedicatedAuditInteropPolicy(safePolicy()));
    try testing.expect(narrow.requiresDedicatedAuditInteropPolicy(mmioPolicy()));
    try testing.expect(narrow.requiresDedicatedAuditInteropPolicy(rawPolicy()));
}
