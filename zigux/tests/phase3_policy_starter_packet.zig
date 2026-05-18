const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const panic_policy = @import("panic_policy");
const unsafe_policy = @import("unsafe_policy");
const layout_assert = @import("layout_assert");
const narrow_surface = @import("narrow_surface");

test "policy starter packet decodes shared interop policy records" {
    const bug_heap = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.bug),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const warn_arena = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 0,
    };
    const reserved = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 1,
    };

    try testing.expectEqual(@as(?abi.PanicMode, .bug), panic_policy.modeFromInteropPolicy(bug_heap));
    try testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), allocator_policy.modeFromInteropPolicy(bug_heap));
    try testing.expectEqual(@as(?abi.UnsafeScope, .none), unsafe_policy.modeFromInteropPolicy(bug_heap));
    try testing.expectEqual(@as(?abi.PanicMode, .warn), panic_policy.modeFromInteropPolicy(warn_arena));
    try testing.expectEqual(@as(?abi.AllocatorMode, .arena), allocator_policy.modeFromInteropPolicy(warn_arena));
    try testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), unsafe_policy.modeFromInteropPolicy(warn_arena));
    try testing.expectEqual(@as(?abi.PanicMode, null), panic_policy.modeFromInteropPolicy(reserved));
    try testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicy(reserved));
    try testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.modeFromInteropPolicy(reserved));

    try testing.expectEqual(@as(?abi.UnsafeScope, .none), unsafe_policy.scopeFromInteropPolicy(bug_heap));
    try testing.expectEqual(@as(?abi.UnsafeScope, .raw_pointer_bridge), unsafe_policy.scopeFromInteropPolicy(warn_arena));
    try testing.expectEqual(@as(?abi.UnsafeScope, null), unsafe_policy.scopeFromInteropPolicy(reserved));

    try testing.expect(unsafe_policy.permitsNoUnsafeInteropPolicy(bug_heap));
    try testing.expect(!unsafe_policy.permitsVolatileMmioInteropPolicy(bug_heap));
    try testing.expect(!unsafe_policy.permitsRawPointerBridgeInteropPolicy(bug_heap));

    try testing.expect(!unsafe_policy.permitsNoUnsafeInteropPolicy(warn_arena));
    try testing.expect(!unsafe_policy.permitsVolatileMmioInteropPolicy(warn_arena));
    try testing.expect(unsafe_policy.permitsRawPointerBridgeInteropPolicy(warn_arena));

    try testing.expect(!unsafe_policy.permitsNoUnsafeInteropPolicy(reserved));
    try testing.expect(!unsafe_policy.permitsVolatileMmioInteropPolicy(reserved));
    try testing.expect(!unsafe_policy.permitsRawPointerBridgeInteropPolicy(reserved));
}

test "policy starter packet keeps interop-policy layout explicit" {
    try layout_assert.expectLayout(abi.InteropPolicy, 4, 1);
    try layout_assert.expectFieldLayout(abi.InteropPolicy, "panic_mode", 0);
    try layout_assert.expectFieldLayout(abi.InteropPolicy, "allocator_mode", 1);
    try layout_assert.expectFieldLayout(abi.InteropPolicy, "unsafe_scope", 2);
    try layout_assert.expectFieldLayout(abi.InteropPolicy, "reserved", 3);
}

test "policy starter packet exercises exported layout assertion guards" {
    try layout_assert.assertBoundaryHeaderLayout();
    try layout_assert.assertExportStatusLayout();
    try layout_assert.assertInteropPolicyLayout();
    try layout_assert.assertNotifierBlockLayout();
    try layout_assert.assertNotifierChainPriorityIncreaseLayout();
    layout_assert.assertInteropPolicyModeValues();
    layout_assert.assertNotifierResultValues();
}

