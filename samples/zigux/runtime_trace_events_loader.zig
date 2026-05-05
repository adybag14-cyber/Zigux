const std = @import("std");
const runtime_trace_events_sample = @import("runtime_trace_events_sample");

const trace_event_families = [_]runtime_trace_events_sample.EventFamily{
    .foo_bar,
    .template,
    .conditional,
    .relative_location,
    .function_callback,
};

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
            .event_families = trace_event_families[0..],
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
            .summary = buildSummary(module),
        };
    }

    pub fn prepare(self: *Self, module: *const runtime_trace_events_sample.RuntimeTraceEventsSample) !RuntimeTraceEventsLoadPlan {
        if (self.stage_state != .idle) return error.LoaderAlreadyPrepared;

        const plan = try planFor(module);
        self.cached_plan = plan;
        self.stage_state = .prepared;
        return plan;
    }

    pub fn requestRuntimeLoad(self: *Self) !RuntimeTraceEventsLoadPlan {
        if (self.stage_state != .prepared) return error.InvalidLoaderState;

        self.stage_state = .waiting_on_runtime_substrate;
        return self.cached_plan orelse error.MissingLoadPlan;
    }

    pub fn releaseWithoutSubstrate(self: *Self) !void {
        if (self.stage_state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
        self.stage_state = .released_without_substrate;
    }
};

test "runtime trace-events loader prepares a bounded registration handoff plan" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    const selftest = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    const plan = try loader.prepare(&module);

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
}

test "runtime trace-events loader keeps unavailable substrate and lifecycle guards explicit" {
    var cold_module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeTraceEventsLoader.planFor(&cold_module));

    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();

    var loader = RuntimeTraceEventsLoader{};
    const prepared = try loader.prepare(&module);
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.initialized, prepared.handoff_stage);
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

    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(5);
    try module.unregisterFunctionThread();
    _ = try module.emitMainIteration(11);

    const live_summary = RuntimeTraceEventsLoader.buildSummary(&module);
    const pending_plan = try loader.requestRuntimeLoad();

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

    _ = prepared;
}
