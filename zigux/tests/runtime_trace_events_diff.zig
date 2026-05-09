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
    try std.testing.expectError(error.FunctionThreadAlreadyRegistered, module.registerFunctionThread());
    try std.testing.expectEqual(@as(usize, 1), module.summary().registration_depth);
    try std.testing.expectEqual(@as(usize, 1), module.summary().registration_start_runs);

    const emitted = try module.emitFunctionIteration(9);
    try std.testing.expectEqual(@as(usize, 2), emitted);

    const summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 1), summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), summary.total_events);
    try std.testing.expectEqual(@as(i32, 9), summary.last_fn_count);
    try std.testing.expectEqual(@as(usize, 0), summary.last_main_emitted_events);
    try std.testing.expectEqual(@as(usize, 2), summary.last_fn_emitted_events);

    const payload = summary.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", payload.template_message);

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
    try std.testing.expectEqual(@as(usize, 5), emission_summary.event_families.len);
    try std.testing.expectEqual(sample.EventFamily.foo_bar, emission_summary.event_families[0]);
    try std.testing.expectEqual(sample.EventFamily.template, emission_summary.event_families[1]);
    try std.testing.expectEqual(sample.EventFamily.conditional, emission_summary.event_families[2]);
    try std.testing.expectEqual(sample.EventFamily.relative_location, emission_summary.event_families[3]);
    try std.testing.expectEqual(sample.EventFamily.function_callback, emission_summary.event_families[4]);
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

test "runtime trace-events diff gate keeps initialized-stage failed-exit rollback visible through the stable summary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    _ = try module.emitMainIteration(4);
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(6);

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.unregister_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.registration_stop_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 8), before_failed_exit.total_events);
    try std.testing.expectEqual(@as(i32, 4), before_failed_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 6), before_failed_exit.last_fn_count);
    try std.testing.expectEqual(@as(usize, 6), before_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.last_fn_emitted_events);
    try std.testing.expect(before_failed_exit.saw_vararg_payload);
    try std.testing.expect(before_failed_exit.saw_rel_loc_payload);
    try std.testing.expect(before_failed_exit.saw_conditional_path);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.exit_runs);
    const before_main_payload = before_failed_exit.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", before_main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", before_main_payload.format_template);
    const before_function_payload = before_failed_exit.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", before_function_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", before_function_payload.template_message);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(before_failed_exit.stage, after_failed_exit.stage);
    try std.testing.expectEqual(before_failed_exit.registration_depth, after_failed_exit.registration_depth);
    try std.testing.expectEqual(before_failed_exit.register_runs, after_failed_exit.register_runs);
    try std.testing.expectEqual(before_failed_exit.unregister_runs, after_failed_exit.unregister_runs);
    try std.testing.expectEqual(before_failed_exit.registration_start_runs, after_failed_exit.registration_start_runs);
    try std.testing.expectEqual(before_failed_exit.registration_stop_runs, after_failed_exit.registration_stop_runs);
    try std.testing.expectEqual(before_failed_exit.main_iterations, after_failed_exit.main_iterations);
    try std.testing.expectEqual(before_failed_exit.fn_iterations, after_failed_exit.fn_iterations);
    try std.testing.expectEqual(before_failed_exit.total_events, after_failed_exit.total_events);
    try std.testing.expectEqual(before_failed_exit.last_main_count, after_failed_exit.last_main_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, after_failed_exit.last_fn_count);
    try std.testing.expectEqual(before_failed_exit.last_main_emitted_events, after_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(before_failed_exit.last_fn_emitted_events, after_failed_exit.last_fn_emitted_events);
    try std.testing.expectEqual(before_failed_exit.saw_vararg_payload, after_failed_exit.saw_vararg_payload);
    try std.testing.expectEqual(before_failed_exit.saw_rel_loc_payload, after_failed_exit.saw_rel_loc_payload);
    try std.testing.expectEqual(before_failed_exit.saw_conditional_path, after_failed_exit.saw_conditional_path);
    try std.testing.expectEqual(before_failed_exit.selftest_runs, after_failed_exit.selftest_runs);
    try std.testing.expectEqual(before_failed_exit.exit_runs, after_failed_exit.exit_runs);
    const after_main_payload = after_failed_exit.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", after_main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", after_main_payload.format_template);
    const after_function_payload = after_failed_exit.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", after_function_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", after_function_payload.template_message);

    try module.unregisterFunctionThread();
    try module.exit();

    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 0), exited_summary.registration_depth);
    try std.testing.expectEqual(before_failed_exit.main_iterations, exited_summary.main_iterations);
    try std.testing.expectEqual(before_failed_exit.fn_iterations, exited_summary.fn_iterations);
    try std.testing.expectEqual(before_failed_exit.total_events, exited_summary.total_events);
    try std.testing.expectEqual(before_failed_exit.last_main_count, exited_summary.last_main_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, exited_summary.last_fn_count);
    try std.testing.expectEqual(before_failed_exit.last_main_emitted_events, exited_summary.last_main_emitted_events);
    try std.testing.expectEqual(before_failed_exit.last_fn_emitted_events, exited_summary.last_fn_emitted_events);
    try std.testing.expectEqual(before_failed_exit.saw_vararg_payload, exited_summary.saw_vararg_payload);
    try std.testing.expectEqual(before_failed_exit.saw_rel_loc_payload, exited_summary.saw_rel_loc_payload);
    try std.testing.expectEqual(before_failed_exit.saw_conditional_path, exited_summary.saw_conditional_path);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.registration_stop_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    const exited_main_payload = exited_summary.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", exited_main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", exited_main_payload.format_template);
    const exited_function_payload = exited_summary.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", exited_function_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", exited_function_payload.template_message);
}

