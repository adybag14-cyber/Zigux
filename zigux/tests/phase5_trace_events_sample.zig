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

test "phase 5 trace-events sample keeps the conditional-event boundary explicit" {
    var module = sample.TraceEventsReferenceSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runConditionalBoundaryReplay(0));
    try module.init();

    const conditional_boundary = try module.runConditionalBoundaryReplay(0);
    try std.testing.expectEqual(sample.SampleStage.initialized, conditional_boundary.stage_before_iteration);
    try std.testing.expectEqual(sample.SampleStage.initialized, conditional_boundary.stage_after_iteration);
    try std.testing.expectEqual(@as(i32, 0), conditional_boundary.main_count);
    try std.testing.expectEqualStrings("iter=0", conditional_boundary.formatted_message);
    try std.testing.expectEqualStrings("Mother Goose", conditional_boundary.selected_string);
    try std.testing.expectEqual(@as(usize, 0xdeadbeef), conditional_boundary.bitmask_word);
    try std.testing.expectEqual(sample.TraceEventsReferenceSample.event_family_count, conditional_boundary.main_thread_event_calls);
    try std.testing.expectEqual(sample.TraceEventsReferenceSample.event_family_count, conditional_boundary.total_event_calls_after_replay);
    try std.testing.expect(conditional_boundary.conditional_paths_checked);
    try std.testing.expect(conditional_boundary.vararg_payload_path_checked);
    try std.testing.expect(conditional_boundary.relative_location_path_checked);
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
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
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
}

test "phase 5 trace-events sample makes ownership and teardown boundaries explicit" {
    var module = sample.TraceEventsReferenceSample{};

    try std.testing.expectEqual(sample.SampleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runAnchorReplay());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());

    try module.init();
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());
    try module.registerFunctionCallback();
    try std.testing.expectError(error.OutstandingRegistration, module.exit());
    try std.testing.expectError(error.OutstandingRegistration, module.runCallbackBoundaryReplay(1));
    try module.unregisterFunctionCallback();
    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.replayMainIteration(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionCallback());
}
