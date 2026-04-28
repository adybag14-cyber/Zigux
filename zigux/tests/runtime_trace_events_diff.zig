const std = @import("std");
const sample = @import("runtime_trace_events_sample");

test "runtime trace-events diff gate replays the Linux sample's concrete main-thread payload literals and random-string choice through the diagnostics summary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    const emitted = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 6), emitted);

    const payload = module.last_main_payload orelse return error.ExpectedMainPayload;
    const replay = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, replay.stage);
    try std.testing.expectEqual(@as(usize, 1), replay.main_iterations);
    try std.testing.expectEqual(@as(usize, 6), replay.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), replay.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 6), replay.total_events);
    try std.testing.expectEqual(@as(i32, 7), replay.last_main_count);
    try std.testing.expect(replay.saw_vararg_payload);
    try std.testing.expect(replay.saw_rel_loc_payload);
    try std.testing.expect(replay.saw_conditional_path);
    try std.testing.expectEqualStrings(payload.foo_bar_message, replay.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(payload.random_choice_message, replay.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Gandalf", payload.random_choice_message);
    try std.testing.expectEqualStrings(payload.template_message, replay.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(payload.conditional_message, replay.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(payload.template_cond_message, replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(payload.template_print_message, replay.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(payload.relative_location_message, replay.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(payload.format_template, replay.last_format_template orelse return error.ExpectedMainPayload);
}

test "runtime trace-events diff gate keeps function-callback registration balance and replay labels explicit through the diagnostics summary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(0));

    try module.registerFunctionThread();
    try module.registerFunctionThread();
    try std.testing.expectEqual(@as(usize, 2), module.summary().registration_depth);

    const emitted = try module.emitFunctionIteration(9);
    try std.testing.expectEqual(@as(usize, 2), emitted);

    const payload = module.last_function_payload orelse return error.ExpectedFunctionPayload;
    const replay = module.summary();
    try std.testing.expectEqual(@as(usize, 1), replay.fn_iterations);
    try std.testing.expectEqual(@as(usize, 0), replay.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), replay.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 2), replay.total_events);
    try std.testing.expectEqual(@as(i32, 9), replay.last_fn_count);
    try std.testing.expectEqual(@as(usize, 2), replay.registration_depth);
    try std.testing.expectEqualStrings(payload.foo_bar_message, replay.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(payload.template_message, replay.last_function_template_message orelse return error.ExpectedFunctionPayload);

    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 1), module.summary().registration_depth);
    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 0), module.summary().registration_depth);
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());
}

test "runtime trace-events diff gate keeps the selftest family order and replay summary totals explicit" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    const summary = try module.runSelftest();
    try std.testing.expectEqual(@as(usize, 5), summary.event_families.len);
    try std.testing.expectEqual(sample.EventFamily.foo_bar, summary.event_families[0]);
    try std.testing.expectEqual(sample.EventFamily.template, summary.event_families[1]);
    try std.testing.expectEqual(sample.EventFamily.conditional, summary.event_families[2]);
    try std.testing.expectEqual(sample.EventFamily.relative_location, summary.event_families[3]);
    try std.testing.expectEqual(sample.EventFamily.function_callback, summary.event_families[4]);
    try std.testing.expect(summary.registration_paths_checked);
    try std.testing.expect(summary.conditional_paths_checked);
    try std.testing.expectEqual(@as(usize, 6), summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), summary.total_events);

    const replay = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, replay.stage);
    try std.testing.expectEqual(@as(usize, 0), replay.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), replay.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), replay.fn_iterations);
    try std.testing.expectEqual(@as(usize, 6), replay.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), replay.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), replay.total_events);
    try std.testing.expectEqual(@as(usize, 1), replay.selftest_runs);
    try std.testing.expectEqualStrings("hello", replay.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Mother Goose", replay.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", replay.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", replay.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", replay.last_function_template_message orelse return error.ExpectedFunctionPayload);
}