test "runtime trace-events diff gate keeps selftest-ready failed-exit rollback visible through the stable summary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    try module.registerFunctionThread();
    _ = try module.emitMainIteration(4);
    _ = try module.emitFunctionIteration(6);

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.unregister_runs);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_stop_runs);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 16), before_failed_exit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(i32, 4), before_failed_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 6), before_failed_exit.last_fn_count);
    try std.testing.expectEqual(@as(usize, 6), before_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.last_fn_emitted_events);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.exit_runs);
    const before_main_payload = before_failed_exit.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", before_main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", before_main_payload.format_template);
    const before_function_payload = before_failed_exit.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", before_function_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", before_function_payload.template_message);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(before_failed_exit.stage, after_failed_exit.stage);
    try std.testing.expectEqual(before_failed_exit.registration_depth, after_failed_exit.registration_depth);
    try std.testing.expectEqual(before_failed_exit.register_runs, after_failed_exit.register_runs);
    try std.testing.expectEqual(before_failed_exit.unregister_runs, after_failed_exit.unregister_runs);
    try std.testing.expectEqual(before_failed_exit.registration_start_runs, after_failed_exit.registration_start_runs);
    try std.testing.expectEqual(before_failed_exit.registration_stop_runs, after_failed_exit.registration_stop_runs);
    try std.testing.expectEqual(before_failed_exit.main_iterations, after_failed_exit.main_iterations);
    try std.testing.expectEqual(before_failed_exit.fn_iterations, after_failed_exit.fn_iterations);
    try std.testing.expectEqual(before_failed_exit.total_events, after_failed_exit.total_events);
    try std.testing.expectEqual(before_failed_exit.selftest_runs, after_failed_exit.selftest_runs);
    try std.testing.expectEqual(before_failed_exit.last_main_count, after_failed_exit.last_main_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, after_failed_exit.last_fn_count);
    try std.testing.expectEqual(before_failed_exit.last_main_emitted_events, after_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(before_failed_exit.last_fn_emitted_events, after_failed_exit.last_fn_emitted_events);
    try std.testing.expectEqual(before_failed_exit.saw_vararg_payload, after_failed_exit.saw_vararg_payload);
    try std.testing.expectEqual(before_failed_exit.saw_rel_loc_payload, after_failed_exit.saw_rel_loc_payload);
    try std.testing.expectEqual(before_failed_exit.saw_conditional_path, after_failed_exit.saw_conditional_path);
    try std.testing.expectEqual(before_failed_exit.exit_runs, after_failed_exit.exit_runs);
    const after_main_payload = after_failed_exit.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", after_main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", after_main_payload.format_template);
    const after_function_payload = after_failed_exit.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", after_function_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", after_function_payload.template_message);

    try module.unregisterFunctionThread();
    try module.exit();

    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 0), exited_summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), exited_summary.register_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_summary.unregister_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_summary.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_summary.registration_stop_runs);
    try std.testing.expectEqual(before_failed_exit.total_events, exited_summary.total_events);
    try std.testing.expectEqual(before_failed_exit.selftest_runs, exited_summary.selftest_runs);
    try std.testing.expectEqual(before_failed_exit.last_main_emitted_events, exited_summary.last_main_emitted_events);
    try std.testing.expectEqual(before_failed_exit.last_fn_emitted_events, exited_summary.last_fn_emitted_events);
    try std.testing.expectEqual(before_failed_exit.saw_vararg_payload, exited_summary.saw_vararg_payload);
    try std.testing.expectEqual(before_failed_exit.saw_rel_loc_payload, exited_summary.saw_rel_loc_payload);
    try std.testing.expectEqual(before_failed_exit.saw_conditional_path, exited_summary.saw_conditional_path);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    const exited_main_payload = exited_summary.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", exited_main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", exited_main_payload.format_template);
    const exited_function_payload = exited_summary.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", exited_function_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", exited_function_payload.template_message);
}

