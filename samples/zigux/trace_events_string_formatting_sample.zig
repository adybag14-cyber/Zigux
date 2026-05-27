const std = @import("std");

pub const SampleStage = enum(u8) {
    cold,
    initialized,
    replay_complete,
    exited,
};

pub const SampleFocus = enum {
    string_selection,
    formatted_message,
    bounded_destination_discipline,
    non_allocating_runtime_safe,
};

pub const SampleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selfcheck: bool,
};

pub const RenderedText = struct {
    bytes: [40]u8 = [_]u8{0} ** 40,
    len: usize = 0,
};

pub const ReplaySummary = struct {
    anchor: []const u8,
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    main_iteration_count: i32,
    selected_string: []const u8,
    formatted_message: RenderedText,
    selected_iteration_message: RenderedText,
    checked_focus: []const SampleFocus,
};

const random_strings = [_][]const u8{
    "Mother Goose",
    "Snoopy",
    "Gandalf",
    "Frodo",
    "One ring to rule them all",
};

pub const StringFormattingCase = struct {
    iteration_count: i32,
    selected_string: []const u8,
    formatted_message: RenderedText,
    selected_iteration_message: RenderedText,
};

pub const StringFormattingCycleSummary = struct {
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    cases: [random_strings.len]StringFormattingCase,
    checked_focus: []const SampleFocus,
};

pub const FormattingBoundaryCase = struct {
    iteration_count: i32,
    selected_string: []const u8,
    formatted_message: []const u8,
    selected_iteration_message: []const u8,
};

pub const FormattingBoundaryContract = struct {
    anchor: []const u8,
    review_focus: []const SampleFocus,
    preserves_initialized_stage: bool,
    replay_runs_after_cycle: usize,
    exact_iteration_fit_len: usize,
    exact_selected_fit_len: usize,
    exact_wrapped_selected_fit_len: usize,
    cases: [random_strings.len]FormattingBoundaryCase,
};

