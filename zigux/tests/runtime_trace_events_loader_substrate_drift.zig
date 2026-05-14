const std = @import("std");
const runtime_loader = @import("runtime_loader");
const runtime_trace_events_loader = @import("runtime_trace_events_loader");
const runtime_trace_events_sample = @import("runtime_trace_events_sample");

fn expectPreparedRuntimeSubstrateDriftKeepsPreparedState(
    shared_request: runtime_loader.PreparedRequest,
    stable_plan: runtime_loader.LoadPlan,
) !void {
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(shared_request.prepared_plan.requires_runtime_substrate);
    try std.testing.expect(!shared_request.plan.requires_runtime_substrate);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(shared_request.prepared_plan, stable_plan));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(shared_request.plan, stable_plan));
}

test "phase 9 runtime trace-events loader rejects prepared shared runtime-substrate drift before any local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = runtime_trace_events_loader.RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    const prepared_plan = shared_request.plan;
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
    shared_request.plan.requires_runtime_substrate = false;

    try std.testing.expectError(error.PreparedPlanDrift, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try expectPreparedRuntimeSubstrateDriftKeepsPreparedState(shared_request, prepared_plan);
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
    const prepared_plan = shared_request.plan;
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

    try std.testing.expectError(error.PreparedPlanDrift, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try expectPreparedRuntimeSubstrateDriftKeepsPreparedState(shared_request, prepared_plan);
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
    try std.testing.expectError(error.PreparedPlanDrift, loader.requestSharedRuntimeLoad(&shared_request));
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
    try std.testing.expectError(error.PreparedPlanDrift, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
}

test "phase 9 runtime trace-events loader keeps initialized prepared requests explicit across later direct registration replay" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();

    var loader = runtime_trace_events_loader.RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    const prepared_plan = shared_request.plan;
    const prepared_snapshot = runtime_trace_events_loader.registrationSnapshot(loader.cached_plan.?);
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, prepared_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), prepared_plan.init_flow.selftest_runs);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_plan,
    ));
    try std.testing.expect(runtime_trace_events_loader.keepsRegistrationSnapshotExplicit(
        loader.cached_plan.?,
        prepared_snapshot,
    ));

    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(7);
    try module.unregisterFunctionThread();
    _ = try module.emitMainIteration(11);

    const live_plan = try runtime_trace_events_loader.RuntimeTraceEventsLoader.planFor(&module);
    const live_snapshot = runtime_trace_events_loader.registrationSnapshot(live_plan);
    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);
    const pending_snapshot = runtime_trace_events_loader.registrationSnapshot(loader.cached_plan.?);

    try std.testing.expectEqual(@as(usize, 6), live_snapshot.total_events);
    try std.testing.expectEqual(@as(usize, 4), live_snapshot.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), live_snapshot.fn_thread_events);
    try std.testing.expect(live_snapshot.registration_paths_checked);
    try std.testing.expectEqual(@as(i32, 11), live_snapshot.last_main_count);
    try std.testing.expectEqual(@as(i32, 7), live_snapshot.last_fn_count);
    try std.testing.expectEqual(@as(usize, 0), live_snapshot.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), live_snapshot.selftest_runs);

    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(prepared_plan, pending_plan));
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, pending_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.init_flow.selftest_runs);
    try std.testing.expect(pending_plan.provides_selftest_hook);

    try std.testing.expect(runtime_trace_events_loader.keepsRegistrationSnapshotExplicit(
        loader.cached_plan.?,
        prepared_snapshot,
    ));
    try std.testing.expect(runtime_trace_events_loader.keepsRegistrationSnapshotExplicit(
        loader.cached_plan.?,
        pending_snapshot,
    ));
    try std.testing.expect(!runtime_trace_events_loader.keepsRegistrationSnapshotExplicit(
        loader.cached_plan.?,
        live_snapshot,
    ));
    try std.testing.expectEqual(@as(usize, 0), pending_snapshot.total_events);
    try std.testing.expectEqual(@as(usize, 0), pending_snapshot.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), pending_snapshot.fn_thread_events);
    try std.testing.expect(!pending_snapshot.registration_paths_checked);
    try std.testing.expectEqual(@as(i32, -1), pending_snapshot.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), pending_snapshot.last_fn_count);
    try std.testing.expectEqual(@as(usize, 0), pending_snapshot.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), pending_snapshot.selftest_runs);

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
}

test "phase 9 runtime trace-events loader rejects non-prepared shared requests before any local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = runtime_trace_events_loader.RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    _ = try shared_request.requestRuntimeLoad();

    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        shared_request.plan,
    ));

    try std.testing.expectError(error.InvalidLoaderState, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        shared_request.plan,
    ));
}

test "phase 9 runtime trace-events loader rejects idle shared-loader handoff before any local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var prepared_loader = runtime_trace_events_loader.RuntimeTraceEventsLoader{};
    var shared_request = try prepared_loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, prepared_loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));

    var idle_loader = runtime_trace_events_loader.RuntimeTraceEventsLoader{};
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.idle, idle_loader.stage());

    try std.testing.expectError(error.InvalidLoaderState, idle_loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.idle, idle_loader.stage());
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, prepared_loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
}

test "phase 9 runtime trace-events loader keeps selftest-complete shared-request snapshots stable across later exit activity" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = runtime_trace_events_loader.RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    const prepared_plan = shared_request.plan;
    const selftested_summary = module.summary();
    try std.testing.expect(prepared_plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, prepared_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), prepared_plan.init_flow.selftest_runs);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_plan,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(prepared_plan));
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.selftest_complete, selftested_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftested_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), selftested_summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 6), selftested_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), selftested_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), selftested_summary.total_events);
    try std.testing.expect(selftested_summary.saw_conditional_path);

    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectEqual(selftested_summary.main_thread_events, exited_summary.main_thread_events);
    try std.testing.expectEqual(selftested_summary.fn_thread_events, exited_summary.fn_thread_events);
    try std.testing.expectEqual(selftested_summary.total_events, exited_summary.total_events);
    try std.testing.expectEqual(selftested_summary.last_main_count, exited_summary.last_main_count);
    try std.testing.expectEqual(selftested_summary.last_fn_count, exited_summary.last_fn_count);
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, runtime_trace_events_loader.RuntimeTraceEventsLoader.planFor(&module));

    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);

    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));
    try std.testing.expectEqualStrings(prepared_plan.module_name, pending_plan.module_name);
    try std.testing.expectEqualStrings(prepared_plan.anchor, pending_plan.anchor);
    try std.testing.expectEqualStrings(prepared_plan.entry_symbol, pending_plan.entry_symbol);
    try std.testing.expectEqualStrings(prepared_plan.exit_symbol, pending_plan.exit_symbol);
    try std.testing.expect(pending_plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, pending_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), pending_plan.init_flow.selftest_runs);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        pending_plan,
        .caller_provided,
        .{
            .handoff_stage = .selftest_complete,
            .init_runs = 1,
            .selftest_runs = 1,
            .exit_runs = 0,
        },
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending_plan));

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
}
