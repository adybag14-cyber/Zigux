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
    try layout_assert.assertPublishedAbiLayouts();
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

test "policy starter packet keeps narrow byte and denial symmetry explicit" {
    const cases = [_]struct {
        unsafe_scope: u8,
        reserved: u8,
        expected: ?abi.UnsafeScope,
        typed_only: bool,
        volatile_mmio: bool,
        raw_pointer_bridge: bool,
    }{
        .{ .unsafe_scope = 0, .reserved = 0, .expected = .none, .typed_only = true, .volatile_mmio = false, .raw_pointer_bridge = false },
        .{ .unsafe_scope = 1, .reserved = 0, .expected = .volatile_mmio, .typed_only = false, .volatile_mmio = true, .raw_pointer_bridge = false },
        .{ .unsafe_scope = 2, .reserved = 0, .expected = .raw_pointer_bridge, .typed_only = false, .volatile_mmio = false, .raw_pointer_bridge = true },
        .{ .unsafe_scope = 9, .reserved = 0, .expected = null, .typed_only = false, .volatile_mmio = false, .raw_pointer_bridge = false },
        .{ .unsafe_scope = 2, .reserved = 1, .expected = null, .typed_only = false, .volatile_mmio = false, .raw_pointer_bridge = false },
    };

    for (cases) |case| {
        try testing.expectEqual(case.expected, unsafe_policy.scopeFromInteropPolicyBytes(case.unsafe_scope, case.reserved));
        try testing.expectEqual(case.expected, narrow_surface.scopeFromInteropPolicyBytes(case.unsafe_scope, case.reserved));

        try testing.expectEqual(case.typed_only, unsafe_policy.permitsNoUnsafePolicyBytes(case.unsafe_scope, case.reserved));
        try testing.expectEqual(case.typed_only, narrow_surface.permitsNoUnsafePolicyBytes(case.unsafe_scope, case.reserved));

        try testing.expectEqual(case.volatile_mmio, unsafe_policy.permitsVolatileMmioPolicyBytes(case.unsafe_scope, case.reserved));
        try testing.expectEqual(case.volatile_mmio, narrow_surface.permitsVolatileMmioPolicyBytes(case.unsafe_scope, case.reserved));
        try testing.expectEqual(case.volatile_mmio, narrow_surface.allowsVolatileMmioPolicyBytes(case.unsafe_scope, case.reserved));

        try testing.expectEqual(case.raw_pointer_bridge, unsafe_policy.permitsRawPointerBridgePolicyBytes(case.unsafe_scope, case.reserved));
        try testing.expectEqual(case.raw_pointer_bridge, narrow_surface.permitsRawPointerBridgePolicyBytes(case.unsafe_scope, case.reserved));
        try testing.expectEqual(case.raw_pointer_bridge, narrow_surface.allowsRawPointerBridgePolicyBytes(case.unsafe_scope, case.reserved));

        if (case.typed_only) {
            try unsafe_policy.requireNoUnsafePolicyBytes(case.unsafe_scope, case.reserved);
            try narrow_surface.requireNoUnsafePolicyBytes(case.unsafe_scope, case.reserved);
        } else {
            try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireNoUnsafePolicyBytes(case.unsafe_scope, case.reserved));
            try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireNoUnsafePolicyBytes(case.unsafe_scope, case.reserved));
        }

        if (case.volatile_mmio) {
            try unsafe_policy.requireVolatileMmioPolicyBytes(case.unsafe_scope, case.reserved);
            try narrow_surface.requireVolatileMmioPolicyBytes(case.unsafe_scope, case.reserved);
        } else {
            try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireVolatileMmioPolicyBytes(case.unsafe_scope, case.reserved));
            try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireVolatileMmioPolicyBytes(case.unsafe_scope, case.reserved));
        }

        if (case.raw_pointer_bridge) {
            try unsafe_policy.requireRawPointerBridgePolicyBytes(case.unsafe_scope, case.reserved);
            try narrow_surface.requireRawPointerBridgePolicyBytes(case.unsafe_scope, case.reserved);
        } else {
            try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgePolicyBytes(case.unsafe_scope, case.reserved));
            try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireRawPointerBridgePolicyBytes(case.unsafe_scope, case.reserved));
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

