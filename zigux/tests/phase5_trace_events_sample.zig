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
    try module.init();
    const replay = try module.runAnchorReplay();

    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expectEqualStrings("iter=7", replay.formatted_message);
    try std.testing.expectEqualStrings("Gandalf", replay.selected_string);
    try std.testing.expectEqual(@as(usize, 2), replay.selected_index);
    try std.testing.expectEqual(@as(usize, 2), replay.array_prefix_len);
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
    try std.testing.expectEqual(sample.SampleFocus.payload_shape, replay.checked_focus[0]);
    try std.testing.expectEqual(sample.SampleFocus.string_selection, replay.checked_focus[1]);
    try std.testing.expectEqual(sample.SampleFocus.formatted_message, replay.checked_focus[2]);
    try std.testing.expectEqual(sample.SampleFocus.conditional_event_families, replay.checked_focus[3]);
    try std.testing.expectEqual(sample.SampleFocus.function_callback_registration, replay.checked_focus[4]);
    try std.testing.expectEqual(sample.SampleFocus.ownership_and_lifetime, replay.checked_focus[5]);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.replay_runs);
}

test "phase 5 trace-events sample keeps payload and callback boundaries explicit" {
    var module = sample.TraceEventsReferenceSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runPayloadBoundaryReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runCallbackBoundaryReplay(3));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.replayMainIteration(0));
    try module.init();
    try std.testing.expectError(error.InvalidIterationCount, module.replayMainIteration(-1));

    const payload_boundary = try module.runPayloadBoundaryReplay();
    try std.testing.expectEqual(sample.SampleStage.initialized, payload_boundary.stage_before_iteration);
    try std.testing.expectEqual(sample.SampleStage.initialized, payload_boundary.stage_after_iteration);
    try std.testing.expectEqualStrings("iter=4", payload_boundary.formatted_message);
    try std.testing.expectEqualStrings("One ring to rule them all", payload_boundary.selected_string);
    try std.testing.expectEqual(@as(usize, 4), payload_boundary.selected_index);
    try std.testing.expectEqual(@as(usize, 4), payload_boundary.payload_prefix_len);
    try std.testing.expectEqual(@as(i32, 1), payload_boundary.payload_prefix[0]);
    try std.testing.expectEqual(@as(i32, 2), payload_boundary.payload_prefix[1]);
    try std.testing.expectEqual(@as(i32, 3), payload_boundary.payload_prefix[2]);
    try std.testing.expectEqual(@as(i32, 4), payload_boundary.payload_prefix[3]);
    try std.testing.expectEqual(@as(i32, 0), payload_boundary.payload_sentinel);
    try std.testing.expectEqual(@as(usize, sample.TraceEventsReferenceSample.event_family_count), payload_boundary.main_thread_event_calls);
    try std.testing.expect(payload_boundary.vararg_payload_path_checked);
    try std.testing.expect(payload_boundary.relative_location_path_checked);
    try std.testing.expect(payload_boundary.conditional_paths_checked);
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());

    try std.testing.expectError(error.FunctionCallbackNotRegistered, module.replayFunctionIteration(0));
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionCallback());
    const callback_boundary = try module.runCallbackBoundaryReplay(3);
    try std.testing.expectEqual(sample.SampleStage.initialized, callback_boundary.stage_before_callback);
    try std.testing.expectEqual(sample.SampleStage.initialized, callback_boundary.stage_after_callback);
    try std.testing.expectEqual(@as(i32, 3), callback_boundary.function_count);
    try std.testing.expectEqual(@as(usize, sample.TraceEventsReferenceSample.function_callback_family_count), callback_boundary.function_callback_event_calls);
    try std.testing.expectEqual(@as(usize, 8), callback_boundary.total_event_calls_after_replay);
    try std.testing.expect(callback_boundary.function_callback_path_checked);
    try std.testing.expectEqual(@as(usize, 1), callback_boundary.registration_depth_after_register);
    try std.testing.expectEqual(@as(usize, 0), callback_boundary.registration_depth_after_unregister);
    try std.testing.expect(callback_boundary.registration_balance_restored);
    try std.testing.expectEqual(@as(usize, 6), callback_boundary.checked_focus.len);
    try std.testing.expectEqual(sample.SampleFocus.payload_shape, callback_boundary.checked_focus[0]);
    try std.testing.expectEqual(sample.SampleFocus.string_selection, callback_boundary.checked_focus[1]);
    try std.testing.expectEqual(sample.SampleFocus.formatted_message, callback_boundary.checked_focus[2]);
    try std.testing.expectEqual(sample.SampleFocus.conditional_event_families, callback_boundary.checked_focus[3]);
    try std.testing.expectEqual(sample.SampleFocus.function_callback_registration, callback_boundary.checked_focus[4]);
    try std.testing.expectEqual(sample.SampleFocus.ownership_and_lifetime, callback_boundary.checked_focus[5]);
}

