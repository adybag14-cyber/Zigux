const std = @import("std");
const runtime_loader = @import("runtime_loader");

fn makePlan(stage: runtime_loader.HandoffStage) runtime_loader.LoadPlan {
    const is_initialized = stage == .initialized;
    return .{
        .module_name = if (is_initialized) "runtime_bitmap" else "runtime_trace_events",
        .anchor = if (is_initialized) "lib/test_bitmap.c" else "samples/trace_events/trace-events-sample.c",
        .entry_symbol = if (is_initialized) "zigux_runtime_bitmap_init" else "zigux_runtime_trace_events_init",
        .exit_symbol = if (is_initialized) "zigux_runtime_bitmap_exit" else "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = if (is_initialized)
            .{ .license = "GPL", .aliases = &.{"zigux:runtime-pilot:runtime_bitmap"} }
        else
            .{ .license = "GPL", .aliases = &.{"zigux:runtime-pilot:runtime_trace_events"} },
        .allocator_handoff = .caller_provided,
        .init_flow = switch (stage) {
            .initialized => .{
                .handoff_stage = .initialized,
                .init_runs = 1,
                .selftest_runs = 0,
                .exit_runs = 0,
            },
            .selftest_complete => .{
                .handoff_stage = .selftest_complete,
                .init_runs = 1,
                .selftest_runs = 1,
                .exit_runs = 0,
            },
        },
    };
}

fn expectPreparedState(
    request: runtime_loader.PreparedRequest,
    stable: runtime_loader.LoadPlan,
) !void {
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(request.prepared_plan, stable));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(request.plan, stable));
}

fn expectWaitingState(
    request: runtime_loader.PreparedRequest,
    stable: runtime_loader.LoadPlan,
    pending: runtime_loader.LoadPlan,
) !void {
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(request.prepared_plan, stable));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(pending, stable));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(request.plan, stable));
}

test "phase9 runtime trace-events shared loader rejects prepared substrate drift before handoff" {
    var request = try runtime_loader.prepareRequest(makePlan(.selftest_complete));
    const stable = request.plan;

    request.plan.requires_runtime_substrate = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedState(request, stable);
}

test "phase9 runtime trace-events shared loader rejects initialized-stage prepared substrate drift before handoff" {
    var request = try runtime_loader.prepareRequest(makePlan(.initialized));
    const stable = request.plan;

    request.plan.requires_runtime_substrate = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedState(request, stable);
}

test "phase9 runtime trace-events shared loader rejects prepared selftest-hook and init-flow count drift before handoff" {
    var hook_request = try runtime_loader.prepareRequest(makePlan(.selftest_complete));
    const stable_hook = hook_request.plan;

    hook_request.plan.provides_selftest_hook = false;
    try std.testing.expectError(error.PreparedPlanDrift, hook_request.requestRuntimeLoad());
    try expectPreparedState(hook_request, stable_hook);

    var stage_request = try runtime_loader.prepareRequest(makePlan(.selftest_complete));
    const stable_stage = stage_request.plan;

    stage_request.plan.init_flow.handoff_stage = .initialized;
    stage_request.plan.init_flow.selftest_runs = 0;
    try std.testing.expectError(error.PreparedPlanDrift, stage_request.requestRuntimeLoad());
    try expectPreparedState(stage_request, stable_stage);

    var init_runs_request = try runtime_loader.prepareRequest(makePlan(.selftest_complete));
    const stable_init_runs = init_runs_request.plan;

    init_runs_request.plan.init_flow.init_runs = 2;
    try std.testing.expectError(error.PreparedPlanDrift, init_runs_request.requestRuntimeLoad());
    try expectPreparedState(init_runs_request, stable_init_runs);

    var initialized_request = try runtime_loader.prepareRequest(makePlan(.initialized));
    const stable_initialized = initialized_request.plan;

    initialized_request.plan.provides_selftest_hook = false;
    try std.testing.expectError(error.PreparedPlanDrift, initialized_request.requestRuntimeLoad());
    try expectPreparedState(initialized_request, stable_initialized);

    initialized_request.plan = stable_initialized;
    initialized_request.plan.init_flow.handoff_stage = .selftest_complete;
    initialized_request.plan.init_flow.selftest_runs = 1;
    try std.testing.expectError(error.PreparedPlanDrift, initialized_request.requestRuntimeLoad());
    try expectPreparedState(initialized_request, stable_initialized);

    var exit_runs_request = try runtime_loader.prepareRequest(makePlan(.initialized));
    const stable_exit_runs = exit_runs_request.plan;

    exit_runs_request.plan.init_flow.exit_runs = 1;
    try std.testing.expectError(error.PreparedPlanDrift, exit_runs_request.requestRuntimeLoad());
    try expectPreparedState(exit_runs_request, stable_exit_runs);
}

test "phase9 runtime trace-events shared loader rejects release drift after waiting handoff" {
    var request = try runtime_loader.prepareRequest(makePlan(.selftest_complete));
    const stable = request.plan;
    const pending = try request.requestRuntimeLoad();

    request.plan.requires_runtime_substrate = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try expectWaitingState(request, stable, pending);
}

