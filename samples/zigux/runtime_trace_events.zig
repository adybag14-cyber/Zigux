const std = @import("std");

pub const ModuleStage = enum(u8) {
    cold,
    initialized,
    selftest_complete,
    exited,
};

pub const EventFamily = enum {
    foo_bar,
    template,
    conditional,
    relative_location,
    function_callback,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
};

pub const MainThreadPayload = struct {
    foo_bar_message: []const u8,
    template_message: []const u8,
    conditional_message: []const u8,
    template_cond_message: []const u8,
    template_print_message: []const u8,
    relative_location_message: []const u8,
    format_template: []const u8,
};

pub const FunctionThreadPayload = struct {
    foo_bar_message: []const u8,
    template_message: []const u8,
};

pub const EmissionSummary = struct {
    anchor: []const u8,
    event_families: []const EventFamily,
    main_thread_events: usize,
    fn_thread_events: usize,
    total_events: usize,
    conditional_paths_checked: bool,
    registration_paths_checked: bool,
};

pub const RuntimeTraceEventsSummary = struct {
    stage: ModuleStage,
    registration_depth: usize,
    register_runs: usize,
    unregister_runs: usize,
    registration_start_runs: usize,
    registration_stop_runs: usize,
    main_iterations: usize,
    fn_iterations: usize,
    total_events: usize,
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,
    last_main_count: i32,
    last_fn_count: i32,
    last_main_emitted_events: usize,
    last_fn_emitted_events: usize,
    saw_vararg_payload: bool,
    saw_rel_loc_payload: bool,
    saw_conditional_path: bool,
    last_main_payload: ?MainThreadPayload,
    last_function_payload: ?FunctionThreadPayload,
};

pub const RuntimeTraceEventsSample = struct {
    const Self = @This();

    stage_state: ModuleStage = .cold,
    registration_depth: usize = 0,
    register_runs: usize = 0,
    unregister_runs: usize = 0,
    registration_start_runs: usize = 0,
    registration_stop_runs: usize = 0,
    main_iterations: usize = 0,
    fn_iterations: usize = 0,
    total_events: usize = 0,
    init_runs: usize = 0,
    selftest_runs: usize = 0,
    exit_runs: usize = 0,
    last_main_count: i32 = -1,
    last_fn_count: i32 = -1,
    last_main_emitted_events: usize = 0,
    last_fn_emitted_events: usize = 0,
    saw_vararg_payload: bool = false,
    saw_rel_loc_payload: bool = false,
    saw_conditional_path: bool = false,
    last_main_payload: ?MainThreadPayload = null,
    last_function_payload: ?FunctionThreadPayload = null,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "runtime_trace_events",
            .anchor = "samples/trace_events/trace-events-sample.c",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
        };
    }

    pub fn stage(self: *const Self) ModuleStage {
        return self.stage_state;
    }

    pub fn summary(self: *const Self) RuntimeTraceEventsSummary {
        return .{
            .stage = self.stage_state,
            .registration_depth = self.registration_depth,
            .register_runs = self.register_runs,
            .unregister_runs = self.unregister_runs,
            .registration_start_runs = self.registration_start_runs,
            .registration_stop_runs = self.registration_stop_runs,
            .main_iterations = self.main_iterations,
            .fn_iterations = self.fn_iterations,
            .total_events = self.total_events,
            .init_runs = self.init_runs,
            .selftest_runs = self.selftest_runs,
            .exit_runs = self.exit_runs,
            .last_main_count = self.last_main_count,
            .last_fn_count = self.last_fn_count,
            .last_main_emitted_events = self.last_main_emitted_events,
            .last_fn_emitted_events = self.last_fn_emitted_events,
            .saw_vararg_payload = self.saw_vararg_payload,
            .saw_rel_loc_payload = self.saw_rel_loc_payload,
            .saw_conditional_path = self.saw_conditional_path,
            .last_main_payload = self.last_main_payload,
            .last_function_payload = self.last_function_payload,
        };
    }

    fn ensureMutable(self: *const Self) !void {
        return switch (self.stage()) {
            .initialized, .selftest_complete => {},
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        self.registration_depth = 0;
        self.register_runs = 0;
        self.unregister_runs = 0;
        self.registration_start_runs = 0;
        self.registration_stop_runs = 0;
        self.main_iterations = 0;
        self.fn_iterations = 0;
        self.total_events = 0;
        self.last_main_count = -1;
        self.last_fn_count = -1;
        self.last_main_emitted_events = 0;
        self.last_fn_emitted_events = 0;
        self.saw_vararg_payload = false;
        self.saw_rel_loc_payload = false;
        self.saw_conditional_path = false;
        self.last_main_payload = null;
        self.last_function_payload = null;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn registerFunctionThread(self: *Self) !void {
        try self.ensureMutable();
        if (self.registration_depth == 0) self.registration_start_runs += 1;
        self.registration_depth += 1;
        self.register_runs += 1;
    }

    pub fn unregisterFunctionThread(self: *Self) !void {
        try self.ensureMutable();
        if (self.registration_depth == 0) return error.RegistrationUnderflow;
        self.registration_depth -= 1;
        self.unregister_runs += 1;
        if (self.registration_depth == 0) self.registration_stop_runs += 1;
    }

    pub fn emitMainIteration(self: *Self, count: i32) !usize {
        try self.ensureMutable();

        self.main_iterations += 1;
        self.last_main_count = count;
        self.last_main_emitted_events = 6;
        self.saw_vararg_payload = true;
        self.saw_rel_loc_payload = true;
        self.saw_conditional_path = true;
        self.last_main_payload = .{
            .foo_bar_message = "hello",
            .template_message = "HELLO",
            .conditional_message = "Some times print",
            .template_cond_message = "prints other times",
            .template_print_message = "I have to be different",
            .relative_location_message = "Hello __rel_loc",
            .format_template = "iter=%d",
        };
        self.total_events += 6;
        return 6;
    }

    pub fn emitFunctionIteration(self: *Self, count: i32) !usize {
        try self.ensureMutable();
        if (self.registration_depth == 0) return error.FunctionThreadNotRegistered;

        self.fn_iterations += 1;
        self.last_fn_count = count;
        self.last_fn_emitted_events = 2;
        self.last_function_payload = .{
            .foo_bar_message = "Look at me",
            .template_message = "Look at me too",
        };
        self.total_events += 2;
        return 2;
    }

    pub fn runSelftest(self: *Self) !EmissionSummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        _ = try self.emitMainIteration(0);
        try self.registerFunctionThread();
        _ = try self.emitFunctionIteration(1);
        try self.unregisterFunctionThread();

        self.selftest_runs += 1;
        self.stage_state = .selftest_complete;
        return .{
            .anchor = descriptor().anchor,
            .event_families = &.{
                .foo_bar,
                .template,
                .conditional,
                .relative_location,
                .function_callback,
            },
            .main_thread_events = self.main_iterations * 6,
            .fn_thread_events = self.fn_iterations * 2,
            .total_events = self.total_events,
            .conditional_paths_checked = self.saw_conditional_path,
            .registration_paths_checked = true,
        };
    }

    pub fn exit(self: *Self) !void {
        switch (self.stage()) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidLifecycleTransition,
        }
        if (self.registration_depth != 0) return error.OutstandingRegistration;

        self.exit_runs += 1;
        self.stage_state = .exited;
    }
};

