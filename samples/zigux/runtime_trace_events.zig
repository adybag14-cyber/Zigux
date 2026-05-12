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
    random_choice_message: []const u8,
    vararg_array_length: usize,
    vararg_array_terminator_zero: bool,
    template_message: []const u8,
    conditional_message: ?[]const u8,
    template_cond_message: ?[]const u8,
    template_print_message: []const u8,
    relative_location_message: []const u8,
    format_template: []const u8,
};

pub const FunctionThreadPayload = struct {
    foo_bar_message: []const u8,
    template_message: []const u8,
};

const function_thread_events_per_iteration: usize = 2;
const random_strings = [_][]const u8{
    "Mother Goose",
    "Snoopy",
    "Gandalf",
    "Frodo",
    "One ring to rule them all",
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
    main_iterations: usize,
    fn_iterations: usize,
    main_thread_events: usize,
    fn_thread_events: usize,
    total_events: usize,
    last_main_emitted_events: ?usize,
    last_fn_emitted_events: ?usize,
    last_main_conditional_event_count: ?usize,
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,
    last_main_count: i32,
    last_fn_count: i32,
    saw_vararg_payload: bool,
    saw_rel_loc_payload: bool,
    saw_conditional_path: bool,
    main_thread_label: ?[]const u8,
    function_thread_label: ?[]const u8,
    last_register_label: ?[]const u8,
    last_unregister_label: ?[]const u8,
    last_main_foo_bar_message: ?[]const u8,
    last_main_random_choice_message: ?[]const u8,
    last_main_vararg_array_length: ?usize,
    last_main_vararg_array_terminator_zero: ?bool,
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
    main_thread_events: usize = 0,
    fn_thread_events: usize = 0,
    total_events: usize = 0,
    last_main_emitted_events: ?usize = null,
    last_fn_emitted_events: ?usize = null,
    last_main_conditional_event_count: ?usize = null,
    init_runs: usize = 0,
    selftest_runs: usize = 0,
    exit_runs: usize = 0,
    last_main_count: i32 = -1,
    last_fn_count: i32 = -1,
    saw_vararg_payload: bool = false,
    saw_rel_loc_payload: bool = false,
    saw_conditional_path: bool = false,
    main_thread_label: ?[]const u8 = null,
    function_thread_label: ?[]const u8 = null,
    last_register_label: ?[]const u8 = null,
    last_unregister_label: ?[]const u8 = null,
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
            .main_thread_events = self.main_thread_events,
            .fn_thread_events = self.fn_thread_events,
            .total_events = self.total_events,
            .last_main_emitted_events = self.last_main_emitted_events,
            .last_fn_emitted_events = self.last_fn_emitted_events,
            .last_main_conditional_event_count = self.last_main_conditional_event_count,
            .init_runs = self.init_runs,
            .selftest_runs = self.selftest_runs,
            .exit_runs = self.exit_runs,
            .last_main_count = self.last_main_count,
            .last_fn_count = self.last_fn_count,
            .saw_vararg_payload = self.saw_vararg_payload,
            .saw_rel_loc_payload = self.saw_rel_loc_payload,
            .saw_conditional_path = self.saw_conditional_path,
            .main_thread_label = self.main_thread_label,
            .function_thread_label = self.function_thread_label,
            .last_register_label = self.last_register_label,
            .last_unregister_label = self.last_unregister_label,
            .last_main_foo_bar_message = if (self.last_main_payload) |payload| payload.foo_bar_message else null,
            .last_main_random_choice_message = if (self.last_main_payload) |payload| payload.random_choice_message else null,
            .last_main_vararg_array_length = if (self.last_main_payload) |payload| payload.vararg_array_length else null,
            .last_main_vararg_array_terminator_zero = if (self.last_main_payload) |payload| payload.vararg_array_terminator_zero else null,
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
        self.main_thread_events = 0;
        self.fn_thread_events = 0;
        self.total_events = 0;
        self.last_main_emitted_events = null;
        self.last_fn_emitted_events = null;
        self.last_main_conditional_event_count = null;
        self.last_main_count = -1;
        self.last_fn_count = -1;
        self.saw_vararg_payload = false;
        self.saw_rel_loc_payload = false;
        self.saw_conditional_path = false;
        self.main_thread_label = "event-sample";
        self.function_thread_label = "event-sample-fn";
        self.last_register_label = null;
        self.last_unregister_label = null;
        self.last_main_payload = null;
        self.last_function_payload = null;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn registerFunctionThread(self: *Self) !void {
        try self.ensureMutable();
        if (self.registration_depth != 0) return error.FunctionThreadAlreadyRegistered;
        self.registration_depth = 1;
        self.last_register_label = "foo_bar_reg";
    }

    pub fn unregisterFunctionThread(self: *Self) !void {
        try self.ensureMutable();
        if (self.registration_depth == 0) return error.RegistrationUnderflow;
        self.registration_depth -= 1;
        self.last_unregister_label = "foo_bar_unreg";
    }

    fn randomStringForCount(count: i32) []const u8 {
        const len: i32 = @mod(count, @as(i32, @intCast(random_strings.len)));
        return random_strings[@as(usize, @intCast(len))];
    }

    fn mainArrayLengthForCount(count: i32) usize {
        return @as(usize, @intCast(@mod(count, @as(i32, @intCast(random_strings.len)))));
    }

    fn conditionalMessageForCount(count: i32) ?[]const u8 {
        return if (@mod(count, 10) == 0) "Some times print" else null;
    }

    fn templateConditionalMessageForCount(count: i32) ?[]const u8 {
        return if (@mod(count, 8) == 0) "prints other times" else null;
    }

    fn mainThreadConditionalEventCountForCount(count: i32) usize {
        var conditional_events: usize = 0;
        if (conditionalMessageForCount(count) != null) conditional_events += 1;
        if (templateConditionalMessageForCount(count) != null) conditional_events += 1;
        return conditional_events;
    }

    fn mainThreadEventCountForCount(count: i32) usize {
        return 4 + mainThreadConditionalEventCountForCount(count);
    }

    pub fn emitMainIteration(self: *Self, count: i32) !usize {
        try self.ensureMutable();

        const conditional_message = conditionalMessageForCount(count);
        const template_cond_message = templateConditionalMessageForCount(count);
        const conditional_events = mainThreadConditionalEventCountForCount(count);
        const emitted_events = mainThreadEventCountForCount(count);

        self.main_iterations += 1;
        self.last_main_count = count;
        self.saw_vararg_payload = true;
        self.saw_rel_loc_payload = true;
        self.saw_conditional_path = self.saw_conditional_path or conditional_message != null or template_cond_message != null;
        self.last_main_payload = .{
            .foo_bar_message = "hello",
            .random_choice_message = randomStringForCount(count),
            .vararg_array_length = mainArrayLengthForCount(count),
            .vararg_array_terminator_zero = true,
            .template_message = "HELLO",
            .conditional_message = conditional_message,
            .template_cond_message = template_cond_message,
            .template_print_message = "I have to be different",
            .relative_location_message = "Hello __rel_loc",
            .format_template = "iter=%d",
        };
        self.main_thread_events += emitted_events;
        self.total_events += emitted_events;
        self.last_main_emitted_events = emitted_events;
        self.last_main_conditional_event_count = conditional_events;
        return emitted_events;
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
        self.fn_thread_events += function_thread_events_per_iteration;
        self.total_events += function_thread_events_per_iteration;
        self.last_fn_emitted_events = function_thread_events_per_iteration;
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
            .main_thread_events = self.main_thread_events,
            .fn_thread_events = self.fn_thread_events,
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

test "count-gated main-thread replay matches the Linux sample conditions" {
    var module = RuntimeTraceEventsSample{};
    try module.init();

    const emitted = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 4), emitted);

    const replay = module.summary();
    try std.testing.expectEqual(@as(usize, 4), replay.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), replay.total_events);
    try std.testing.expectEqual(@as(?usize, 4), replay.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), replay.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, 0), replay.last_main_conditional_event_count);
    try std.testing.expect(!replay.saw_conditional_path);
    try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_template_cond_message);
    try std.testing.expectEqualStrings("Gandalf", replay.last_main_random_choice_message orelse return error.ExpectedMainPayload);
}

