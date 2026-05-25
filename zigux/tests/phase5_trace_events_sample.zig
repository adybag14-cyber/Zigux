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
    try std.testing.expectEqualSlices(i32, &.{ 1, 2 }, replay.array_prefix[0..]);
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
    try std.testing.expectEqualSlices(sample.SampleFocus, &expected_focus, replay.checked_focus);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.replay_runs);
}

test "phase 5 trace-events sample keeps payload and callback boundaries explicit" {
    var module = sample.TraceEventsReferenceSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, module.replayMainIteration(0));
    try module.init();
    try std.testing.expectError(error.InvalidIterationCount, module.replayMainIteration(-1));

    try module.replayMainIteration(4);
    try std.testing.expectEqual(@as(i32, 1), module.array_payload[0]);
    try std.testing.expectEqual(@as(i32, 2), module.array_payload[1]);
    try std.testing.expectEqual(@as(i32, 3), module.array_payload[2]);
    try std.testing.expectEqual(@as(i32, 4), module.array_payload[3]);
    try std.testing.expectEqual(@as(i32, 0), module.array_payload[4]);
    try std.testing.expectEqualStrings("One ring to rule them all", module.selected_string);
    try std.testing.expectEqualStrings("iter=4", module.formattedMessage());
    try std.testing.expect(module.saw_vararg_payload);
    try std.testing.expect(module.saw_rel_loc_payload);
    try std.testing.expect(module.saw_conditional_path);

    try std.testing.expectError(error.FunctionCallbackNotRegistered, module.replayFunctionIteration(0));
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionCallback());
    try module.registerFunctionCallback();
    try std.testing.expectError(error.CallbackAlreadyRegistered, module.registerFunctionCallback());
    try module.replayFunctionIteration(3);
    try std.testing.expectEqual(@as(i32, 3), module.last_function_count);
    try std.testing.expect(module.saw_function_callback_path);
    try std.testing.expectEqual(@as(usize, 8), module.total_event_calls);
    try module.unregisterFunctionCallback();
    try std.testing.expectEqual(@as(usize, 0), module.registration_depth);
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
    try std.testing.expectError(error.CallbackAlreadyRegistered, module.registerFunctionCallback());
    try std.testing.expectError(error.OutstandingRegistration, module.exit());
    try module.unregisterFunctionCallback();
    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.replayMainIteration(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionCallback());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.replayFunctionIteration(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionCallback());
}