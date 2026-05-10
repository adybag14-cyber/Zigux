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

    const duplicate_selftest = LoadPlan{
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
            .selftest_runs = 2,
            .exit_runs = 0,
        },
    };
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(duplicate_selftest));

    const initialized_with_premature_selftest = LoadPlan{
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
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(initialized_with_premature_selftest));

    const exited_plan = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 1,
        },
    };
    try std.testing.expectError(error.InvalidInitFlow, prepareRequest(exited_plan));

    const mismatched_module_name = LoadPlan{
        .module_name = "runtime_atomic64_drift",
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
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(mismatched_module_name));

    const mismatched_anchor = LoadPlan{
        .module_name = "runtime_atomic64",
        .anchor = "lib/test_bitmap.c",
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
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(mismatched_anchor));

    const mismatched_entry_symbol = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init_drift",
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
    };
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(mismatched_entry_symbol));

    const mismatched_exit_symbol = LoadPlan{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit_drift",
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
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(mismatched_exit_symbol));

    const unknown_family = LoadPlan{
        .module_name = "runtime_spinlock",
        .anchor = "kernel/locking/spinlock.c",
        .entry_symbol = "zigux_runtime_spinlock_init",
        .exit_symbol = "zigux_runtime_spinlock_exit",
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
    try std.testing.expectError(error.InvalidPilotFamilyContract, prepareRequest(unknown_family));

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

    const initialized_without_selftest_hook = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = false,
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
    try std.testing.expect(!keepsSelftestHookEvidenceConsistent(initialized_without_selftest_hook));
    try std.testing.expectError(error.InvalidSelftestHookEvidence, prepareRequest(initialized_without_selftest_hook));

    const selftest_runs_without_hook = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = false,
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    try std.testing.expect(!keepsSelftestHookEvidenceConsistent(selftest_runs_without_hook));
    try std.testing.expectError(error.InvalidSelftestHookEvidence, prepareRequest(selftest_runs_without_hook));

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

test "runtime loader facade keeps initialized bitmap and kretprobe requests pinned to the smallest shared handoff shape" {
    const bitmap_initialized = LoadPlan{
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
    };
    var bitmap_request = try prepareRequest(bitmap_initialized);
    try std.testing.expectEqual(RequestState.prepared, bitmap_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .prepared,
        bitmap_initialized,
    ));

    var bitmap_live_selftested = bitmap_initialized;
    bitmap_live_selftested.init_flow.handoff_stage = .selftest_complete;
    bitmap_live_selftested.init_flow.selftest_runs = 1;
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .prepared,
        bitmap_live_selftested,
    ));

    const bitmap_pending = try bitmap_request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, bitmap_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .waiting_on_runtime_substrate,
        bitmap_initialized,
    ));
    try std.testing.expect(keepsAllocatorInitFlowConsistent(
        bitmap_pending,
        .arena,
        bitmap_initialized.init_flow,
    ));
    try std.testing.expect(keepsSelftestHookEvidenceConsistent(bitmap_pending));

    const kretprobe_initialized = LoadPlan{
        .module_name = "runtime_kretprobe",
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .kernel_heap,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
    var kretprobe_request = try prepareRequest(kretprobe_initialized);
    try std.testing.expectEqual(RequestState.prepared, kretprobe_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .prepared,
        kretprobe_initialized,
    ));

    var kretprobe_live_selftested = kretprobe_initialized;
    kretprobe_live_selftested.init_flow.handoff_stage = .selftest_complete;
    kretprobe_live_selftested.init_flow.selftest_runs = 1;
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .prepared,
        kretprobe_live_selftested,
    ));

    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, kretprobe_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .waiting_on_runtime_substrate,
        kretprobe_initialized,
    ));
    try std.testing.expect(keepsAllocatorInitFlowConsistent(
        kretprobe_pending,
        .kernel_heap,
        kretprobe_initialized.init_flow,
    ));
    try std.testing.expect(keepsSelftestHookEvidenceConsistent(kretprobe_pending));

    try std.testing.expectEqual(bitmap_pending.requires_runtime_substrate, kretprobe_pending.requires_runtime_substrate);
    try std.testing.expectEqual(bitmap_pending.provides_selftest_hook, kretprobe_pending.provides_selftest_hook);
    try std.testing.expectEqual(bitmap_pending.init_flow.handoff_stage, kretprobe_pending.init_flow.handoff_stage);
    try std.testing.expectEqual(bitmap_pending.init_flow.init_runs, kretprobe_pending.init_flow.init_runs);
    try std.testing.expectEqual(bitmap_pending.init_flow.selftest_runs, kretprobe_pending.init_flow.selftest_runs);
    try std.testing.expectEqual(bitmap_pending.init_flow.exit_runs, kretprobe_pending.init_flow.exit_runs);

    try bitmap_request.releaseWithoutSubstrate();
    try kretprobe_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(RequestState.released_without_substrate, bitmap_request.state);
    try std.testing.expectEqual(RequestState.released_without_substrate, kretprobe_request.state);
}

