const std = @import("std");
const runtime_loader = @import("runtime_loader");

fn makePlan(
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
) runtime_loader.LoadPlan {
    return .{
        .module_name = module_name,
        .anchor = anchor,
        .entry_symbol = entry_symbol,
        .exit_symbol = exit_symbol,
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
}

test "phase 9 caller-provided prepared snapshots stay pinned across later initialized exit drift" {
    const stable_atomic64 = makePlan(
        "runtime_atomic64",
        "lib/atomic64_test.c",
        "zigux_runtime_atomic64_init",
        "zigux_runtime_atomic64_exit",
    );
    var atomic64_request = try runtime_loader.prepareRequest(stable_atomic64);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, atomic64_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        atomic64_request,
        .prepared,
        stable_atomic64,
    ));

    var atomic64_live_exited = stable_atomic64;
    atomic64_live_exited.init_flow.exit_runs = 1;
    try std.testing.expect(!atomic64_live_exited.init_flow.readyForRuntimeLoad());
    try std.testing.expect(!runtime_loader.keepsRequestStateAndPlanExplicit(
        atomic64_request,
        .prepared,
        atomic64_live_exited,
    ));

    const atomic64_pending = try atomic64_request.requestRuntimeLoad();
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, atomic64_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        atomic64_request,
        .waiting_on_runtime_substrate,
        stable_atomic64,
    ));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(atomic64_pending, stable_atomic64));
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.caller_provided, atomic64_pending.allocator_handoff);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        atomic64_pending,
        .caller_provided,
        stable_atomic64.init_flow,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(atomic64_pending));

    const stable_trace_events = makePlan(
        "runtime_trace_events",
        "samples/trace_events/trace-events-sample.c",
        "zigux_runtime_trace_events_init",
        "zigux_runtime_trace_events_exit",
    );
    var trace_events_request = try runtime_loader.prepareRequest(stable_trace_events);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, trace_events_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        trace_events_request,
        .prepared,
        stable_trace_events,
    ));

    var trace_events_live_exited = stable_trace_events;
    trace_events_live_exited.init_flow.exit_runs = 1;
    try std.testing.expect(!trace_events_live_exited.init_flow.readyForRuntimeLoad());
    try std.testing.expect(!runtime_loader.keepsRequestStateAndPlanExplicit(
        trace_events_request,
        .prepared,
        trace_events_live_exited,
    ));

    const trace_events_pending = try trace_events_request.requestRuntimeLoad();
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, trace_events_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        trace_events_request,
        .waiting_on_runtime_substrate,
        stable_trace_events,
    ));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(trace_events_pending, stable_trace_events));
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.caller_provided, trace_events_pending.allocator_handoff);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        trace_events_pending,
        .caller_provided,
        stable_trace_events.init_flow,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(trace_events_pending));

    try std.testing.expectEqual(atomic64_pending.allocator_handoff, trace_events_pending.allocator_handoff);
    try std.testing.expectEqual(atomic64_pending.init_flow.handoff_stage, trace_events_pending.init_flow.handoff_stage);
    try std.testing.expectEqual(atomic64_pending.init_flow.init_runs, trace_events_pending.init_flow.init_runs);
    try std.testing.expectEqual(atomic64_pending.init_flow.selftest_runs, trace_events_pending.init_flow.selftest_runs);
    try std.testing.expectEqual(atomic64_pending.init_flow.exit_runs, trace_events_pending.init_flow.exit_runs);
    try std.testing.expectEqual(atomic64_pending.requires_runtime_substrate, trace_events_pending.requires_runtime_substrate);
    try std.testing.expectEqual(atomic64_pending.provides_selftest_hook, trace_events_pending.provides_selftest_hook);

    try atomic64_request.releaseWithoutSubstrate();
    try trace_events_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, atomic64_request.state);
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, trace_events_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        atomic64_request,
        .released_without_substrate,
        stable_atomic64,
    ));
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        trace_events_request,
        .released_without_substrate,
        stable_trace_events,
    ));
}
