const std = @import("std");
const runtime_loader = @import("runtime_loader");
const contract = @import("runtime_loader_contract");

const AllocatorHandoff = contract.AllocatorHandoff;
const HandoffStage = contract.HandoffStage;
const LoadPlan = contract.LoadPlan;
const PreparedRequest = runtime_loader.PreparedRequest;
const RequestState = contract.RequestState;

fn makeInitializedPlan(
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    allocator_handoff: AllocatorHandoff,
) LoadPlan {
    return .{
        .module_name = module_name,
        .anchor = anchor,
        .entry_symbol = entry_symbol,
        .exit_symbol = exit_symbol,
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = allocator_handoff,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
}

fn makeSelftestCompletePlan(
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    allocator_handoff: AllocatorHandoff,
) LoadPlan {
    return .{
        .module_name = module_name,
        .anchor = anchor,
        .entry_symbol = entry_symbol,
        .exit_symbol = exit_symbol,
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = allocator_handoff,
        .init_flow = .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    };
}

fn expectInitializedSharedRequestShape(plan: LoadPlan, allocator_handoff: AllocatorHandoff) !void {
    try std.testing.expect(plan.requires_runtime_substrate);
    try std.testing.expect(plan.provides_selftest_hook);
    try std.testing.expectEqual(allocator_handoff, plan.allocator_handoff);
    try std.testing.expectEqual(HandoffStage.initialized, plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), plan.init_flow.init_runs);
    try std.testing.expectEqual(@as(usize, 0), plan.init_flow.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), plan.init_flow.exit_runs);
    try std.testing.expect(plan.init_flow.readyForRuntimeLoad());
}

fn expectSelftestCompleteSharedRequestShape(
    plan: LoadPlan,
    allocator_handoff: AllocatorHandoff,
) !void {
    try std.testing.expect(plan.requires_runtime_substrate);
    try std.testing.expect(plan.provides_selftest_hook);
    try std.testing.expectEqual(allocator_handoff, plan.allocator_handoff);
    try std.testing.expectEqual(HandoffStage.selftest_complete, plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), plan.init_flow.init_runs);
    try std.testing.expectEqual(@as(usize, 1), plan.init_flow.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), plan.init_flow.exit_runs);
    try std.testing.expect(plan.init_flow.readyForRuntimeLoad());
}

fn expectPreparedRequestStable(request: PreparedRequest, plan: LoadPlan, state: RequestState) !void {
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, state, plan));
    try std.testing.expect(
        runtime_loader.keepsAllocatorInitFlowConsistent(
            plan,
            plan.allocator_handoff,
            plan.init_flow,
        ),
    );
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(plan));
}

test "shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned" {
    const bitmap_plan = makeInitializedPlan(
        "runtime_bitmap",
        "lib/test_bitmap.c",
        "zigux_runtime_bitmap_init",
        "zigux_runtime_bitmap_exit",
        .arena,
    );
    const kretprobe_plan = makeInitializedPlan(
        "runtime_kretprobe",
        "samples/kprobes/kretprobe_example.c",
        "zigux_runtime_kretprobe_init",
        "zigux_runtime_kretprobe_exit",
        .caller_provided,
    );

    try expectInitializedSharedRequestShape(bitmap_plan, .arena);
    try expectInitializedSharedRequestShape(kretprobe_plan, .caller_provided);
    try std.testing.expect(bitmap_plan.allocator_handoff != kretprobe_plan.allocator_handoff);
    try std.testing.expectEqualStrings("runtime_bitmap", bitmap_plan.module_name);
    try std.testing.expectEqualStrings("runtime_kretprobe", kretprobe_plan.module_name);

    var bitmap_request = try runtime_loader.prepareRequest(bitmap_plan);
    var kretprobe_request = try runtime_loader.prepareRequest(kretprobe_plan);

    try expectPreparedRequestStable(bitmap_request, bitmap_plan, .prepared);
    try expectPreparedRequestStable(kretprobe_request, kretprobe_plan, .prepared);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(bitmap_request.prepared_plan, bitmap_plan));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(kretprobe_request.prepared_plan, kretprobe_plan));

    const bitmap_pending = try bitmap_request.requestRuntimeLoad();
    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();

    try expectPreparedRequestStable(bitmap_request, bitmap_pending, .waiting_on_runtime_substrate);
    try expectPreparedRequestStable(kretprobe_request, kretprobe_pending, .waiting_on_runtime_substrate);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(bitmap_pending, bitmap_request.prepared_plan));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(kretprobe_pending, kretprobe_request.prepared_plan));

    try bitmap_request.releaseWithoutSubstrate();
    try kretprobe_request.releaseWithoutSubstrate();

    try expectPreparedRequestStable(bitmap_request, bitmap_pending, .released_without_substrate);
    try expectPreparedRequestStable(kretprobe_request, kretprobe_pending, .released_without_substrate);
}

