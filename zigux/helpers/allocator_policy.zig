const std = @import("std");
const abi = @import("abi_bindings");

pub const InitFlow = enum {
    caller_prepared,
    helper_owned,
    helper_owned_with_reset,
};

pub const AllocatorPolicyError = error{UnexpectedAllocatorMode};

pub fn modeFromInteropPolicyBytes(mode: u8, reserved: u8) ?abi.AllocatorMode {
    if (reserved != 0) return null;
    return switch (mode) {
        @intFromEnum(abi.AllocatorMode.caller_provided) => .caller_provided,
        @intFromEnum(abi.AllocatorMode.kernel_heap) => .kernel_heap,
        @intFromEnum(abi.AllocatorMode.arena) => .arena,
        else => null,
    };
}

pub fn modeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.AllocatorMode {
    return modeFromInteropPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn modeFromByte(mode: u8) ?abi.AllocatorMode {
    return modeFromInteropPolicyBytes(mode, 0);
}

pub fn recognizesInteropPolicyBytes(mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(mode, reserved) != null;
}

pub fn recognizesInteropPolicy(policy: abi.InteropPolicy) bool {
    return modeFromInteropPolicy(policy) != null;
}

pub fn recognizesByte(mode: u8) bool {
    return recognizesInteropPolicyBytes(mode, 0);
}

pub fn initFlowFor(mode: abi.AllocatorMode) InitFlow {
    return switch (mode) {
        .caller_provided => .caller_prepared,
        .kernel_heap => .helper_owned,
        .arena => .helper_owned_with_reset,
    };
}

fn requireInitFlow(mode: abi.AllocatorMode, expected: InitFlow) AllocatorPolicyError!void {
    if (initFlowFor(mode) != expected) {
        return error.UnexpectedAllocatorMode;
    }
}

fn requireOutcome(result: anyerror!void) ?anyerror {
    result catch |err| return err;
    return null;
}

fn expectOutcomeEqual(actual: ?anyerror, expected: ?anyerror) !void {
    if (expected) |expected_err| {
        const actual_err = actual orelse return error.TestExpectedEqual;
        try std.testing.expect(actual_err == expected_err);
        return;
    }
    try std.testing.expectEqual(@as(?anyerror, null), actual);
}

pub fn initFlowFromInteropPolicyBytes(mode: u8, reserved: u8) ?InitFlow {
    return initFlowFor(modeFromInteropPolicyBytes(mode, reserved) orelse return null);
}

pub fn initFlowFromInteropPolicy(policy: abi.InteropPolicy) ?InitFlow {
    return initFlowFromInteropPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn initFlowFromByte(mode: u8) ?InitFlow {
    return initFlowFromInteropPolicyBytes(mode, 0);
}

pub fn requiresExplicitCaller(mode: abi.AllocatorMode) bool {
    return mode == .caller_provided;
}

pub fn requireExplicitCaller(mode: abi.AllocatorMode) AllocatorPolicyError!void {
    try requireInitFlow(mode, .caller_prepared);
}

pub fn requiresExplicitCallerPolicyBytes(mode: u8, reserved: u8) bool {
    return modeFromInteropPolicyBytes(mode, reserved) == .caller_provided;
}

pub fn requiresExplicitCallerInteropPolicy(policy: abi.InteropPolicy) bool {
    return requiresExplicitCallerPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn requiresExplicitCallerByte(mode: u8) bool {
    return requiresExplicitCallerPolicyBytes(mode, 0);
}

pub fn requireExplicitCallerPolicyBytes(mode: u8, reserved: u8) AllocatorPolicyError!void {
    return requireExplicitCaller(modeFromInteropPolicyBytes(mode, reserved) orelse return error.UnexpectedAllocatorMode);
}

pub fn requireExplicitCallerInteropPolicy(policy: abi.InteropPolicy) AllocatorPolicyError!void {
    return requireExplicitCallerPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn requireExplicitCallerByte(mode: u8) AllocatorPolicyError!void {
    return requireExplicitCallerPolicyBytes(mode, 0);
}

pub fn permitsGlobalFallback(mode: abi.AllocatorMode) bool {
    return switch (mode) {
        .caller_provided => false,
        .kernel_heap, .arena => true,
    };
}

pub fn requireGlobalFallback(mode: abi.AllocatorMode) AllocatorPolicyError!void {
    if (!permitsGlobalFallback(mode)) return error.UnexpectedAllocatorMode;
}

pub fn permitsGlobalFallbackPolicyBytes(mode: u8, reserved: u8) bool {
    return switch (modeFromInteropPolicyBytes(mode, reserved) orelse return false) {
        .caller_provided => false,
        .kernel_heap, .arena => true,
    };
}

pub fn permitsGlobalFallbackInteropPolicy(policy: abi.InteropPolicy) bool {
    return permitsGlobalFallbackPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn permitsGlobalFallbackByte(mode: u8) bool {
    return permitsGlobalFallbackPolicyBytes(mode, 0);
}

pub fn requireGlobalFallbackPolicyBytes(mode: u8, reserved: u8) AllocatorPolicyError!void {
    return requireGlobalFallback(modeFromInteropPolicyBytes(mode, reserved) orelse return error.UnexpectedAllocatorMode);
}

pub fn requireGlobalFallbackInteropPolicy(policy: abi.InteropPolicy) AllocatorPolicyError!void {
    return requireGlobalFallbackPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn requireGlobalFallbackByte(mode: u8) AllocatorPolicyError!void {
    return requireGlobalFallbackPolicyBytes(mode, 0);
}

pub fn initializesOwnedState(mode: abi.AllocatorMode) bool {
    return switch (initFlowFor(mode)) {
        .caller_prepared => false,
        .helper_owned, .helper_owned_with_reset => true,
    };
}

pub fn requireOwnedStateInit(mode: abi.AllocatorMode) AllocatorPolicyError!void {
    if (!initializesOwnedState(mode)) return error.UnexpectedAllocatorMode;
}

pub fn initializesOwnedStatePolicyBytes(mode: u8, reserved: u8) bool {
    return initializesOwnedState(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn initializesOwnedStateInteropPolicy(policy: abi.InteropPolicy) bool {
    return initializesOwnedStatePolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn initializesOwnedStateByte(mode: u8) bool {
    return initializesOwnedStatePolicyBytes(mode, 0);
}

pub fn requireOwnedStateInitPolicyBytes(mode: u8, reserved: u8) AllocatorPolicyError!void {
    return requireOwnedStateInit(modeFromInteropPolicyBytes(mode, reserved) orelse return error.UnexpectedAllocatorMode);
}

pub fn requireOwnedStateInitInteropPolicy(policy: abi.InteropPolicy) AllocatorPolicyError!void {
    return requireOwnedStateInitPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn requireOwnedStateInitByte(mode: u8) AllocatorPolicyError!void {
    return requireOwnedStateInitPolicyBytes(mode, 0);
}

pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {
    return initFlowFor(mode) == .helper_owned_with_reset;
}

pub fn requireResetOnInit(mode: abi.AllocatorMode) AllocatorPolicyError!void {
    try requireInitFlow(mode, .helper_owned_with_reset);
}

pub fn requiresResetOnInitPolicyBytes(mode: u8, reserved: u8) bool {
    return requiresResetOnInit(modeFromInteropPolicyBytes(mode, reserved) orelse return false);
}

pub fn requiresResetOnInitInteropPolicy(policy: abi.InteropPolicy) bool {
    return requiresResetOnInitPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn requiresResetOnInitByte(mode: u8) bool {
    return requiresResetOnInitPolicyBytes(mode, 0);
}

pub fn requireResetOnInitPolicyBytes(mode: u8, reserved: u8) AllocatorPolicyError!void {
    return requireResetOnInit(modeFromInteropPolicyBytes(mode, reserved) orelse return error.UnexpectedAllocatorMode);
}

pub fn requireResetOnInitInteropPolicy(policy: abi.InteropPolicy) AllocatorPolicyError!void {
    return requireResetOnInitPolicyBytes(policy.allocator_mode, policy.reserved);
}

pub fn requireResetOnInitByte(mode: u8) AllocatorPolicyError!void {
    return requireResetOnInitPolicyBytes(mode, 0);
}

test "phase3 allocator policy keeps init ownership explicit" {
    try std.testing.expectEqual(InitFlow.caller_prepared, initFlowFor(.caller_provided));
    try std.testing.expectEqual(InitFlow.helper_owned, initFlowFor(.kernel_heap));
    try std.testing.expectEqual(InitFlow.helper_owned_with_reset, initFlowFor(.arena));

    try std.testing.expect(!initializesOwnedState(.caller_provided));
    try std.testing.expect(initializesOwnedState(.kernel_heap));
    try std.testing.expect(initializesOwnedState(.arena));

    try std.testing.expect(!requiresResetOnInit(.caller_provided));
    try std.testing.expect(!requiresResetOnInit(.kernel_heap));
    try std.testing.expect(requiresResetOnInit(.arena));

    try requireExplicitCaller(.caller_provided);
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireExplicitCaller(.kernel_heap));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireExplicitCaller(.arena));

    try std.testing.expectError(error.UnexpectedAllocatorMode, requireGlobalFallback(.caller_provided));
    try requireGlobalFallback(.kernel_heap);
    try requireGlobalFallback(.arena);

    try std.testing.expectError(error.UnexpectedAllocatorMode, requireOwnedStateInit(.caller_provided));
    try requireOwnedStateInit(.kernel_heap);
    try requireOwnedStateInit(.arena);

    try std.testing.expectError(error.UnexpectedAllocatorMode, requireResetOnInit(.caller_provided));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireResetOnInit(.kernel_heap));
    try requireResetOnInit(.arena);
}

test "phase3 allocator policy stays explicit" {
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), modeFromByte(0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), modeFromByte(1));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), modeFromByte(2));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromByte(9));

    try std.testing.expectEqual(@as(?InitFlow, .caller_prepared), initFlowFromByte(0));
    try std.testing.expectEqual(@as(?InitFlow, .helper_owned), initFlowFromByte(1));
    try std.testing.expectEqual(@as(?InitFlow, .helper_owned_with_reset), initFlowFromByte(2));
    try std.testing.expectEqual(@as(?InitFlow, null), initFlowFromByte(9));

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), modeFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), modeFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), modeFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicyBytes(2, 1));

    try std.testing.expectEqual(@as(?InitFlow, .caller_prepared), initFlowFromInteropPolicyBytes(0, 0));
    try std.testing.expectEqual(@as(?InitFlow, .helper_owned), initFlowFromInteropPolicyBytes(1, 0));
    try std.testing.expectEqual(@as(?InitFlow, .helper_owned_with_reset), initFlowFromInteropPolicyBytes(2, 0));
    try std.testing.expectEqual(@as(?InitFlow, null), initFlowFromInteropPolicyBytes(9, 0));
    try std.testing.expectEqual(@as(?InitFlow, null), initFlowFromInteropPolicyBytes(2, 1));

    try std.testing.expect(recognizesInteropPolicyBytes(0, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(1, 0));
    try std.testing.expect(recognizesInteropPolicyBytes(2, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(9, 0));
    try std.testing.expect(!recognizesInteropPolicyBytes(2, 1));

    try std.testing.expect(recognizesByte(0));
    try std.testing.expect(recognizesByte(1));
    try std.testing.expect(recognizesByte(2));
    try std.testing.expect(!recognizesByte(9));

    const caller_policy = abi.InteropPolicy{
        .panic_mode = 0,
        .allocator_mode = 0,
        .unsafe_scope = 0,
        .reserved = 0,
    };
    const heap_policy = abi.InteropPolicy{
        .panic_mode = 1,
        .allocator_mode = 1,
        .unsafe_scope = 1,
        .reserved = 0,
    };
    const arena_policy = abi.InteropPolicy{
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
        .allocator_mode = 9,
        .unsafe_scope = 0,
        .reserved = 0,
    };

    try std.testing.expectEqual(@as(?abi.AllocatorMode, .caller_provided), modeFromInteropPolicy(caller_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .kernel_heap), modeFromInteropPolicy(heap_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, .arena), modeFromInteropPolicy(arena_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?abi.AllocatorMode, null), modeFromInteropPolicy(reserved_policy));

    try std.testing.expectEqual(@as(?InitFlow, .caller_prepared), initFlowFromInteropPolicy(caller_policy));
    try std.testing.expectEqual(@as(?InitFlow, .helper_owned), initFlowFromInteropPolicy(heap_policy));
    try std.testing.expectEqual(@as(?InitFlow, .helper_owned_with_reset), initFlowFromInteropPolicy(arena_policy));
    try std.testing.expectEqual(@as(?InitFlow, null), initFlowFromInteropPolicy(unknown_policy));
    try std.testing.expectEqual(@as(?InitFlow, null), initFlowFromInteropPolicy(reserved_policy));

    try std.testing.expect(recognizesInteropPolicy(caller_policy));
    try std.testing.expect(recognizesInteropPolicy(heap_policy));
    try std.testing.expect(recognizesInteropPolicy(arena_policy));
    try std.testing.expect(!recognizesInteropPolicy(unknown_policy));
    try std.testing.expect(!recognizesInteropPolicy(reserved_policy));

    try std.testing.expect(requiresExplicitCaller(.caller_provided));
    try std.testing.expect(requiresExplicitCallerByte(0));
    try std.testing.expect(requiresExplicitCallerPolicyBytes(0, 0));
    try std.testing.expect(requiresExplicitCallerInteropPolicy(caller_policy));
    try std.testing.expect(!requiresExplicitCallerInteropPolicy(heap_policy));
    try std.testing.expect(!requiresExplicitCallerInteropPolicy(reserved_policy));
    try std.testing.expect(!requiresExplicitCallerPolicyBytes(1, 0));
    try std.testing.expect(!requiresExplicitCallerPolicyBytes(2, 1));
    try std.testing.expect(!requiresExplicitCallerByte(1));
    try std.testing.expect(!requiresExplicitCallerByte(9));
    try requireExplicitCallerByte(0);
    try requireExplicitCallerPolicyBytes(0, 0);
    try requireExplicitCallerInteropPolicy(caller_policy);
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireExplicitCallerByte(1));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireExplicitCallerPolicyBytes(2, 1));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireExplicitCallerInteropPolicy(heap_policy));

    try std.testing.expect(!permitsGlobalFallback(.caller_provided));
    try std.testing.expect(!permitsGlobalFallbackByte(0));
    try std.testing.expect(!permitsGlobalFallbackPolicyBytes(0, 0));
    try std.testing.expect(!permitsGlobalFallbackInteropPolicy(caller_policy));
    try std.testing.expect(permitsGlobalFallback(.kernel_heap));
    try std.testing.expect(permitsGlobalFallback(.arena));
    try std.testing.expect(permitsGlobalFallbackByte(1));
    try std.testing.expect(permitsGlobalFallbackByte(2));
    try std.testing.expect(permitsGlobalFallbackPolicyBytes(1, 0));
    try std.testing.expect(permitsGlobalFallbackPolicyBytes(2, 0));
    try std.testing.expect(permitsGlobalFallbackInteropPolicy(heap_policy));
    try std.testing.expect(permitsGlobalFallbackInteropPolicy(arena_policy));
    try std.testing.expect(!permitsGlobalFallbackInteropPolicy(reserved_policy));
    try std.testing.expect(!permitsGlobalFallbackPolicyBytes(2, 1));
    try std.testing.expect(!permitsGlobalFallbackByte(9));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireGlobalFallbackByte(0));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireGlobalFallbackPolicyBytes(0, 0));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireGlobalFallbackInteropPolicy(caller_policy));
    try requireGlobalFallbackByte(1);
    try requireGlobalFallbackPolicyBytes(2, 0);
    try requireGlobalFallbackInteropPolicy(arena_policy);
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireGlobalFallbackPolicyBytes(2, 1));

    try std.testing.expect(!initializesOwnedStateByte(0));
    try std.testing.expect(initializesOwnedStateByte(1));
    try std.testing.expect(initializesOwnedStateByte(2));
    try std.testing.expect(!initializesOwnedStateByte(9));
    try std.testing.expect(!initializesOwnedStatePolicyBytes(0, 0));
    try std.testing.expect(initializesOwnedStatePolicyBytes(1, 0));
    try std.testing.expect(initializesOwnedStatePolicyBytes(2, 0));
    try std.testing.expect(!initializesOwnedStatePolicyBytes(2, 1));
    try std.testing.expect(!initializesOwnedStateInteropPolicy(caller_policy));
    try std.testing.expect(initializesOwnedStateInteropPolicy(heap_policy));
    try std.testing.expect(initializesOwnedStateInteropPolicy(arena_policy));
    try std.testing.expect(!initializesOwnedStateInteropPolicy(reserved_policy));
    try std.testing.expect(!initializesOwnedStateInteropPolicy(unknown_policy));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireOwnedStateInitByte(0));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireOwnedStateInitPolicyBytes(0, 0));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireOwnedStateInitInteropPolicy(caller_policy));
    try requireOwnedStateInitByte(1);
    try requireOwnedStateInitPolicyBytes(2, 0);
    try requireOwnedStateInitInteropPolicy(arena_policy);
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireOwnedStateInitPolicyBytes(2, 1));

    try std.testing.expect(!requiresResetOnInitByte(0));
    try std.testing.expect(!requiresResetOnInitByte(1));
    try std.testing.expect(requiresResetOnInitByte(2));
    try std.testing.expect(!requiresResetOnInitByte(9));
    try std.testing.expect(!requiresResetOnInitPolicyBytes(0, 0));
    try std.testing.expect(!requiresResetOnInitPolicyBytes(1, 0));
    try std.testing.expect(requiresResetOnInitPolicyBytes(2, 0));
    try std.testing.expect(!requiresResetOnInitPolicyBytes(2, 1));
    try std.testing.expect(!requiresResetOnInitInteropPolicy(caller_policy));
    try std.testing.expect(!requiresResetOnInitInteropPolicy(heap_policy));
    try std.testing.expect(requiresResetOnInitInteropPolicy(arena_policy));
    try std.testing.expect(!requiresResetOnInitInteropPolicy(reserved_policy));
    try std.testing.expect(!requiresResetOnInitInteropPolicy(unknown_policy));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireResetOnInitByte(0));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireResetOnInitPolicyBytes(1, 0));
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireResetOnInitInteropPolicy(heap_policy));
    try requireResetOnInitByte(2);
    try requireResetOnInitPolicyBytes(2, 0);
    try requireResetOnInitInteropPolicy(arena_policy);
    try std.testing.expectError(error.UnexpectedAllocatorMode, requireResetOnInitPolicyBytes(2, 1));
}

