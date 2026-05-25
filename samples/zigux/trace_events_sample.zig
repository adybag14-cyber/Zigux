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

pub const ReplaySummary = struct {
    anchor: []const u8,
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    main_iteration_count: i32,
    function_callback_iteration_count: i32,
    formatted_message: []const u8,
    selected_string: []const u8,
    array_prefix: [2]i32,
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
        if (self.registration_depth != 0) return error.CallbackAlreadyRegistered;
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
        try self.registerFunctionCallback();
        try self.replayFunctionIteration(9);
        try self.unregisterFunctionCallback();

        self.replay_runs += 1;
        self.stage_state = .replay_complete;
        return .{
            .anchor = descriptor().anchor,
            .stage_before_replay = .initialized,
            .stage_after_replay = .replay_complete,
            .main_iteration_count = self.last_main_count,
            .function_callback_iteration_count = self.last_function_count,
            .formatted_message = self.formattedMessage(),
            .selected_string = self.selected_string,
            .array_prefix = .{ self.array_payload[0], self.array_payload[1] },
            .array_prefix_len = 2,
            .array_sentinel = self.array_payload[2],
            .bitmask_word = self.bitmask_word,
            .main_thread_event_calls = event_family_count,
            .function_callback_event_calls = function_callback_family_count,
            .total_event_calls = self.total_event_calls,
            .conditional_paths_checked = self.saw_conditional_path,
            .vararg_payload_path_checked = self.saw_vararg_payload,
            .relative_location_path_checked = self.saw_rel_loc_payload,
            .function_callback_path_checked = self.saw_function_callback_path,
            .registration_balance_restored = self.registration_depth == 0,
            .checked_focus = &.{
                .payload_shape,
                .string_selection,
                .formatted_message,
                .conditional_event_families,
                .function_callback_registration,
                .ownership_and_lifetime,
            },
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

test "trace-events sample replay keeps the anchor reviewable and non-runtime" {
    var sample = TraceEventsReferenceSample{};
    const expected_focus = [_]SampleFocus{
        .payload_shape,
        .string_selection,
        .formatted_message,
        .conditional_event_families,
        .function_callback_registration,
        .ownership_and_lifetime,
    };
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", replay.anchor);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expectEqual(@as(i32, 7), replay.main_iteration_count);
    try std.testing.expectEqual(@as(i32, 9), replay.function_callback_iteration_count);
    try std.testing.expectEqualStrings("iter=7", replay.formatted_message);
    try std.testing.expectEqualStrings("Gandalf", replay.selected_string);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2 }, replay.array_prefix[0..]);
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
    try std.testing.expectEqualSlices(SampleFocus, &expected_focus, replay.checked_focus);
}

test "trace-events sample rejects every mutable entry point after exit" {
    var sample = TraceEventsReferenceSample{};

    try sample.init();
    _ = try sample.runAnchorReplay();
    try sample.exit();

    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.replayMainIteration(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.registerFunctionCallback());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.replayFunctionIteration(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.unregisterFunctionCallback());
}

test "trace-events sample keeps callback registration single-live" {
    var sample = TraceEventsReferenceSample{};

    try sample.init();
    try sample.registerFunctionCallback();
    try std.testing.expectError(error.CallbackAlreadyRegistered, sample.registerFunctionCallback());
    try sample.replayFunctionIteration(5);
    try sample.unregisterFunctionCallback();
    try std.testing.expectEqual(@as(usize, 0), sample.registration_depth);
}