test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity" {
    var module = RuntimeTraceEventsSample{};
    try module.init();

    const selftest_summary = try module.runSelftest();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.selftest_runs);
    try std.testing.expectEqual(@as(usize, 6), selftest_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), selftest_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), selftest_summary.total_events);

    try module.registerFunctionThread();
    _ = try module.emitMainIteration(3);
    _ = try module.emitFunctionIteration(5);
    try module.unregisterFunctionThread();

    const after_replay = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, after_replay.stage);
    try std.testing.expectEqual(@as(usize, 0), after_replay.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), after_replay.register_runs);
    try std.testing.expectEqual(@as(usize, 2), after_replay.unregister_runs);
    try std.testing.expectEqual(@as(usize, 2), after_replay.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 2), after_replay.registration_stop_runs);
    try std.testing.expectEqual(@as(usize, 2), after_replay.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), after_replay.fn_iterations);
    try std.testing.expectEqual(@as(usize, 16), after_replay.total_events);
    try std.testing.expectEqual(@as(i32, 3), after_replay.last_main_count);
    try std.testing.expectEqual(@as(i32, 5), after_replay.last_fn_count);
    try std.testing.expectEqual(@as(usize, 6), after_replay.last_main_emitted_events);
    try std.testing.expectEqual(@as(usize, 2), after_replay.last_fn_emitted_events);
    const main_payload = after_replay.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", main_payload.format_template);
    const function_payload = after_replay.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", function_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", function_payload.template_message);

    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectEqual(after_replay.total_events, exited_summary.total_events);
    try std.testing.expectEqual(after_replay.register_runs, exited_summary.register_runs);
    try std.testing.expectEqual(after_replay.unregister_runs, exited_summary.unregister_runs);
}