test "selftest path still records both conditional families at count zero" {
    var module = RuntimeTraceEventsSample{};
    try module.init();

    const summary = try module.runSelftest();
    try std.testing.expectEqual(@as(usize, 6), summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), summary.total_events);

    const replay = module.summary();
    try std.testing.expectEqual(@as(?usize, 6), replay.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), replay.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), replay.last_main_conditional_event_count);
    try std.testing.expect(replay.saw_conditional_path);
    try std.testing.expectEqualStrings("Some times print", replay.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);
}

test "mixed replay keeps explicit event totals honest across direct and selftest paths" {
    var module = RuntimeTraceEventsSample{};
    try module.init();

    _ = try module.emitMainIteration(7);
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(9);
    try module.unregisterFunctionThread();

    const summary = try module.runSelftest();
    try std.testing.expectEqual(@as(usize, 10), summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), summary.total_events);
}

test "trace-events sample rejects duplicate function-thread registration" {
    var module = RuntimeTraceEventsSample{};
    try module.init();

    try module.registerFunctionThread();
    try std.testing.expectEqual(@as(usize, 1), module.summary().registration_depth);
    try std.testing.expectError(error.FunctionThreadAlreadyRegistered, module.registerFunctionThread());
    try std.testing.expectEqual(@as(usize, 1), module.summary().registration_depth);
    try std.testing.expectEqualStrings("foo_bar_reg", module.summary().last_register_label orelse return error.ExpectedFunctionPayload);
}

