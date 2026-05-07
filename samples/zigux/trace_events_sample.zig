const std = @import("std");

pub const SampleStage = enum(u8) {
    cold,
    initialized,
    replay_complete,
    exited,
};

pub const SampleFocus = enum {
    payload_shape,
    string_selection,
    formatted_message,
    conditional_event_families,
    function_callback_registration,
    ownership_and_lifetime,
};

pub const SampleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selfcheck: bool,
};

pub const ReviewContract = struct {
    focus: []const SampleFocus,
    non_goals: []const []const u8,
};

pub const ReplaySummary = struct {
    anchor: []const u8,
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    formatted_message: []const u8,
    selected_string: []const u8,
    array_prefix_len: usize,
    array_sentinel: i32,
    bitmask_word: usize,
    main_thread_event_calls: usize,
    function_callback_event_calls: usize,
    total_event_calls: usize,
    conditional_paths_checked: bool,
    vararg_payload_path_checked: bool,
    relative_location_path_checked: bool,
    function_callback_path_checked: bool,
    registration_balance_restored: bool,
    checked_focus: []const SampleFocus,
};

pub const PayloadBoundarySummary = struct {
    stage_before_iteration: SampleStage,
    stage_after_iteration: SampleStage,
    formatted_message: []const u8,
    selected_string: []const u8,
    payload_prefix_len: usize,
    payload_prefix: [4]i32,
    payload_sentinel: i32,
    main_thread_event_calls: usize,
    conditional_paths_checked: bool,
    vararg_payload_path_checked: bool,
    relative_location_path_checked: bool,
};

pub const CallbackBoundarySummary = struct {
    stage_before_callback: SampleStage,
    stage_after_callback: SampleStage,
    function_count: i32,
    function_callback_event_calls: usize,
    total_event_calls_after_replay: usize,
    function_callback_path_checked: bool,
    registration_depth_after_register: usize,
    registration_depth_after_unregister: usize,
    registration_balance_restored: bool,
};

