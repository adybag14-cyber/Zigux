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

const main_thread_events_per_iteration: usize = 6;
const function_thread_events_per_iteration: usize = 2;

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
    main_iterations: usize,
    fn_iterations: usize,
    main_thread_events: usize,
    fn_thread_events: usize,
    total_events: usize,
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,
    last_main_count: i32,
    last_fn_count: i32,
    saw_vararg_payload: bool,
    saw_rel_loc_payload: bool,
    saw_conditional_path: bool,
    last_main_foo_bar_message: ?[]const u8,
    last_main_template_message: ?[]const u8,
    last_main_conditional_message: ?[]const u8,
    last_main_template_cond_message: ?[]const u8,
    last_main_template_print_message: ?[]const u8,
    last_main_relative_location_message: ?[]const u8,
    last_function_template_message: ?[]const u8,
    last_function_foo_bar_message: ?[]const u8,
    last_format_template: ?[]const u8,
};

pub const RuntimeTraceEventsSample = struct {
    const Self = @This();

    stage_state: ModuleStage = .cold,
    registration_depth: usize = 0,
    main_iterations: usize = 0,
    fn_iterations: usize = 0,
    total_events: usize = 0,
    init_runs: usize = 0,
    selftest_runs: usize = 0,
    exit_runs: usize = 0,
    last_main_count: i32 = -1,
    last_fn_count: i32 = -1,
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
            .stage = self.stage(),
            .registration_depth = self.registration_depth,
            .main_iterations = self.main_iterations,
            .fn_iterations = self.fn_iterations,
            .main_thread_events = self.main_iterations * main_thread_events_per_iteration,
            .fn_thread_events = self.fn_iterations * function_thread_events_per_iteration,
            .total_events = self.total_events,
            .init_runs = self.init_runs,
            .selftest_runs = self.selftest_runs,
            .exit_runs = self.exit_runs,
            .last_main_count = self.last_main_count,
            .last_fn_count = self.last_fn_count,
            .saw_vararg_payload = self.saw_vararg_payload,
            .saw_rel_loc_payload = self.saw_rel_loc_payload,
            .saw_conditional_path = self.saw_conditional_path,
            .last_main_foo_bar_message = if (self.last_main_payload) |payload| payload.foo_bar_message else null,
            .last_main_template_message = if (self.last_main_payload) |payload| payload.template_message else null,
            .last_main_conditional_message = if (self.last_main_payload) |payload| payload.conditional_message else null,
            .last_main_template_cond_message = if (self.last_main_payload) |payload| payload.template_cond_message else null,
            .last_main_template_print_message = if (self.last_main_payload) |payload| payload.template_print_message else null,
            .last_main_relative_location_message = if (self.last_main_payload) |payload| payload.relative_location_message else null,
            .last_function_template_message = if (self.last_function_payload) |payload| payload.template_message else null,
            .last_function_foo_bar_message = if (self.last_function_payload) |payload| payload.foo_bar_message else null,
            .last_format_template = if (self.last_main_payload) |payload| payload.format_template else null,
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
        self.main_iterations = 0;
        self.fn_iterations = 0;
        self.total_events = 0;
        self.last_main_count = -1;
        self.last_fn_count = -1;
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
        self.registration_depth += 1;
    }

    pub fn unregisterFunctionThread(self: *Self) !void {
        try self.ensureMutable();
        if (self.registration_depth == 0) return error.RegistrationUnderflow;
        self.registration_depth -= 1;
    }

    pub fn emitMainIteration(self: *Self, count: i32) !usize {
        try self.ensureMutable();

        self.main_iterations += 1;
        self.last_main_count = count;
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
        self.total_events += main_thread_events_per_iteration;
        return main_thread_events_per_iteration;
    }

    pub fn emitFunctionIteration(self: *Self, count: i32) !usize {
        try self.ensureMutable();
        if (self.registration_depth == 0) return error.FunctionThreadNotRegistered;

        self.fn_iterations += 1;
        self.last_fn_count = count;
        self.last_function_payload = .{
            .foo_bar_message = "Look at me",
            .template_message = "Look at me too",
        };
        self.total_events += function_thread_events_per_iteration;
        return function_thread_events_per_iteration;
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
            .main_thread_events = self.main_iterations * main_thread_events_per_iteration,
            .fn_thread_events = self.fn_iterations * function_thread_events_per_iteration,
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

test "runtime trace-events sample keeps selftest replay explicit" {
    const descriptor = RuntimeTraceEventsSample.descriptor();
    try std.testing.expectEqualStrings("runtime_trace_events", descriptor.name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    var module = RuntimeTraceEventsSample{};
    try module.init();

    const selftest = try module.runSelftest();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings(descriptor.anchor, selftest.anchor);
    try std.testing.expectEqual(@as(usize, 5), selftest.event_families.len);
    try std.testing.expectEqual(@as(usize, 6), selftest.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), selftest.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), selftest.total_events);
    try std.testing.expect(selftest.conditional_paths_checked);
    try std.testing.expect(selftest.registration_paths_checked);

    try module.registerFunctionThread();
    const fn_events = try module.emitFunctionIteration(9);
    try std.testing.expectEqual(@as(usize, 2), fn_events);
    try module.unregisterFunctionThread();
    const main_events = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 6), main_events);

    const summary = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, summary.stage);
    try std.testing.expectEqual(@as(usize, 0), summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), summary.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 12), summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 16), summary.total_events);
    try std.testing.expectEqual(@as(usize, 1), summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), summary.selftest_runs);
    try std.testing.expectEqual(@as(i32, 7), summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 9), summary.last_fn_count);
    try std.testing.expect(summary.saw_vararg_payload);
    try std.testing.expect(summary.saw_rel_loc_payload);
    try std.testing.expect(summary.saw_conditional_path);
    try std.testing.expectEqualStrings("hello", summary.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", summary.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Some times print", summary.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", summary.last_main_template_cond_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("I have to be different", summary.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", summary.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", summary.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("iter=%d", summary.last_format_template orelse return error.ExpectedMainPayload);
}