pub const TraceEventsStringFormattingSample = struct {
    const Self = @This();

    stage_state: SampleStage = .cold,
    init_runs: usize = 0,
    replay_runs: usize = 0,
    exit_runs: usize = 0,

    pub fn descriptor() SampleDescriptor {
        return .{
            .name = "trace_events_string_formatting_sample",
            .anchor = "samples/trace_events/trace-events-sample.c",
            .requires_runtime_substrate = false,
            .provides_selfcheck = true,
        };
    }

    pub fn stage(self: *const Self) SampleStage {
        return self.stage_state;
    }

    pub fn referencePattern() FormattingBoundaryContract {
        return .{
            .anchor = descriptor().anchor,
            .review_focus = &.{
                .string_selection,
                .formatted_message,
                .bounded_destination_discipline,
                .non_allocating_runtime_safe,
            },
            .preserves_initialized_stage = true,
            .replay_runs_after_cycle = 0,
            .exact_iteration_fit_len = 7,
            .exact_selected_fit_len = 12,
            .exact_wrapped_selected_fit_len = 32,
            .cases = .{
                .{
                    .iteration_count = 0,
                    .selected_string = "Mother Goose",
                    .formatted_message = "iter=0",
                    .selected_iteration_message = "Mother Goose iter=0",
                },
                .{
                    .iteration_count = 1,
                    .selected_string = "Snoopy",
                    .formatted_message = "iter=1",
                    .selected_iteration_message = "Snoopy iter=1",
                },
                .{
                    .iteration_count = 2,
                    .selected_string = "Gandalf",
                    .formatted_message = "iter=2",
                    .selected_iteration_message = "Gandalf iter=2",
                },
                .{
                    .iteration_count = 3,
                    .selected_string = "Frodo",
                    .formatted_message = "iter=3",
                    .selected_iteration_message = "Frodo iter=3",
                },
                .{
                    .iteration_count = 4,
                    .selected_string = "One ring to rule them all",
                    .formatted_message = "iter=4",
                    .selected_iteration_message = "One ring to rule them all iter=4",
                },
            },
        };
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn formatIterationMessageInto(
        self: *const Self,
        iteration_count: i32,
        destination: []u8,
    ) ![]const u8 {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;
        if (iteration_count < 0) return error.InvalidIterationCount;
        return std.fmt.bufPrint(destination, "iter={d}", .{iteration_count});
    }

    pub fn formatSelectedIterationMessageInto(
        self: *const Self,
        iteration_count: i32,
        destination: []u8,
    ) ![]const u8 {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;
        if (iteration_count < 0) return error.InvalidIterationCount;
        return std.fmt.bufPrint(
            destination,
            "{s} iter={d}",
            .{ selectedStringForIteration(iteration_count), iteration_count },
        );
    }

    pub fn runAnchorReplay(self: *Self, iteration_count: i32) !ReplaySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;
        if (iteration_count < 0) return error.InvalidIterationCount;

        const selected_string = selectedStringForIteration(iteration_count);

        var rendered = RenderedText{};
        const rendered_slice = try self.formatIterationMessageInto(
            iteration_count,
            &rendered.bytes,
        );
        rendered.len = rendered_slice.len;

        var selected_iteration_message = RenderedText{};
        const selected_iteration_slice = try self.formatSelectedIterationMessageInto(
            iteration_count,
            &selected_iteration_message.bytes,
        );
        selected_iteration_message.len = selected_iteration_slice.len;

        self.replay_runs += 1;
        self.stage_state = .replay_complete;

        return .{
            .anchor = descriptor().anchor,
            .stage_before_replay = .initialized,
            .stage_after_replay = self.stage(),
            .main_iteration_count = iteration_count,
            .selected_string = selected_string,
            .formatted_message = rendered,
            .selected_iteration_message = selected_iteration_message,
            .checked_focus = &.{
                .string_selection,
                .formatted_message,
                .bounded_destination_discipline,
                .non_allocating_runtime_safe,
            },
        };
    }

    pub fn runStringFormattingCycleReplay(self: *Self) !StringFormattingCycleSummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        var cases: [random_strings.len]StringFormattingCase = undefined;
        for (random_strings, 0..) |expected_string, i| {
            var rendered = RenderedText{};
            const rendered_slice = try self.formatIterationMessageInto(
                @intCast(i),
                &rendered.bytes,
            );
            rendered.len = rendered_slice.len;

            var selected_iteration_message = RenderedText{};
            const selected_iteration_slice = try self.formatSelectedIterationMessageInto(
                @intCast(i),
                &selected_iteration_message.bytes,
            );
            selected_iteration_message.len = selected_iteration_slice.len;

            cases[i] = .{
                .iteration_count = @intCast(i),
                .selected_string = expected_string,
                .formatted_message = rendered,
                .selected_iteration_message = selected_iteration_message,
            };
        }

        return .{
            .stage_before_replay = .initialized,
            .stage_after_replay = self.stage(),
            .cases = cases,
            .checked_focus = &.{
                .string_selection,
                .formatted_message,
                .bounded_destination_discipline,
                .non_allocating_runtime_safe,
            },
        };
    }

    pub fn exit(self: *Self) !void {
        switch (self.stage()) {
            .initialized, .replay_complete => {},
            else => return error.InvalidLifecycleTransition,
        }

        self.exit_runs += 1;
        self.stage_state = .exited;
    }

    fn selectedStringForIteration(iteration_count: i32) []const u8 {
        const index: usize = @intCast(@mod(iteration_count, @as(i32, @intCast(random_strings.len))));
        return random_strings[index];
    }
};

