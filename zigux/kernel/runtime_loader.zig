const std = @import("std");
const contract = @import("runtime_loader_contract.zig");

pub const AllocatorHandoff = contract.AllocatorHandoff;
pub const HandoffStage = contract.HandoffStage;
pub const RequestState = contract.RequestState;
pub const InitFlow = contract.InitFlow;
pub const LoadPlan = contract.LoadPlan;
pub const PreparedRequest = contract.PreparedRequest;

pub fn prepareRequest(plan: LoadPlan) !PreparedRequest {
    return contract.prepareRequest(plan);
}

pub fn keepsAllocatorInitFlowConsistent(
    plan: LoadPlan,
    allocator_handoff: AllocatorHandoff,
    init_flow: InitFlow,
) bool {
    return contract.keepsAllocatorInitFlowConsistent(plan, allocator_handoff, init_flow);
}

pub fn keepsRequestStateAndPlanExplicit(
    request: PreparedRequest,
    expected_state: RequestState,
    expected_plan: LoadPlan,
) bool {
    return contract.keepsRequestStateAndPlanExplicit(request, expected_state, expected_plan);
}

pub fn keepsSelftestHookEvidenceConsistent(plan: LoadPlan) bool {
    return contract.keepsSelftestHookEvidenceConsistent(plan);
}

test "runtime loader facade keeps the shared loader contract reachable from the Phase 9 kernel surface" {
    const cases = [_]LoadPlan{
        .{
            .module_name = "runtime_atomic64",
            .anchor = "lib/atomic64_test.c",
            .entry_symbol = "zigux_runtime_atomic64_init",
            .exit_symbol = "zigux_runtime_atomic64_exit",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
            .allocator_handoff = .caller_provided,
            .init_flow = .{
                .handoff_stage = .selftest_complete,
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
        .{
            .module_name = "runtime_bitmap",
            .anchor = "lib/test_bitmap.c",
            .entry_symbol = "zigux_runtime_bitmap_init",
            .exit_symbol = "zigux_runtime_bitmap_exit",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
            .allocator_handoff = .arena,
            .init_flow = .{
                .handoff_stage = .initialized,
                .init_runs = 1,
                .selftest_runs = 0,
                .exit_runs = 0,
            },
        },
        .{
            .module_name = "runtime_trace_events",
            .anchor = "samples/trace_events/trace-events-sample.c",
            .entry_symbol = "zigux_runtime_trace_events_init",
            .exit_symbol = "zigux_runtime_trace_events_exit",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
            .allocator_handoff = .caller_provided,
            .init_flow = .{
                .handoff_stage = .selftest_complete,
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
        .{
            .module_name = "runtime_kretprobe",
            .anchor = "samples/kprobes/kretprobe_example.c",
            .entry_symbol = "zigux_runtime_kretprobe_init",
            .exit_symbol = "zigux_runtime_kretprobe_exit",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
            .allocator_handoff = .kernel_heap,
            .init_flow = .{
                .handoff_stage = .selftest_complete,
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };

    for (cases) |plan| {
        var request = try prepareRequest(plan);
        try std.testing.expectEqual(RequestState.prepared, request.state);
        try std.testing.expect(keepsRequestStateAndPlanExplicit(request, .prepared, plan));

        const pending_plan = try request.requestRuntimeLoad();
        try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
        try std.testing.expect(keepsRequestStateAndPlanExplicit(
            request,
            .waiting_on_runtime_substrate,
            plan,
        ));
        try std.testing.expectEqualStrings(plan.module_name, pending_plan.module_name);
        try std.testing.expectEqualStrings(plan.anchor, pending_plan.anchor);
        try std.testing.expectEqualStrings(plan.entry_symbol, pending_plan.entry_symbol);
        try std.testing.expectEqualStrings(plan.exit_symbol, pending_plan.exit_symbol);
        try std.testing.expectEqual(plan.provides_selftest_hook, pending_plan.provides_selftest_hook);
        try std.testing.expect(keepsAllocatorInitFlowConsistent(
            pending_plan,
            plan.allocator_handoff,
            plan.init_flow,
        ));
        try std.testing.expect(keepsSelftestHookEvidenceConsistent(pending_plan));

        try request.releaseWithoutSubstrate();
        try std.testing.expectEqual(RequestState.released_without_substrate, request.state);
        try std.testing.expect(keepsRequestStateAndPlanExplicit(
            request,
            .released_without_substrate,
            plan,
        ));
    }
}

test "runtime loader facade preserves shared runtime lifecycle failures" {
    const invalid_init = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 0,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(invalid_init));

    const duplicate_init = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 2,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(duplicate_init));

    const incomplete_selftest = LoadPlan{
        .module_name = "runtime_kretprobe",
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .kernel_heap,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
    try std.testing.expectError(error.InvalidSelftestHookEvidence, prepareRequest(incomplete_selftest));

    const loader_not_required = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = false,
        .provides_selftest_hook = true,
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    try std.testing.expectError(error.LoaderNotRequired, prepareRequest(loader_not_required));

    const missing_selftest_hook = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = false,
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    try std.testing.expect(!keepsSelftestHookEvidenceConsistent(missing_selftest_hook));
    try std.testing.expectError(error.InvalidSelftestHookEvidence, prepareRequest(missing_selftest_hook));

    const stable_plan = LoadPlan{
        .module_name = "runtime_kretprobe",
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .kernel_heap,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };

    var request = try prepareRequest(stable_plan);
    try std.testing.expectError(error.InvalidLoaderState, request.releaseWithoutSubstrate());
    _ = try request.requestRuntimeLoad();
    try std.testing.expectError(error.InvalidLoaderState, request.requestRuntimeLoad());

    try request.releaseWithoutSubstrate();
    try std.testing.expectError(error.InvalidLoaderState, request.releaseWithoutSubstrate());
}

test "runtime loader facade rejects request state or plan drift" {
    const stable_plan = LoadPlan{
        .module_name = "runtime_atomic64",
        .anchor = "lib/atomic64_test.c",
        .entry_symbol = "zigux_runtime_atomic64_init",
        .exit_symbol = "zigux_runtime_atomic64_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };

    const request = try prepareRequest(stable_plan);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(request, .prepared, stable_plan));
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(
        request,
        .released_without_substrate,
        stable_plan,
    ));

    var drifted_plan = stable_plan;
    drifted_plan.exit_symbol = "zigux_runtime_atomic64_exit_drift";
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_plan));
}
