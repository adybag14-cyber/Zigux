const std = @import("std");
const runtime_loader = @import("runtime_loader");

fn makePlan(stage: runtime_loader.HandoffStage) runtime_loader.LoadPlan {
    return .{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
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