test "runtime loader facade keeps initialized prepared snapshots stable even if later live state would look exited" {
    const bitmap_initialized = LoadPlan{
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
    };
    var bitmap_request = try prepareRequest(bitmap_initialized);
    try std.testing.expectEqual(RequestState.prepared, bitmap_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .prepared,
        bitmap_initialized,
    ));

    var bitmap_live_exited = bitmap_initialized;
    bitmap_live_exited.init_flow.exit_runs = 1;
    try std.testing.expect(!bitmap_live_exited.init_flow.readyForRuntimeLoad());
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .prepared,
        bitmap_live_exited,
    ));

    const bitmap_pending = try bitmap_request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, bitmap_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .waiting_on_runtime_substrate,
        bitmap_initialized,
    ));
    try std.testing.expect(keepsAllocatorInitFlowConsistent(
        bitmap_pending,
        .arena,
        bitmap_initialized.init_flow,
    ));
    try std.testing.expect(keepsSelftestHookEvidenceConsistent(bitmap_pending));

    const kretprobe_initialized = LoadPlan{
        .module_name = "runtime_kretprobe",
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .kernel_heap,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
    var kretprobe_request = try prepareRequest(kretprobe_initialized);
    try std.testing.expectEqual(RequestState.prepared, kretprobe_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .prepared,
        kretprobe_initialized,
    ));

    var kretprobe_live_exited = kretprobe_initialized;
    kretprobe_live_exited.init_flow.exit_runs = 1;
    try std.testing.expect(!kretprobe_live_exited.init_flow.readyForRuntimeLoad());
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .prepared,
        kretprobe_live_exited,
    ));

    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, kretprobe_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .waiting_on_runtime_substrate,
        kretprobe_initialized,
    ));
    try std.testing.expect(keepsAllocatorInitFlowConsistent(
        kretprobe_pending,
        .kernel_heap,
        kretprobe_initialized.init_flow,
    ));
    try std.testing.expect(keepsSelftestHookEvidenceConsistent(kretprobe_pending));

    try std.testing.expectEqual(bitmap_pending.requires_runtime_substrate, kretprobe_pending.requires_runtime_substrate);
    try std.testing.expectEqual(bitmap_pending.provides_selftest_hook, kretprobe_pending.provides_selftest_hook);
    try std.testing.expectEqual(bitmap_pending.init_flow.handoff_stage, kretprobe_pending.init_flow.handoff_stage);
    try std.testing.expectEqual(bitmap_pending.init_flow.init_runs, kretprobe_pending.init_flow.init_runs);
    try std.testing.expectEqual(bitmap_pending.init_flow.selftest_runs, kretprobe_pending.init_flow.selftest_runs);
    try std.testing.expectEqual(bitmap_pending.init_flow.exit_runs, kretprobe_pending.init_flow.exit_runs);

    try bitmap_request.releaseWithoutSubstrate();
    try kretprobe_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(RequestState.released_without_substrate, bitmap_request.state);
    try std.testing.expectEqual(RequestState.released_without_substrate, kretprobe_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .released_without_substrate,
        bitmap_initialized,
    ));
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .released_without_substrate,
        kretprobe_initialized,
    ));
}

