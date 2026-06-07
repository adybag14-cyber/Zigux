const std = @import("std");
const abi = @import("abi_bindings");
const allocator_policy = @import("allocator_policy");

const ModeRow = struct {
    byte: u8,
    mode: abi.AllocatorMode,
    flow: allocator_policy.InitFlow,
    ownership: allocator_policy.Ownership,
    explicit_caller: bool,
    global_fallback: bool,
    owned_state: bool,
    reset_on_init: bool,
};

const mode_rows = [_]ModeRow{
    .{
        .byte = abi.ALLOC_CALLER_PROVIDED,
        .mode = .caller_provided,
        .flow = .caller_prepared,
        .ownership = .caller_managed,
        .explicit_caller = true,
        .global_fallback = false,
        .owned_state = false,
        .reset_on_init = false,
    },
    .{
        .byte = abi.ALLOC_KERNEL_HEAP,
        .mode = .kernel_heap,
        .flow = .helper_owned,
        .ownership = .helper_managed,
        .explicit_caller = false,
        .global_fallback = true,
        .owned_state = true,
        .reset_on_init = false,
    },
    .{
        .byte = abi.ALLOC_ARENA,
        .mode = .arena,
        .flow = .helper_owned_with_reset,
        .ownership = .helper_managed_resettable,
        .explicit_caller = false,
        .global_fallback = true,
        .owned_state = true,
        .reset_on_init = true,
    },
};

fn policyFor(row: ModeRow) abi.InteropPolicy {
    return .{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = row.byte,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    };
}

test "allocator policy mode rows keep flow and ownership in lockstep" {
    for (mode_rows) |row| {
        const policy = policyFor(row);

        try std.testing.expectEqual(row.mode, allocator_policy.modeFromByte(row.byte).?);
        try std.testing.expectEqual(row.mode, allocator_policy.modeFromInteropPolicyBytes(row.byte, 0).?);
        try std.testing.expectEqual(row.mode, allocator_policy.modeFromInteropPolicy(policy).?);

        try std.testing.expectEqual(row.flow, allocator_policy.initFlowFor(row.mode));
        try std.testing.expectEqual(row.flow, allocator_policy.initFlowFromByte(row.byte).?);
        try std.testing.expectEqual(row.flow, allocator_policy.initFlowFromInteropPolicyBytes(row.byte, 0).?);
        try std.testing.expectEqual(row.flow, allocator_policy.initFlowFromInteropPolicy(policy).?);

        try std.testing.expectEqual(row.ownership, allocator_policy.ownershipFor(row.mode));
        try std.testing.expectEqual(row.ownership, allocator_policy.ownershipFromByte(row.byte).?);
        try std.testing.expectEqual(row.ownership, allocator_policy.ownershipFromInteropPolicyBytes(row.byte, 0).?);
        try std.testing.expectEqual(row.ownership, allocator_policy.ownershipFromInteropPolicy(policy).?);
    }
}

test "allocator policy predicates stay aligned across enum byte and policy views" {
    for (mode_rows) |row| {
        const policy = policyFor(row);

        try std.testing.expectEqual(row.explicit_caller, allocator_policy.requiresExplicitCaller(row.mode));
        try std.testing.expectEqual(row.explicit_caller, allocator_policy.requiresExplicitCallerByte(row.byte));
        try std.testing.expectEqual(row.explicit_caller, allocator_policy.requiresExplicitCallerPolicyBytes(row.byte, 0));
        try std.testing.expectEqual(row.explicit_caller, allocator_policy.requiresExplicitCallerInteropPolicy(policy));

        try std.testing.expectEqual(row.global_fallback, allocator_policy.permitsGlobalFallback(row.mode));
        try std.testing.expectEqual(row.global_fallback, allocator_policy.permitsGlobalFallbackByte(row.byte));
        try std.testing.expectEqual(row.global_fallback, allocator_policy.permitsGlobalFallbackPolicyBytes(row.byte, 0));
        try std.testing.expectEqual(row.global_fallback, allocator_policy.permitsGlobalFallbackInteropPolicy(policy));

        try std.testing.expectEqual(row.owned_state, allocator_policy.initializesOwnedState(row.mode));
        try std.testing.expectEqual(row.owned_state, allocator_policy.initializesOwnedStateByte(row.byte));
        try std.testing.expectEqual(row.owned_state, allocator_policy.initializesOwnedStatePolicyBytes(row.byte, 0));
        try std.testing.expectEqual(row.owned_state, allocator_policy.initializesOwnedStateInteropPolicy(policy));

        try std.testing.expectEqual(row.reset_on_init, allocator_policy.requiresResetOnInit(row.mode));
        try std.testing.expectEqual(row.reset_on_init, allocator_policy.requiresResetOnInitByte(row.byte));
        try std.testing.expectEqual(row.reset_on_init, allocator_policy.requiresResetOnInitPolicyBytes(row.byte, 0));
        try std.testing.expectEqual(row.reset_on_init, allocator_policy.requiresResetOnInitInteropPolicy(policy));
    }
}

