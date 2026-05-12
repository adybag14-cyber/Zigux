const std = @import("std");
const runtime_trace_events_sample = @import("runtime_trace_events_sample");
const runtime_loader = @import("runtime_loader");

const trace_event_families = [_]runtime_trace_events_sample.EventFamily{
    .foo_bar,
    .template,
    .conditional,
    .relative_location,
    .function_callback,
};

const empty_trace_event_families = [_]runtime_trace_events_sample.EventFamily{};

pub const LoaderStage = enum(u8) {
    idle,
    prepared,
    waiting_on_runtime_substrate,
    released_without_substrate,
};

pub const RuntimeTraceEventsLoadSummary = struct {
    anchor: []const u8,
    event_families: []const runtime_trace_events_sample.EventFamily,
    main_thread_events: usize,
    fn_thread_events: usize,
    total_events: usize,
    conditional_paths_checked: bool,
    registration_paths_checked: bool,
    last_main_count: i32,
    last_fn_count: i32,
    registration_depth: usize,
    selftest_runs: usize,
};

pub const RuntimeTraceEventsLoadPlan = struct {
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    register_api: []const u8,
    unregister_api: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
    handoff_stage: runtime_trace_events_sample.ModuleStage,
    summary: RuntimeTraceEventsLoadSummary,
};

pub const RuntimeTraceEventsRegistrationSnapshot = struct {
    register_api: []const u8,
    unregister_api: []const u8,
    main_thread_events: usize,
    fn_thread_events: usize,
    total_events: usize,
    conditional_paths_checked: bool,
    registration_paths_checked: bool,
    last_main_count: i32,
    last_fn_count: i32,
    registration_depth: usize,
    selftest_runs: usize,
};

fn sharedHandoffStage(stage: runtime_trace_events_sample.ModuleStage) runtime_loader.HandoffStage {
    return switch (stage) {
        .initialized => .initialized,
        .selftest_complete => .selftest_complete,
        else => unreachable,
    };
}

fn ensureIdleRegistrationSnapshot(summary: RuntimeTraceEventsLoadSummary) !void {
    if (summary.registration_depth != 0) {
        return error.OutstandingRegistrationForLoader;
    }
}

pub fn toSharedLoadPlan(plan: RuntimeTraceEventsLoadPlan) runtime_loader.LoadPlan {
    return .{
        .module_name = plan.module_name,
        .anchor = plan.anchor,
        .entry_symbol = plan.entry_symbol,
        .exit_symbol = plan.exit_symbol,
        .requires_runtime_substrate = plan.requires_runtime_substrate,
        .provides_selftest_hook = plan.provides_selftest_hook,
        .allocator_handoff = .caller_provided,
        .init_flow = .{
            .handoff_stage = sharedHandoffStage(plan.handoff_stage),
            .init_runs = 1,
            .selftest_runs = plan.summary.selftest_runs,
            .exit_runs = 0,
        },
    };
}

pub fn registrationSnapshot(plan: RuntimeTraceEventsLoadPlan) RuntimeTraceEventsRegistrationSnapshot {
    return .{
        .register_api = plan.register_api,
        .unregister_api = plan.unregister_api,
        .main_thread_events = plan.summary.main_thread_events,
        .fn_thread_events = plan.summary.fn_thread_events,
        .total_events = plan.summary.total_events,
        .conditional_paths_checked = plan.summary.conditional_paths_checked,
        .registration_paths_checked = plan.summary.registration_paths_checked,
        .last_main_count = plan.summary.last_main_count,
        .last_fn_count = plan.summary.last_fn_count,
        .registration_depth = plan.summary.registration_depth,
        .selftest_runs = plan.summary.selftest_runs,
    };
}