test "shared runtime loader keeps selftest-complete trace-events and atomic64 request shape aligned" {
    const trace_events_plan = makeSelftestCompletePlan(
        "runtime_trace_events",
        "samples/trace_events/trace-events-sample.c",
        "zigux_runtime_trace_events_init",
        "zigux_runtime_trace_events_exit",
        .caller_provided,
    );
    const atomic64_plan = makeSelftestCompletePlan(
        "runtime_atomic64",
        "lib/atomic64_test.c",
        "zigux_runtime_atomic64_init",
        "zigux_runtime_atomic64_exit",
        .caller_provided,
    );

    try expectSelftestCompleteSharedRequestShape(trace_events_plan, .caller_provided);
    try expectSelftestCompleteSharedRequestShape(atomic64_plan, .caller_provided);
    try std.testing.expectEqualStrings("runtime_trace_events", trace_events_plan.module_name);
    try std.testing.expectEqualStrings("runtime_atomic64", atomic64_plan.module_name);

    var trace_events_request = try runtime_loader.prepareRequest(trace_events_plan);
    var atomic64_request = try runtime_loader.prepareRequest(atomic64_plan);

    try expectPreparedRequestStable(trace_events_request, trace_events_plan, .prepared);
    try expectPreparedRequestStable(atomic64_request, atomic64_plan, .prepared);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(trace_events_request.prepared_plan, trace_events_plan));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(atomic64_request.prepared_plan, atomic64_plan));

    const trace_events_pending = try trace_events_request.requestRuntimeLoad();
    const atomic64_pending = try atomic64_request.requestRuntimeLoad();

    try expectPreparedRequestStable(
        trace_events_request,
        trace_events_pending,
        .waiting_on_runtime_substrate,
    );
    try expectPreparedRequestStable(
        atomic64_request,
        atomic64_pending,
        .waiting_on_runtime_substrate,
    );
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(
        trace_events_pending,
        trace_events_request.prepared_plan,
    ));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(
        atomic64_pending,
        atomic64_request.prepared_plan,
    ));

    try trace_events_request.releaseWithoutSubstrate();
    try atomic64_request.releaseWithoutSubstrate();

    try expectPreparedRequestStable(
        trace_events_request,
        trace_events_pending,
        .released_without_substrate,
    );
    try expectPreparedRequestStable(
        atomic64_request,
        atomic64_pending,
        .released_without_substrate,
    );
}

test "shared runtime loader keeps rejected release-order transitions fail-closed across loader families" {
    const bitmap_plan = makeInitializedPlan(
        "runtime_bitmap",
        "lib/test_bitmap.c",
        "zigux_runtime_bitmap_init",
        "zigux_runtime_bitmap_exit",
        .arena,
    );
    const trace_events_plan = makeSelftestCompletePlan(
        "runtime_trace_events",
        "samples/trace_events/trace-events-sample.c",
        "zigux_runtime_trace_events_init",
        "zigux_runtime_trace_events_exit",
        .caller_provided,
    );

    var bitmap_request = try runtime_loader.prepareRequest(bitmap_plan);
    var trace_events_request = try runtime_loader.prepareRequest(trace_events_plan);

    try std.testing.expectError(error.InvalidLoaderState, bitmap_request.releaseWithoutSubstrate());
    try std.testing.expectError(error.InvalidLoaderState, trace_events_request.releaseWithoutSubstrate());

    try expectPreparedRequestStable(bitmap_request, bitmap_plan, .prepared);
    try expectPreparedRequestStable(trace_events_request, trace_events_plan, .prepared);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(bitmap_request.prepared_plan, bitmap_plan));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(
        trace_events_request.prepared_plan,
        trace_events_plan,
    ));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(bitmap_request.plan, bitmap_plan));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(trace_events_request.plan, trace_events_plan));

    const bitmap_pending = try bitmap_request.requestRuntimeLoad();
    const trace_events_pending = try trace_events_request.requestRuntimeLoad();

    try bitmap_request.releaseWithoutSubstrate();
    try trace_events_request.releaseWithoutSubstrate();

    try expectPreparedRequestStable(
        bitmap_request,
        bitmap_pending,
        .released_without_substrate,
    );
    try expectPreparedRequestStable(
        trace_events_request,
        trace_events_pending,
        .released_without_substrate,
    );

    try std.testing.expectError(error.InvalidLoaderState, bitmap_request.releaseWithoutSubstrate());
    try std.testing.expectError(error.InvalidLoaderState, trace_events_request.releaseWithoutSubstrate());
    try std.testing.expectError(error.InvalidLoaderState, bitmap_request.requestRuntimeLoad());
    try std.testing.expectError(error.InvalidLoaderState, trace_events_request.requestRuntimeLoad());

    try expectPreparedRequestStable(
        bitmap_request,
        bitmap_pending,
        .released_without_substrate,
    );
    try expectPreparedRequestStable(
        trace_events_request,
        trace_events_pending,
        .released_without_substrate,
    );
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(bitmap_request.prepared_plan, bitmap_plan));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(
        trace_events_request.prepared_plan,
        trace_events_plan,
    ));
}

