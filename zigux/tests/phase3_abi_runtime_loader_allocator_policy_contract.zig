const std = @import("std");
const allocator_policy = @import("allocator_policy");
const runtime_loader_contract = @import("runtime_loader_contract");

const AllocatorHandoff = runtime_loader_contract.AllocatorHandoff;
const AllocatorRuntimeInitPolicy = runtime_loader_contract.AllocatorRuntimeInitPolicy;
const LoadPlan = runtime_loader_contract.LoadPlan;

const ExpectedBridge = struct {
    handoff: AllocatorHandoff,
    abi_mode: u8,
    runtime_policy: AllocatorRuntimeInitPolicy,
    allocator_flow: allocator_policy.InitFlow,
    allocator_owner: allocator_policy.Ownership,
};

const expected_bridges = [_]ExpectedBridge{
    .{
        .handoff = .caller_provided,
        .abi_mode = 0,
        .runtime_policy = .{
            .init_owner = .caller_prepared,
            .requires_explicit_caller = true,
            .permits_global_fallback = false,
            .initializes_owned_state = false,
            .requires_reset_on_init = false,
        },
        .allocator_flow = .caller_prepared,
        .allocator_owner = .caller_managed,
    },
    .{
        .handoff = .kernel_heap,
        .abi_mode = 1,
        .runtime_policy = .{
            .init_owner = .helper_owned,
            .requires_explicit_caller = false,
            .permits_global_fallback = true,
            .initializes_owned_state = true,
            .requires_reset_on_init = false,
        },
        .allocator_flow = .helper_owned,
        .allocator_owner = .helper_managed,
    },
    .{
        .handoff = .arena,
        .abi_mode = 2,
        .runtime_policy = .{
            .init_owner = .helper_owned_with_reset,
            .requires_explicit_caller = false,
            .permits_global_fallback = true,
            .initializes_owned_state = true,
            .requires_reset_on_init = true,
        },
        .allocator_flow = .helper_owned_with_reset,
        .allocator_owner = .helper_managed_resettable,
    },
};

fn planWithHandoff(handoff: AllocatorHandoff) LoadPlan {
    return .{
        .module_name = "runtime_allocator_probe",
        .anchor = "lib/test_allocator.c",
        .entry_symbol = "zigux_runtime_allocator_probe_init",
        .exit_symbol = "zigux_runtime_allocator_probe_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:allocator-probe"},
        },
        .allocator_handoff = handoff,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
}

test "runtime-loader allocator handoffs map to allocator-policy ABI bytes" {
    inline for (expected_bridges) |expected| {
        const mode = allocator_policy.modeFromByte(expected.abi_mode) orelse return error.TestUnexpectedResult;

        try std.testing.expect(allocator_policy.recognizesByte(expected.abi_mode));
        try std.testing.expectEqual(mode, allocator_policy.modeFromInteropPolicyBytes(expected.abi_mode, 0).?);
        try std.testing.expectEqual(expected.allocator_flow, allocator_policy.initFlowFor(mode));
        try std.testing.expectEqual(expected.allocator_flow, allocator_policy.initFlowFromByte(expected.abi_mode).?);
        try std.testing.expectEqual(expected.allocator_owner, allocator_policy.ownershipFor(mode));
        try std.testing.expectEqual(expected.allocator_owner, allocator_policy.ownershipFromByte(expected.abi_mode).?);

        try std.testing.expect(runtime_loader_contract.keepsAllocatorRuntimeInitPolicyConsistent(
            expected.handoff,
            expected.runtime_policy,
        ));
    }
}

test "runtime-loader allocator policy mirrors allocator-policy booleans" {
    inline for (expected_bridges) |expected| {
        const mode = allocator_policy.modeFromByte(expected.abi_mode) orelse return error.TestUnexpectedResult;
        const runtime_policy = runtime_loader_contract.allocatorRuntimeInitPolicyFor(expected.handoff);

        try std.testing.expectEqual(allocator_policy.requiresExplicitCaller(mode), runtime_policy.requires_explicit_caller);
        try std.testing.expectEqual(allocator_policy.requiresExplicitCallerByte(expected.abi_mode), runtime_policy.requires_explicit_caller);
        try std.testing.expectEqual(allocator_policy.permitsGlobalFallback(mode), runtime_policy.permits_global_fallback);
        try std.testing.expectEqual(allocator_policy.permitsGlobalFallbackByte(expected.abi_mode), runtime_policy.permits_global_fallback);
        try std.testing.expectEqual(allocator_policy.initializesOwnedState(mode), runtime_policy.initializes_owned_state);
        try std.testing.expectEqual(allocator_policy.initializesOwnedStateByte(expected.abi_mode), runtime_policy.initializes_owned_state);
        try std.testing.expectEqual(allocator_policy.requiresResetOnInit(mode), runtime_policy.requires_reset_on_init);
        try std.testing.expectEqual(allocator_policy.requiresResetOnInitByte(expected.abi_mode), runtime_policy.requires_reset_on_init);
    }
}

test "runtime-loader load plans preserve handoff while ABI policy rejects reserved drift" {
    inline for (expected_bridges) |expected| {
        const plan = planWithHandoff(expected.handoff);
        const roundtrip = planWithHandoff(expected.handoff);

        try std.testing.expect(runtime_loader_contract.keepsLoadPlanExplicit(plan, roundtrip));
        try std.testing.expectEqual(expected.handoff, plan.allocator_handoff);
        try std.testing.expectEqual(@as(?allocator_policy.InitFlow, null), allocator_policy.initFlowFromInteropPolicyBytes(expected.abi_mode, 1));
        try std.testing.expectEqual(@as(?allocator_policy.Ownership, null), allocator_policy.ownershipFromInteropPolicyBytes(expected.abi_mode, 1));
        try std.testing.expect(!allocator_policy.recognizesInteropPolicyBytes(expected.abi_mode, 1));
    }
}

test "allocator handoff bridge stays out of request state and depmod alias records" {
    try std.testing.expect(!@hasField(runtime_loader_contract.RequestState, "allocator_handoff"));

    const blocked_alias_record_fields = [_][]const u8{
        "allocator_handoff",
        "allocator_mode",
        "allocator_policy",
        "init_owner",
        "requires_reset_on_init",
    };

    inline for (blocked_alias_record_fields) |field| {
        try std.testing.expect(!@hasField(runtime_loader_contract.DepmodAliasRecord, field));
    }
}