test "runtime loader facade keeps selftest-complete prepared snapshots stable even if later live state would look exited" {
    const atomic64_selftested = LoadPlan{
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
    var atomic64_request = try prepareRequest(atomic64_selftested);
    try std.testing.expectEqual(RequestState.prepared, atomic64_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        atomic64_request,
        .prepared,
        atomic64_selftested,
    ));

    var atomic64_live_exited = atomic64_selftested;
    atomic64_live_exited.init_flow.exit_runs = 1;
    try std.testing.expect(!atomic64_live_exited.init_flow.readyForRuntimeLoad());
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(
        atomic64_request,
        .prepared,
        atomic64_live_exited,
    ));

    const atomic64_pending = try atomic64_request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, atomic64_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        atomic64_request,
        .waiting_on_runtime_substrate,
        atomic64_selftested,
    ));
    try std.testing.expect(keepsAllocatorInitFlowConsistent(
        atomic64_pending,
        .caller_provided,
        atomic64_selftested.init_flow,
    ));
    try std.testing.expect(keepsSelftestHookEvidenceConsistent(atomic64_pending));

    const trace_events_selftested = LoadPlan{
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
    };
    var trace_events_request = try prepareRequest(trace_events_selftested);
    try std.testing.expectEqual(RequestState.prepared, trace_events_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        trace_events_request,
        .prepared,
        trace_events_selftested,
    ));

    var trace_events_live_exited = trace_events_selftested;
    trace_events_live_exited.init_flow.exit_runs = 1;
    try std.testing.expect(!trace_events_live_exited.init_flow.readyForRuntimeLoad());
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(
        trace_events_request,
        .prepared,
        trace_events_live_exited,
    ));

    const trace_events_pending = try trace_events_request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, trace_events_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        trace_events_request,
        .waiting_on_runtime_substrate,
        trace_events_selftested,
    ));
    try std.testing.expect(keepsAllocatorInitFlowConsistent(
        trace_events_pending,
        .caller_provided,
        trace_events_selftested.init_flow,
    ));
    try std.testing.expect(keepsSelftestHookEvidenceConsistent(trace_events_pending));

    try std.testing.expectEqual(atomic64_pending.allocator_handoff, trace_events_pending.allocator_handoff);
    try std.testing.expectEqual(atomic64_pending.init_flow.handoff_stage, trace_events_pending.init_flow.handoff_stage);
    try std.testing.expectEqual(atomic64_pending.init_flow.init_runs, trace_events_pending.init_flow.init_runs);
    try std.testing.expectEqual(atomic64_pending.init_flow.selftest_runs, trace_events_pending.init_flow.selftest_runs);
    try std.testing.expectEqual(atomic64_pending.init_flow.exit_runs, trace_events_pending.init_flow.exit_runs);
    try std.testing.expectEqual(atomic64_pending.requires_runtime_substrate, trace_events_pending.requires_runtime_substrate);
    try std.testing.expectEqual(atomic64_pending.provides_selftest_hook, trace_events_pending.provides_selftest_hook);

    try atomic64_request.releaseWithoutSubstrate();
    try trace_events_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(RequestState.released_without_substrate, atomic64_request.state);
    try std.testing.expectEqual(RequestState.released_without_substrate, trace_events_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        atomic64_request,
        .released_without_substrate,
        atomic64_selftested,
    ));
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        trace_events_request,
        .released_without_substrate,
        trace_events_selftested,
    ));
}

