const std = @import("std");
const sample = @import("runtime_trace_events");

test "runtime trace-events diff gate keeps count-gated main-thread replay explicit through the diagnostics summary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    const emitted = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 4), emitted);

    const replay = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, replay.stage);
    try std.testing.expectEqual(@as(usize, 1), replay.main_iterations);
    try std.testing.expectEqual(@as(usize, 4), replay.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), replay.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 4), replay.total_events);
    try std.testing.expectEqual(@as(?usize, 4), replay.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), replay.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, 0), replay.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(i32, 7), replay.last_main_count);
    try std.testing.expect(replay.saw_vararg_payload);
    try std.testing.expect(replay.saw_rel_loc_payload);
    try std.testing.expect(!replay.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", replay.main_thread_label orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("event-sample-fn", replay.function_thread_label orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("hello", replay.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Gandalf", replay.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 2), replay.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(replay.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", replay.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", replay.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", replay.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("iter=%d", replay.last_format_template orelse return error.ExpectedMainPayload);
}

test "runtime trace-events diff gate keeps function-callback registration balance and replay labels explicit through the diagnostics summary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(0));

    try std.testing.expectEqualStrings("event-sample", module.summary().main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("event-sample-fn", module.summary().function_thread_label orelse return error.ExpectedFunctionPayload);
    try module.registerFunctionThread();
    try std.testing.expectError(error.FunctionThreadAlreadyRegistered, module.registerFunctionThread());
    try std.testing.expectEqual(@as(usize, 1), module.summary().registration_depth);
    try std.testing.expectEqualStrings("foo_bar_reg", module.summary().last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), module.summary().last_unregister_label);

    const emitted = try module.emitFunctionIteration(9);
    try std.testing.expectEqual(@as(usize, 2), emitted);

    const replay = module.summary();
    try std.testing.expectEqual(@as(usize, 1), replay.fn_iterations);
    try std.testing.expectEqual(@as(usize, 0), replay.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), replay.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 2), replay.total_events);
    try std.testing.expectEqual(@as(?usize, null), replay.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), replay.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), replay.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(i32, 9), replay.last_fn_count);
    try std.testing.expectEqual(@as(usize, 1), replay.registration_depth);
    try std.testing.expectEqualStrings("event-sample", replay.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("event-sample-fn", replay.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_reg", replay.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), replay.last_unregister_label);
    try std.testing.expectEqualStrings("Look at me", replay.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", replay.last_function_template_message orelse return error.ExpectedFunctionPayload);

    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 0), module.summary().registration_depth);
    try std.testing.expectEqualStrings("foo_bar_unreg", module.summary().last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());
}

test "runtime trace-events diff gate keeps the selftest family order and gated replay totals explicit" {
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
    try std.testing.expectEqual(@as(?usize, 6), replay.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), replay.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), replay.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(usize, 1), replay.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.exit_runs);
    try std.testing.expectEqual(@as(i32, 0), replay.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), replay.last_fn_count);
    try std.testing.expect(replay.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", replay.main_thread_label orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("event-sample-fn", replay.function_thread_label orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Mother Goose", replay.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Some times print", replay.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", replay.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", replay.last_function_template_message orelse return error.ExpectedFunctionPayload);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.summary().stage);
    try std.testing.expectEqual(@as(usize, 1), module.summary().exit_runs);
}
