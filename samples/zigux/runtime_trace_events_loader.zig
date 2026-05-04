const std = @import("std");
const runtime_trace_events_sample = @import("runtime_trace_events_sample");
const runtime_loader = @import("runtime_loader");

pub const LoaderStage = runtime_loader.LoaderStage;

pub const RuntimeTraceEventsLoadPlan = struct {
    module_name: []const u8,
    command_name: ?[]const u8,
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
            .command_name = null,
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

    pub fn withCommandName(
        plan: RuntimeTraceEventsLoadPlan,
        command_name: ?[]const u8,
    ) !RuntimeTraceEventsLoadPlan {
        if (command_name) |value| {
            if (value.len == 0) return error.InvalidCommandName;
        }

        var updated = plan;
        updated.command_name = command_name;
        return updated;
    }

    pub fn prepare(
        self: *Self,
        module: *const runtime_trace_events_sample.RuntimeTraceEventsSample,
    ) !RuntimeTraceEventsLoadPlan {
        return self.prepareWithCommandName(module, null);
    }

    pub fn prepareWithCommandName(
        self: *Self,
        module: *const runtime_trace_events_sample.RuntimeTraceEventsSample,
        command_name: ?[]const u8,
    ) !RuntimeTraceEventsLoadPlan {
        if (self.stage_state != .idle) return error.LoaderAlreadyPrepared;

        const plan = try withCommandName(try planFor(module), command_name);
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
        if (self.stage_state == .idle) return error.MissingLoadPlan;
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
    try std.testing.expectEqual(@as(?[]const u8, null), plan.command_name);
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

test "runtime trace-events loader keeps the released fallback snapshot stable after request-time replay" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    const prepared = try loader.prepare(&module);
    const pending_plan = try loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.selftest_complete, pending_plan.handoff_stage);
    try std.testing.expectEqual(@as(usize, 6), pending_plan.summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), pending_plan.summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), pending_plan.summary.total_events);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), pending_plan.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), pending_plan.summary.exit_runs);
    try std.testing.expectEqualStrings("foo_bar_reg", pending_plan.summary.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", pending_plan.summary.last_unregister_label orelse return error.ExpectedFunctionPayload);

    const replayed_main = try module.emitMainIteration(5);
    try std.testing.expectEqual(@as(usize, 4), replayed_main);
    try module.registerFunctionThread();
    const replayed_fn = try module.emitFunctionIteration(13);
    try std.testing.expectEqual(@as(usize, 2), replayed_fn);

    const mutated_summary = module.summary();
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.selftest_complete, mutated_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), mutated_summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), mutated_summary.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), mutated_summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), mutated_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), mutated_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), mutated_summary.total_events);
    try std.testing.expectEqual(@as(i32, 5), mutated_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 13), mutated_summary.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", mutated_summary.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", mutated_summary.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Mother Goose", mutated_summary.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", mutated_summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);

    const released_plan = try loader.releasePlanWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqual(prepared.handoff_stage, released_plan.handoff_stage);
    try std.testing.expectEqual(pending_plan.handoff_stage, released_plan.handoff_stage);
    try std.testing.expectEqual(prepared.summary.registration_depth, released_plan.summary.registration_depth);
    try std.testing.expectEqual(prepared.summary.main_iterations, released_plan.summary.main_iterations);
    try std.testing.expectEqual(prepared.summary.fn_iterations, released_plan.summary.fn_iterations);
    try std.testing.expectEqual(prepared.summary.main_thread_events, released_plan.summary.main_thread_events);
    try std.testing.expectEqual(prepared.summary.fn_thread_events, released_plan.summary.fn_thread_events);
    try std.testing.expectEqual(prepared.summary.total_events, released_plan.summary.total_events);
    try std.testing.expectEqual(prepared.summary.last_main_count, released_plan.summary.last_main_count);
    try std.testing.expectEqual(prepared.summary.last_fn_count, released_plan.summary.last_fn_count);
    try std.testing.expectEqual(prepared.summary.selftest_runs, released_plan.summary.selftest_runs);
    try std.testing.expectEqual(prepared.summary.exit_runs, released_plan.summary.exit_runs);
    try std.testing.expectEqualStrings(prepared.summary.main_thread_label orelse return error.ExpectedFunctionPayload, released_plan.summary.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(prepared.summary.function_thread_label orelse return error.ExpectedFunctionPayload, released_plan.summary.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(prepared.summary.last_register_label orelse return error.ExpectedFunctionPayload, released_plan.summary.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(prepared.summary.last_unregister_label orelse return error.ExpectedFunctionPayload, released_plan.summary.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(prepared.summary.last_main_foo_bar_message orelse return error.ExpectedMainPayload, released_plan.summary.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(prepared.summary.last_main_random_choice_message orelse return error.ExpectedMainPayload, released_plan.summary.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(prepared.summary.last_main_vararg_array_length, released_plan.summary.last_main_vararg_array_length);
    try std.testing.expectEqual(prepared.summary.last_main_vararg_array_terminator_zero, released_plan.summary.last_main_vararg_array_terminator_zero);
    try std.testing.expectEqualStrings(prepared.summary.last_main_template_message orelse return error.ExpectedMainPayload, released_plan.summary.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(prepared.summary.last_main_conditional_message, released_plan.summary.last_main_conditional_message);
    try std.testing.expectEqual(prepared.summary.last_main_template_cond_message, released_plan.summary.last_main_template_cond_message);
    try std.testing.expectEqualStrings(prepared.summary.last_main_template_print_message orelse return error.ExpectedMainPayload, released_plan.summary.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(prepared.summary.last_main_relative_location_message orelse return error.ExpectedMainPayload, released_plan.summary.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(prepared.summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload, released_plan.summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(prepared.summary.last_function_template_message orelse return error.ExpectedFunctionPayload, released_plan.summary.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(prepared.summary.last_format_template orelse return error.ExpectedMainPayload, released_plan.summary.last_format_template orelse return error.ExpectedMainPayload);

    try std.testing.expectEqual(@as(usize, 0), released_plan.summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), mutated_summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 8), released_plan.summary.total_events);
    try std.testing.expectEqual(@as(usize, 14), mutated_summary.total_events);
    try std.testing.expectEqual(@as(i32, 0), released_plan.summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 5), mutated_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), released_plan.summary.last_fn_count);
    try std.testing.expectEqual(@as(i32, 13), mutated_summary.last_fn_count);

    try module.unregisterFunctionThread();
    try std.testing.expectEqualStrings("foo_bar_unreg", module.summary().last_unregister_label orelse return error.ExpectedFunctionPayload);
}

test "runtime trace-events loader keeps initialized-stage fallback snapshots explicit after request-time replay" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();

    var loader = RuntimeTraceEventsLoader{};
    const prepared = try loader.prepareWithCommandName(&module, "perf-runtime-trace-events");
    try std.testing.expectEqual(LoaderStage.prepared, loader.stage());
    try std.testing.expectEqualStrings("perf-runtime-trace-events", prepared.command_name.?);
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.initialized, prepared.handoff_stage);
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.initialized, prepared.summary.stage);
    try std.testing.expectEqual(@as(usize, 1), prepared.summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.main_iterations);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 0), prepared.summary.total_events);
    try std.testing.expectEqual(@as(i32, -1), prepared.summary.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), prepared.summary.last_fn_count);
    try std.testing.expectEqual(@as(?[]const u8, null), prepared.summary.last_register_label);
    try std.testing.expectEqual(@as(?[]const u8, null), prepared.summary.last_unregister_label);

    const pending_plan = try loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, loader.stage());
    try std.testing.expectEqualStrings("perf-runtime-trace-events", pending_plan.command_name.?);
    try std.testing.expectEqual(prepared.handoff_stage, pending_plan.handoff_stage);
    try std.testing.expectEqual(prepared.summary.stage, pending_plan.summary.stage);
    try std.testing.expectEqual(prepared.summary.registration_depth, pending_plan.summary.registration_depth);
    try std.testing.expectEqual(prepared.summary.main_iterations, pending_plan.summary.main_iterations);
    try std.testing.expectEqual(prepared.summary.fn_iterations, pending_plan.summary.fn_iterations);
    try std.testing.expectEqual(prepared.summary.main_thread_events, pending_plan.summary.main_thread_events);
    try std.testing.expectEqual(prepared.summary.fn_thread_events, pending_plan.summary.fn_thread_events);
    try std.testing.expectEqual(prepared.summary.total_events, pending_plan.summary.total_events);
    try std.testing.expectEqual(prepared.summary.last_main_count, pending_plan.summary.last_main_count);
    try std.testing.expectEqual(prepared.summary.last_fn_count, pending_plan.summary.last_fn_count);
    try std.testing.expectEqual(prepared.summary.selftest_runs, pending_plan.summary.selftest_runs);
    try std.testing.expectEqual(prepared.summary.exit_runs, pending_plan.summary.exit_runs);
    try std.testing.expectEqual(prepared.summary.last_register_label, pending_plan.summary.last_register_label);
    try std.testing.expectEqual(prepared.summary.last_unregister_label, pending_plan.summary.last_unregister_label);

    const replayed_main = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 4), replayed_main);
    try module.registerFunctionThread();
    const replayed_fn = try module.emitFunctionIteration(11);
    try std.testing.expectEqual(@as(usize, 2), replayed_fn);
    try module.unregisterFunctionThread();

    const mutated_summary = module.summary();
    try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.initialized, mutated_summary.stage);
    try std.testing.expectEqual(@as(usize, 0), mutated_summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), mutated_summary.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), mutated_summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 4), mutated_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), mutated_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 6), mutated_summary.total_events);
    try std.testing.expectEqual(@as(i32, 7), mutated_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 11), mutated_summary.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", mutated_summary.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", mutated_summary.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Gandalf", mutated_summary.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", mutated_summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);

    const released_plan = try loader.releasePlanWithoutSubstrate();
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
    try std.testing.expectEqualStrings("perf-runtime-trace-events", released_plan.command_name.?);
    try std.testing.expectEqual(prepared.handoff_stage, released_plan.handoff_stage);
    try std.testing.expectEqual(pending_plan.handoff_stage, released_plan.handoff_stage);
    try std.testing.expectEqual(prepared.summary.stage, released_plan.summary.stage);
    try std.testing.expectEqual(prepared.summary.registration_depth, released_plan.summary.registration_depth);
    try std.testing.expectEqual(prepared.summary.main_iterations, released_plan.summary.main_iterations);
    try std.testing.expectEqual(prepared.summary.fn_iterations, released_plan.summary.fn_iterations);
    try std.testing.expectEqual(prepared.summary.main_thread_events, released_plan.summary.main_thread_events);
    try std.testing.expectEqual(prepared.summary.fn_thread_events, released_plan.summary.fn_thread_events);
    try std.testing.expectEqual(prepared.summary.total_events, released_plan.summary.total_events);
    try std.testing.expectEqual(prepared.summary.last_main_count, released_plan.summary.last_main_count);
    try std.testing.expectEqual(prepared.summary.last_fn_count, released_plan.summary.last_fn_count);
    try std.testing.expectEqual(prepared.summary.selftest_runs, released_plan.summary.selftest_runs);
    try std.testing.expectEqual(prepared.summary.exit_runs, released_plan.summary.exit_runs);
    try std.testing.expectEqual(prepared.summary.last_register_label, released_plan.summary.last_register_label);
    try std.testing.expectEqual(prepared.summary.last_unregister_label, released_plan.summary.last_unregister_label);
    try std.testing.expectEqual(@as(usize, 0), released_plan.summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 6), mutated_summary.total_events);
    try std.testing.expectEqual(@as(i32, -1), released_plan.summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 7), mutated_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), released_plan.summary.last_fn_count);
    try std.testing.expectEqual(@as(i32, 11), mutated_summary.last_fn_count);
    try std.testing.expectError(error.InvalidLoaderState, loader.requestRuntimeLoad());
}