pub fn keepsRegistrationSnapshotExplicit(
    plan: RuntimeTraceEventsLoadPlan,
    snapshot: RuntimeTraceEventsRegistrationSnapshot,
) bool {
    return std.mem.eql(u8, snapshot.register_api, plan.register_api) and
        std.mem.eql(u8, snapshot.unregister_api, plan.unregister_api) and
        snapshot.main_thread_events == plan.summary.main_thread_events and
        snapshot.fn_thread_events == plan.summary.fn_thread_events and
        snapshot.total_events == plan.summary.total_events and
        snapshot.conditional_paths_checked == plan.summary.conditional_paths_checked and
        snapshot.registration_paths_checked == plan.summary.registration_paths_checked and
        snapshot.last_main_count == plan.summary.last_main_count and
        snapshot.last_fn_count == plan.summary.last_fn_count and
        snapshot.registration_depth == plan.summary.registration_depth and
        snapshot.selftest_runs == plan.summary.selftest_runs;
}

pub fn keepsSharedLoadPlanSnapshotExplicit(
    plan: RuntimeTraceEventsLoadPlan,
    shared_plan: runtime_loader.LoadPlan,
) bool {
    return std.mem.eql(u8, shared_plan.module_name, plan.module_name) and
        std.mem.eql(u8, shared_plan.anchor, plan.anchor) and
        std.mem.eql(u8, shared_plan.entry_symbol, plan.entry_symbol) and
        std.mem.eql(u8, shared_plan.exit_symbol, plan.exit_symbol) and
        shared_plan.requires_runtime_substrate == plan.requires_runtime_substrate and
        shared_plan.provides_selftest_hook == plan.provides_selftest_hook and
        shared_plan.allocator_handoff == .caller_provided and
        shared_plan.init_flow.handoff_stage == sharedHandoffStage(plan.handoff_stage) and
        shared_plan.init_flow.init_runs == 1 and
        shared_plan.init_flow.selftest_runs == plan.summary.selftest_runs and
        shared_plan.init_flow.exit_runs == 0;
}

