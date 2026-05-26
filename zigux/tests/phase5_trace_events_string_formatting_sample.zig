const std = @import("std");
const companion = @import("trace_events_string_formatting_sample");

test "phase 5 trace-events string-formatting companion keeps the anchor-local formatting idiom reviewable through a focused replay" {
    const descriptor = companion.TraceEventsStringFormattingSample.descriptor();
    var sample = companion.TraceEventsStringFormattingSample{};
    const expected_focus = [_]companion.SampleFocus{
        .string_selection,
        .formatted_message,
        .bounded_destination_discipline,
        .non_allocating_runtime_safe,
    };

    try std.testing.expectEqualStrings("trace_events_string_formatting_sample", descriptor.name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);

    try sample.init();
    const replay = try sample.runAnchorReplay(7);
    try std.testing.expectEqual(companion.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(companion.SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expectEqual(@as(i32, 7), replay.main_iteration_count);
    try std.testing.expectEqualStrings("Gandalf", replay.selected_string);
    try std.testing.expectEqualStrings("iter=7", replay.formatted_message.bytes[0..replay.formatted_message.len]);
    try std.testing.expectEqualStrings(
        "Gandalf iter=7",
        replay.selected_iteration_message.bytes[0..replay.selected_iteration_message.len],
    );
    try std.testing.expectEqualSlices(companion.SampleFocus, &expected_focus, replay.checked_focus);
}

test "phase 5 trace-events string-formatting companion keeps exact-fit and wrapped boundaries explicit through the focused replay" {
    var sample = companion.TraceEventsStringFormattingSample{};
    try sample.init();

    var exact_destination: [7]u8 = undefined;
    const exact_message = try sample.formatIterationMessageInto(12, &exact_destination);
    try std.testing.expectEqualStrings("iter=12", exact_message);
    try std.testing.expectEqual(companion.SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.replay_runs);

    var exact_selected_destination: [14]u8 = undefined;
    const exact_selected_message = try sample.formatSelectedIterationMessageInto(2, &exact_selected_destination);
    try std.testing.expectEqualStrings("Gandalf iter=2", exact_selected_message);
    try std.testing.expectEqual(companion.SampleStage.initialized, sample.stage());
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
    try std.testing.expectEqual(companion.SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(@as(usize, 0), sample.replay_runs);
}