test "policy starter packet keeps unsafe require gates explicit on shared records" {
    const safe_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = 0,
        .reserved = 0,
    };
    const mmio_policy = abi.InteropPolicy{
        .panic_mode = 1,
        .allocator_mode = 1,
        .unsafe_scope = 1,
        .reserved = 0,
    };
    const raw_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 2,
        .unsafe_scope = 2,
        .reserved = 0,
    };
    const reserved_policy = abi.InteropPolicy{
        .panic_mode = 2,
        .allocator_mode = 2,
        .unsafe_scope = 2,
        .reserved = 1,
    };
    const unknown_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = 9,
        .reserved = 0,
    };

    try unsafe_policy.requireNoUnsafeInteropPolicy(safe_policy);
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireNoUnsafeInteropPolicy(mmio_policy));
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireNoUnsafeInteropPolicy(raw_policy));
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireNoUnsafeInteropPolicy(reserved_policy));
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireNoUnsafeInteropPolicy(unknown_policy));

    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireVolatileMmioInteropPolicy(safe_policy));
    try unsafe_policy.requireVolatileMmioInteropPolicy(mmio_policy);
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireVolatileMmioInteropPolicy(raw_policy));
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireVolatileMmioInteropPolicy(reserved_policy));
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireVolatileMmioInteropPolicy(unknown_policy));

    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgeInteropPolicy(safe_policy));
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgeInteropPolicy(mmio_policy));
    try unsafe_policy.requireRawPointerBridgeInteropPolicy(raw_policy);
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgeInteropPolicy(reserved_policy));
    try testing.expectError(error.UnsafeScopeDenied, unsafe_policy.requireRawPointerBridgeInteropPolicy(unknown_policy));

    try narrow_surface.requireNoUnsafeInteropPolicy(safe_policy);
    try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireNoUnsafeInteropPolicy(mmio_policy));
    try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireNoUnsafeInteropPolicy(raw_policy));
    try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireNoUnsafeInteropPolicy(reserved_policy));
    try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireNoUnsafeInteropPolicy(unknown_policy));

    try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireVolatileMmioInteropPolicy(safe_policy));
    try narrow_surface.requireVolatileMmioInteropPolicy(mmio_policy);
    try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireVolatileMmioInteropPolicy(raw_policy));
    try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireVolatileMmioInteropPolicy(reserved_policy));
    try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireVolatileMmioInteropPolicy(unknown_policy));

    try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireRawPointerBridgeInteropPolicy(safe_policy));
    try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireRawPointerBridgeInteropPolicy(mmio_policy));
    try narrow_surface.requireRawPointerBridgeInteropPolicy(raw_policy);
    try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireRawPointerBridgeInteropPolicy(reserved_policy));
    try testing.expectError(error.UnsafeScopeDenied, narrow_surface.requireRawPointerBridgeInteropPolicy(unknown_policy));
}

test "policy starter packet keeps unsafe boundary and audit semantics explicit" {
    const cases = [_]struct {
        policy: abi.InteropPolicy,
        expected_scope: ?abi.UnsafeScope,
        expected_boundary: ?unsafe_policy.AccessBoundary,
        expected_unsafe: bool,
        expected_audit: bool,
    }{
        .{ .policy = .{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 }, .expected_scope = .none, .expected_boundary = .typed_safe, .expected_unsafe = false, .expected_audit = false },
        .{ .policy = .{ .panic_mode = 1, .allocator_mode = 1, .unsafe_scope = 1, .reserved = 0 }, .expected_scope = .volatile_mmio, .expected_boundary = .volatile_mmio_window, .expected_unsafe = true, .expected_audit = true },
        .{ .policy = .{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 0 }, .expected_scope = .raw_pointer_bridge, .expected_boundary = .raw_pointer_bridge, .expected_unsafe = true, .expected_audit = true },
        .{ .policy = .{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 9, .reserved = 0 }, .expected_scope = null, .expected_boundary = null, .expected_unsafe = false, .expected_audit = false },
        .{ .policy = .{ .panic_mode = 2, .allocator_mode = 2, .unsafe_scope = 2, .reserved = 1 }, .expected_scope = null, .expected_boundary = null, .expected_unsafe = false, .expected_audit = false },
    };

    for (cases) |case| {
        try testing.expectEqual(case.expected_scope, unsafe_policy.modeFromInteropPolicy(case.policy));
        try testing.expectEqual(case.expected_scope, unsafe_policy.scopeFromInteropPolicy(case.policy));
        try testing.expectEqual(case.expected_boundary, unsafe_policy.accessBoundaryFromInteropPolicy(case.policy));
        try testing.expectEqual(case.expected_unsafe, unsafe_policy.isUnsafeInteropPolicy(case.policy));
        try testing.expectEqual(case.expected_audit, unsafe_policy.requiresDedicatedAuditInteropPolicy(case.policy));

        if (case.expected_scope) |scope| {
            try testing.expectEqual(case.expected_boundary.?, unsafe_policy.accessBoundaryFor(scope));
            try testing.expectEqual(case.expected_unsafe, unsafe_policy.isUnsafe(scope));
            try testing.expectEqual(case.expected_audit, unsafe_policy.requiresDedicatedAudit(scope));
        }
    }

    const byte_cases = [_]struct {
        unsafe_scope: u8,
        reserved: u8,
        expected_boundary: ?unsafe_policy.AccessBoundary,
        expected_unsafe: bool,
        expected_audit: bool,
    }{
        .{ .unsafe_scope = 0, .reserved = 0, .expected_boundary = .typed_safe, .expected_unsafe = false, .expected_audit = false },
        .{ .unsafe_scope = 1, .reserved = 0, .expected_boundary = .volatile_mmio_window, .expected_unsafe = true, .expected_audit = true },
        .{ .unsafe_scope = 2, .reserved = 0, .expected_boundary = .raw_pointer_bridge, .expected_unsafe = true, .expected_audit = true },
        .{ .unsafe_scope = 9, .reserved = 0, .expected_boundary = null, .expected_unsafe = false, .expected_audit = false },
        .{ .unsafe_scope = 2, .reserved = 1, .expected_boundary = null, .expected_unsafe = false, .expected_audit = false },
    };

    for (byte_cases) |case| {
        try testing.expectEqual(case.expected_boundary, unsafe_policy.accessBoundaryFromInteropPolicyBytes(case.unsafe_scope, case.reserved));
        try testing.expectEqual(case.expected_unsafe, unsafe_policy.isUnsafePolicyBytes(case.unsafe_scope, case.reserved));
        try testing.expectEqual(case.expected_audit, unsafe_policy.requiresDedicatedAuditPolicyBytes(case.unsafe_scope, case.reserved));

        if (case.reserved == 0) {
            try testing.expectEqual(case.expected_boundary, unsafe_policy.accessBoundaryFromByte(case.unsafe_scope));
            try testing.expectEqual(case.expected_unsafe, unsafe_policy.isUnsafeByte(case.unsafe_scope));
            try testing.expectEqual(case.expected_audit, unsafe_policy.requiresDedicatedAuditByte(case.unsafe_scope));
        }
    }
}