pub const TraceEventsReferenceSample = struct {
    const Self = @This();

    pub const random_strings = [_][]const u8{
        "Mother Goose",
        "Snoopy",
        "Gandalf",
        "Frodo",
        "One ring to rule them all",
    };
    pub const event_family_count: usize = 6;
    pub const function_callback_family_count: usize = 2;

    pub const sample_review_focus = [_]SampleFocus{
        .payload_shape,
        .string_selection,
        .formatted_message,
        .conditional_event_families,
        .function_callback_registration,
        .ownership_and_lifetime,
    };

    pub const sample_review_non_goals = [_][]const u8{
        "CREATE_TRACE_POINTS parity",
        "tracepoint macro parity from trace-events-sample.h",
        "kernel thread scheduling or timeout parity",
        "module registration or unregister wiring parity",
    };

    stage_state: SampleStage = .cold,
    registration_depth: usize = 0,
    total_event_calls: usize = 0,
    init_runs: usize = 0,
    replay_runs: usize = 0,
    exit_runs: usize = 0,
    last_main_count: i32 = -1,
    last_function_count: i32 = -1,
    array_payload: [6]i32 = [_]i32{0} ** 6,
    selected_string: []const u8 = "",
    bitmask_word: usize = 0,
    saw_vararg_payload: bool = false,
    saw_rel_loc_payload: bool = false,
    saw_conditional_path: bool = false,
    saw_function_callback_path: bool = false,
    message_buffer: [32]u8 = [_]u8{0} ** 32,
    message_len: usize = 0,

    pub fn descriptor() SampleDescriptor {
        return .{
            .name = "trace_events_sample",
            .anchor = "samples/trace_events/trace-events-sample.c",
            .requires_runtime_substrate = false,
            .provides_selfcheck = true,
        };
    }

    pub fn reviewContract() ReviewContract {
        return .{
            .focus = &sample_review_focus,
            .non_goals = &sample_review_non_goals,
        };
    }

    pub fn stage(self: *const Self) SampleStage {
        return self.stage_state;
    }

    pub fn formattedMessage(self: *const Self) []const u8 {
        return self.message_buffer[0..self.message_len];
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        self.registration_depth = 0;
        self.total_event_calls = 0;
        self.last_main_count = -1;
        self.last_function_count = -1;
        self.array_payload = [_]i32{0} ** 6;
        self.selected_string = "";
        self.bitmask_word = 0;
        self.saw_vararg_payload = false;
        self.saw_rel_loc_payload = false;
        self.saw_conditional_path = false;
        self.saw_function_callback_path = false;
        self.message_buffer = [_]u8{0} ** 32;
        self.message_len = 0;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    fn ensureMutable(self: *const Self) !void {
        return switch (self.stage()) {
            .initialized, .replay_complete => {},
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn replayMainIteration(self: *Self, count: i32) !void {
        try self.ensureMutable();
        if (count < 0) return error.InvalidIterationCount;

        const len: usize = @intCast(@mod(count, 5));
        self.array_payload = [_]i32{0} ** 6;
        for (0..len) |i| {
            self.array_payload[i] = @intCast(i + 1);
        }
        self.array_payload[len] = 0;

        self.last_main_count = count;
        self.selected_string = random_strings[len];
        self.bitmask_word = 0xdeadbeef;
        const message = try std.fmt.bufPrint(&self.message_buffer, "iter={d}", .{count});
        self.message_len = message.len;
        self.saw_vararg_payload = true;
        self.saw_rel_loc_payload = true;
        self.saw_conditional_path = true;
        self.total_event_calls += event_family_count;
    }

    pub fn registerFunctionCallback(self: *Self) !void {
        try self.ensureMutable();
        self.registration_depth += 1;
    }

    pub fn unregisterFunctionCallback(self: *Self) !void {
        try self.ensureMutable();
        if (self.registration_depth == 0) return error.RegistrationUnderflow;
        self.registration_depth -= 1;
    }

    pub fn replayFunctionIteration(self: *Self, count: i32) !void {
        try self.ensureMutable();
        if (self.registration_depth == 0) return error.FunctionCallbackNotRegistered;

        self.last_function_count = count;
        self.saw_function_callback_path = true;
        self.total_event_calls += function_callback_family_count;
    }

    pub fn runAnchorReplay(self: *Self) !ReplaySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        try self.replayMainIteration(7);
        const callback_boundary = try self.runCallbackBoundaryReplay(9);

        self.replay_runs += 1;
        self.stage_state = .replay_complete;
        return .{
            .anchor = descriptor().anchor,
            .stage_before_replay = .initialized,
            .stage_after_replay = .replay_complete,
            .formatted_message = self.formattedMessage(),
            .selected_string = self.selected_string,
            .array_prefix_len = 2,
            .array_sentinel = self.array_payload[2],
            .bitmask_word = self.bitmask_word,
            .main_thread_event_calls = event_family_count,
            .function_callback_event_calls = callback_boundary.function_callback_event_calls,
            .total_event_calls = self.total_event_calls,
            .conditional_paths_checked = self.saw_conditional_path,
            .vararg_payload_path_checked = self.saw_vararg_payload,
            .relative_location_path_checked = self.saw_rel_loc_payload,
            .function_callback_path_checked = callback_boundary.function_callback_path_checked,
            .registration_balance_restored = callback_boundary.registration_balance_restored,
            .checked_focus = reviewContract().focus,
        };
    }

    pub fn runPayloadBoundaryReplay(self: *Self) !PayloadBoundarySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        const events_before = self.total_event_calls;
        try self.replayMainIteration(4);

        return .{
            .stage_before_iteration = .initialized,
            .stage_after_iteration = self.stage(),
            .formatted_message = self.formattedMessage(),
            .selected_string = self.selected_string,
            .payload_prefix_len = 4,
            .payload_prefix = .{
                self.array_payload[0],
                self.array_payload[1],
                self.array_payload[2],
                self.array_payload[3],
            },
            .payload_sentinel = self.array_payload[4],
            .main_thread_event_calls = self.total_event_calls - events_before,
            .conditional_paths_checked = self.saw_conditional_path,
            .vararg_payload_path_checked = self.saw_vararg_payload,
            .relative_location_path_checked = self.saw_rel_loc_payload,
        };
    }

    pub fn runCallbackBoundaryReplay(self: *Self, count: i32) !CallbackBoundarySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;
        if (self.registration_depth != 0) return error.OutstandingRegistration;

        const events_before = self.total_event_calls;
        try self.registerFunctionCallback();
        const registration_depth_after_register = self.registration_depth;
        try self.replayFunctionIteration(count);
        try self.unregisterFunctionCallback();
        const registration_depth_after_unregister = self.registration_depth;

        return .{
            .stage_before_callback = .initialized,
            .stage_after_callback = self.stage(),
            .function_count = self.last_function_count,
            .function_callback_event_calls = self.total_event_calls - events_before,
            .total_event_calls_after_replay = self.total_event_calls,
            .function_callback_path_checked = self.saw_function_callback_path,
            .registration_depth_after_register = registration_depth_after_register,
            .registration_depth_after_unregister = registration_depth_after_unregister,
            .registration_balance_restored = registration_depth_after_unregister == 0,
        };
    }

    pub fn exit(self: *Self) !void {
        switch (self.stage()) {
            .initialized, .replay_complete => {},
            else => return error.InvalidLifecycleTransition,
        }
        if (self.registration_depth != 0) return error.OutstandingRegistration;

        self.exit_runs += 1;
        self.stage_state = .exited;
    }
};