test "runtime loader facade keeps bitmap and kretprobe selftest-complete request shape parity explicit" {
    const bitmap_selftested = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
    var bitmap_request = try prepareRequest(bitmap_selftested);
    try std.testing.expectEqual(RequestState.prepared, bitmap_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .prepared,
        bitmap_selftested,
    ));
    const bitmap_pending = try bitmap_request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, bitmap_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .waiting_on_runtime_substrate,
        bitmap_selftested,
    ));
    try std.testing.expect(keepsAllocatorInitFlowConsistent(
        bitmap_pending,
        .arena,
        bitmap_selftested.init_flow,
    ));
    try std.testing.expect(keepsSelftestHookEvidenceConsistent(bitmap_pending));

    const kretprobe_selftested = LoadPlan{
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
    var kretprobe_request = try prepareRequest(kretprobe_selftested);
    try std.testing.expectEqual(RequestState.prepared, kretprobe_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .prepared,
        kretprobe_selftested,
    ));
    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, kretprobe_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .waiting_on_runtime_substrate,
        kretprobe_selftested,
    ));
    try std.testing.expect(keepsAllocatorInitFlowConsistent(
        kretprobe_pending,
        .kernel_heap,
        kretprobe_selftested.init_flow,
    ));
    try std.testing.expect(keepsSelftestHookEvidenceConsistent(kretprobe_pending));

    try std.testing.expectEqual(bitmap_pending.init_flow.handoff_stage, kretprobe_pending.init_flow.handoff_stage);
    try std.testing.expectEqual(bitmap_pending.init_flow.init_runs, kretprobe_pending.init_flow.init_runs);
    try std.testing.expectEqual(bitmap_pending.init_flow.selftest_runs, kretprobe_pending.init_flow.selftest_runs);
    try std.testing.expectEqual(bitmap_pending.init_flow.exit_runs, kretprobe_pending.init_flow.exit_runs);
    try std.testing.expectEqual(bitmap_pending.requires_runtime_substrate, kretprobe_pending.requires_runtime_substrate);
    try std.testing.expectEqual(bitmap_pending.provides_selftest_hook, kretprobe_pending.provides_selftest_hook);

    try bitmap_request.releaseWithoutSubstrate();
    try kretprobe_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(RequestState.released_without_substrate, bitmap_request.state);
    try std.testing.expectEqual(RequestState.released_without_substrate, kretprobe_request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        bitmap_request,
        .released_without_substrate,
        bitmap_selftested,
    ));
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        kretprobe_request,
        .released_without_substrate,
        kretprobe_selftested,
    ));
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

    var drifted_module = stable_plan;
    drifted_module.module_name = "runtime_atomic64_drift";
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_module));

    var drifted_anchor = stable_plan;
    drifted_anchor.anchor = "lib/atomic64_test_drift.c";
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_anchor));

    var drifted_entry_symbol = stable_plan;
    drifted_entry_symbol.entry_symbol = "zigux_runtime_atomic64_init_drift";
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_entry_symbol));

    var drifted_plan = stable_plan;
    drifted_plan.exit_symbol = "zigux_runtime_atomic64_exit_drift";
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_plan));

    var drifted_runtime_requirement = stable_plan;
    drifted_runtime_requirement.requires_runtime_substrate = false;
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(
        request,
        .prepared,
        drifted_runtime_requirement,
    ));

    var drifted_selftest_hook = stable_plan;
    drifted_selftest_hook.provides_selftest_hook = false;
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(
        request,
        .prepared,
        drifted_selftest_hook,
    ));

    var drifted_allocator = stable_plan;
    drifted_allocator.allocator_handoff = .arena;
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_allocator));

    var drifted_init_flow = stable_plan;
    drifted_init_flow.init_flow.selftest_runs = 0;
    try std.testing.expect(!keepsRequestStateAndPlanExplicit(request, .prepared, drifted_init_flow));
}

test "runtime loader facade keeps prepared trace-events requests pinned when prepared-plan drift appears before handoff" {
    const stable_plan = LoadPlan{
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
    };

    var request = try prepareRequest(stable_plan);
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(request, .prepared, stable_plan));

    request.plan.requires_runtime_substrate = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.module_name = "runtime_trace_events_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));
    try std.testing.expectEqualStrings(stable_plan.module_name, request.prepared_plan.module_name);
    try std.testing.expectEqualStrings("runtime_trace_events_drift", request.plan.module_name);

    request.plan = stable_plan;
    request.plan.anchor = "samples/trace_events/trace-events-sample-drift.c";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.entry_symbol = "zigux_runtime_trace_events_init_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.exit_symbol = "zigux_runtime_trace_events_exit_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.allocator_handoff = .arena;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.init_flow = .{
        .handoff_stage = .initialized,
        .init_runs = 1,
        .selftest_runs = 0,
        .exit_runs = 0,
    };
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.provides_selftest_hook = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.init_flow.exit_runs = 1;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));
}

test "runtime loader facade keeps releaseWithoutSubstrate waiting state pinned across broader prepared-plan drift" {
    const stable_plan = LoadPlan{
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
    };

    var request = try prepareRequest(stable_plan);
    _ = try request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(keepsRequestStateAndPlanExplicit(
        request,
        .waiting_on_runtime_substrate,
        stable_plan,
    ));

    request.plan.requires_runtime_substrate = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.module_name = "runtime_trace_events_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.anchor = "samples/trace_events/trace-events-sample-drift.c";
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.entry_symbol = "zigux_runtime_trace_events_init_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.exit_symbol = "zigux_runtime_trace_events_exit_drift";
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.allocator_handoff = .arena;
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.provides_selftest_hook = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));

    request.plan = stable_plan;
    request.plan.init_flow.selftest_runs = 2;
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(contract.keepsLoadPlanExplicit(request.prepared_plan, stable_plan));
    try std.testing.expect(!contract.keepsLoadPlanExplicit(request.plan, stable_plan));
}