test "policy starter packet keeps narrow-surface decoding aligned" {
    const cases = [_]struct {
        policy: abi.InteropPolicy,
        expected: ?abi.UnsafeScope,
        typed_only: bool,
        volatile_mmio: bool,
        raw_pointer_bridge: bool,
    }{
        .{ .policy = .{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 }, .expected = .none, .typed_only = true, .volatile_mmio = false, .raw_pointer_bridge = false },
        .{ .policy = .{ .panic_mode = 1, .allocator_mode = 1, .unsafe_scope = 1, .reserved = 0 }, .expected = .volatile_mmio, .typed_only = false, .volatile_mmio = true, .raw_pointer_bridge = false },
        .{ .policy = .{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 0 }, .expected = .raw_pointer_bridge, .typed_only = false, .volatile_mmio = false, .raw_pointer_bridge = true },
        .{ .policy = .{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 9, .reserved = 0 }, .expected = null, .typed_only = false, .volatile_mmio = false, .raw_pointer_bridge = false },
        .{ .policy = .{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 1 }, .expected = null, .typed_only = false, .volatile_mmio = false, .raw_pointer_bridge = false },
    };

    for (cases) |case| {
        const helper_scope = unsafe_policy.scopeFromInteropPolicy(case.policy);
        const narrow_scope = narrow_surface.scopeFromInteropPolicy(case.policy);
        try testing.expectEqual(case.expected, helper_scope);
        try testing.expectEqual(case.expected, narrow_scope);
        try testing.expectEqual(case.typed_only, unsafe_policy.allowsTypedOnlyAccessInteropPolicy(case.policy));
        try testing.expectEqual(case.volatile_mmio, unsafe_policy.permitsVolatileMmioInteropPolicy(case.policy));
        try testing.expectEqual(case.raw_pointer_bridge, unsafe_policy.permitsRawPointerBridgeInteropPolicy(case.policy));

        if (narrow_scope) |scope| {
            try testing.expectEqual(case.typed_only, scope == .none);
            try testing.expectEqual(case.volatile_mmio, narrow_surface.allowsVolatileMmio(scope));
            try testing.expectEqual(case.raw_pointer_bridge, narrow_surface.allowsRawPointerBridge(scope));
            try testing.expectEqual(!case.typed_only, narrow_surface.requiresDedicatedAudit(scope));
        } else {
            try testing.expect(!case.typed_only);
            try testing.expect(!case.volatile_mmio);
            try testing.expect(!case.raw_pointer_bridge);
        }
    }
}

test "policy starter packet keeps unsafe alias symmetry explicit on shared records" {
    const cases = [_]struct {
        policy: abi.InteropPolicy,
        expected: ?abi.UnsafeScope,
    }{
        .{ .policy = .{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 }, .expected = .none },
        .{ .policy = .{ .panic_mode = 1, .allocator_mode = 1, .unsafe_scope = 1, .reserved = 0 }, .expected = .volatile_mmio },
        .{ .policy = .{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 0 }, .expected = .raw_pointer_bridge },
        .{ .policy = .{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 9, .reserved = 0 }, .expected = null },
        .{ .policy = .{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 1 }, .expected = null },
    };

    for (cases) |case| {
        try testing.expectEqual(case.expected, unsafe_policy.modeFromInteropPolicy(case.policy));
        try testing.expectEqual(case.expected, unsafe_policy.scopeFromInteropPolicy(case.policy));
        try testing.expectEqual(
            unsafe_policy.permitsNoUnsafeInteropPolicy(case.policy),
            unsafe_policy.allowsTypedOnlyAccessInteropPolicy(case.policy),
        );
        try testing.expectEqual(
            unsafe_policy.permitsVolatileMmioInteropPolicy(case.policy),
            unsafe_policy.requiresVolatileMmioAccessInteropPolicy(case.policy),
        );
        try testing.expectEqual(
            unsafe_policy.permitsRawPointerBridgeInteropPolicy(case.policy),
            unsafe_policy.requiresRawPointerBridgeInteropPolicy(case.policy),
        );
    }
}

