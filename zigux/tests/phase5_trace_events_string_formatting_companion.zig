const std = @import("std");
const trace_events_string_formatting_sample = @import("trace_events_string_formatting_sample");

const Sample = trace_events_string_formatting_sample.TraceEventsStringFormattingSample;
const SampleFocus = trace_events_string_formatting_sample.SampleFocus;

test "phase 5 focused replay keeps the trace-events string-formatting reference pattern aligned" {
    const contract = Sample.referencePattern();
    const expected_focus = [_]SampleFocus{
        .string_selection,
        .formatted_message,
        .bounded_destination_discipline,
        .non_allocating_runtime_safe,
    };

    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", contract.anchor);
    try std.testing.expect(contract.preserves_initialized_stage);
    try std.testing.expectEqual(@as(usize, 0), contract.replay_runs_after_cycle);
    try std.testing.expectEqualSlices(SampleFocus, &expected_focus, contract.review_focus);

    for (contract.cases, 0..) |current, index| {
        try std.testing.expectEqual(@as(i32, @intCast(index)), current.iteration_count);
        try std.testing.expectEqualStrings(contract.cases[index].selected_string, current.selected_string);
        try std.testing.expectEqualStrings(contract.cases[index].formatted_message, current.formatted_message);
        try std.testing.expectEqualStrings(
            contract.cases[index].selected_iteration_message,
            current.selected_iteration_message,
        );
    }
}

test "phase 5 focused replay keeps exact-fit formatting boundaries executable" {
    const contract = Sample.referencePattern();

    var sample = Sample{};
    try sample.init();

    var iteration_storage: [16]u8 = undefined;
    try std.testing.expectError(
        error.NoSpaceLeft,
        sample.formatIterationMessageInto(12, iteration_storage[0 .. contract.exact_iteration_fit_len - 1]),
    );
    const exact_iteration = try sample.formatIterationMessageInto(
        12,
        iteration_storage[0..contract.exact_iteration_fit_len],
    );
    try std.testing.expectEqualStrings("iter=12", exact_iteration);

    var selected_storage: [40]u8 = undefined;
    try std.testing.expectError(
        error.NoSpaceLeft,
        sample.formatSelectedIterationMessageInto(3, selected_storage[0 .. contract.exact_selected_fit_len - 1]),
    );
    const exact_selected = try sample.formatSelectedIterationMessageInto(
        3,
        selected_storage[0..contract.exact_selected_fit_len],
    );
    try std.testing.expectEqualStrings("Frodo iter=3", exact_selected);

    try std.testing.expectError(
        error.NoSpaceLeft,
        sample.formatSelectedIterationMessageInto(9, selected_storage[0 .. contract.exact_wrapped_selected_fit_len - 1]),
    );
    const exact_wrapped = try sample.formatSelectedIterationMessageInto(
        9,
        selected_storage[0..contract.exact_wrapped_selected_fit_len],
    );
    try std.testing.expectEqualStrings("One ring to rule them all iter=9", exact_wrapped);
    try std.testing.expectEqual(trace_events_string_formatting_sample.SampleStage.initialized, sample.stage());
    try std.testing.expectEqual(contract.replay_runs_after_cycle, sample.replay_runs);
}