test "trace-events sample review contract keeps focus and non-goals explicit" {
    const contract = TraceEventsReferenceSample.reviewContract();

    try std.testing.expectEqual(@as(usize, 6), contract.focus.len);
    try std.testing.expectEqual(SampleFocus.payload_shape, contract.focus[0]);
    try std.testing.expectEqual(SampleFocus.string_selection, contract.focus[1]);
    try std.testing.expectEqual(SampleFocus.formatted_message, contract.focus[2]);
    try std.testing.expectEqual(SampleFocus.conditional_event_families, contract.focus[3]);
    try std.testing.expectEqual(SampleFocus.function_callback_registration, contract.focus[4]);
    try std.testing.expectEqual(SampleFocus.ownership_and_lifetime, contract.focus[5]);

    try std.testing.expectEqual(@as(usize, 4), contract.non_goals.len);
    try std.testing.expectEqualStrings("CREATE_TRACE_POINTS parity", contract.non_goals[0]);
    try std.testing.expectEqualStrings("tracepoint macro parity from trace-events-sample.h", contract.non_goals[1]);
    try std.testing.expectEqualStrings("kernel thread scheduling or timeout parity", contract.non_goals[2]);
    try std.testing.expectEqualStrings("module registration or unregister wiring parity", contract.non_goals[3]);
}

test "trace-events sample replay keeps the anchor reviewable and non-runtime" {
    var sample = TraceEventsReferenceSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", replay.anchor);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expectEqualStrings("iter=7", replay.formatted_message);
    try std.testing.expectEqualStrings("Gandalf", replay.selected_string);
    try std.testing.expectEqual(@as(usize, 2), replay.array_prefix_len);
    try std.testing.expectEqual(@as(i32, 0), replay.array_sentinel);
    try std.testing.expectEqual(@as(usize, 0xdeadbeef), replay.bitmask_word);
    try std.testing.expectEqual(@as(usize, 6), replay.main_thread_event_calls);
    try std.testing.expectEqual(@as(usize, 2), replay.function_callback_event_calls);
    try std.testing.expectEqual(@as(usize, 8), replay.total_event_calls);
    try std.testing.expect(replay.conditional_paths_checked);
    try std.testing.expect(replay.vararg_payload_path_checked);
    try std.testing.expect(replay.relative_location_path_checked);
    try std.testing.expect(replay.function_callback_path_checked);
    try std.testing.expect(replay.registration_balance_restored);
    try std.testing.expectEqual(@as(usize, 6), replay.checked_focus.len);
    try std.testing.expectEqual(SampleFocus.payload_shape, replay.checked_focus[0]);
    try std.testing.expectEqual(SampleFocus.string_selection, replay.checked_focus[1]);
    try std.testing.expectEqual(SampleFocus.formatted_message, replay.checked_focus[2]);
    try std.testing.expectEqual(SampleFocus.conditional_event_families, replay.checked_focus[3]);
    try std.testing.expectEqual(SampleFocus.function_callback_registration, replay.checked_focus[4]);
    try std.testing.expectEqual(SampleFocus.ownership_and_lifetime, replay.checked_focus[5]);
    try std.testing.expectEqual(SampleStage.replay_complete, sample.stage());
    try std.testing.expectEqual(@as(usize, 1), sample.replay_runs);
}