pub const RuntimeTraceEventsLoader = struct {
    const Self = @This();

    stage_state: LoaderStage = .idle,
    cached_plan: ?RuntimeTraceEventsLoadPlan = null,

    pub fn stage(self: *const Self) LoaderStage {
        return self.stage_state;
    }

    fn buildSummary(module: *const runtime_trace_events_sample.RuntimeTraceEventsSample) RuntimeTraceEventsLoadSummary {
        return .{
            .anchor = runtime_trace_events_sample.RuntimeTraceEventsSample.descriptor().anchor,
            .event_families = switch (module.stage()) {
                .initialized => empty_trace_event_families[0..],
                .selftest_complete => trace_event_families[0..],
                else => unreachable,
            },
            .main_thread_events = module.main_iterations * 6,
            .fn_thread_events = module.fn_iterations * 2,
            .total_events = module.total_events,
            .conditional_paths_checked = module.saw_conditional_path,
            .registration_paths_checked = module.fn_iterations > 0 and module.registration_depth == 0,
            .last_main_count = module.last_main_count,
            .last_fn_count = module.last_fn_count,
            .registration_depth = module.registration_depth,
            .selftest_runs = module.selftest_runs,
        };
    }

    pub fn planFor(module: *const runtime_trace_events_sample.RuntimeTraceEventsSample) !RuntimeTraceEventsLoadPlan {
        const descriptor = runtime_trace_events_sample.RuntimeTraceEventsSample.descriptor();
        const module_stage = module.stage();
        switch (module_stage) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidModuleLifecycleForLoader,
        }

        if (!descriptor.requires_runtime_substrate) return error.LoaderNotRequired;
        const summary = buildSummary(module);
        try ensureIdleRegistrationSnapshot(summary);

        return .{
            .module_name = descriptor.name,
            .anchor = descriptor.anchor,
            .entry_symbol = "zigux_runtime_trace_events_init",
            .exit_symbol = "zigux_runtime_trace_events_exit",
            .register_api = "tracepoint_probe_register",
            .unregister_api = "tracepoint_probe_unregister",
            .requires_runtime_substrate = descriptor.requires_runtime_substrate,
            .provides_selftest_hook = descriptor.provides_selftest_hook,
            .handoff_stage = module_stage,
            .summary = summary,
        };
    }

    pub fn prepare(self: *Self, module: *const runtime_trace_events_sample.RuntimeTraceEventsSample) !RuntimeTraceEventsLoadPlan {
        if (self.stage_state != .idle) return error.LoaderAlreadyPrepared;

        const plan = try planFor(module);
        self.cached_plan = plan;
        self.stage_state = .prepared;
        return plan;
    }

    pub fn prepareSharedRequest(self: *Self, module: *const runtime_trace_events_sample.RuntimeTraceEventsSample) !runtime_loader.PreparedRequest {
        const plan = try self.prepare(module);
        return runtime_loader.prepareRequest(toSharedLoadPlan(plan));
    }

    pub fn requestRuntimeLoad(self: *Self) !RuntimeTraceEventsLoadPlan {
        if (self.stage_state != .prepared) return error.InvalidLoaderState;

        self.stage_state = .waiting_on_runtime_substrate;
        return self.cached_plan orelse error.MissingLoadPlan;
    }

    pub fn requestSharedRuntimeLoad(
        self: *Self,
        shared_request: *runtime_loader.PreparedRequest,
    ) !runtime_loader.LoadPlan {
        if (self.stage_state != .prepared) return error.InvalidLoaderState;
        if (shared_request.state != .prepared) return error.InvalidLoaderState;
        if (!runtime_loader.keepsLoadPlanExplicit(shared_request.plan, shared_request.prepared_plan)) {
            return error.PreparedPlanDrift;
        }
        _ = try runtime_loader.prepareRequest(shared_request.plan);

        const plan = self.cached_plan orelse return error.MissingLoadPlan;
        if (!keepsSharedLoadPlanSnapshotExplicit(plan, shared_request.plan)) {
            return error.SharedLoadPlanDrift;
        }

        _ = try self.requestRuntimeLoad();
        return shared_request.requestRuntimeLoad();
    }

    pub fn releaseWithoutSubstrate(self: *Self) !void {
        if (self.stage_state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
        self.stage_state = .released_without_substrate;
    }

    pub fn releaseSharedWithoutSubstrate(
        self: *Self,
        shared_request: *runtime_loader.PreparedRequest,
    ) !void {
        if (self.stage_state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
        try shared_request.releaseWithoutSubstrate();
        self.stage_state = .released_without_substrate;
    }
};

test "runtime trace-events loader prepares a bounded registration handoff plan" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    const selftest = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    const plan = try loader.prepare(&module);
    const snapshot = registrationSnapshot(plan);

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqualStrings("runtime_trace_events", plan.module_name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_trace_events_init", plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_trace_events_exit", plan.exit_symbol);
    try std.testing.expectEqualStrings("tracepoint_probe_register", plan.register_api);
    try std.testing.expectEqualStrings("tracepoint_probe_unregister", plan.unregister_api);
    try std.testing.expect(plan.requires_runtime_substrate);
    try std.testing.expect(plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.selftest_complete, plan.handoff_stage);
    try std.testing.expectEqual(@as(usize, 5), selftest.event_families.len);
    try std.testing.expectEqual(@as(usize, 6), plan.summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), plan.summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), plan.summary.total_events);
    try std.testing.expect(plan.summary.conditional_paths_checked);
    try std.testing.expect(plan.summary.registration_paths_checked);
    try std.testing.expectEqual(@as(i32, 0), plan.summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), plan.summary.last_fn_count);
    try std.testing.expectEqual(@as(usize, 0), plan.summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.selftest_runs);
    try std.testing.expect(keepsRegistrationSnapshotExplicit(plan, snapshot));
    try std.testing.expectEqualStrings("tracepoint_probe_register", snapshot.register_api);
    try std.testing.expectEqualStrings("tracepoint_probe_unregister", snapshot.unregister_api);
    try std.testing.expectEqual(@as(usize, 8), snapshot.total_events);
    try std.testing.expectEqual(@as(usize, 0), snapshot.registration_depth);
}

