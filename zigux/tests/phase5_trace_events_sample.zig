const std = @import("std");
const sample = @import("trace_events_sample");

test "phase 5 trace-events sample stays in the reference-sample lane" {
    const descriptor = sample.TraceEventsReferenceSample.descriptor();

    try std.testing.expectEqualStrings("trace_events_sample", descriptor.name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
}

test "phase 5 trace-events sample replays the bounded payload and callback idioms" {
    var module = sample.TraceEventsReferenceSample{};
    const expected_focus = [_]sample.SampleFocus{
        .payload_shape,
        .string_selection,
        .formatted_message,
        .conditional_event_families,
        .function_callback_registration,
        .ownership_and_lifetime,
    };
    try module.init();
    const replay = try module.runAnchorReplay();

    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay.stage_after_replay);
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
    try std.testing.expectEqual(@as(usize, sample.TraceEventsReferenceSample.event_family_count), replay.main_thread_event_calls);
    try std.testing.expectEqual(@as(usize, sample.TraceEventsReferenceSample.function_callback_family_count), replay.function_callback_event_calls);
    try std.testing.expectEqual(@as(usize, 8), replay.total_event_calls);
    try std.testing.expect(replay.conditional_paths_checked);
    try std.testing.expect(replay.vararg_payload_path_checked);
    try std.testing.expect(replay.relative_location_path_checked);
    try std.testing.expect(replay.function_callback_path_checked);
    try std.testing.expect(replay.registration_balance_restored);
    try std.testing.expectEqual(@as(usize, 6), replay.checked_focus.len);
    try std.testing.expectEqualSlices(sample.SampleFocus, &expected_focus, replay.checked_focus);
    const lifecycle = module.lifecycleSummary();
    try std.testing.expectEqual(sample.SampleStage.replay_complete, lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 1), lifecycle.replay_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.registration_depth);
    try std.testing.expectEqual(@as(usize, 8), lifecycle.total_event_calls);

    try module.exit();
    const exited_lifecycle = module.lifecycleSummary();
    try std.testing.expectEqual(sample.SampleStage.exited, exited_lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 1), exited_lifecycle.replay_run_count);
    try std.testing.expectEqual(@as(usize, 1), exited_lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), exited_lifecycle.registration_depth);
    try std.testing.expectEqual(@as(usize, 8), exited_lifecycle.total_event_calls);
}

test "phase 5 trace-events sample keeps payload and callback boundaries explicit" {
    var module = sample.TraceEventsReferenceSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, module.replayMainIteration(0));
    try module.init();
    try std.testing.expectError(error.InvalidIterationCount, module.replayMainIteration(-1));

    const payload_boundary = try module.runPayloadBoundaryReplay(4);
    try std.testing.expectEqual(sample.SampleStage.initialized, payload_boundary.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.initialized, payload_boundary.stage_after_replay);
    try std.testing.expectEqual(@as(i32, 4), payload_boundary.iteration_count);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2, 3, 4 }, payload_boundary.payload_preview[0..payload_boundary.payload_preview_len]);
    try std.testing.expectEqual(@as(usize, 4), payload_boundary.payload_preview_len);
    try std.testing.expectEqual(@as(usize, 4), payload_boundary.payload_len);
    try std.testing.expectEqual(@as(i32, 0), payload_boundary.array_sentinel);
    try std.testing.expectEqualStrings("One ring to rule them all", payload_boundary.selected_string);
    try std.testing.expectEqual(@as(usize, 4), payload_boundary.selected_string_slot);
    try std.testing.expectEqualStrings("iter=4", payload_boundary.formatted_message);
    try std.testing.expect(payload_boundary.vararg_payload_path_checked);
    try std.testing.expect(payload_boundary.relative_location_path_checked);
    try std.testing.expect(payload_boundary.conditional_paths_checked);
    try std.testing.expectEqual(@as(usize, sample.TraceEventsReferenceSample.event_family_count), payload_boundary.total_event_calls_after_replay);

    const callback_boundary = try module.runCallbackBoundaryRecoveryReplay();
    try std.testing.expectEqual(sample.SampleStage.initialized, callback_boundary.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.initialized, callback_boundary.stage_after_recovery);
    try std.testing.expectEqual(@as(i32, 5), callback_boundary.callback_iteration_count);
    try std.testing.expect(callback_boundary.missing_registration_rejected);
    try std.testing.expect(callback_boundary.underflow_before_registration_rejected);
    try std.testing.expect(callback_boundary.double_registration_rejected);
    try std.testing.expect(callback_boundary.invalid_callback_count_rejected);
    try std.testing.expect(callback_boundary.armed_exit_rejected);
    try std.testing.expect(callback_boundary.callback_path_checked);
    try std.testing.expectEqual(@as(usize, 0), callback_boundary.registration_depth_after_recovery);
    try std.testing.expectEqual(@as(usize, 8), callback_boundary.total_event_calls_after_recovery);
}

test "phase 5 trace-events sample keeps the full string and formatting cycle explicit" {
    var module = sample.TraceEventsReferenceSample{};
    const expected_strings = [_][]const u8{
        "Mother Goose",
        "Snoopy",
        "Gandalf",
        "Frodo",
        "One ring to rule them all",
    };
    var message_buffer: [16]u8 = undefined;

    try module.init();
    const cycle = try module.runStringFormattingCycleReplay();

    try std.testing.expectEqual(sample.SampleStage.initialized, cycle.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.initialized, cycle.stage_after_replay);
    try std.testing.expect(cycle.conditional_paths_checked);
    try std.testing.expect(cycle.vararg_payload_path_checked);
    try std.testing.expect(cycle.relative_location_path_checked);
    try std.testing.expectEqual(@as(usize, expected_strings.len * sample.TraceEventsReferenceSample.event_family_count), cycle.total_event_calls_after_cycle);

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

    const lifecycle = module.lifecycleSummary();
    try std.testing.expectEqual(sample.SampleStage.initialized, lifecycle.stage);
    try std.testing.expectEqual(@as(usize, 1), lifecycle.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.replay_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), lifecycle.registration_depth);
    try std.testing.expectEqual(@as(usize, expected_strings.len * sample.TraceEventsReferenceSample.event_family_count), lifecycle.total_event_calls);
}

test "phase 5 trace-events sample makes ownership and teardown boundaries explicit" {
    var module = sample.TraceEventsReferenceSample{};

    const replay = try module.runLifecycleBoundaryReplay();

    try std.testing.expectEqual(sample.SampleStage.cold, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_after_init);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_after_callback_boundary);
    try std.testing.expectEqual(sample.SampleStage.exited, replay.stage_after_exit);
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
    try std.testing.expectEqual(@as(usize, 2), replay.callback_boundary.total_event_calls_after_recovery);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.lifecycle_before_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), replay.lifecycle_before_exit.init_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay.lifecycle_before_exit.replay_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay.lifecycle_before_exit.exit_run_count);
    try std.testing.expectEqual(@as(usize, 0), replay.lifecycle_before_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), replay.lifecycle_before_exit.total_event_calls);
    try std.testing.expectEqual(sample.SampleStage.exited, replay.lifecycle_after_exit.stage);
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