test "phase9 runtime trace-events shared loader rejects initialized-stage release drift after waiting handoff" {
    var request = try runtime_loader.prepareRequest(makePlan(.initialized));
    const stable = request.plan;
    const pending = try request.requestRuntimeLoad();

    request.plan.requires_runtime_substrate = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.releaseWithoutSubstrate());
    try expectWaitingState(request, stable, pending);
}

test "phase9 runtime trace-events shared loader rejects waiting selftest-hook and init-flow count drift before release" {
    var hook_request = try runtime_loader.prepareRequest(makePlan(.selftest_complete));
    const stable_hook = hook_request.plan;
    const pending_hook = try hook_request.requestRuntimeLoad();

    hook_request.plan.provides_selftest_hook = false;
    try std.testing.expectError(error.PreparedPlanDrift, hook_request.releaseWithoutSubstrate());
    try expectWaitingState(hook_request, stable_hook, pending_hook);

    var stage_request = try runtime_loader.prepareRequest(makePlan(.selftest_complete));
    const stable_stage = stage_request.plan;
    const pending_stage = try stage_request.requestRuntimeLoad();

    stage_request.plan = pending_stage;
    stage_request.plan.init_flow.handoff_stage = .initialized;
    stage_request.plan.init_flow.selftest_runs = 0;
    try std.testing.expectError(error.PreparedPlanDrift, stage_request.releaseWithoutSubstrate());
    try expectWaitingState(stage_request, stable_stage, pending_stage);

    var init_runs_request = try runtime_loader.prepareRequest(makePlan(.selftest_complete));
    const stable_init_runs = init_runs_request.plan;
    const pending_init_runs = try init_runs_request.requestRuntimeLoad();

    init_runs_request.plan = pending_init_runs;
    init_runs_request.plan.init_flow.init_runs = 2;
    try std.testing.expectError(error.PreparedPlanDrift, init_runs_request.releaseWithoutSubstrate());
    try expectWaitingState(init_runs_request, stable_init_runs, pending_init_runs);

    var initialized_request = try runtime_loader.prepareRequest(makePlan(.initialized));
    const stable_initialized = initialized_request.plan;
    const pending_initialized = try initialized_request.requestRuntimeLoad();

    initialized_request.plan.provides_selftest_hook = false;
    try std.testing.expectError(error.PreparedPlanDrift, initialized_request.releaseWithoutSubstrate());
    try expectWaitingState(initialized_request, stable_initialized, pending_initialized);

    initialized_request.plan = pending_initialized;
    initialized_request.plan.init_flow.handoff_stage = .selftest_complete;
    initialized_request.plan.init_flow.selftest_runs = 1;
    try std.testing.expectError(error.PreparedPlanDrift, initialized_request.releaseWithoutSubstrate());
    try expectWaitingState(initialized_request, stable_initialized, pending_initialized);

    var exit_runs_request = try runtime_loader.prepareRequest(makePlan(.initialized));
    const stable_exit_runs = exit_runs_request.plan;
    const pending_exit_runs = try exit_runs_request.requestRuntimeLoad();

    exit_runs_request.plan = pending_exit_runs;
    exit_runs_request.plan.init_flow.exit_runs = 1;
    try std.testing.expectError(error.PreparedPlanDrift, exit_runs_request.releaseWithoutSubstrate());
    try expectWaitingState(exit_runs_request, stable_exit_runs, pending_exit_runs);
}

test "phase9 runtime trace-events shared loader rejects approved-family release drift after waiting handoff" {
    var anchor_request = try runtime_loader.prepareRequest(makePlan(.selftest_complete));
    const stable_anchor = anchor_request.plan;
    const pending_anchor = try anchor_request.requestRuntimeLoad();
    anchor_request.plan.anchor = "samples/trace_events/trace-events-sample-drift.c";
    try std.testing.expectError(error.PreparedPlanDrift, anchor_request.releaseWithoutSubstrate());
    try expectWaitingState(anchor_request, stable_anchor, pending_anchor);

    var entry_request = try runtime_loader.prepareRequest(makePlan(.initialized));
    const stable_entry = entry_request.plan;
    const pending_entry = try entry_request.requestRuntimeLoad();
    entry_request.plan.entry_symbol = "zigux_runtime_trace_events_init_drift";
    try std.testing.expectError(error.PreparedPlanDrift, entry_request.releaseWithoutSubstrate());
    try expectWaitingState(entry_request, stable_entry, pending_entry);

    var exit_request = try runtime_loader.prepareRequest(makePlan(.selftest_complete));
    const stable_exit = exit_request.plan;
    const pending_exit = try exit_request.requestRuntimeLoad();
    exit_request.plan.exit_symbol = "zigux_runtime_trace_events_exit_drift";
    try std.testing.expectError(error.PreparedPlanDrift, exit_request.releaseWithoutSubstrate());
    try expectWaitingState(exit_request, stable_exit, pending_exit);
}
