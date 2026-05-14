const std = @import("std");
const runtime_loader = @import("runtime_loader");
const runtime_trace_events_loader = @import("runtime_trace_events_loader");
const runtime_trace_events_sample = @import("runtime_trace_events_sample");

test "phase 9 runtime trace-events loader rejects prepared shared runtime-substrate drift before any local runtime handoff" {
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

    try std.testing.expectError(error.LoaderNotRequired, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
}

test "phase 9 runtime trace-events loader rejects initialized-stage prepared shared runtime-substrate drift before any local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();

    var loader = runtime_trace_events_loader.RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, shared_request.plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), shared_request.plan.init_flow.selftest_runs);
    shared_request.plan.requires_runtime_substrate = false;

    try std.testing.expectError(error.LoaderNotRequired, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
}

test "phase 9 runtime trace-events loader rejects prepared shared selftest-hook drift before any local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = runtime_trace_events_loader.RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(shared_request.plan.provides_selftest_hook);
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(shared_request.plan));
    shared_request.plan.provides_selftest_hook = false;

    try std.testing.expect(!runtime_loader.keepsSelftestHookEvidenceConsistent(shared_request.plan));
    try std.testing.expectError(error.InvalidSelftestHookEvidence, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
}

test "phase 9 runtime trace-events loader rejects initialized-stage prepared shared selftest-hook drift before any local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();

    var loader = runtime_trace_events_loader.RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, shared_request.plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), shared_request.plan.init_flow.selftest_runs);
    try std.testing.expect(shared_request.plan.provides_selftest_hook);
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(shared_request.plan));
    shared_request.plan.provides_selftest_hook = false;

    try std.testing.expect(!runtime_loader.keepsSelftestHookEvidenceConsistent(shared_request.plan));
    try std.testing.expectError(error.InvalidSelftestHookEvidence, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
}