test "phase3 allocator policy require aliases stay synchronized" {
    const modes = [_]abi.AllocatorMode{ .caller_provided, .kernel_heap, .arena };
    const known_mode_bytes = [_]u8{
        @intFromEnum(abi.AllocatorMode.caller_provided),
        @intFromEnum(abi.AllocatorMode.kernel_heap),
        @intFromEnum(abi.AllocatorMode.arena),
        9,
    };
    const reserved_values = [_]u8{ 0, 1 };
    const policies = [_]abi.InteropPolicy{
        .{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 0 },
        .{ .panic_mode = 0, .allocator_mode = 1, .unsafe_scope = 0, .reserved = 0 },
        .{ .panic_mode = 0, .allocator_mode = 2, .unsafe_scope = 0, .reserved = 0 },
        .{ .panic_mode = 0, .allocator_mode = 2, .unsafe_scope = 0, .reserved = 1 },
        .{ .panic_mode = 0, .allocator_mode = 9, .unsafe_scope = 0, .reserved = 0 },
    };

    for (modes) |mode| {
        const wants_caller = requiresExplicitCaller(mode);
        const wants_fallback = permitsGlobalFallback(mode);
        const wants_owned_state = initializesOwnedState(mode);
        const wants_reset = requiresResetOnInit(mode);

        try expectOutcomeEqual(
            if (wants_caller) @as(?anyerror, null) else error.UnexpectedAllocatorMode,
            requireOutcome(requireExplicitCaller(mode)),
        );
        try expectOutcomeEqual(
            if (wants_fallback) @as(?anyerror, null) else error.UnexpectedAllocatorMode,
            requireOutcome(requireGlobalFallback(mode)),
        );
        try expectOutcomeEqual(
            if (wants_owned_state) @as(?anyerror, null) else error.UnexpectedAllocatorMode,
            requireOutcome(requireOwnedStateInit(mode)),
        );
        try expectOutcomeEqual(
            if (wants_reset) @as(?anyerror, null) else error.UnexpectedAllocatorMode,
            requireOutcome(requireResetOnInit(mode)),
        );
    }

    for (known_mode_bytes) |mode| {
        try expectOutcomeEqual(
            requireOutcome(requireExplicitCallerPolicyBytes(mode, 0)),
            requireOutcome(requireExplicitCallerByte(mode)),
        );
        try expectOutcomeEqual(
            requireOutcome(requireGlobalFallbackPolicyBytes(mode, 0)),
            requireOutcome(requireGlobalFallbackByte(mode)),
        );
        try expectOutcomeEqual(
            requireOutcome(requireOwnedStateInitPolicyBytes(mode, 0)),
            requireOutcome(requireOwnedStateInitByte(mode)),
        );
        try expectOutcomeEqual(
            requireOutcome(requireResetOnInitPolicyBytes(mode, 0)),
            requireOutcome(requireResetOnInitByte(mode)),
        );
    }

    for (known_mode_bytes) |mode| {
        for (reserved_values) |reserved| {
            const resolved = modeFromInteropPolicyBytes(mode, reserved);
            const caller_outcome = requireOutcome(requireExplicitCallerPolicyBytes(mode, reserved));
            const fallback_outcome = requireOutcome(requireGlobalFallbackPolicyBytes(mode, reserved));
            const owned_outcome = requireOutcome(requireOwnedStateInitPolicyBytes(mode, reserved));
            const reset_outcome = requireOutcome(requireResetOnInitPolicyBytes(mode, reserved));

            if (resolved) |known| {
                try expectOutcomeEqual(
                    requireOutcome(requireExplicitCaller(known)),
                    caller_outcome,
                );
                try expectOutcomeEqual(
                    requireOutcome(requireGlobalFallback(known)),
                    fallback_outcome,
                );
                try expectOutcomeEqual(
                    requireOutcome(requireOwnedStateInit(known)),
                    owned_outcome,
                );
                try expectOutcomeEqual(
                    requireOutcome(requireResetOnInit(known)),
                    reset_outcome,
                );
            } else {
                try expectOutcomeEqual(@as(?anyerror, error.UnexpectedAllocatorMode), caller_outcome);
                try expectOutcomeEqual(@as(?anyerror, error.UnexpectedAllocatorMode), fallback_outcome);
                try expectOutcomeEqual(@as(?anyerror, error.UnexpectedAllocatorMode), owned_outcome);
                try expectOutcomeEqual(@as(?anyerror, error.UnexpectedAllocatorMode), reset_outcome);
            }
        }
    }

    for (policies) |policy| {
        try expectOutcomeEqual(
            requireOutcome(requireExplicitCallerPolicyBytes(policy.allocator_mode, policy.reserved)),
            requireOutcome(requireExplicitCallerInteropPolicy(policy)),
        );
        try expectOutcomeEqual(
            requireOutcome(requireGlobalFallbackPolicyBytes(policy.allocator_mode, policy.reserved)),
            requireOutcome(requireGlobalFallbackInteropPolicy(policy)),
        );
        try expectOutcomeEqual(
            requireOutcome(requireOwnedStateInitPolicyBytes(policy.allocator_mode, policy.reserved)),
            requireOutcome(requireOwnedStateInitInteropPolicy(policy)),
        );
        try expectOutcomeEqual(
            requireOutcome(requireResetOnInitPolicyBytes(policy.allocator_mode, policy.reserved)),
            requireOutcome(requireResetOnInitInteropPolicy(policy)),
        );
    }
}
