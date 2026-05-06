const std = @import("std");
const sample = @import("runtime_trace_events_sample");

test "runtime trace-events diff gate replays the Linux sample's concrete main-thread payload literals through the stable summary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    const emitted = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 6), emitted);

    const summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, summary.stage);
    try std.testing.expectEqual(@as(usize, 1), summary.main_iterations);
    try std.testing.expectEqual(@as(usize, 0), summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 6), summary.total_events);
    try std.testing.expectEqual(@as(i32, 7), summary.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), summary.last_fn_count);
    try std.testing.expectEqual(@as(usize, 6), summary.last_main_emitted_events);
    try std.testing.expectEqual(@as(usize, 0), summary.last_fn_emitted_events);
    try std.testing.expect(summary.saw_vararg_payload);
    try std.testing.expect(summary.saw_rel_loc_payload);
    try std.testing.expect(summary.saw_conditional_path);

    const payload = summary.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", payload.foo_bar_message);
    try std.testing.expectEqualStrings("HELLO", payload.template_message);
    try std.testing.expectEqualStrings("Some times print", payload.conditional_message);
    try std.testing.expectEqualStrings("prints other times", payload.template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", payload.template_print_message);
    try std.testing.expectEqualStrings("Hello __rel_loc", payload.relative_location_message);
    try std.testing.expectEqualStrings("iter=%d", payload.format_template);
}

test "runtime trace-events diff gate keeps function-callback registration balance and payload labels explicit through the stable summary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(0));

    try module.registerFunctionThread();
    try module.registerFunctionThread();
    try std.testing.expectEqual(@as(usize, 2), module.summary().registration_depth);
    try std.testing.expectEqual(@as(usize, 1), module.summary().registration_start_runs);

    const emitted = try module.emitFunctionIteration(9);
    try std.testing.expectEqual(@as(usize, 2), emitted);

    const summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 2), summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), summary.total_events);
    try std.testing.expectEqual(@as(i32, 9), summary.last_fn_count);
    try std.testing.expectEqual(@as(usize, 0), summary.last_main_emitted_events);
    try std.testing.expectEqual(@as(usize, 2), summary.last_fn_emitted_events);

    const payload = summary.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", payload.template_message);

    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 1), module.summary().registration_depth);
    try std.testing.expectEqual(@as(usize, 0), module.summary().registration_stop_runs);
    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 0), module.summary().registration_depth);
    try std.testing.expectEqual(@as(usize, 1), module.summary().registration_stop_runs);
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());
}

test "runtime trace-events diff gate keeps selftest totals machine-checkable through the stable summary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    const emission_summary = try module.runSelftest();
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", emission_summary.anchor);
    try std.testing.expectEqual(@as(usize, 6), emission_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), emission_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), emission_summary.total_events);

    const summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, summary.stage);
    try std.testing.expectEqual(@as(usize, 0), summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), summary.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 1), summary.registration_stop_runs);
    try std.testing.expectEqual(@as(usize, 1), summary.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 8), summary.total_events);
    try std.testing.expectEqual(@as(usize, 1), summary.selftest_runs);
    try std.testing.expectEqual(@as(i32, 0), summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), summary.last_fn_count);
    try std.testing.expectEqual(@as(usize, 6), summary.last_main_emitted_events);
    try std.testing.expectEqual(@as(usize, 2), summary.last_fn_emitted_events);
    try std.testing.expect(summary.saw_conditional_path);
}
