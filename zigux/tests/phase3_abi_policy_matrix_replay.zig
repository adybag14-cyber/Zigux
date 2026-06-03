const std = @import("std");

const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");
const narrow_unsafe = @import("narrow_unsafe");
const panic_policy = @import("panic_policy");

const ExpectedPolicy = struct {
    panic_mode: ?abi.PanicMode,
    panic_action: ?panic_policy.Action,
    allocator_mode: ?abi.AllocatorMode,
    unsafe_scope: ?narrow_unsafe.UnsafeScopeTag,
    can_return: bool,
    requires_caller_allocator: bool,
    permits_global_allocator_fallback: bool,
};

fn expectPolicy(policy: abi.InteropPolicy, expected: ExpectedPolicy) !void {
    try std.testing.expectEqual(expected.panic_mode, panic_policy.modeFromInteropPolicy(policy));
    try std.testing.expectEqual(expected.panic_action, panic_policy.actionForInteropPolicy(policy));
    try std.testing.expectEqual(expected.allocator_mode, allocator_policy.modeFromInteropPolicy(policy));
    try std.testing.expectEqual(expected.unsafe_scope, narrow_unsafe.scopeFromInteropPolicy(policy));

    try std.testing.expectEqual(expected.can_return, panic_policy.canReturnInteropPolicy(policy));
    try std.testing.expectEqual(
        expected.requires_caller_allocator,
        allocator_policy.requiresExplicitCallerInteropPolicy(policy),
    );
    try std.testing.expectEqual(
        expected.permits_global_allocator_fallback,
        allocator_policy.permitsGlobalFallbackInteropPolicy(policy),
    );

    try std.testing.expectEqual(expected.panic_mode != null, panic_policy.recognizesInteropPolicy(policy));
    try std.testing.expectEqual(expected.allocator_mode != null, allocator_policy.recognizesInteropPolicy(policy));
    try std.testing.expectEqual(expected.unsafe_scope != null, narrow_unsafe.recognizesInteropPolicy(policy));
}

test "phase3 abi policy matrix keeps valid interop triples aligned" {
    const matrix = [_]struct {
        policy: abi.InteropPolicy,
        expected: ExpectedPolicy,
    }{
        .{
            .policy = .{
                .panic_mode = abi.PANIC_ABORT,
                .allocator_mode = abi.ALLOC_CALLER_PROVIDED,
                .unsafe_scope = abi.UNSAFE_NONE,
                .reserved = 0,
            },
            .expected = .{
                .panic_mode = .abort,
                .panic_action = .abort_now,
                .allocator_mode = .caller_provided,
                .unsafe_scope = .none,
                .can_return = false,
                .requires_caller_allocator = true,
                .permits_global_allocator_fallback = false,
            },
        },
        .{
            .policy = .{
                .panic_mode = abi.PANIC_BUG,
                .allocator_mode = abi.ALLOC_KERNEL_HEAP,
                .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
                .reserved = 0,
            },
            .expected = .{
                .panic_mode = .bug,
                .panic_action = .bug_check,
                .allocator_mode = .kernel_heap,
                .unsafe_scope = .volatile_mmio,
                .can_return = false,
                .requires_caller_allocator = false,
                .permits_global_allocator_fallback = true,
            },
        },
        .{
            .policy = .{
                .panic_mode = abi.PANIC_WARN,
                .allocator_mode = abi.ALLOC_ARENA,
                .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
                .reserved = 0,
            },
            .expected = .{
                .panic_mode = .warn,
                .panic_action = .warn_and_return,
                .allocator_mode = .arena,
                .unsafe_scope = .raw_pointer_bridge,
                .can_return = true,
                .requires_caller_allocator = false,
                .permits_global_allocator_fallback = true,
            },
        },
    };

    for (matrix) |case| {
        try expectPolicy(case.policy, case.expected);
    }
}

test "phase3 abi policy matrix rejects reserved and unknown interop bytes" {
    const invalid_cases = [_]struct {
        policy: abi.InteropPolicy,
        expected: ExpectedPolicy,
    }{
        .{
            .policy = .{
                .panic_mode = abi.PANIC_WARN,
                .allocator_mode = abi.ALLOC_ARENA,
                .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
                .reserved = 1,
            },
            .expected = .{
                .panic_mode = null,
                .panic_action = null,
                .allocator_mode = null,
                .unsafe_scope = null,
                .can_return = false,
                .requires_caller_allocator = false,
                .permits_global_allocator_fallback = false,
            },
        },
        .{
            .policy = .{
                .panic_mode = 9,
                .allocator_mode = abi.ALLOC_CALLER_PROVIDED,
                .unsafe_scope = abi.UNSAFE_NONE,
                .reserved = 0,
            },
            .expected = .{
                .panic_mode = null,
                .panic_action = null,
                .allocator_mode = .caller_provided,
                .unsafe_scope = .none,
                .can_return = false,
                .requires_caller_allocator = true,
                .permits_global_allocator_fallback = false,
            },
        },
        .{
            .policy = .{
                .panic_mode = abi.PANIC_ABORT,
                .allocator_mode = 9,
                .unsafe_scope = abi.UNSAFE_NONE,
                .reserved = 0,
            },
            .expected = .{
                .panic_mode = .abort,
                .panic_action = .abort_now,
                .allocator_mode = null,
                .unsafe_scope = .none,
                .can_return = false,
                .requires_caller_allocator = false,
                .permits_global_allocator_fallback = false,
            },
        },
        .{
            .policy = .{
                .panic_mode = abi.PANIC_ABORT,
                .allocator_mode = abi.ALLOC_CALLER_PROVIDED,
                .unsafe_scope = 9,
                .reserved = 0,
            },
            .expected = .{
                .panic_mode = .abort,
                .panic_action = .abort_now,
                .allocator_mode = .caller_provided,
                .unsafe_scope = null,
                .can_return = false,
                .requires_caller_allocator = true,
                .permits_global_allocator_fallback = false,
            },
        },
    };

    for (invalid_cases) |case| {
        const policy = case.policy;
        try expectPolicy(policy, case.expected);
        if (case.expected.unsafe_scope == null) {
            try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireNoUnsafeInteropPolicy(policy));
            try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireVolatileMmioInteropPolicy(policy));
            try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireRawPointerBridgeInteropPolicy(policy));
            continue;
        }

        switch (case.expected.unsafe_scope.?) {
            .none => {
                try narrow_unsafe.requireNoUnsafeInteropPolicy(policy);
                try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireVolatileMmioInteropPolicy(policy));
                try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireRawPointerBridgeInteropPolicy(policy));
            },
            .volatile_mmio => {
                try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireNoUnsafeInteropPolicy(policy));
                try narrow_unsafe.requireVolatileMmioInteropPolicy(policy);
                try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireRawPointerBridgeInteropPolicy(policy));
            },
            .raw_pointer_bridge => {
                try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireNoUnsafeInteropPolicy(policy));
                try std.testing.expectError(error.UnsafeScopeDenied, narrow_unsafe.requireVolatileMmioInteropPolicy(policy));
                try narrow_unsafe.requireRawPointerBridgeInteropPolicy(policy);
            },
        }
    }
}