test "trace-events sample keeps payload and callback boundaries explicit" {
    var module = TraceEventsReferenceSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runPayloadBoundaryReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runCallbackBoundaryReplay(3));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.replayMainIteration(0));
    try module.init();
    try std.testing.expectError(error.InvalidIterationCount, module.replayMainIteration(-1));

    const payload_boundary = try module.runPayloadBoundaryReplay();
    try std.testing.expectEqual(SampleStage.initialized, payload_boundary.stage_before_iteration);
    try std.testing.expectEqual(SampleStage.initialized, payload_boundary.stage_after_iteration);
    try std.testing.expectEqualStrings("iter=4", payload_boundary.formatted_message);
    try std.testing.expectEqualStrings("One ring to rule them all", payload_boundary.selected_string);
    try std.testing.expectEqual(@as(usize, 4), payload_boundary.payload_prefix_len);
    try std.testing.expectEqual(@as(i32, 1), payload_boundary.payload_prefix[0]);
    try std.testing.expectEqual(@as(i32, 2), payload_boundary.payload_prefix[1]);
    try std.testing.expectEqual(@as(i32, 3), payload_boundary.payload_prefix[2]);
    try std.testing.expectEqual(@as(i32, 4), payload_boundary.payload_prefix[3]);
    try std.testing.expectEqual(@as(i32, 0), payload_boundary.payload_sentinel);
    try std.testing.expectEqual(TraceEventsReferenceSample.event_family_count, payload_boundary.main_thread_event_calls);
    try std.testing.expect(payload_boundary.vararg_payload_path_checked);
    try std.testing.expect(payload_boundary.relative_location_path_checked);
    try std.testing.expect(payload_boundary.conditional_paths_checked);
    try std.testing.expectEqual(SampleStage.initialized, module.stage());

    try std.testing.expectError(error.FunctionCallbackNotRegistered, module.replayFunctionIteration(0));
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionCallback());
    const callback_boundary = try module.runCallbackBoundaryReplay(3);
    try std.testing.expectEqual(SampleStage.initialized, callback_boundary.stage_before_callback);
    try std.testing.expectEqual(SampleStage.initialized, callback_boundary.stage_after_callback);
    try std.testing.expectEqual(@as(i32, 3), callback_boundary.function_count);
    try std.testing.expectEqual(TraceEventsReferenceSample.function_callback_family_count, callback_boundary.function_callback_event_calls);
    try std.testing.expectEqual(@as(usize, 8), callback_boundary.total_event_calls_after_replay);
    try std.testing.expect(callback_boundary.function_callback_path_checked);
    try std.testing.expectEqual(@as(usize, 1), callback_boundary.registration_depth_after_register);
    try std.testing.expectEqual(@as(usize, 0), callback_boundary.registration_depth_after_unregister);
    try std.testing.expect(callback_boundary.registration_balance_restored);
    try std.testing.expectEqual(SampleStage.initialized, module.stage());
}

test "trace-events sample makes ownership and teardown boundaries explicit" {
    var module = TraceEventsReferenceSample{};

    try std.testing.expectEqual(SampleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());

    try module.init();
    try std.testing.expectEqual(SampleStage.initialized, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());
    try module.registerFunctionCallback();
    try std.testing.expectError(error.OutstandingRegistration, module.exit());
    try std.testing.expectError(error.OutstandingRegistration, module.runCallbackBoundaryReplay(1));
    try module.unregisterFunctionCallback();
    try module.exit();
    try std.testing.expectEqual(SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.replayMainIteration(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionCallback());
}
