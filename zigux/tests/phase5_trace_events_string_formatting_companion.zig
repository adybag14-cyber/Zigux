const std = @import("std");
const companion = @import("trace_events_string_formatting_sample");

test "phase 5 trace-events string-formatting companion keeps the selected-string and formatting anchor reviewable" {
    const descriptor = companion.TraceEventsStringFormattingSample.descriptor();

    try std.testing.expectEqualStrings("trace_events_string_formatting_sample", descriptor.name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
}

test "phase 5 trace-events string-formatting companion keeps modulo string replay and exact-fit boundaries explicit" {
    var sample = companion.TraceEventsStringFormattingSample{};
    try sample.init();

    const cycle = try sample.runStringFormattingCycleReplay();
    const expected_focus = [_]companion.SampleFocus{
        .string_selection,
        .formatted_message,
        .bounded_destination_discipline,
        .non_allocating_runtime_safe,
    };

    try std.testing.expectEqual(companion.SampleStage.initialized, cycle.stage_before_replay);
    try std.testing.expectEqual(companion.SampleStage.initialized, cycle.stage_after_replay);
    try std.testing.expectEqualSlices(companion.SampleFocus, &expected_focus, cycle.checked_focus);
    try std.testing.expectEqualStrings("Gandalf", cycle.cases[2].selected_string);
    try std.testing.expectEqualStrings(
        "One ring to rule them all",
        cycle.cases[4].selected_string,
    );

    var exact_selected_destination: [14]u8 = undefined;
    const exact_selected_message = try sample.formatSelectedIterationMessageInto(
        2,
        &exact_selected_destination,
    );
    try std.testing.expectEqualStrings("Gandalf iter=2", exact_selected_message);

    var exact_wrapped_selected_destination: [32]u8 = undefined;
    const exact_wrapped_selected_message = try sample.formatSelectedIterationMessageInto(
        9,
        &exact_wrapped_selected_destination,
    );
    try std.testing.expectEqualStrings(
        "One ring to rule them all iter=9",
        exact_wrapped_selected_message,
    );
}