test "runtime trace-events sample keeps exit lifecycle explicit" {
    var module = RuntimeTraceEventsSample{};
    try module.init();

    try module.registerFunctionThread();
    try std.testing.expectError(error.OutstandingRegistration, module.exit());
    try module.unregisterFunctionThread();

    _ = try module.runSelftest();
    try module.exit();

    const summary = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(ModuleStage.exited, summary.stage);
    try std.testing.expectEqual(@as(usize, 1), summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 6), summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), summary.total_events);
    try std.testing.expectEqual(@as(usize, 0), summary.registration_depth);
    try std.testing.expectEqual(@as(i32, 0), summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), summary.last_fn_count);
    try std.testing.expect(summary.saw_vararg_payload);
    try std.testing.expect(summary.saw_rel_loc_payload);
    try std.testing.expect(summary.saw_conditional_path);
    try std.testing.expectEqualStrings("hello", summary.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(0));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(0));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}

test "runtime trace-events sample keeps failed exit rollback explicit" {
    var module = RuntimeTraceEventsSample{};
    try module.init();
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(5);
    _ = try module.emitMainIteration(3);

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 8), before_failed_exit.total_events);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(ModuleStage.initialized, after_failed_exit.stage);
    try std.testing.expectEqual(before_failed_exit.registration_depth, after_failed_exit.registration_depth);
    try std.testing.expectEqual(before_failed_exit.main_iterations, after_failed_exit.main_iterations);
    try std.testing.expectEqual(before_failed_exit.fn_iterations, after_failed_exit.fn_iterations);
    try std.testing.expectEqual(before_failed_exit.main_thread_events, after_failed_exit.main_thread_events);
    try std.testing.expectEqual(before_failed_exit.fn_thread_events, after_failed_exit.fn_thread_events);
    try std.testing.expectEqual(before_failed_exit.total_events, after_failed_exit.total_events);
    try std.testing.expectEqual(before_failed_exit.exit_runs, after_failed_exit.exit_runs);
    try std.testing.expectEqualStrings(
        before_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload,
        after_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload,
        after_failed_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload,
    );

    try module.unregisterFunctionThread();
    _ = try module.runSelftest();
    try module.exit();

    const final_summary = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, final_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), final_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), final_summary.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), final_summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 16), final_summary.total_events);
}