test "shared runtime loader keeps selftest-complete counters from drifting before handoff" {
    const trace_events_plan = makeSelftestCompletePlan(
        "runtime_trace_events",
        "samples/trace_events/trace-events-sample.c",
        "zigux_runtime_trace_events_init",
        "zigux_runtime_trace_events_exit",
        .caller_provided,
    );

    var request = try runtime_loader.prepareRequest(trace_events_plan);

    request.plan.init_flow.selftest_runs = 2;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(request.prepared_plan, trace_events_plan));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(request.plan, trace_events_plan));

    request.plan = trace_events_plan;
    request.plan.init_flow.exit_runs = 1;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(request.prepared_plan, trace_events_plan));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(request.plan, trace_events_plan));
}

test "shared runtime loader keeps prepared init-flow counters from drifting before handoff" {
    const kretprobe_plan = makeInitializedPlan(
        "runtime_kretprobe",
        "samples/kprobes/kretprobe_example.c",
        "zigux_runtime_kretprobe_init",
        "zigux_runtime_kretprobe_exit",
        .caller_provided,
    );

    var request = try runtime_loader.prepareRequest(kretprobe_plan);

    request.plan.init_flow.init_runs = 2;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(request.prepared_plan, kretprobe_plan));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(request.plan, kretprobe_plan));

    request.plan = kretprobe_plan;
    request.plan.init_flow.exit_runs = 1;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(request.prepared_plan, kretprobe_plan));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(request.plan, kretprobe_plan));
}

test "shared runtime loader keeps prepared selftest-hook and handoff-stage labels from drifting before handoff" {
    const trace_events_plan = makeSelftestCompletePlan(
        "runtime_trace_events",
        "samples/trace_events/trace-events-sample.c",
        "zigux_runtime_trace_events_init",
        "zigux_runtime_trace_events_exit",
        .caller_provided,
    );
    var trace_events_request = try runtime_loader.prepareRequest(trace_events_plan);

    trace_events_request.plan.provides_selftest_hook = false;
    try std.testing.expectError(error.PreparedPlanDrift, trace_events_request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, trace_events_request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(
        trace_events_request.prepared_plan,
        trace_events_plan,
    ));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(
        trace_events_request.plan,
        trace_events_plan,
    ));

    trace_events_request.plan = trace_events_plan;
    trace_events_request.plan.init_flow.handoff_stage = .initialized;
    trace_events_request.plan.init_flow.selftest_runs = 0;
    try std.testing.expectError(error.PreparedPlanDrift, trace_events_request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, trace_events_request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(
        trace_events_request.prepared_plan,
        trace_events_plan,
    ));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(
        trace_events_request.plan,
        trace_events_plan,
    ));

    const kretprobe_plan = makeInitializedPlan(
        "runtime_kretprobe",
        "samples/kprobes/kretprobe_example.c",
        "zigux_runtime_kretprobe_init",
        "zigux_runtime_kretprobe_exit",
        .caller_provided,
    );
    var kretprobe_request = try runtime_loader.prepareRequest(kretprobe_plan);

    kretprobe_request.plan.init_flow.handoff_stage = .selftest_complete;
    kretprobe_request.plan.init_flow.selftest_runs = 1;
    try std.testing.expectError(error.PreparedPlanDrift, kretprobe_request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, kretprobe_request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(
        kretprobe_request.prepared_plan,
        kretprobe_plan,
    ));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(
        kretprobe_request.plan,
        kretprobe_plan,
    ));
}