const std = @import("std");
const contract = @import("runtime_loader_contract");

fn expectPolicy(
    handoff: contract.AllocatorHandoff,
    expected: contract.AllocatorRuntimeInitPolicy,
) !void {
    const actual = contract.allocatorRuntimeInitPolicyFor(handoff);
    try std.testing.expect(contract.keepsAllocatorRuntimeInitPolicyExplicit(actual, expected));
    try std.testing.expect(contract.keepsAllocatorRuntimeInitPolicyConsistent(handoff, expected));
}

test "allocator runtime init policy pins caller, arena, and kernel heap ownership" {
    try expectPolicy(.caller_provided, .{
        .init_owner = .caller_prepared,
        .requires_explicit_caller = true,
        .permits_global_fallback = false,
        .initializes_owned_state = false,
        .requires_reset_on_init = false,
    });

    try expectPolicy(.arena, .{
        .init_owner = .helper_owned_with_reset,
        .requires_explicit_caller = false,
        .permits_global_fallback = true,
        .initializes_owned_state = true,
        .requires_reset_on_init = true,
    });

    try expectPolicy(.kernel_heap, .{
        .init_owner = .helper_owned,
        .requires_explicit_caller = false,
        .permits_global_fallback = true,
        .initializes_owned_state = true,
        .requires_reset_on_init = false,
    });
}

test "allocator runtime init policy comparison checks each derived field" {
    const stable = contract.allocatorRuntimeInitPolicyFor(.arena);
    try std.testing.expect(contract.keepsAllocatorRuntimeInitPolicyExplicit(stable, stable));

    var drifted = stable;
    drifted.init_owner = .helper_owned;
    try std.testing.expect(!contract.keepsAllocatorRuntimeInitPolicyExplicit(drifted, stable));

    drifted = stable;
    drifted.requires_explicit_caller = true;
    try std.testing.expect(!contract.keepsAllocatorRuntimeInitPolicyExplicit(drifted, stable));

    drifted = stable;
    drifted.permits_global_fallback = false;
    try std.testing.expect(!contract.keepsAllocatorRuntimeInitPolicyExplicit(drifted, stable));

    drifted = stable;
    drifted.initializes_owned_state = false;
    try std.testing.expect(!contract.keepsAllocatorRuntimeInitPolicyExplicit(drifted, stable));

    drifted = stable;
    drifted.requires_reset_on_init = false;
    try std.testing.expect(!contract.keepsAllocatorRuntimeInitPolicyExplicit(drifted, stable));
}

test "load plan keeps allocator handoff as the ABI boundary policy input" {
    const plan = contract.LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_bitmap"},
        },
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };

    try std.testing.expect(contract.keepsAllocatorRuntimeInitPolicyConsistent(plan.allocator_handoff, .{
        .init_owner = .helper_owned_with_reset,
        .requires_explicit_caller = false,
        .permits_global_fallback = true,
        .initializes_owned_state = true,
        .requires_reset_on_init = true,
    }));
    try std.testing.expect(contract.keepsDepmodAliasReady(plan.module_metadata));
    try std.testing.expectEqual(@as(usize, 1), contract.depmodAliasRecordCount(plan));

    const blocked_policy_fields = [_][]const u8{
        "allocator_runtime_init_policy",
        "init_owner",
        "requires_explicit_caller",
        "permits_global_fallback",
        "initializes_owned_state",
        "requires_reset_on_init",
    };

    inline for (blocked_policy_fields) |field| {
        try std.testing.expect(!@hasField(contract.LoadPlan, field));
    }
}

test "allocator policy derivation stays independent from module metadata aliases" {
    var plan = contract.LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_trace_events"},
        },
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };

    try std.testing.expect(contract.keepsAllocatorRuntimeInitPolicyConsistent(plan.allocator_handoff, .{
        .init_owner = .caller_prepared,
        .requires_explicit_caller = true,
        .permits_global_fallback = false,
        .initializes_owned_state = false,
        .requires_reset_on_init = false,
    }));
    try std.testing.expect(contract.keepsDepmodAliasReady(plan.module_metadata));

    plan.module_metadata.aliases = &.{
        "zigux:runtime-pilot:runtime_trace_events",
        "zigux:runtime-pilot:trace-events-anchor",
    };
    try std.testing.expect(contract.keepsAllocatorRuntimeInitPolicyConsistent(plan.allocator_handoff, .{
        .init_owner = .caller_prepared,
        .requires_explicit_caller = true,
        .permits_global_fallback = false,
        .initializes_owned_state = false,
        .requires_reset_on_init = false,
    }));
    try std.testing.expectEqual(@as(usize, 2), contract.depmodAliasRecordCount(plan));
    try std.testing.expectEqualStrings(
        "zigux:runtime-pilot:trace-events-anchor",
        contract.depmodAliasRecordFor(plan, 1).?.module_alias,
    );
}