test "runtime trace-events loader keeps unavailable substrate and lifecycle guards explicit" {
    var cold_module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeTraceEventsLoader.planFor(&cold_module));

    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();

    var loader = RuntimeTraceEventsLoader{};
    const prepared = try loader.prepare(&module);
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.initialized, prepared.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.event_families.len);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.total_events);
    try std.testing.expect(!prepared.summary.conditional_paths_checked);
    try std.testing.expect(!prepared.summary.registration_paths_checked);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.selftest_runs);

    try std.testing.expectError(error.LoaderAlreadyPrepared, loader.prepare(&module));

    const pending_plan = try loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.initialized, pending_plan.handoff_stage);

    try loader.releaseWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectError(error.InvalidLoaderState, loader.requestRuntimeLoad());

    try module.exit();
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeTraceEventsLoader.planFor(&module));
}

test "runtime trace-events loader keeps the prepared snapshot stable across later sample mutation" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    const prepared = try loader.prepare(&module);
    const prepared_snapshot = registrationSnapshot(prepared);

    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(5);
    try module.unregisterFunctionThread();
    _ = try module.emitMainIteration(11);

    const live_summary = RuntimeTraceEventsLoader.buildSummary(&module);
    const pending_plan = try loader.requestRuntimeLoad();
    const pending_snapshot = registrationSnapshot(pending_plan);

    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(@as(usize, 16), live_summary.total_events);
    try std.testing.expectEqual(@as(usize, 8), pending_plan.summary.total_events);
    try std.testing.expectEqual(@as(usize, 12), live_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 6), pending_plan.summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), live_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 2), pending_plan.summary.fn_thread_events);
    try std.testing.expectEqual(@as(i32, 11), live_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 0), pending_plan.summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 5), live_summary.last_fn_count);
    try std.testing.expectEqual(@as(i32, 1), pending_plan.summary.last_fn_count);
    try std.testing.expectEqual(@as(usize, 1), live_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), pending_plan.summary.selftest_runs);
    try std.testing.expect(keepsRegistrationSnapshotExplicit(pending_plan, prepared_snapshot));
    try std.testing.expect(keepsRegistrationSnapshotExplicit(pending_plan, pending_snapshot));
    try std.testing.expectEqualStrings("tracepoint_probe_register", prepared_snapshot.register_api);
    try std.testing.expectEqualStrings("tracepoint_probe_register", pending_snapshot.register_api);
    try std.testing.expectEqual(@as(usize, 8), prepared_snapshot.total_events);
    try std.testing.expectEqual(@as(usize, 8), pending_snapshot.total_events);
    try std.testing.expectEqual(@as(i32, 0), prepared_snapshot.last_main_count);
    try std.testing.expectEqual(@as(i32, 0), pending_snapshot.last_main_count);
}

test "runtime trace-events loader emits the shared runtime-loader contract plan" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    const plan = try loader.prepare(&module);
    const shared_plan = toSharedLoadPlan(plan);

    try std.testing.expect(keepsSharedLoadPlanSnapshotExplicit(plan, shared_plan));
    try std.testing.expect(shared_plan.provides_selftest_hook);
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(shared_plan));
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.caller_provided, shared_plan.allocator_handoff);
    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, shared_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), shared_plan.init_flow.init_runs);
    try std.testing.expectEqual(@as(usize, 1), shared_plan.init_flow.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), shared_plan.init_flow.exit_runs);

    var shared_request = try runtime_loader.prepareRequest(shared_plan);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_plan,
    ));

    const pending_plan = try shared_request.requestRuntimeLoad();
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));
    try std.testing.expect(keepsSharedLoadPlanSnapshotExplicit(plan, pending_plan));
    try std.testing.expect(pending_plan.provides_selftest_hook);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        pending_plan,
        .caller_provided,
        shared_plan.init_flow,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending_plan));

    try shared_request.releaseWithoutSubstrate();
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
}