test "phase 5 trace-events formatting companion keeps the selected-string cue reviewable" {
    var sample = TraceEventsStringFormattingSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay(7);
    const expected_focus = [_]SampleFocus{
        .string_selection,
        .formatted_message,
        .bounded_destination_discipline,
        .non_allocating_runtime_safe,
    };

    try std.testing.expectEqualStrings("trace_events_string_formatting_sample", TraceEventsStringFormattingSample.descriptor().name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", replay.anchor);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expectEqual(@as(i32, 7), replay.main_iteration_count);
    try std.testing.expectEqualStrings("Gandalf", replay.selected_string);
    try std.testing.expectEqual(@as(usize, 6), replay.formatted_message.len);
    try std.testing.expectEqualSlices(u8, "iter=7", replay.formatted_message.bytes[0..replay.formatted_message.len]);
    try std.testing.expectEqual(@as(usize, 14), replay.selected_iteration_message.len);
    try std.testing.expectEqualSlices(
        u8,
        "Gandalf iter=7",
        replay.selected_iteration_message.bytes[0..replay.selected_iteration_message.len],
    );
    try std.testing.expectEqualSlices(SampleFocus, &expected_focus, replay.checked_focus);
}

test "phase 5 trace-events formatting companion keeps the modulo-selected string cycle reviewable" {
    var sample = TraceEventsStringFormattingSample{};
    const expected_focus = [_]SampleFocus{
        .string_selection,
        .formatted_message,
        .bounded_destination_discipline,
        .non_allocating_runtime_safe,
    };

    try sample.init();
    const cycle = try sample.runStringFormattingCycleReplay();
    try std.testing.expectEqual(SampleStage.initialized, cycle.stage_before_replay);
    try std.testing.expectEqual(SampleStage.initialized, cycle.stage_after_replay);
    try std.testing.expectEqual(@as(usize, 0), sample.replay_runs);
    try std.testing.expectEqualSlices(SampleFocus, &expected_focus, cycle.checked_focus);

    for (random_strings, 0..) |expected_string, i| {
        const current = cycle.cases[i];
        var expected_message: [40]u8 = undefined;
        var expected_selected_iteration_message: [40]u8 = undefined;
        const rendered = try std.fmt.bufPrint(&expected_message, "iter={d}", .{i});
        const selected_iteration_rendered = try std.fmt.bufPrint(
            &expected_selected_iteration_message,
            "{s} iter={d}",
            .{ expected_string, i },
        );

        try std.testing.expectEqual(@as(i32, @intCast(i)), current.iteration_count);
        try std.testing.expectEqualStrings(expected_string, current.selected_string);
        try std.testing.expectEqual(rendered.len, current.formatted_message.len);
        try std.testing.expectEqualSlices(
            u8,
            rendered,
            current.formatted_message.bytes[0..current.formatted_message.len],
        );
        try std.testing.expectEqual(selected_iteration_rendered.len, current.selected_iteration_message.len);
        try std.testing.expectEqualSlices(
            u8,
            selected_iteration_rendered,
            current.selected_iteration_message.bytes[0..current.selected_iteration_message.len],
        );
    }
}

test "phase 5 trace-events formatting companion exports a stable reference pattern for focused replays" {
    const contract = TraceEventsStringFormattingSample.referencePattern();
    const expected_focus = [_]SampleFocus{
        .string_selection,
        .formatted_message,
        .bounded_destination_discipline,
        .non_allocating_runtime_safe,
    };

    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", contract.anchor);
    try std.testing.expect(contract.preserves_initialized_stage);
    try std.testing.expectEqual(@as(usize, 0), contract.replay_runs_after_cycle);
    try std.testing.expectEqual(@as(usize, 7), contract.exact_iteration_fit_len);
    try std.testing.expectEqual(@as(usize, 12), contract.exact_selected_fit_len);
    try std.testing.expectEqual(@as(usize, 32), contract.exact_wrapped_selected_fit_len);
    try std.testing.expectEqualSlices(SampleFocus, &expected_focus, contract.review_focus);
    try std.testing.expectEqual(@as(i32, 4), contract.cases[4].iteration_count);
    try std.testing.expectEqualStrings("One ring to rule them all", contract.cases[4].selected_string);
    try std.testing.expectEqualStrings("iter=4", contract.cases[4].formatted_message);
    try std.testing.expectEqualStrings(
        "One ring to rule them all iter=4",
        contract.cases[4].selected_iteration_message,
    );
}

test "phase 5 trace-events formatting companion keeps lifecycle boundaries explicit" {
    var sample = TraceEventsStringFormattingSample{};
    var rendered_destination: [32]u8 = undefined;
    var selected_destination: [40]u8 = undefined;

    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runAnchorReplay(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runStringFormattingCycleReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.formatIterationMessageInto(1, &rendered_destination));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.formatSelectedIterationMessageInto(1, &selected_destination));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.exit());

    try sample.init();
    try std.testing.expectError(error.InvalidIterationCount, sample.runAnchorReplay(-1));
    try std.testing.expectError(error.InvalidIterationCount, sample.formatIterationMessageInto(-1, &rendered_destination));
    try std.testing.expectError(error.InvalidIterationCount, sample.formatSelectedIterationMessageInto(-1, &selected_destination));

    _ = try sample.runAnchorReplay(4);
    try sample.exit();
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 1), sample.replay_runs);
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runAnchorReplay(2));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runStringFormattingCycleReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.formatIterationMessageInto(2, &rendered_destination));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.formatSelectedIterationMessageInto(2, &selected_destination));
}