test "phase 5 trace-events sample keeps the public conditional helper explicit" {
    var module = sample.TraceEventsReferenceSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runConditionalBoundaryReplay(0));
    try module.init();

    const expected_strings = [_][]const u8{
        "Mother Goose",
        "Snoopy",
        "Gandalf",
        "Frodo",
        "One ring to rule them all",
        "Mother Goose",
    };

    for (expected_strings, 0..) |expected_string, count| {
        const boundary = try module.runConditionalBoundaryReplay(@intCast(count));
        var expected_message_buffer: [16]u8 = undefined;
        const expected_message = try std.fmt.bufPrint(&expected_message_buffer, "iter={d}", .{count});

        try std.testing.expectEqual(sample.SampleStage.initialized, boundary.stage_before_iteration);
        try std.testing.expectEqual(sample.SampleStage.initialized, boundary.stage_after_iteration);
        try std.testing.expectEqual(@as(i32, @intCast(count)), boundary.main_count);
        try std.testing.expectEqualStrings(expected_message, boundary.formatted_message);
        try std.testing.expectEqualStrings(expected_string, boundary.selected_string);
        try std.testing.expectEqual(@as(usize, count % 5), boundary.selected_index);
        try std.testing.expectEqual(@as(usize, 0xdeadbeef), boundary.bitmask_word);
        try std.testing.expectEqual(sample.TraceEventsReferenceSample.event_family_count, boundary.main_thread_event_calls);
        try std.testing.expectEqual(sample.TraceEventsReferenceSample.event_family_count * (count + 1), boundary.total_event_calls_after_replay);
        try std.testing.expect(boundary.conditional_paths_checked);
        try std.testing.expect(boundary.vararg_payload_path_checked);
        try std.testing.expect(boundary.relative_location_path_checked);
    }
}

test "phase 5 trace-events sample keeps ownership replay explicit" {
    var module = sample.TraceEventsReferenceSample{};

    var summary = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.cold, summary.stage);
    try std.testing.expectEqual(@as(usize, 0), summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), summary.total_event_calls);
    try std.testing.expectEqual(@as(usize, 0), summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.replay_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.exit_runs);
    try std.testing.expectEqualStrings("", summary.selected_string);
    try std.testing.expectEqualStrings("", summary.formatted_message);

    const ownership_replay = try module.runOwnershipReplay();
    try std.testing.expectEqual(sample.SampleStage.cold, ownership_replay.stage_before_init);
    try std.testing.expectEqual(sample.SampleStage.initialized, ownership_replay.stage_after_init);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, ownership_replay.stage_after_replay);
    try std.testing.expectEqual(sample.SampleStage.exited, ownership_replay.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 1), ownership_replay.init_runs);
    try std.testing.expectEqual(@as(usize, 1), ownership_replay.replay_runs);
    try std.testing.expectEqual(@as(usize, 1), ownership_replay.exit_runs);
    try std.testing.expectEqual(@as(usize, 8), ownership_replay.total_event_calls);
    try std.testing.expectEqualStrings("Gandalf", ownership_replay.selected_string);
    try std.testing.expectEqual(@as(usize, 2), ownership_replay.selected_index);
    try std.testing.expectEqualStrings("iter=7", ownership_replay.formatted_message);
    try std.testing.expectEqual(@as(usize, 2), ownership_replay.function_callback_event_calls);
    try std.testing.expect(ownership_replay.registration_balance_restored);
    try std.testing.expect(ownership_replay.saw_conditional_path);
    try std.testing.expect(ownership_replay.saw_vararg_payload);
    try std.testing.expect(ownership_replay.saw_rel_loc_payload);
    try std.testing.expect(ownership_replay.saw_function_callback_path);

    summary = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.exited, summary.stage);
    try std.testing.expectEqual(@as(usize, 0), summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 8), summary.total_event_calls);
    try std.testing.expectEqual(@as(usize, 1), summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), summary.replay_runs);
    try std.testing.expectEqual(@as(usize, 1), summary.exit_runs);
    try std.testing.expectEqualStrings("Gandalf", summary.selected_string);
    try std.testing.expectEqualStrings("iter=7", summary.formatted_message);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runOwnershipReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionCallback());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.replayMainIteration(1));
}