test "runtime trace-events loader keeps initialized-stage shared contract plans explicit" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();

    var loader = RuntimeTraceEventsLoader{};
    const plan = try loader.prepare(&module);
    const shared_plan = toSharedLoadPlan(plan);

    try std.testing.expectEqual(@as(usize, 0), plan.summary.event_families.len);
    try std.testing.expect(keepsSharedLoadPlanSnapshotExplicit(plan, shared_plan));
    try std.testing.expect(shared_plan.provides_selftest_hook);
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(shared_plan));
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, shared_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), shared_plan.init_flow.selftest_runs);

    var shared_request = try runtime_loader.prepareRequest(shared_plan);
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_plan,
    ));

    const pending_plan = try shared_request.requestRuntimeLoad();
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));
    try std.testing.expect(keepsSharedLoadPlanSnapshotExplicit(plan, pending_plan));
    try std.testing.expect(pending_plan.provides_selftest_hook);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        pending_plan,
        .caller_provided,
        shared_plan.init_flow,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending_plan));
}

test "runtime trace-events loader keeps initialized shared-request snapshots stable across later selftest activity" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();

    var loader = RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    const prepared_plan = shared_request.plan;
    try std.testing.expect(prepared_plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, prepared_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), prepared_plan.init_flow.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), loader.cached_plan.?.summary.event_families.len);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        prepared_plan,
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(prepared_plan));

    const selftest = try module.runSelftest();
    const live_plan = try RuntimeTraceEventsLoader.planFor(&module);
    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);

    try std.testing.expectEqual(@as(usize, 5), selftest.event_families.len);
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.selftest_complete, live_plan.handoff_stage);
    try std.testing.expectEqual(@as(usize, 5), live_plan.summary.event_families.len);
    try std.testing.expectEqual(@as(usize, 1), live_plan.summary.selftest_runs);
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
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
    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, pending_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.init_flow.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), loader.cached_plan.?.summary.event_families.len);
    try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(
        pending_plan,
        .caller_provided,
        .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    ));
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending_plan));

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
}

test "runtime trace-events loader keeps selftest-complete shared-request snapshots stable across later exit activity" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
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
    try std.testing.expectEqual(@as(usize, 0), selftested_summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 6), selftested_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), selftested_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), selftested_summary.total_events);
    try std.testing.expectEqual(@as(usize, 1), selftested_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftested_summary.exit_runs);
    try std.testing.expectEqual(@as(i32, 0), selftested_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), selftested_summary.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", selftested_summary.last_register_label orelse unreachable);
    try std.testing.expectEqualStrings("foo_bar_unreg", selftested_summary.last_unregister_label orelse unreachable);

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
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeTraceEventsLoader.planFor(&module));

    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);

    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
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
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
}

test "runtime trace-events loader bridges the shared request lifecycle without widening registration claims" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));

    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .waiting_on_runtime_substrate,
        pending_plan,
    ));
    try std.testing.expectEqualStrings("runtime_trace_events", pending_plan.module_name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", pending_plan.anchor);
    try std.testing.expect(pending_plan.provides_selftest_hook);
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
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .released_without_substrate,
        pending_plan,
    ));
}

test "runtime trace-events loader keeps shared release failures from desynchronizing loader state" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    _ = try loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    try std.testing.expectError(error.InvalidLoaderState, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    try std.testing.expectError(error.InvalidLoaderState, loader.releaseSharedWithoutSubstrate(&shared_request));
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    _ = try shared_request.requestRuntimeLoad();
    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
}

