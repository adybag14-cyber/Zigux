const std = @import("std");
const runtime_trace_events_sample = @import("runtime_trace_events_sample");
const runtime_loader = @import("runtime_loader");

pub const LoaderStage = runtime_loader.LoaderStage;

pub const RuntimeTraceEventsLoadPlan = struct {
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    register_api: []const u8,
    unregister_api: []const u8,
    main_thread_label: []const u8,
    function_thread_label: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
    handoff_stage: runtime_trace_events_sample.ModuleStage,
    summary: runtime_trace_events_sample.RuntimeTraceEventsSummary,
};

pub const RuntimeTraceEventsLoader = struct {
    const Self = @This();

    stage_state: LoaderStage = .idle,
    cached_plan: ?RuntimeTraceEventsLoadPlan = null,

    pub fn stage(self: *const Self) LoaderStage {
        return self.stage_state;
    }

    pub fn planFor(
        module: *const runtime_trace_events_sample.RuntimeTraceEventsSample,
    ) !RuntimeTraceEventsLoadPlan {
        const descriptor = runtime_trace_events_sample.RuntimeTraceEventsSample.descriptor();
        const module_stage = module.stage();
        switch (module_stage) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidModuleLifecycleForLoader,
        }

        if (!descriptor.requires_runtime_substrate) return error.LoaderNotRequired;

        const summary = module.summary();
        return .{
            .module_name = descriptor.name,
            .anchor = descriptor.anchor,
            .entry_symbol = "zigux_runtime_trace_events_init",
            .exit_symbol = "zigux_runtime_trace_events_exit",
            .register_api = "foo_bar_reg",
            .unregister_api = "foo_bar_unreg",
            .main_thread_label = summary.main_thread_label orelse "event-sample",
            .function_thread_label = summary.function_thread_label orelse "event-sample-fn",
            .requires_runtime_substrate = descriptor.requires_runtime_substrate,
            .provides_selftest_hook = descriptor.provides_selftest_hook,
            .handoff_stage = module_stage,
            .summary = summary,
        };
    }

    pub fn prepare(
        self: *Self,
        module: *const runtime_trace_events_sample.RuntimeTraceEventsSample,
    ) !RuntimeTraceEventsLoadPlan {
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

    pub fn releasePlanWithoutSubstrate(self: *Self) !RuntimeTraceEventsLoadPlan {
        const plan = self.cached_plan orelse error.MissingLoadPlan;
        try self.releaseWithoutSubstrate();
        return plan;
    }

    pub fn releaseWithoutSubstrate(self: *Self) !void {
        if (self.stage_state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
        self.stage_state = .released_without_substrate;
    }
};

test "runtime trace-events loader prepares a bounded registration handoff plan" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    const plan = try loader.prepare(&module);

    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqualStrings("runtime_trace_events", plan.module_name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_trace_events_init", plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_trace_events_exit", plan.exit_symbol);
    try std.testing.expectEqualStrings("foo_bar_reg", plan.register_api);
    try std.testing.expectEqualStrings("foo_bar_unreg", plan.unregister_api);
    try std.testing.expectEqualStrings("event-sample", plan.main_thread_label);
    try std.testing.expectEqualStrings("event-sample-fn", plan.function_thread_label);
    try std.testing.expect(plan.requires_runtime_substrate);
    try std.testing.expect(plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.selftest_complete, plan.handoff_stage);
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.selftest_complete, plan.summary.stage);
    try std.testing.expectEqual(@as(usize, 0), plan.summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 6), plan.summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), plan.summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), plan.summary.total_events);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), plan.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), plan.summary.exit_runs);
    try std.testing.expectEqualStrings("foo_bar_reg", plan.summary.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", plan.summary.last_unregister_label orelse return error.ExpectedFunctionPayload);
}

test "runtime trace-events loader keeps unavailable substrate and lifecycle guards explicit" {
    var cold_module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeTraceEventsLoader.planFor(&cold_module));

    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();

    var loader = RuntimeTraceEventsLoader{};
    const prepared = try loader.prepare(&module);
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.initialized, prepared.handoff_stage);
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.initialized, prepared.summary.stage);
    try std.testing.expectEqual(@as(usize, 1), prepared.summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.exit_runs);

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

test "runtime trace-events loader snapshots the prepared summary before later sample mutation" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();

    var loader = RuntimeTraceEventsLoader{};
    const prepared = try loader.prepare(&module);

    _ = try module.emitMainIteration(7);
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(9);

    const mutated_summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), mutated_summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 4), mutated_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), mutated_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 6), mutated_summary.total_events);
    try std.testing.expectEqualStrings("foo_bar_reg", mutated_summary.last_register_label orelse return error.ExpectedFunctionPayload);

    const pending_plan = try loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.initialized, prepared.handoff_stage);
    try std.testing.expectEqual(prepared.handoff_stage, pending_plan.handoff_stage);
    try std.testing.expectEqual(prepared.summary.registration_depth, pending_plan.summary.registration_depth);
    try std.testing.expectEqual(prepared.summary.main_thread_events, pending_plan.summary.main_thread_events);
    try std.testing.expectEqual(prepared.summary.fn_thread_events, pending_plan.summary.fn_thread_events);
    try std.testing.expectEqual(prepared.summary.total_events, pending_plan.summary.total_events);
    try std.testing.expectEqual(prepared.summary.last_main_count, pending_plan.summary.last_main_count);
    try std.testing.expectEqual(prepared.summary.last_fn_count, pending_plan.summary.last_fn_count);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.total_events);
    try std.testing.expectEqual(@as(i32, -1), pending_plan.summary.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), pending_plan.summary.last_fn_count);
}

test "runtime trace-events loader keeps the release-without-substrate fallback explicit" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    _ = try loader.prepare(&module);
    _ = try loader.requestRuntimeLoad();

    const released_plan = try loader.releasePlanWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqualStrings("runtime_trace_events", released_plan.module_name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", released_plan.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_trace_events_init", released_plan.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_trace_events_exit", released_plan.exit_symbol);
    try std.testing.expectEqualStrings("foo_bar_reg", released_plan.register_api);
    try std.testing.expectEqualStrings("foo_bar_unreg", released_plan.unregister_api);
    try std.testing.expectEqualStrings("event-sample", released_plan.main_thread_label);
    try std.testing.expectEqualStrings("event-sample-fn", released_plan.function_thread_label);
    try std.testing.expect(released_plan.requires_runtime_substrate);
    try std.testing.expect(released_plan.provides_selftest_hook);
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.selftest_complete, released_plan.handoff_stage);
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.selftest_complete, released_plan.summary.stage);
    try std.testing.expectEqual(@as(usize, 0), released_plan.summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 6), released_plan.summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), released_plan.summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), released_plan.summary.total_events);
    try std.testing.expectEqual(@as(usize, 1), released_plan.summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), released_plan.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), released_plan.summary.exit_runs);
    try std.testing.expectEqualStrings("foo_bar_reg", released_plan.summary.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", released_plan.summary.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectError(error.InvalidLoaderState, loader.requestRuntimeLoad());
    try std.testing.expectError(error.InvalidLoaderState, loader.releasePlanWithoutSubstrate());
}