test "runtime trace-events diff gate keeps outstanding-registration selftest rollback visible through the stable summary" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.emitMainIteration(8);
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(9);

    const before_failed_selftest = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_failed_selftest.stage);
    try std.testing.expectEqual(@as(usize, 1), before_failed_selftest.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), before_failed_selftest.register_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_selftest.unregister_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_selftest.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_selftest.registration_stop_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_selftest.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), before_failed_selftest.fn_iterations);
    try std.testing.expectEqual(@as(usize, 8), before_failed_selftest.total_events);
    try std.testing.expectEqual(@as(usize, 0), before_failed_selftest.selftest_runs);
    try std.testing.expectEqual(@as(i32, 8), before_failed_selftest.last_main_count);
    try std.testing.expectEqual(@as(i32, 9), before_failed_selftest.last_fn_count);
    try std.testing.expectEqual(@as(usize, 6), before_failed_selftest.last_main_emitted_events);
    try std.testing.expectEqual(@as(usize, 2), before_failed_selftest.last_fn_emitted_events);
    try std.testing.expect(before_failed_selftest.saw_vararg_payload);
    try std.testing.expect(before_failed_selftest.saw_rel_loc_payload);
    try std.testing.expect(before_failed_selftest.saw_conditional_path);
    const before_main_payload = before_failed_selftest.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", before_main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", before_main_payload.format_template);
    const before_function_payload = before_failed_selftest.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", before_function_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", before_function_payload.template_message);

    try std.testing.expectError(error.OutstandingRegistration, module.runSelftest());

    const after_failed_selftest = module.summary();
    try std.testing.expectEqual(before_failed_selftest.stage, after_failed_selftest.stage);
    try std.testing.expectEqual(before_failed_selftest.registration_depth, after_failed_selftest.registration_depth);
    try std.testing.expectEqual(before_failed_selftest.register_runs, after_failed_selftest.register_runs);
    try std.testing.expectEqual(before_failed_selftest.unregister_runs, after_failed_selftest.unregister_runs);
    try std.testing.expectEqual(before_failed_selftest.registration_start_runs, after_failed_selftest.registration_start_runs);
    try std.testing.expectEqual(before_failed_selftest.registration_stop_runs, after_failed_selftest.registration_stop_runs);
    try std.testing.expectEqual(before_failed_selftest.main_iterations, after_failed_selftest.main_iterations);
    try std.testing.expectEqual(before_failed_selftest.fn_iterations, after_failed_selftest.fn_iterations);
    try std.testing.expectEqual(before_failed_selftest.total_events, after_failed_selftest.total_events);
    try std.testing.expectEqual(before_failed_selftest.selftest_runs, after_failed_selftest.selftest_runs);
    try std.testing.expectEqual(before_failed_selftest.last_main_count, after_failed_selftest.last_main_count);
    try std.testing.expectEqual(before_failed_selftest.last_fn_count, after_failed_selftest.last_fn_count);
    try std.testing.expectEqual(before_failed_selftest.last_main_emitted_events, after_failed_selftest.last_main_emitted_events);
    try std.testing.expectEqual(before_failed_selftest.last_fn_emitted_events, after_failed_selftest.last_fn_emitted_events);
    try std.testing.expectEqual(before_failed_selftest.saw_vararg_payload, after_failed_selftest.saw_vararg_payload);
    try std.testing.expectEqual(before_failed_selftest.saw_rel_loc_payload, after_failed_selftest.saw_rel_loc_payload);
    try std.testing.expectEqual(before_failed_selftest.saw_conditional_path, after_failed_selftest.saw_conditional_path);
    const after_main_payload = after_failed_selftest.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", after_main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", after_main_payload.format_template);
    const after_function_payload = after_failed_selftest.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", after_function_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", after_function_payload.template_message);

    try module.unregisterFunctionThread();
    const selftest_summary = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 12), selftest_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), selftest_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 16), selftest_summary.total_events);
}
