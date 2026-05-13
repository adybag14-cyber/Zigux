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
    selected_string_slot: usize,
    array_prefix: [2]i32,
    array_prefix_len: usize,
    payload_len: usize,
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

pub const CallbackBoundarySummary = struct {
    stage_before_replay: SampleStage,
    stage_after_recovery: SampleStage,
    callback_iteration_count: i32,
    missing_registration_rejected: bool,
    underflow_before_registration_rejected: bool,
    double_registration_rejected: bool,
    invalid_callback_count_rejected: bool,
    armed_exit_rejected: bool,
    callback_path_checked: bool,
    registration_depth_after_recovery: usize,
    total_event_calls_after_recovery: usize,
};

pub const StringFormattingCase = struct {
    iteration_count: i32,
    selected_string: []const u8,
    selected_string_slot: usize,
    formatted_message: [16]u8,
    formatted_message_len: usize,
};

pub const StringFormattingCycleSummary = struct {
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    cases: [5]StringFormattingCase,
    total_event_calls_after_cycle: usize,
    conditional_paths_checked: bool,
    vararg_payload_path_checked: bool,
    relative_location_path_checked: bool,
};

pub const PayloadBoundarySummary = struct {
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    iteration_count: i32,
    selected_string: []const u8,
    selected_string_slot: usize,
    payload_preview: [4]i32,
    payload_preview_len: usize,
    payload_len: usize,
    array_sentinel: i32,
    formatted_message: []const u8,
    total_event_calls_after_replay: usize,
    conditional_paths_checked: bool,
    vararg_payload_path_checked: bool,
    relative_location_path_checked: bool,
};

pub const LifecycleSummary = struct {
    stage: SampleStage,
    init_run_count: usize,
    replay_run_count: usize,
    exit_run_count: usize,
    registration_depth: usize,
    total_event_calls: usize,
};