test "runtime trace-events loader rejects prepared shared allocator and init-flow drift before any local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var allocator_loader = RuntimeTraceEventsLoader{};
    var allocator_request = try allocator_loader.prepareSharedRequest(&module);
    const prepared_allocator_plan = allocator_request.plan;
    try std.testing.expectEqual(LoaderStage.prepared, allocator_loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, allocator_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        allocator_request,
        .prepared,
        allocator_request.plan,
    ));
    allocator_request.plan.allocator_handoff = .arena;

    try std.testing.expectError(error.PreparedPlanDrift, allocator_loader.requestSharedRuntimeLoad(&allocator_request));
    try std.testing.expectEqual(LoaderStage.prepared, allocator_loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, allocator_request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(
        allocator_request.prepared_plan,
        prepared_allocator_plan,
    ));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(
        allocator_request.plan,
        prepared_allocator_plan,
    ));

    var init_flow_loader = RuntimeTraceEventsLoader{};
    var init_flow_request = try init_flow_loader.prepareSharedRequest(&module);
    const prepared_init_flow_plan = init_flow_request.plan;
    try std.testing.expectEqual(LoaderStage.prepared, init_flow_loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, init_flow_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        init_flow_request,
        .prepared,
        init_flow_request.plan,
    ));
    init_flow_request.plan.init_flow.handoff_stage = .initialized;
    init_flow_request.plan.init_flow.selftest_runs = 0;

    try std.testing.expectError(error.PreparedPlanDrift, init_flow_loader.requestSharedRuntimeLoad(&init_flow_request));
    try std.testing.expectEqual(LoaderStage.prepared, init_flow_loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, init_flow_request.state);
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(
        init_flow_request.prepared_plan,
        prepared_init_flow_plan,
    ));
    try std.testing.expect(!runtime_loader.keepsLoadPlanExplicit(
        init_flow_request.plan,
        prepared_init_flow_plan,
    ));
}

test "runtime trace-events loader rejects prepared shared request drift before any local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
    shared_request.plan.module_name = "runtime_trace_events_drift";

    try std.testing.expectError(error.PreparedPlanDrift, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
}

test "runtime trace-events loader rejects prepared shared selftest-hook drift before any local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
    try std.testing.expect(shared_request.plan.provides_selftest_hook);
    shared_request.plan.provides_selftest_hook = false;
    try std.testing.expect(!runtime_loader.keepsSelftestHookEvidenceConsistent(shared_request.plan));

    try std.testing.expectError(error.InvalidSelftestHookEvidence, loader.requestSharedRuntimeLoad(&shared_request));
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(
        shared_request,
        .prepared,
        shared_request.plan,
    ));
}

test "runtime trace-events loader rejects shared selftest-hook drift before any local runtime handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();

    const initialized_plan = try RuntimeTraceEventsLoader.planFor(&module);
    var initialized_shared_plan = toSharedLoadPlan(initialized_plan);
    try std.testing.expect(initialized_shared_plan.provides_selftest_hook);
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(initialized_shared_plan));

    initialized_shared_plan.provides_selftest_hook = false;
    try std.testing.expect(!runtime_loader.keepsSelftestHookEvidenceConsistent(initialized_shared_plan));
    try std.testing.expectError(
        error.InvalidSelftestHookEvidence,
        runtime_loader.prepareRequest(initialized_shared_plan),
    );

    _ = try module.runSelftest();

    const selftest_plan = try RuntimeTraceEventsLoader.planFor(&module);
    var selftest_shared_plan = toSharedLoadPlan(selftest_plan);
    try std.testing.expect(selftest_shared_plan.provides_selftest_hook);
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(selftest_shared_plan));

    selftest_shared_plan.provides_selftest_hook = false;
    try std.testing.expect(!runtime_loader.keepsSelftestHookEvidenceConsistent(selftest_shared_plan));
    try std.testing.expectError(
        error.InvalidSelftestHookEvidence,
        runtime_loader.prepareRequest(selftest_shared_plan),
    );
}