test "policy starter packet keeps panic and allocator byte guards explicit" {
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
        .panic_mode = @intFromEnum(abi.PanicMode.warn),
        .allocator_mode = @intFromEnum(abi.AllocatorMode.arena),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.raw_pointer_bridge),
        .reserved = 1,
    };
    const unknown_panic = abi.InteropPolicy{
        .panic_mode = 9,
        .allocator_mode = @intFromEnum(abi.AllocatorMode.kernel_heap),
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };
    const unknown_allocator = abi.InteropPolicy{
        .panic_mode = @intFromEnum(abi.PanicMode.abort),
        .allocator_mode = 9,
        .unsafe_scope = @intFromEnum(abi.UnsafeScope.none),
        .reserved = 0,
    };

    try testing.expectEqual(@as(?panic_policy.Escalation, .kernel_bug), panic_policy.escalationFromInteropPolicy(bug_heap));
    try testing.expectEqual(@as(?panic_policy.Escalation, .warning_only), panic_policy.escalationFromInteropPolicy(warn_arena));
    try testing.expectEqual(@as(?panic_policy.Escalation, null), panic_policy.escalationFromInteropPolicy(reserved));
    try testing.expectEqual(@as(?panic_policy.Escalation, null), panic_policy.escalationFromInteropPolicy(unknown_panic));
    try testing.expect(panic_policy.recognizesInteropPolicy(bug_heap));
    try testing.expect(!panic_policy.recognizesInteropPolicy(reserved));
    try testing.expect(!panic_policy.recognizesInteropPolicy(unknown_panic));
    try testing.expect(panic_policy.causesImmediateHaltInteropPolicy(bug_heap));
    try testing.expect(!panic_policy.causesImmediateHaltInteropPolicy(warn_arena));
    try testing.expect(!panic_policy.causesImmediateHaltInteropPolicy(reserved));
    try testing.expect(panic_policy.emitsKernelBugByte(@intFromEnum(abi.PanicMode.bug)));
    try testing.expect(!panic_policy.emitsKernelBugByte(9));
    try testing.expect(panic_policy.permitsWarningOnlyContinuationByte(@intFromEnum(abi.PanicMode.warn)));
    try testing.expect(!panic_policy.permitsWarningOnlyContinuationPolicyBytes(@intFromEnum(abi.PanicMode.warn), 1));

    try testing.expect(allocator_policy.recognizesInteropPolicy(bug_heap));
    try testing.expect(allocator_policy.recognizesInteropPolicy(warn_arena));
    try testing.expect(!allocator_policy.recognizesInteropPolicy(reserved));
    try testing.expect(!allocator_policy.recognizesInteropPolicy(unknown_allocator));
    try testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(bug_heap));
    try testing.expect(allocator_policy.permitsGlobalFallbackInteropPolicy(warn_arena));
    try testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(reserved));
    try testing.expect(allocator_policy.initializesOwnedStateInteropPolicy(bug_heap));
    try testing.expect(allocator_policy.initializesOwnedStateInteropPolicy(warn_arena));
    try testing.expect(!allocator_policy.initializesOwnedStateInteropPolicy(reserved));
    try testing.expect(allocator_policy.requiresResetOnInitInteropPolicy(warn_arena));
    try testing.expect(!allocator_policy.requiresResetOnInitInteropPolicy(bug_heap));
    try testing.expect(!allocator_policy.requiresResetOnInitInteropPolicy(reserved));
    try testing.expect(allocator_policy.requiresExplicitCallerByte(@intFromEnum(abi.AllocatorMode.caller_provided)));
    try testing.expect(!allocator_policy.requiresExplicitCallerByte(@intFromEnum(abi.AllocatorMode.kernel_heap)));
    try testing.expect(allocator_policy.permitsGlobalFallbackByte(@intFromEnum(abi.AllocatorMode.arena)));
    try testing.expect(allocator_policy.requiresResetOnInitByte(@intFromEnum(abi.AllocatorMode.arena)));
    try testing.expect(!allocator_policy.requiresResetOnInitByte(9));
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