test "panic policy starter packet keeps escalation semantics explicit" {
    try testing.expectEqual(panic_policy.Escalation.immediate_abort, panic_policy.escalationFor(.abort));
    try testing.expectEqual(panic_policy.Escalation.kernel_bug, panic_policy.escalationFor(.bug));
    try testing.expectEqual(panic_policy.Escalation.warning_only, panic_policy.escalationFor(.warn));

    try testing.expect(panic_policy.causesImmediateHalt(.abort));
    try testing.expect(panic_policy.causesImmediateHalt(.bug));
    try testing.expect(!panic_policy.causesImmediateHalt(.warn));
    try testing.expect(panic_policy.emitsKernelBug(.bug));
    try testing.expect(!panic_policy.emitsKernelBug(.warn));
    try testing.expect(panic_policy.permitsWarningOnlyContinuation(.warn));
}

test "allocator policy starter packet keeps init ownership semantics explicit" {
    try testing.expectEqual(allocator_policy.InitFlow.caller_prepared, allocator_policy.initFlowFor(.caller_provided));
    try testing.expectEqual(allocator_policy.InitFlow.helper_owned, allocator_policy.initFlowFor(.kernel_heap));
    try testing.expectEqual(allocator_policy.InitFlow.helper_owned_with_reset, allocator_policy.initFlowFor(.arena));

    try testing.expect(allocator_policy.requiresExplicitCaller(.caller_provided));
    try testing.expect(!allocator_policy.requiresExplicitCaller(.kernel_heap));
    try testing.expect(allocator_policy.permitsGlobalFallback(.kernel_heap));
    try testing.expect(allocator_policy.permitsGlobalFallback(.arena));
    try testing.expect(!allocator_policy.permitsGlobalFallback(.caller_provided));
    try testing.expect(allocator_policy.initializesOwnedState(.kernel_heap));
    try testing.expect(allocator_policy.initializesOwnedState(.arena));
    try testing.expect(!allocator_policy.initializesOwnedState(.caller_provided));
    try testing.expect(allocator_policy.requiresResetOnInit(.arena));
    try testing.expect(!allocator_policy.requiresResetOnInit(.kernel_heap));
}

test "unsafe policy starter packet keeps access semantics explicit" {
    try testing.expectEqual(unsafe_policy.AccessBoundary.typed_safe, unsafe_policy.accessBoundaryFor(.none));
    try testing.expectEqual(unsafe_policy.AccessBoundary.volatile_mmio_window, unsafe_policy.accessBoundaryFor(.volatile_mmio));
    try testing.expectEqual(unsafe_policy.AccessBoundary.raw_pointer_bridge, unsafe_policy.accessBoundaryFor(.raw_pointer_bridge));

    try testing.expect(unsafe_policy.allowsTypedOnlyAccess(.none));
    try testing.expect(unsafe_policy.permitsNoUnsafe(.none));
    try testing.expect(!unsafe_policy.allowsTypedOnlyAccess(.volatile_mmio));
    try testing.expect(!unsafe_policy.permitsNoUnsafe(.volatile_mmio));
    try testing.expect(!unsafe_policy.allowsTypedOnlyAccess(.raw_pointer_bridge));
    try testing.expect(!unsafe_policy.permitsNoUnsafe(.raw_pointer_bridge));
    try testing.expect(!unsafe_policy.requiresVolatileMmioAccess(.none));
    try testing.expect(!unsafe_policy.permitsVolatileMmio(.none));
    try testing.expect(unsafe_policy.requiresVolatileMmioAccess(.volatile_mmio));
    try testing.expect(unsafe_policy.permitsVolatileMmio(.volatile_mmio));
    try testing.expect(!unsafe_policy.requiresVolatileMmioAccess(.raw_pointer_bridge));
    try testing.expect(!unsafe_policy.permitsVolatileMmio(.raw_pointer_bridge));
    try testing.expect(!unsafe_policy.requiresRawPointerBridge(.none));
    try testing.expect(!unsafe_policy.permitsRawPointerBridge(.none));
    try testing.expect(!unsafe_policy.requiresRawPointerBridge(.volatile_mmio));
    try testing.expect(!unsafe_policy.permitsRawPointerBridge(.volatile_mmio));
    try testing.expect(unsafe_policy.requiresRawPointerBridge(.raw_pointer_bridge));
    try testing.expect(unsafe_policy.permitsRawPointerBridge(.raw_pointer_bridge));
}