test "runtime trace-events loader rejects shared-load-plan snapshot drift" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    const plan = try RuntimeTraceEventsLoader.planFor(&module);
    const shared_plan = toSharedLoadPlan(plan);
    try std.testing.expect(keepsSharedLoadPlanSnapshotExplicit(plan, shared_plan));

    var drifted_module = shared_plan;
    drifted_module.module_name = "runtime_trace_events_drift";
    try std.testing.expect(!keepsSharedLoadPlanSnapshotExplicit(plan, drifted_module));

    var drifted_allocator = shared_plan;
    drifted_allocator.allocator_handoff = .kernel_heap;
    try std.testing.expect(!keepsSharedLoadPlanSnapshotExplicit(plan, drifted_allocator));

    var drifted_stage = shared_plan;
    drifted_stage.init_flow.handoff_stage = .initialized;
    try std.testing.expect(!keepsSharedLoadPlanSnapshotExplicit(plan, drifted_stage));

    var drifted_selftest = shared_plan;
    drifted_selftest.init_flow.selftest_runs += 1;
    try std.testing.expect(!keepsSharedLoadPlanSnapshotExplicit(plan, drifted_selftest));
}

test "runtime trace-events loader rejects registration snapshot drift" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    const plan = try RuntimeTraceEventsLoader.planFor(&module);
    const snapshot = registrationSnapshot(plan);
    try std.testing.expect(keepsRegistrationSnapshotExplicit(plan, snapshot));

    var drifted_register_api = snapshot;
    drifted_register_api.register_api = "tracepoint_probe_register_rcu";
    try std.testing.expect(!keepsRegistrationSnapshotExplicit(plan, drifted_register_api));

    var drifted_unregister_api = snapshot;
    drifted_unregister_api.unregister_api = "tracepoint_synchronize_unregister";
    try std.testing.expect(!keepsRegistrationSnapshotExplicit(plan, drifted_unregister_api));

    var drifted_total_events = snapshot;
    drifted_total_events.total_events += 2;
    try std.testing.expect(!keepsRegistrationSnapshotExplicit(plan, drifted_total_events));

    var drifted_main_count = snapshot;
    drifted_main_count.last_main_count += 11;
    try std.testing.expect(!keepsRegistrationSnapshotExplicit(plan, drifted_main_count));
}

test "runtime trace-events loader rejects non-idle registration state at the metadata-only handoff boundary" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    try module.registerFunctionThread();

    try std.testing.expectError(error.OutstandingRegistrationForLoader, RuntimeTraceEventsLoader.planFor(&module));

    try module.unregisterFunctionThread();
    const recovered_plan = try RuntimeTraceEventsLoader.planFor(&module);
    try std.testing.expectEqual(@as(usize, 0), recovered_plan.summary.registration_depth);
    try std.testing.expect(!recovered_plan.summary.registration_paths_checked);
}

test "runtime trace-events loader keeps selftest-ready single registration drain explicit before shared handoff" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    try module.registerFunctionThread();
    try std.testing.expectError(error.FunctionThreadAlreadyRegistered, module.registerFunctionThread());
    _ = try module.emitFunctionIteration(9);

    try std.testing.expectError(error.OutstandingRegistrationForLoader, RuntimeTraceEventsLoader.planFor(&module));

    var blocked_loader = RuntimeTraceEventsLoader{};
    try std.testing.expectError(error.OutstandingRegistrationForLoader, blocked_loader.prepare(&module));

    try module.unregisterFunctionThread();

    var loader = RuntimeTraceEventsLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);

    const recovered_plan = try RuntimeTraceEventsLoader.planFor(&module);
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.selftest_complete, recovered_plan.handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), recovered_plan.summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 5), recovered_plan.summary.event_families.len);
    try std.testing.expectEqual(@as(usize, 6), recovered_plan.summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), recovered_plan.summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 10), recovered_plan.summary.total_events);
    try std.testing.expect(recovered_plan.summary.conditional_paths_checked);
    try std.testing.expect(recovered_plan.summary.registration_paths_checked);
    try std.testing.expectEqual(@as(i32, 0), recovered_plan.summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 9), recovered_plan.summary.last_fn_count);
    try std.testing.expectEqual(@as(usize, 1), recovered_plan.summary.selftest_runs);

    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expectEqualStrings("runtime_trace_events", pending_plan.module_name);
    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, pending_plan.init_flow.handoff_stage);
    try std.testing.expectEqual(@as(usize, 1), pending_plan.init_flow.selftest_runs);
    try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending_plan));

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
}