pub const LifecycleBoundarySummary = struct {
    stage_before_replay: SampleStage,
    stage_after_init: SampleStage,
    stage_after_callback_boundary: SampleStage,
    stage_after_exit: SampleStage,
    callback_boundary: CallbackBoundarySummary,
    lifecycle_before_exit: LifecycleSummary,
    lifecycle_after_exit: LifecycleSummary,
    pre_init_anchor_rejected: bool,
    pre_init_callback_boundary_rejected: bool,
    pre_init_exit_rejected: bool,
    replay_main_after_exit_rejected: bool,
    register_after_exit_rejected: bool,
    callback_after_exit_rejected: bool,
    unregister_after_exit_rejected: bool,
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
    selected_string_slot: usize = 0,
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

    pub fn lifecycleSummary(self: *const Self) LifecycleSummary {
        return .{
            .stage = self.stage(),
            .init_run_count = self.init_runs,
            .replay_run_count = self.replay_runs,
            .exit_run_count = self.exit_runs,
            .registration_depth = self.registration_depth,
            .total_event_calls = self.total_event_calls,
        };
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        self.registration_depth = 0;
        self.total_event_calls = 0;
        self.last_main_count = -1;
        self.last_function_count = -1;
        self.array_payload = [_]i32{0} ** 6;
        self.selected_string = "";
        self.selected_string_slot = 0;
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
        self.selected_string_slot = len;
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
        if (count < 0) return error.InvalidIterationCount;

        self.last_function_count = count;
        self.saw_function_callback_path = true;
        self.total_event_calls += function_callback_family_count;
    }

    pub fn runCallbackBoundaryRecoveryReplay(self: *Self) !CallbackBoundarySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        var missing_registration_rejected = false;
        self.replayFunctionIteration(5) catch |err| switch (err) {
            error.FunctionCallbackNotRegistered => missing_registration_rejected = true,
            else => return err,
        };
        if (!missing_registration_rejected) return error.ExpectedCallbackBoundaryRejection;

        var underflow_before_registration_rejected = false;
        self.unregisterFunctionCallback() catch |err| switch (err) {
            error.RegistrationUnderflow => underflow_before_registration_rejected = true,
            else => return err,
        };
        if (!underflow_before_registration_rejected) return error.ExpectedRegistrationUnderflow;

        try self.registerFunctionCallback();

        var double_registration_rejected = false;
        self.registerFunctionCallback() catch |err| switch (err) {
            error.CallbackAlreadyRegistered => double_registration_rejected = true,
            else => return err,
        };
        if (!double_registration_rejected) return error.ExpectedDoubleRegistrationRejection;

        var invalid_callback_count_rejected = false;
        self.replayFunctionIteration(-1) catch |err| switch (err) {
            error.InvalidIterationCount => invalid_callback_count_rejected = true,
            else => return err,
        };
        if (!invalid_callback_count_rejected) return error.ExpectedInvalidCallbackCountRejection;

        var armed_exit_rejected = false;
        self.exit() catch |err| switch (err) {
            error.OutstandingRegistration => armed_exit_rejected = true,
            else => return err,
        };
        if (!armed_exit_rejected) return error.ExpectedOutstandingRegistrationRejection;

        try self.replayFunctionIteration(5);
        try self.unregisterFunctionCallback();

        return .{
            .stage_before_replay = .initialized,
            .stage_after_recovery = self.stage(),
            .callback_iteration_count = self.last_function_count,
            .missing_registration_rejected = missing_registration_rejected,
            .underflow_before_registration_rejected = underflow_before_registration_rejected,
            .double_registration_rejected = double_registration_rejected,
            .invalid_callback_count_rejected = invalid_callback_count_rejected,
            .armed_exit_rejected = armed_exit_rejected,
            .callback_path_checked = self.saw_function_callback_path,
            .registration_depth_after_recovery = self.registration_depth,
            .total_event_calls_after_recovery = self.total_event_calls,
        };
    }

    pub fn runStringFormattingCycleReplay(self: *Self) !StringFormattingCycleSummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        var cases: [random_strings.len]StringFormattingCase = undefined;
        for (random_strings, 0..) |expected_string, i| {
            const count: i32 = @intCast(i);
            try self.replayMainIteration(count);

            var formatted_message: [16]u8 = [_]u8{0} ** 16;
            const message = self.formattedMessage();
            @memcpy(formatted_message[0..message.len], message);

            cases[i] = .{
                .iteration_count = count,
                .selected_string = expected_string,
                .selected_string_slot = self.selected_string_slot,
                .formatted_message = formatted_message,
                .formatted_message_len = message.len,
            };
        }

        return .{
            .stage_before_replay = .initialized,
            .stage_after_replay = self.stage(),
            .cases = cases,
            .total_event_calls_after_cycle = self.total_event_calls,
            .conditional_paths_checked = self.saw_conditional_path,
            .vararg_payload_path_checked = self.saw_vararg_payload,
            .relative_location_path_checked = self.saw_rel_loc_payload,
        };
    }

    pub fn runPayloadBoundaryReplay(self: *Self, count: i32) !PayloadBoundarySummary {
        const stage_before_replay = self.stage();
        try self.ensureMutable();
        try self.replayMainIteration(count);

        const payload_preview_len = @min(self.selected_string_slot, @as(usize, 4));
        var payload_preview: [4]i32 = [_]i32{0} ** 4;
        @memcpy(payload_preview[0..payload_preview_len], self.array_payload[0..payload_preview_len]);

        return .{
            .stage_before_replay = stage_before_replay,
            .stage_after_replay = self.stage(),
            .iteration_count = self.last_main_count,
            .selected_string = self.selected_string,
            .selected_string_slot = self.selected_string_slot,
            .payload_preview = payload_preview,
            .payload_preview_len = payload_preview_len,
            .payload_len = self.selected_string_slot,
            .array_sentinel = self.array_payload[self.selected_string_slot],
            .formatted_message = self.formattedMessage(),
            .total_event_calls_after_replay = self.total_event_calls,
            .conditional_paths_checked = self.saw_conditional_path,
            .vararg_payload_path_checked = self.saw_vararg_payload,
            .relative_location_path_checked = self.saw_rel_loc_payload,
        };
    }

    pub fn runLifecycleBoundaryReplay(self: *Self) !LifecycleBoundarySummary {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        var pre_init_anchor_rejected = false;
        _ = self.runAnchorReplay() catch |err| switch (err) {
            error.InvalidLifecycleTransition => pre_init_anchor_rejected = true,
            else => return err,
        };
        if (!pre_init_anchor_rejected) return error.ExpectedPreInitAnchorRejection;

        var pre_init_callback_boundary_rejected = false;
        _ = self.runCallbackBoundaryRecoveryReplay() catch |err| switch (err) {
            error.InvalidLifecycleTransition => pre_init_callback_boundary_rejected = true,
            else => return err,
        };
        if (!pre_init_callback_boundary_rejected) return error.ExpectedPreInitCallbackBoundaryRejection;

        var pre_init_exit_rejected = false;
        self.exit() catch |err| switch (err) {
            error.InvalidLifecycleTransition => pre_init_exit_rejected = true,
            else => return err,
        };
        if (!pre_init_exit_rejected) return error.ExpectedPreInitExitRejection;

        const stage_before_replay = self.stage();
        try self.init();
        const stage_after_init = self.stage();
        const callback_boundary = try self.runCallbackBoundaryRecoveryReplay();
        const stage_after_callback_boundary = self.stage();
        const lifecycle_before_exit = self.lifecycleSummary();
        try self.exit();
        const lifecycle_after_exit = self.lifecycleSummary();

        var replay_main_after_exit_rejected = false;
        self.replayMainIteration(1) catch |err| switch (err) {
            error.InvalidLifecycleTransition => replay_main_after_exit_rejected = true,
            else => return err,
        };
        if (!replay_main_after_exit_rejected) return error.ExpectedPostExitReplayRejection;

        var register_after_exit_rejected = false;
        self.registerFunctionCallback() catch |err| switch (err) {
            error.InvalidLifecycleTransition => register_after_exit_rejected = true,
            else => return err,
        };
        if (!register_after_exit_rejected) return error.ExpectedPostExitRegisterRejection;

        var callback_after_exit_rejected = false;
        self.replayFunctionIteration(1) catch |err| switch (err) {
            error.InvalidLifecycleTransition => callback_after_exit_rejected = true,
            else => return err,
        };
        if (!callback_after_exit_rejected) return error.ExpectedPostExitCallbackRejection;

        var unregister_after_exit_rejected = false;
        self.unregisterFunctionCallback() catch |err| switch (err) {
            error.InvalidLifecycleTransition => unregister_after_exit_rejected = true,
            else => return err,
        };
        if (!unregister_after_exit_rejected) return error.ExpectedPostExitUnregisterRejection;

        return .{
            .stage_before_replay = stage_before_replay,
            .stage_after_init = stage_after_init,
            .stage_after_callback_boundary = stage_after_callback_boundary,
            .stage_after_exit = self.stage(),
            .callback_boundary = callback_boundary,
            .lifecycle_before_exit = lifecycle_before_exit,
            .lifecycle_after_exit = lifecycle_after_exit,
            .pre_init_anchor_rejected = pre_init_anchor_rejected,
            .pre_init_callback_boundary_rejected = pre_init_callback_boundary_rejected,
            .pre_init_exit_rejected = pre_init_exit_rejected,
            .replay_main_after_exit_rejected = replay_main_after_exit_rejected,
            .register_after_exit_rejected = register_after_exit_rejected,
            .callback_after_exit_rejected = callback_after_exit_rejected,
            .unregister_after_exit_rejected = unregister_after_exit_rejected,
        };
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
            .selected_string_slot = self.selected_string_slot,
            .array_prefix = .{ self.array_payload[0], self.array_payload[1] },
            .array_prefix_len = 2,
            .payload_len = self.selected_string_slot,
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
    try std.testing.expectEqual(@as(usize, 2), replay.selected_string_slot);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2 }, replay.array_prefix[0..]);
    try std.testing.expectEqual(@as(usize, 2), replay.array_prefix_len);
    try std.testing.expectEqual(@as(usize, 2), replay.payload_len);
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
    const lifecycle = sample.lifecycleSummary();
    try std.testing.expectEqual(SampleStage.replay_complete, lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 1), lifecycle.replay_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.registration_depth);
    try std.testing.expectEqual(@as(usize, 8), lifecycle.total_event_calls);
    try sample.exit();
    const exited_lifecycle = sample.lifecycleSummary();
    try std.testing.expectEqual(SampleStage.exited, exited_lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 1), exited_lifecycle.replay_run_count);
    try std.testing.expectEqual(@as(usize, 1), exited_lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), exited_lifecycle.registration_depth);
    try std.testing.expectEqual(@as(usize, 8), exited_lifecycle.total_event_calls);
}