test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity" {
    var module = RuntimeTraceEventsSample{};
    try std.testing.expectEqual(ModuleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());

    try module.init();
    const initialized_summary = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, initialized_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.registration_depth);
    try std.testing.expectEqual(@as(i32, -1), initialized_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), initialized_summary.last_fn_count);
    try std.testing.expectEqual(@as(?usize, null), initialized_summary.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), initialized_summary.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), initialized_summary.last_main_conditional_event_count);

    _ = try module.emitMainIteration(7);
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(9);
    try module.unregisterFunctionThread();

    const selftest = try module.runSelftest();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings(RuntimeTraceEventsSample.descriptor().anchor, selftest.anchor);
    try std.testing.expectEqual(@as(usize, 10), selftest.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), selftest.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), selftest.total_events);
    try std.testing.expect(selftest.conditional_paths_checked);
    try std.testing.expect(selftest.registration_paths_checked);

    const post_selftest_replay = try module.emitMainIteration(3);
    try std.testing.expectEqual(@as(usize, 4), post_selftest_replay);
    try module.registerFunctionThread();
    const post_selftest_fn_replay = try module.emitFunctionIteration(11);
    try std.testing.expectEqual(@as(usize, 2), post_selftest_fn_replay);
    try module.unregisterFunctionThread();

    const selftest_complete_summary = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_complete_summary.stage);
    try std.testing.expectEqual(@as(usize, 3), selftest_complete_summary.main_iterations);
    try std.testing.expectEqual(@as(usize, 3), selftest_complete_summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 14), selftest_complete_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 6), selftest_complete_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 20), selftest_complete_summary.total_events);
    try std.testing.expectEqual(@as(?usize, 4), selftest_complete_summary.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), selftest_complete_summary.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, 0), selftest_complete_summary.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(usize, 1), selftest_complete_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_complete_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_complete_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_complete_summary.registration_depth);
    try std.testing.expectEqual(@as(i32, 3), selftest_complete_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 11), selftest_complete_summary.last_fn_count);
    try std.testing.expect(selftest_complete_summary.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", selftest_complete_summary.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", selftest_complete_summary.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Frodo", selftest_complete_summary.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", selftest_complete_summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", selftest_complete_summary.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), selftest_complete_summary.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), selftest_complete_summary.last_main_template_cond_message);

    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectEqual(selftest_complete_summary.main_iterations, exited_summary.main_iterations);
    try std.testing.expectEqual(selftest_complete_summary.fn_iterations, exited_summary.fn_iterations);
    try std.testing.expectEqual(selftest_complete_summary.main_thread_events, exited_summary.main_thread_events);
    try std.testing.expectEqual(selftest_complete_summary.fn_thread_events, exited_summary.fn_thread_events);
    try std.testing.expectEqual(selftest_complete_summary.total_events, exited_summary.total_events);
    try std.testing.expectEqual(selftest_complete_summary.last_main_emitted_events, exited_summary.last_main_emitted_events);
    try std.testing.expectEqual(selftest_complete_summary.last_fn_emitted_events, exited_summary.last_fn_emitted_events);
    try std.testing.expectEqual(selftest_complete_summary.last_main_conditional_event_count, exited_summary.last_main_conditional_event_count);
    try std.testing.expectEqual(selftest_complete_summary.last_main_count, exited_summary.last_main_count);
    try std.testing.expectEqual(selftest_complete_summary.last_fn_count, exited_summary.last_fn_count);
    try std.testing.expectEqualStrings(selftest_complete_summary.last_main_foo_bar_message orelse return error.ExpectedMainPayload, exited_summary.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(selftest_complete_summary.last_main_random_choice_message orelse return error.ExpectedMainPayload, exited_summary.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(selftest_complete_summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload, exited_summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(selftest_complete_summary.last_function_template_message orelse return error.ExpectedFunctionPayload, exited_summary.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(selftest_complete_summary.last_register_label orelse return error.ExpectedFunctionPayload, exited_summary.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(selftest_complete_summary.last_unregister_label orelse return error.ExpectedFunctionPayload, exited_summary.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(13));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(15));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());
}

test "trace-events sample keeps failed-exit rollback explicit after selftest-ready replay" {
    var module = RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());

    const replayed_main = try module.emitMainIteration(5);
    try std.testing.expectEqual(@as(usize, 4), replayed_main);
    try module.registerFunctionThread();
    const replayed_fn = try module.emitFunctionIteration(15);
    try std.testing.expectEqual(@as(usize, 2), replayed_fn);

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), before_failed_exit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), before_failed_exit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), before_failed_exit.total_events);
    try std.testing.expectEqual(@as(?usize, 4), before_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), before_failed_exit.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, 0), before_failed_exit.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), before_failed_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 15), before_failed_exit.last_fn_count);
    try std.testing.expectEqualStrings("event-sample", before_failed_exit.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("event-sample-fn", before_failed_exit.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_reg", before_failed_exit.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_failed_exit.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("hello", before_failed_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Mother Goose", before_failed_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(before_failed_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", before_failed_exit.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), before_failed_exit.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), before_failed_exit.last_main_template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", before_failed_exit.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", before_failed_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", before_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", before_failed_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("iter=%d", before_failed_exit.last_format_template orelse return error.ExpectedMainPayload);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, after_failed_exit.stage);
    try std.testing.expectEqual(before_failed_exit.registration_depth, after_failed_exit.registration_depth);
    try std.testing.expectEqual(before_failed_exit.main_iterations, after_failed_exit.main_iterations);
    try std.testing.expectEqual(before_failed_exit.fn_iterations, after_failed_exit.fn_iterations);
    try std.testing.expectEqual(before_failed_exit.main_thread_events, after_failed_exit.main_thread_events);
    try std.testing.expectEqual(before_failed_exit.fn_thread_events, after_failed_exit.fn_thread_events);
    try std.testing.expectEqual(before_failed_exit.total_events, after_failed_exit.total_events);
    try std.testing.expectEqual(before_failed_exit.last_main_emitted_events, after_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(before_failed_exit.last_fn_emitted_events, after_failed_exit.last_fn_emitted_events);
    try std.testing.expectEqual(before_failed_exit.last_main_conditional_event_count, after_failed_exit.last_main_conditional_event_count);
    try std.testing.expectEqual(before_failed_exit.init_runs, after_failed_exit.init_runs);
    try std.testing.expectEqual(before_failed_exit.selftest_runs, after_failed_exit.selftest_runs);
    try std.testing.expectEqual(before_failed_exit.exit_runs, after_failed_exit.exit_runs);
    try std.testing.expectEqual(before_failed_exit.last_main_count, after_failed_exit.last_main_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, after_failed_exit.last_fn_count);
    try std.testing.expectEqualStrings(before_failed_exit.main_thread_label orelse return error.ExpectedFunctionPayload, after_failed_exit.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.function_thread_label orelse return error.ExpectedFunctionPayload, after_failed_exit.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_register_label orelse return error.ExpectedFunctionPayload, after_failed_exit.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_unregister_label orelse return error.ExpectedFunctionPayload, after_failed_exit.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload, after_failed_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload, after_failed_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(before_failed_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload, after_failed_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(before_failed_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload, after_failed_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_main_template_message orelse return error.ExpectedMainPayload, after_failed_exit.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit.last_main_template_cond_message);
    try std.testing.expectEqualStrings(before_failed_exit.last_main_template_print_message orelse return error.ExpectedMainPayload, after_failed_exit.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload, after_failed_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload, after_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_function_template_message orelse return error.ExpectedFunctionPayload, after_failed_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_format_template orelse return error.ExpectedMainPayload, after_failed_exit.last_format_template orelse return error.ExpectedMainPayload);

    try module.unregisterFunctionThread();
    try std.testing.expectEqualStrings("foo_bar_unreg", module.summary().last_unregister_label orelse return error.ExpectedFunctionPayload);
    try module.exit();
    try std.testing.expectEqual(ModuleStage.exited, module.summary().stage);
}
