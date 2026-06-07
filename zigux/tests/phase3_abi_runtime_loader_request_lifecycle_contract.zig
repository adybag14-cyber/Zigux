const std = @import("std");
const runtime_loader = @import("runtime_loader");

const LoadPlan = runtime_loader.LoadPlan;
const RequestState = runtime_loader.RequestState;

fn traceEventsPlan() LoadPlan {
    return .{
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
}

fn bitmapPlan() LoadPlan {
    return .{
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
}

test "runtime loader request lifecycle advances through the published states once" {
    const stable = traceEventsPlan();
    var request = try runtime_loader.prepareRequest(stable);

    try std.testing.expectEqual(RequestState.prepared, request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, stable));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(request.prepared_plan, stable));

    const pending = try request.requestRuntimeLoad();
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(pending, stable));
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .waiting_on_runtime_substrate, pending));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(request.prepared_plan, stable));

    try request.releaseWithoutSubstrate();
    try std.testing.expectEqual(RequestState.released_without_substrate, request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .released_without_substrate, pending));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(request.prepared_plan, stable));
}

test "runtime loader request lifecycle rejects plan drift before state mutation" {
    const stable = bitmapPlan();
    var prepared_request = try runtime_loader.prepareRequest(stable);
    prepared_request.plan.module_name = "runtime_bitmap_drift";

    try std.testing.expectError(error.PreparedPlanDrift, prepared_request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.prepared, prepared_request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(prepared_request.prepared_plan, stable));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(prepared_request.plan, stable));

    var waiting_request = try runtime_loader.prepareRequest(stable);
    const pending = try waiting_request.requestRuntimeLoad();
    waiting_request.plan.requires_runtime_substrate = false;

    try std.testing.expectError(error.PreparedPlanDrift, waiting_request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, waiting_request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(waiting_request.prepared_plan, stable));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(pending, stable));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(waiting_request.plan, stable));
}

test "runtime loader request lifecycle rejects invalid edges without disturbing snapshots" {
    const stable = traceEventsPlan();
    var prepared_request = try runtime_loader.prepareRequest(stable);

    try std.testing.expectError(error.InvalidLoaderState, prepared_request.releaseWithoutSubstrate());
    try std.testing.expectEqual(RequestState.prepared, prepared_request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(prepared_request.prepared_plan, stable));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(prepared_request.plan, stable));

    var waiting_request = try runtime_loader.prepareRequest(stable);
    const pending = try waiting_request.requestRuntimeLoad();
    try std.testing.expectError(error.InvalidLoaderState, waiting_request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.waiting_on_runtime_substrate, waiting_request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(waiting_request.prepared_plan, stable));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(waiting_request.plan, pending));

    try waiting_request.releaseWithoutSubstrate();
    try std.testing.expectError(error.InvalidLoaderState, waiting_request.releaseWithoutSubstrate());
    try std.testing.expectError(error.InvalidLoaderState, waiting_request.requestRuntimeLoad());
    try std.testing.expectEqual(RequestState.released_without_substrate, waiting_request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(waiting_request.prepared_plan, stable));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(waiting_request.plan, pending));
}

test "runtime loader request lifecycle fails closed before prepared state exists" {
    var missing_substrate = traceEventsPlan();
    missing_substrate.requires_runtime_substrate = false;
    try std.testing.expectError(error.LoaderNotRequired, runtime_loader.prepareRequest(missing_substrate));

    var unknown_family = bitmapPlan();
    unknown_family.entry_symbol = "zigux_runtime_bitmap_init_drift";
    try std.testing.expectError(error.InvalidPilotFamilyContract, runtime_loader.prepareRequest(unknown_family));

    var shape_drift = bitmapPlan();
    shape_drift.init_flow.handoff_stage = .selftest_complete;
    shape_drift.init_flow.selftest_runs = 1;
    try std.testing.expectError(error.InvalidPilotFamilyShape, runtime_loader.prepareRequest(shape_drift));

    var selftest_drift = traceEventsPlan();
    selftest_drift.provides_selftest_hook = false;
    try std.testing.expectError(error.InvalidSelftestHookEvidence, runtime_loader.prepareRequest(selftest_drift));
}