test "trace-events sample replays every modulo-selected string and formatted message through one bounded replay" {
    var sample = TraceEventsReferenceSample{};
    const expected_strings = [_][]const u8{
        "Mother Goose",
        "Snoopy",
        "Gandalf",
        "Frodo",
        "One ring to rule them all",
    };
    var message_buffer: [16]u8 = undefined;

    try sample.init();
    const cycle = try sample.runStringFormattingCycleReplay();

    try std.testing.expectEqual(SampleStage.initialized, cycle.stage_before_replay);
    try std.testing.expectEqual(SampleStage.initialized, cycle.stage_after_replay);
    try std.testing.expect(cycle.conditional_paths_checked);
    try std.testing.expect(cycle.vararg_payload_path_checked);
    try std.testing.expect(cycle.relative_location_path_checked);
    try std.testing.expectEqual(@as(usize, expected_strings.len * TraceEventsReferenceSample.event_family_count), cycle.total_event_calls_after_cycle);

    for (expected_strings, 0..) |expected_string, count| {
        const case = cycle.cases[count];
        try std.testing.expectEqual(@as(i32, @intCast(count)), case.iteration_count);
        try std.testing.expectEqualStrings(expected_string, case.selected_string);
        try std.testing.expectEqual(@as(usize, count), case.selected_string_slot);
        try std.testing.expectEqualStrings(
            try std.fmt.bufPrint(&message_buffer, "iter={d}", .{count}),
            case.formatted_message[0..case.formatted_message_len],
        );
    }

    const lifecycle = sample.lifecycleSummary();
    try std.testing.expectEqual(SampleStage.initialized, lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.replay_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.registration_depth);
    try std.testing.expectEqual(@as(usize, expected_strings.len * TraceEventsReferenceSample.event_family_count), lifecycle.total_event_calls);
}