test "allocator policy invalid bytes fail closed before flow predicates escape" {
    const invalid_bytes = [_]u8{ 3, 9, 0xff };

    for (invalid_bytes) |byte| {
        try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromByte(byte));
        try std.testing.expectEqual(@as(?allocator_policy.InitFlow, null), allocator_policy.initFlowFromByte(byte));
        try std.testing.expectEqual(@as(?allocator_policy.Ownership, null), allocator_policy.ownershipFromByte(byte));
        try std.testing.expect(!allocator_policy.recognizesByte(byte));
        try std.testing.expect(!allocator_policy.requiresExplicitCallerByte(byte));
        try std.testing.expect(!allocator_policy.permitsGlobalFallbackByte(byte));
        try std.testing.expect(!allocator_policy.initializesOwnedStateByte(byte));
        try std.testing.expect(!allocator_policy.requiresResetOnInitByte(byte));
        try std.testing.expectError(error.InvalidInteropPolicy, allocator_policy.requireInitFlowByte(byte, .helper_owned));
    }
}

test "allocator policy reserved bytes deny every derived flow surface" {
    for (mode_rows) |row| {
        const reserved_policy = abi.InteropPolicy{
            .panic_mode = abi.PANIC_ABORT,
            .allocator_mode = row.byte,
            .unsafe_scope = abi.UNSAFE_NONE,
            .reserved = 1,
        };

        try std.testing.expectEqual(@as(?abi.AllocatorMode, null), allocator_policy.modeFromInteropPolicyBytes(row.byte, 1));
        try std.testing.expectEqual(@as(?allocator_policy.InitFlow, null), allocator_policy.initFlowFromInteropPolicyBytes(row.byte, 1));
        try std.testing.expectEqual(@as(?allocator_policy.Ownership, null), allocator_policy.ownershipFromInteropPolicyBytes(row.byte, 1));
        try std.testing.expect(!allocator_policy.recognizesInteropPolicyBytes(row.byte, 1));
        try std.testing.expect(!allocator_policy.recognizesInteropPolicy(reserved_policy));

        try std.testing.expect(!allocator_policy.requiresExplicitCallerPolicyBytes(row.byte, 1));
        try std.testing.expect(!allocator_policy.permitsGlobalFallbackPolicyBytes(row.byte, 1));
        try std.testing.expect(!allocator_policy.initializesOwnedStatePolicyBytes(row.byte, 1));
        try std.testing.expect(!allocator_policy.requiresResetOnInitPolicyBytes(row.byte, 1));

        try std.testing.expect(!allocator_policy.requiresExplicitCallerInteropPolicy(reserved_policy));
        try std.testing.expect(!allocator_policy.permitsGlobalFallbackInteropPolicy(reserved_policy));
        try std.testing.expect(!allocator_policy.initializesOwnedStateInteropPolicy(reserved_policy));
        try std.testing.expect(!allocator_policy.requiresResetOnInitInteropPolicy(reserved_policy));
        try std.testing.expectError(error.InvalidInteropPolicy, allocator_policy.requireInitFlowInteropPolicy(reserved_policy, row.flow));
    }
}