test "phase 5 trace-events formatting companion keeps bounded destination failures explicit" {
    var sample = TraceEventsStringFormattingSample{};
    try sample.init();

    var short_destination: [5]u8 = undefined;
    try std.testing.expectError(
        error.NoSpaceLeft,
        sample.formatIterationMessageInto(12, &short_destination),
    );
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.replay_runs);

    var exact_destination: [7]u8 = undefined;
    const exact_message = try sample.formatIterationMessageInto(12, &exact_destination);
    try std.testing.expectEqualStrings("iter=12", exact_message);
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.replay_runs);

    var short_selected_destination: [13]u8 = undefined;
    try std.testing.expectError(
        error.NoSpaceLeft,
        sample.formatSelectedIterationMessageInto(2, &short_selected_destination),
    );
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.replay_runs);

    var exact_selected_destination: [14]u8 = undefined;
    const exact_selected_message = try sample.formatSelectedIterationMessageInto(2, &exact_selected_destination);
    try std.testing.expectEqualStrings("Gandalf iter=2", exact_selected_message);
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.replay_runs);
}

test "phase 5 trace-events formatting companion keeps selected-string exact-fit boundaries explicit" {
    var sample = TraceEventsStringFormattingSample{};
    try sample.init();

    var short_selected_destination: [11]u8 = undefined;
    try std.testing.expectError(
        error.NoSpaceLeft,
        sample.formatSelectedIterationMessageInto(3, &short_selected_destination),
    );
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.replay_runs);

    var exact_selected_destination: [12]u8 = undefined;
    const exact_selected_message = try sample.formatSelectedIterationMessageInto(
        3,
        &exact_selected_destination,
    );
    try std.testing.expectEqualStrings("Frodo iter=3", exact_selected_message);
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.replay_runs);
}

test "phase 5 trace-events formatting companion keeps wrapped selected-string exact-fit boundaries explicit" {
    var sample = TraceEventsStringFormattingSample{};
    try sample.init();

    var short_wrapped_selected_destination: [31]u8 = undefined;
    try std.testing.expectError(
        error.NoSpaceLeft,
        sample.formatSelectedIterationMessageInto(9, &short_wrapped_selected_destination),
    );
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.replay_runs);

    var exact_wrapped_selected_destination: [32]u8 = undefined;
    const exact_wrapped_selected_message = try sample.formatSelectedIterationMessageInto(
        9,
        &exact_wrapped_selected_destination,
    );
    try std.testing.expectEqualStrings(
        "One ring to rule them all iter=9",
        exact_wrapped_selected_message,
    );
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.replay_runs);
}