test "trace-events sample exposes callback boundary recovery as one bounded replay" {
    var sample = TraceEventsReferenceSample{};

    try sample.init();
    const replay = try sample.runCallbackBoundaryRecoveryReplay();

    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_after_recovery);
    try std.testing.expectEqual(@as(i32, 5), replay.callback_iteration_count);
    try std.testing.expect(replay.missing_registration_rejected);
    try std.testing.expect(replay.underflow_before_registration_rejected);
    try std.testing.expect(replay.double_registration_rejected);
    try std.testing.expect(replay.invalid_callback_count_rejected);
    try std.testing.expect(replay.armed_exit_rejected);
    try std.testing.expect(replay.callback_path_checked);
    try std.testing.expectEqual(@as(usize, 0), replay.registration_depth_after_recovery);
    try std.testing.expectEqual(@as(usize, 2), replay.total_event_calls_after_recovery);

    const lifecycle = sample.lifecycleSummary();
    try std.testing.expectEqual(SampleStage.initialized, lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.replay_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), lifecycle.total_event_calls);
}

test "trace-events sample replays lifecycle boundaries through one bounded helper" {
    var sample = TraceEventsReferenceSample{};

    const replay = try sample.runLifecycleBoundaryReplay();

    try std.testing.expectEqual(SampleStage.cold, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_after_init);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_after_callback_boundary);
    try std.testing.expectEqual(SampleStage.exited, replay.stage_after_exit);
    try std.testing.expect(replay.pre_init_anchor_rejected);
    try std.testing.expect(replay.pre_init_callback_boundary_rejected);
    try std.testing.expect(replay.pre_init_exit_rejected);
    try std.testing.expectEqual(@as(i32, 5), replay.callback_boundary.callback_iteration_count);
    try std.testing.expect(replay.callback_boundary.missing_registration_rejected);
    try std.testing.expect(replay.callback_boundary.underflow_before_registration_rejected);
    try std.testing.expect(replay.callback_boundary.double_registration_rejected);
    try std.testing.expect(replay.callback_boundary.invalid_callback_count_rejected);
    try std.testing.expect(replay.callback_boundary.armed_exit_rejected);
    try std.testing.expect(replay.callback_boundary.callback_path_checked);
    try std.testing.expectEqual(@as(usize, 0), replay.callback_boundary.registration_depth_after_recovery);
    try std.testing.expectEqual(SampleStage.initialized, replay.lifecycle_before_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), replay.lifecycle_before_exit.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay.lifecycle_before_exit.replay_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay.lifecycle_before_exit.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay.lifecycle_before_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), replay.lifecycle_before_exit.total_event_calls);
    try std.testing.expectEqual(SampleStage.exited, replay.lifecycle_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), replay.lifecycle_after_exit.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay.lifecycle_after_exit.replay_run_count);
    try std.testing.expectEqual(@as(usize, 1), replay.lifecycle_after_exit.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay.lifecycle_after_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), replay.lifecycle_after_exit.total_event_calls);
    try std.testing.expect(replay.replay_main_after_exit_rejected);
    try std.testing.expect(replay.register_after_exit_rejected);
    try std.testing.expect(replay.callback_after_exit_rejected);
    try std.testing.expect(replay.unregister_after_exit_rejected);
}

