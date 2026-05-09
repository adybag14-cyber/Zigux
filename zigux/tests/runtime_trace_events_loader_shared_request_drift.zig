const std = @import("std");
const runtime_loader = @import("runtime_loader");
const runtime_trace_events_loader = @import("runtime_trace_events_loader");
const runtime_trace_events_sample = @import("runtime_trace_events_sample");

test "runtime trace-events loader rejects prepared shared runtime-substrate drift before any local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = runtime_trace_events_loader.RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));

    shared_request.plan.requires_runtime_substrate = false;

    try std.testing.expectError(
        error.LoaderNotRequired,
        loader.requestSharedRuntimeLoad(&shared_request),
    );
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
}

test "runtime trace-events loader rejects prepared shared approved-family anchor and symbol drift before any local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = runtime_trace_events_loader.RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    const prepared_shared_plan = shared_request.plan;

    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_shared_plan,
    ));

    shared_request.plan.anchor = "samples/trace_events/trace-events-sample-drift.c";
    try std.testing.expectError(
        error.InvalidPilotFamilyContract,
        loader.requestSharedRuntimeLoad(&shared_request),
    );
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    shared_request.plan = prepared_shared_plan;
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_shared_plan,
    ));

    shared_request.plan.entry_symbol = "zigux_runtime_trace_events_init_drift";
    try std.testing.expectError(
        error.InvalidPilotFamilyContract,
        loader.requestSharedRuntimeLoad(&shared_request),
    );
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    shared_request.plan = prepared_shared_plan;
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_shared_plan,
    ));

    shared_request.plan.exit_symbol = "zigux_runtime_trace_events_exit_drift";
    try std.testing.expectError(
        error.InvalidPilotFamilyContract,
        loader.requestSharedRuntimeLoad(&shared_request),
    );
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    shared_request.plan = prepared_shared_plan;
    _ = try runtime_trace_events_loader.RuntimeTraceEventsLoader.planFor(&module);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_shared_plan,
    ));
}
