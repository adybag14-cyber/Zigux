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
    bytes: [16]u8 = [_]u8{0} ** 16,
    len: usize = 0,
};

pub const ReplaySummary = struct {
    anchor: []const u8,
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    main_iteration_count: i32,
    selected_string: []const u8,
    formatted_message: RenderedText,
    checked_focus: []const SampleFocus,
};

const random_strings = [_][]const u8{
    "Mother Goose",
    "Snoopy",
    "Gandalf",
    "Frodo",
    "One ring to rule them all",
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

        self.replay_runs += 1;
        self.stage_state = .replay_complete;

        return .{
            .anchor = descriptor().anchor,
            .stage_before_replay = .initialized,
            .stage_after_replay = self.stage(),
            .main_iteration_count = iteration_count,
            .selected_string = selected_string,
            .formatted_message = rendered,
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
    try std.testing.expectEqualSlices(SampleFocus, &expected_focus, replay.checked_focus);
}

test "phase 5 trace-events formatting companion keeps lifecycle boundaries explicit" {
    var sample = TraceEventsStringFormattingSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runAnchorReplay(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.exit());
    try sample.init();
    try std.testing.expectError(error.InvalidIterationCount, sample.runAnchorReplay(-1));
    _ = try sample.runAnchorReplay(4);
    try sample.exit();
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 1), sample.replay_runs);
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.runAnchorReplay(2));
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
    const rendered = try sample.formatIterationMessageInto(12, &exact_destination);
    try std.testing.expectEqualStrings("iter=12", rendered);
    try std.testing.expectEqual(SampleStage.initialized, sample.stage());
}