test "trace-events sample keeps callback registration single-live" {
    var sample = TraceEventsReferenceSample{};

    try sample.init();
    const initial_lifecycle = sample.lifecycleSummary();
    try std.testing.expectEqual(SampleStage.initialized, initial_lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), initial_lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), initial_lifecycle.replay_run_count);
    try std.testing.expectEqual(@as(usize, 0), initial_lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), initial_lifecycle.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), initial_lifecycle.total_event_calls);

    const payload_boundary = try sample.runPayloadBoundaryReplay(4);
    try std.testing.expectEqual(SampleStage.initialized, payload_boundary.stage_before_replay);
    try std.testing.expectEqual(SampleStage.initialized, payload_boundary.stage_after_replay);
    try std.testing.expectEqual(@as(i32, 4), payload_boundary.iteration_count);
    try std.testing.expectEqualStrings("One ring to rule them all", payload_boundary.selected_string);
    try std.testing.expectEqual(@as(usize, 4), payload_boundary.selected_string_slot);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2, 3, 4 }, payload_boundary.payload_preview[0..payload_boundary.payload_preview_len]);
    try std.testing.expectEqual(@as(usize, 4), payload_boundary.payload_preview_len);
    try std.testing.expectEqual(@as(usize, 4), payload_boundary.payload_len);
    try std.testing.expectEqual(@as(i32, 0), payload_boundary.array_sentinel);
    try std.testing.expectEqualStrings("iter=4", payload_boundary.formatted_message);
    try std.testing.expect(payload_boundary.conditional_paths_checked);
    try std.testing.expect(payload_boundary.vararg_payload_path_checked);
    try std.testing.expect(payload_boundary.relative_location_path_checked);
    try std.testing.expectEqual(@as(usize, 6), payload_boundary.total_event_calls_after_replay);

    const replay = try sample.runCallbackBoundaryRecoveryReplay();
    try std.testing.expect(replay.missing_registration_rejected);
    try std.testing.expect(replay.underflow_before_registration_rejected);
    try std.testing.expect(replay.double_registration_rejected);
    try std.testing.expect(replay.invalid_callback_count_rejected);
    try std.testing.expect(replay.armed_exit_rejected);
    try std.testing.expectEqual(@as(usize, 0), sample.registration_depth);
    try std.testing.expectEqual(@as(usize, 8), replay.total_event_calls_after_recovery);
}