test "runtime trace-events loader can release the prepared plan only after a runtime-load request" {
    var idle_loader = RuntimeTraceEventsLoader{};
    try std.testing.expectEqual(LoaderStage.idle, idle_loader.stage());
    try std.testing.expectError(error.InvalidLoaderState, idle_loader.requestRuntimeLoad());
    try std.testing.expectError(error.MissingLoadPlan, idle_loader.releasePlanWithoutSubstrate());
    try std.testing.expectError(error.InvalidLoaderState, idle_loader.releaseWithoutSubstrate());
    try std.testing.expectEqual(LoaderStage.idle, idle_loader.stage());

    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var prepared_loader = RuntimeTraceEventsLoader{};
    const prepared = try prepared_loader.prepareWithCommandName(&module, "perf-runtime-trace-events");
    try std.testing.expectEqual(LoaderStage.prepared, prepared_loader.stage());
    try std.testing.expectEqualStrings("perf-runtime-trace-events", prepared.command_name.?);
    try std.testing.expectError(error.InvalidLoaderState, prepared_loader.releasePlanWithoutSubstrate());
    try std.testing.expectEqual(LoaderStage.prepared, prepared_loader.stage());

    const pending_plan = try prepared_loader.requestRuntimeLoad();
    try std.testing.expectEqual(LoaderStage.waiting_on_runtime_substrate, prepared_loader.stage());
    try std.testing.expectEqualStrings("perf-runtime-trace-events", pending_plan.command_name.?);
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
    try std.testing.expectEqual(@as(?[]const u8, null), released_plan.command_name);
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

test "runtime trace-events loader preserves an explicit review-only command name" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    var loader = RuntimeTraceEventsLoader{};
    const plan = try loader.prepareWithCommandName(&module, "perf-runtime-trace-events");
    try std.testing.expectEqualStrings("perf-runtime-trace-events", plan.command_name.?);

    const pending_plan = try loader.requestRuntimeLoad();
    try std.testing.expectEqualStrings("perf-runtime-trace-events", pending_plan.command_name.?);

    const released_plan = try loader.releasePlanWithoutSubstrate();
    try std.testing.expectEqualStrings("perf-runtime-trace-events", released_plan.command_name.?);
    try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());
}

test "runtime trace-events loader rejects an empty explicit command name" {
    var module = runtime_trace_events_sample.RuntimeTraceEventsSample{};
    try module.init();

    var loader = RuntimeTraceEventsLoader{};
    try std.testing.expectError(
        error.InvalidCommandName,
        loader.prepareWithCommandName(&module, ""),
    );
    try std.testing.expectEqual(LoaderStage.idle, loader.stage());
}
