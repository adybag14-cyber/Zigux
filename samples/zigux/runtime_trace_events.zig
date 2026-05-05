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