test "trace-events sample keeps initialized-stage failed-exit rollback explicit before selftest" {
    var module = RuntimeTraceEventsSample{};
    try module.init();

    _ = try module.emitMainIteration(4);
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(6);

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, before_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.unregister_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.registration_stop_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 8), before_failed_exit.total_events);
    try std.testing.expectEqual(@as(i32, 4), before_failed_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 6), before_failed_exit.last_fn_count);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.exit_runs);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, after_failed_exit.stage);
    try std.testing.expectEqual(before_failed_exit.registration_depth, after_failed_exit.registration_depth);
    try std.testing.expectEqual(before_failed_exit.register_runs, after_failed_exit.register_runs);
    try std.testing.expectEqual(before_failed_exit.unregister_runs, after_failed_exit.unregister_runs);
    try std.testing.expectEqual(before_failed_exit.registration_start_runs, after_failed_exit.registration_start_runs);
    try std.testing.expectEqual(before_failed_exit.registration_stop_runs, after_failed_exit.registration_stop_runs);
    try std.testing.expectEqual(before_failed_exit.main_iterations, after_failed_exit.main_iterations);
    try std.testing.expectEqual(before_failed_exit.fn_iterations, after_failed_exit.fn_iterations);
    try std.testing.expectEqual(before_failed_exit.total_events, after_failed_exit.total_events);
    try std.testing.expectEqual(before_failed_exit.last_main_count, after_failed_exit.last_main_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, after_failed_exit.last_fn_count);
    try std.testing.expectEqual(before_failed_exit.selftest_runs, after_failed_exit.selftest_runs);
    try std.testing.expectEqual(before_failed_exit.exit_runs, after_failed_exit.exit_runs);
    const main_payload = after_failed_exit.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", main_payload.format_template);
    const function_payload = after_failed_exit.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", function_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", function_payload.template_message);

    try module.unregisterFunctionThread();
    try module.exit();

    const exited_summary = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 0), exited_summary.registration_depth);
    try std.testing.expectEqual(before_failed_exit.main_iterations, exited_summary.main_iterations);
    try std.testing.expectEqual(before_failed_exit.fn_iterations, exited_summary.fn_iterations);
    try std.testing.expectEqual(before_failed_exit.total_events, exited_summary.total_events);
    try std.testing.expectEqual(before_failed_exit.last_main_count, exited_summary.last_main_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, exited_summary.last_fn_count);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.registration_stop_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
}

test "trace-events sample keeps failed-exit rollback explicit after selftest-ready replay" {
    var module = RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    try module.registerFunctionThread();
    _ = try module.emitMainIteration(4);
    _ = try module.emitFunctionIteration(6);

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.unregister_runs);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_stop_runs);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 16), before_failed_exit.total_events);
    try std.testing.expectEqual(@as(i32, 4), before_failed_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 6), before_failed_exit.last_fn_count);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.exit_runs);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, after_failed_exit.stage);
    try std.testing.expectEqual(before_failed_exit.registration_depth, after_failed_exit.registration_depth);
    try std.testing.expectEqual(before_failed_exit.register_runs, after_failed_exit.register_runs);
    try std.testing.expectEqual(before_failed_exit.unregister_runs, after_failed_exit.unregister_runs);
    try std.testing.expectEqual(before_failed_exit.registration_start_runs, after_failed_exit.registration_start_runs);
    try std.testing.expectEqual(before_failed_exit.registration_stop_runs, after_failed_exit.registration_stop_runs);
    try std.testing.expectEqual(before_failed_exit.main_iterations, after_failed_exit.main_iterations);
    try std.testing.expectEqual(before_failed_exit.fn_iterations, after_failed_exit.fn_iterations);
    try std.testing.expectEqual(before_failed_exit.total_events, after_failed_exit.total_events);
    try std.testing.expectEqual(before_failed_exit.last_main_count, after_failed_exit.last_main_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, after_failed_exit.last_fn_count);
    try std.testing.expectEqual(before_failed_exit.exit_runs, after_failed_exit.exit_runs);

    try module.unregisterFunctionThread();
    try module.exit();

    const exited_summary = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 0), exited_summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), exited_summary.register_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_summary.unregister_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_summary.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_summary.registration_stop_runs);
    try std.testing.expectEqual(before_failed_exit.total_events, exited_summary.total_events);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
}

test "trace-events sample keeps callback-registration edge refcounts explicit" {
    var module = RuntimeTraceEventsSample{};
    try module.init();

    try module.registerFunctionThread();
    try module.registerFunctionThread();
    try std.testing.expectEqual(@as(usize, 2), module.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), module.register_runs);
    try std.testing.expectEqual(@as(usize, 1), module.registration_start_runs);

    _ = try module.emitFunctionIteration(2);
    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 1), module.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), module.unregister_runs);
    try std.testing.expectEqual(@as(usize, 0), module.registration_stop_runs);
    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 0), module.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), module.unregister_runs);
    try std.testing.expectEqual(@as(usize, 1), module.registration_stop_runs);

    try module.exit();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
}
