const std = @import("std");
const sample = @import("runtime_trace_events_sample");

test "runtime trace-events sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeTraceEventsSample.descriptor();

    try std.testing.expectEqualStrings("runtime_trace_events", descriptor.name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime trace-events sample keeps gated main-thread replay and lifecycle state honest" {
    var module = sample.RuntimeTraceEventsSample{};

    try std.testing.expectEqual(sample.ModuleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(0));

    try module.init();
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(0));

    const emitted = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 4), emitted);

    const replay = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, replay.stage);
    try std.testing.expectEqual(@as(usize, 1), replay.main_iterations);
    try std.testing.expectEqual(@as(usize, 4), replay.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), replay.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 4), replay.total_events);
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

test "runtime trace-events sample keeps replay-summary continuity explicit after selftest completion" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    const selftest = try module.runSelftest();
    try std.testing.expectEqual(@as(usize, 6), selftest.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), selftest.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), selftest.total_events);
    try std.testing.expectEqual(@as(usize, 5), selftest.event_families.len);
    try std.testing.expectEqual(sample.EventFamily.foo_bar, selftest.event_families[0]);
    try std.testing.expectEqual(sample.EventFamily.template, selftest.event_families[1]);
    try std.testing.expectEqual(sample.EventFamily.conditional, selftest.event_families[2]);
    try std.testing.expectEqual(sample.EventFamily.relative_location, selftest.event_families[3]);
    try std.testing.expectEqual(sample.EventFamily.function_callback, selftest.event_families[4]);
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());

    const main_emitted = try module.emitMainIteration(3);
    try std.testing.expectEqual(@as(usize, 4), main_emitted);
    try module.registerFunctionThread();
    const fn_emitted = try module.emitFunctionIteration(11);
    try std.testing.expectEqual(@as(usize, 2), fn_emitted);
    try module.unregisterFunctionThread();

    const replay = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, replay.stage);
    try std.testing.expectEqual(@as(usize, 2), replay.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), replay.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), replay.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), replay.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), replay.total_events);
    try std.testing.expectEqual(@as(usize, 1), replay.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.registration_depth);
    try std.testing.expectEqual(@as(i32, 3), replay.last_main_count);
    try std.testing.expectEqual(@as(i32, 11), replay.last_fn_count);
    try std.testing.expect(replay.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", replay.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("event-sample-fn", replay.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_reg", replay.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", replay.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("hello", replay.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Frodo", replay.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 3), replay.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(replay.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", replay.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", replay.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", replay.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("iter=%d", replay.last_format_template orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", replay.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", replay.last_function_template_message orelse return error.ExpectedFunctionPayload);
}

test "runtime trace-events module gate keeps resumed diagnostics-summary continuity explicit after direct and selftest replay" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    const direct_main = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 4), direct_main);
    try module.registerFunctionThread();
    const direct_fn = try module.emitFunctionIteration(9);
    try std.testing.expectEqual(@as(usize, 2), direct_fn);
    try module.unregisterFunctionThread();

    const selftest = try module.runSelftest();
    try std.testing.expectEqual(@as(usize, 10), selftest.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), selftest.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), selftest.total_events);

    const resumed_main = try module.emitMainIteration(3);
    try std.testing.expectEqual(@as(usize, 4), resumed_main);
    try module.registerFunctionThread();
    const resumed_fn = try module.emitFunctionIteration(11);
    try std.testing.expectEqual(@as(usize, 2), resumed_fn);
    try module.unregisterFunctionThread();

    const replay = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, replay.stage);
    try std.testing.expectEqual(@as(usize, 3), replay.main_iterations);
    try std.testing.expectEqual(@as(usize, 3), replay.fn_iterations);
    try std.testing.expectEqual(@as(usize, 14), replay.main_thread_events);
    try std.testing.expectEqual(@as(usize, 6), replay.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 20), replay.total_events);
    try std.testing.expectEqual(@as(?usize, 4), replay.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), replay.last_fn_emitted_events);
    try std.testing.expectEqual(@as(usize, 1), replay.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.registration_depth);
    try std.testing.expectEqual(@as(i32, 3), replay.last_main_count);
    try std.testing.expectEqual(@as(i32, 11), replay.last_fn_count);
    try std.testing.expect(replay.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", replay.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("event-sample-fn", replay.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_reg", replay.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", replay.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("hello", replay.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Frodo", replay.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 3), replay.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(replay.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", replay.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", replay.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", replay.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("iter=%d", replay.last_format_template orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", replay.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", replay.last_function_template_message orelse return error.ExpectedFunctionPayload);
}

test "runtime trace-events sample keeps registration balance and failed-exit rollback explicit" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());
    try module.registerFunctionThread();
    try std.testing.expectError(error.FunctionThreadAlreadyRegistered, module.registerFunctionThread());
    try std.testing.expectEqualStrings("event-sample", module.summary().main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("event-sample-fn", module.summary().function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_reg", module.summary().last_register_label orelse return error.ExpectedFunctionPayload);
    _ = try module.emitFunctionIteration(5);
    _ = try module.emitMainIteration(3);

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 4), before_failed_exit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 6), before_failed_exit.total_events);
    try std.testing.expectEqual(@as(i32, 3), before_failed_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 5), before_failed_exit.last_fn_count);
    try std.testing.expect(!before_failed_exit.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", before_failed_exit.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("event-sample-fn", before_failed_exit.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), before_failed_exit.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), before_failed_exit.last_main_template_cond_message);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, after_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), after_failed_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), after_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), after_failed_exit.exit_runs);
    try std.testing.expectEqual(before_failed_exit.registration_depth, after_failed_exit.registration_depth);
    try std.testing.expectEqual(before_failed_exit.main_thread_events, after_failed_exit.main_thread_events);
    try std.testing.expectEqual(before_failed_exit.fn_thread_events, after_failed_exit.fn_thread_events);
    try std.testing.expectEqual(before_failed_exit.total_events, after_failed_exit.total_events);
    try std.testing.expectEqual(before_failed_exit.last_main_count, after_failed_exit.last_main_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, after_failed_exit.last_fn_count);
    try std.testing.expectEqualStrings(before_failed_exit.main_thread_label orelse return error.ExpectedFunctionPayload, after_failed_exit.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.function_thread_label orelse return error.ExpectedFunctionPayload, after_failed_exit.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_reg", after_failed_exit.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit.last_unregister_label);
    try std.testing.expectEqualStrings("hello", after_failed_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Frodo", after_failed_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 3), after_failed_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(after_failed_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", after_failed_exit.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("I have to be different", after_failed_exit.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", after_failed_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("iter=%d", after_failed_exit.last_format_template orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", after_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", after_failed_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);

    try module.unregisterFunctionThread();
    try std.testing.expectEqualStrings("foo_bar_unreg", module.summary().last_unregister_label orelse return error.ExpectedFunctionPayload);
    const selftest = try module.runSelftest();
    try std.testing.expectEqual(@as(usize, 10), selftest.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), selftest.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), selftest.total_events);
    try std.testing.expectEqual(@as(usize, 5), selftest.event_families.len);
    try std.testing.expectEqual(sample.EventFamily.foo_bar, selftest.event_families[0]);
    try std.testing.expectEqual(sample.EventFamily.template, selftest.event_families[1]);
    try std.testing.expectEqual(sample.EventFamily.conditional, selftest.event_families[2]);
    try std.testing.expectEqual(sample.EventFamily.relative_location, selftest.event_families[3]);
    try std.testing.expectEqual(sample.EventFamily.function_callback, selftest.event_families[4]);

    const before_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_exit.stage);
    try std.testing.expectEqual(@as(usize, 2), before_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), before_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), before_exit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), before_exit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), before_exit.total_events);
    try std.testing.expectEqual(@as(?usize, 6), before_exit.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), before_exit.last_fn_emitted_events);
    try std.testing.expectEqual(@as(usize, 1), before_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.registration_depth);
    try std.testing.expectEqual(@as(i32, 0), before_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), before_exit.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", before_exit.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_exit.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Some times print", before_exit.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", before_exit.last_main_template_cond_message orelse return error.ExpectedMainPayload);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());

    const after_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(before_exit.main_iterations, after_exit.main_iterations);
    try std.testing.expectEqual(before_exit.fn_iterations, after_exit.fn_iterations);
    try std.testing.expectEqual(before_exit.main_thread_events, after_exit.main_thread_events);
    try std.testing.expectEqual(before_exit.fn_thread_events, after_exit.fn_thread_events);
    try std.testing.expectEqual(before_exit.total_events, after_exit.total_events);
    try std.testing.expectEqual(before_exit.last_main_emitted_events, after_exit.last_main_emitted_events);
    try std.testing.expectEqual(before_exit.last_fn_emitted_events, after_exit.last_fn_emitted_events);
    try std.testing.expectEqual(before_exit.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(before_exit.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqual(before_exit.registration_depth, after_exit.registration_depth);
    try std.testing.expectEqual(before_exit.last_main_count, after_exit.last_main_count);
    try std.testing.expectEqual(before_exit.last_fn_count, after_exit.last_fn_count);
    try std.testing.expectEqual(before_exit.saw_conditional_path, after_exit.saw_conditional_path);
    try std.testing.expectEqualStrings(before_exit.main_thread_label orelse return error.ExpectedFunctionPayload, after_exit.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_exit.function_thread_label orelse return error.ExpectedFunctionPayload, after_exit.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_exit.last_register_label orelse return error.ExpectedFunctionPayload, after_exit.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_exit.last_unregister_label orelse return error.ExpectedFunctionPayload, after_exit.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload, after_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload, after_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(before_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload, after_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(before_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload, after_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_exit.last_main_template_message orelse return error.ExpectedMainPayload, after_exit.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_exit.last_main_conditional_message orelse return error.ExpectedMainPayload, after_exit.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_exit.last_main_template_cond_message orelse return error.ExpectedMainPayload, after_exit.last_main_template_cond_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_exit.last_main_template_print_message orelse return error.ExpectedMainPayload, after_exit.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload, after_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload, after_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_exit.last_function_template_message orelse return error.ExpectedFunctionPayload, after_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_exit.last_format_template orelse return error.ExpectedMainPayload, after_exit.last_format_template orelse return error.ExpectedMainPayload);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(13));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(15));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());
}

test "runtime trace-events module gate keeps selftest-ready failed-exit rollback explicit" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());

    const replayed_main = try module.emitMainIteration(5);
    try std.testing.expectEqual(@as(usize, 4), replayed_main);
    try module.registerFunctionThread();
    const replayed_fn = try module.emitFunctionIteration(15);
    try std.testing.expectEqual(@as(usize, 2), replayed_fn);

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), before_failed_exit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), before_failed_exit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), before_failed_exit.total_events);
    try std.testing.expectEqual(@as(?usize, 4), before_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), before_failed_exit.last_fn_emitted_events);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), before_failed_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 15), before_failed_exit.last_fn_count);
    try std.testing.expect(before_failed_exit.saw_vararg_payload);
    try std.testing.expect(before_failed_exit.saw_rel_loc_payload);
    try std.testing.expect(before_failed_exit.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", before_failed_exit.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_failed_exit.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("hello", before_failed_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Mother Goose", before_failed_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(before_failed_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", before_failed_exit.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), before_failed_exit.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), before_failed_exit.last_main_template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", before_failed_exit.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", before_failed_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("iter=%d", before_failed_exit.last_format_template orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", before_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", before_failed_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, after_failed_exit.stage);
    try std.testing.expectEqual(before_failed_exit.registration_depth, after_failed_exit.registration_depth);
    try std.testing.expectEqual(before_failed_exit.main_iterations, after_failed_exit.main_iterations);
    try std.testing.expectEqual(before_failed_exit.fn_iterations, after_failed_exit.fn_iterations);
    try std.testing.expectEqual(before_failed_exit.main_thread_events, after_failed_exit.main_thread_events);
    try std.testing.expectEqual(before_failed_exit.fn_thread_events, after_failed_exit.fn_thread_events);
    try std.testing.expectEqual(before_failed_exit.total_events, after_failed_exit.total_events);
    try std.testing.expectEqual(before_failed_exit.last_main_emitted_events, after_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(before_failed_exit.last_fn_emitted_events, after_failed_exit.last_fn_emitted_events);
    try std.testing.expectEqual(before_failed_exit.init_runs, after_failed_exit.init_runs);
    try std.testing.expectEqual(before_failed_exit.selftest_runs, after_failed_exit.selftest_runs);
    try std.testing.expectEqual(before_failed_exit.exit_runs, after_failed_exit.exit_runs);
    try std.testing.expectEqual(before_failed_exit.last_main_count, after_failed_exit.last_main_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, after_failed_exit.last_fn_count);
    try std.testing.expectEqual(before_failed_exit.saw_vararg_payload, after_failed_exit.saw_vararg_payload);
    try std.testing.expectEqual(before_failed_exit.saw_rel_loc_payload, after_failed_exit.saw_rel_loc_payload);
    try std.testing.expectEqual(before_failed_exit.saw_conditional_path, after_failed_exit.saw_conditional_path);
    try std.testing.expectEqualStrings(before_failed_exit.main_thread_label orelse return error.ExpectedFunctionPayload, after_failed_exit.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.function_thread_label orelse return error.ExpectedFunctionPayload, after_failed_exit.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_register_label orelse return error.ExpectedFunctionPayload, after_failed_exit.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_unregister_label orelse return error.ExpectedFunctionPayload, after_failed_exit.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload, after_failed_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload, after_failed_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(before_failed_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload, after_failed_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(before_failed_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload, after_failed_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_main_template_message orelse return error.ExpectedMainPayload, after_failed_exit.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit.last_main_template_cond_message);
    try std.testing.expectEqualStrings(before_failed_exit.last_main_template_print_message orelse return error.ExpectedMainPayload, after_failed_exit.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload, after_failed_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload, after_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_function_template_message orelse return error.ExpectedFunctionPayload, after_failed_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_format_template orelse return error.ExpectedMainPayload, after_failed_exit.last_format_template orelse return error.ExpectedMainPayload);

    try module.unregisterFunctionThread();
    try std.testing.expectEqualStrings("foo_bar_unreg", module.summary().last_unregister_label orelse return error.ExpectedFunctionPayload);

    const before_exit = module.summary();
    try std.testing.expectEqual(@as(?usize, 4), before_exit.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), before_exit.last_fn_emitted_events);
    try module.exit();

    const after_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(before_exit.main_iterations, after_exit.main_iterations);
    try std.testing.expectEqual(before_exit.fn_iterations, after_exit.fn_iterations);
    try std.testing.expectEqual(before_exit.main_thread_events, after_exit.main_thread_events);
    try std.testing.expectEqual(before_exit.fn_thread_events, after_exit.fn_thread_events);
    try std.testing.expectEqual(before_exit.total_events, after_exit.total_events);
    try std.testing.expectEqual(before_exit.last_main_emitted_events, after_exit.last_main_emitted_events);
    try std.testing.expectEqual(before_exit.last_fn_emitted_events, after_exit.last_fn_emitted_events);
    try std.testing.expectEqual(before_exit.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(before_exit.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqual(before_exit.registration_depth, after_exit.registration_depth);
    try std.testing.expectEqual(before_exit.last_main_count, after_exit.last_main_count);
    try std.testing.expectEqual(before_exit.last_fn_count, after_exit.last_fn_count);
    try std.testing.expectEqual(before_exit.saw_vararg_payload, after_exit.saw_vararg_payload);
    try std.testing.expectEqual(before_exit.saw_rel_loc_payload, after_exit.saw_rel_loc_payload);
    try std.testing.expectEqual(before_exit.saw_conditional_path, after_exit.saw_conditional_path);
    try std.testing.expectEqualStrings(before_exit.main_thread_label orelse return error.ExpectedFunctionPayload, after_exit.main_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_exit.function_thread_label orelse return error.ExpectedFunctionPayload, after_exit.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_exit.last_register_label orelse return error.ExpectedFunctionPayload, after_exit.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_exit.last_unregister_label orelse return error.ExpectedFunctionPayload, after_exit.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload, after_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload, after_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(before_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload, after_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(before_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload, after_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_exit.last_main_template_message orelse return error.ExpectedMainPayload, after_exit.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), after_exit.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), after_exit.last_main_template_cond_message);
    try std.testing.expectEqualStrings(before_exit.last_main_template_print_message orelse return error.ExpectedMainPayload, after_exit.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload, after_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload, after_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_exit.last_function_template_message orelse return error.ExpectedFunctionPayload, after_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_exit.last_format_template orelse return error.ExpectedMainPayload, after_exit.last_format_template orelse return error.ExpectedMainPayload);
}

test "runtime trace-events module gate keeps rejected re-selftest rollback explicit" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    const before_rejected_selftest = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_rejected_selftest.stage);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_rejected_selftest.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_rejected_selftest.registration_depth);
    try std.testing.expectEqual(@as(?usize, 6), before_rejected_selftest.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), before_rejected_selftest.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), before_rejected_selftest.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(i32, 0), before_rejected_selftest.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), before_rejected_selftest.last_fn_count);
    try std.testing.expect(before_rejected_selftest.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", before_rejected_selftest.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_rejected_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Some times print", before_rejected_selftest.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", before_rejected_selftest.last_main_template_cond_message orelse return error.ExpectedMainPayload);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    const after_rejected_selftest = module.summary();
    try std.testing.expectEqual(before_rejected_selftest.stage, after_rejected_selftest.stage);
    try std.testing.expectEqual(before_rejected_selftest.main_iterations, after_rejected_selftest.main_iterations);
    try std.testing.expectEqual(before_rejected_selftest.fn_iterations, after_rejected_selftest.fn_iterations);
    try std.testing.expectEqual(before_rejected_selftest.main_thread_events, after_rejected_selftest.main_thread_events);
    try std.testing.expectEqual(before_rejected_selftest.fn_thread_events, after_rejected_selftest.fn_thread_events);
    try std.testing.expectEqual(before_rejected_selftest.total_events, after_rejected_selftest.total_events);
    try std.testing.expectEqual(before_rejected_selftest.last_main_emitted_events, after_rejected_selftest.last_main_emitted_events);
    try std.testing.expectEqual(before_rejected_selftest.last_fn_emitted_events, after_rejected_selftest.last_fn_emitted_events);
    try std.testing.expectEqual(before_rejected_selftest.last_main_conditional_event_count, after_rejected_selftest.last_main_conditional_event_count);
    try std.testing.expectEqual(before_rejected_selftest.init_runs, after_rejected_selftest.init_runs);
    try std.testing.expectEqual(before_rejected_selftest.selftest_runs, after_rejected_selftest.selftest_runs);
    try std.testing.expectEqual(before_rejected_selftest.exit_runs, after_rejected_selftest.exit_runs);
    try std.testing.expectEqual(before_rejected_selftest.registration_depth, after_rejected_selftest.registration_depth);
    try std.testing.expectEqual(before_rejected_selftest.last_main_count, after_rejected_selftest.last_main_count);
    try std.testing.expectEqual(before_rejected_selftest.last_fn_count, after_rejected_selftest.last_fn_count);
    try std.testing.expectEqual(before_rejected_selftest.saw_conditional_path, after_rejected_selftest.saw_conditional_path);
    try std.testing.expectEqualStrings(before_rejected_selftest.last_register_label orelse return error.ExpectedFunctionPayload, after_rejected_selftest.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_rejected_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload, after_rejected_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_rejected_selftest.last_main_conditional_message orelse return error.ExpectedMainPayload, after_rejected_selftest.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_rejected_selftest.last_main_template_cond_message orelse return error.ExpectedMainPayload, after_rejected_selftest.last_main_template_cond_message orelse return error.ExpectedMainPayload);

    try module.exit();

    const before_rejected_exit_selftest = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, before_rejected_exit_selftest.stage);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    const after_rejected_exit_selftest = module.summary();
    try std.testing.expectEqual(before_rejected_exit_selftest.stage, after_rejected_exit_selftest.stage);
    try std.testing.expectEqual(before_rejected_exit_selftest.main_iterations, after_rejected_exit_selftest.main_iterations);
    try std.testing.expectEqual(before_rejected_exit_selftest.fn_iterations, after_rejected_exit_selftest.fn_iterations);
    try std.testing.expectEqual(before_rejected_exit_selftest.main_thread_events, after_rejected_exit_selftest.main_thread_events);
    try std.testing.expectEqual(before_rejected_exit_selftest.fn_thread_events, after_rejected_exit_selftest.fn_thread_events);
    try std.testing.expectEqual(before_rejected_exit_selftest.total_events, after_rejected_exit_selftest.total_events);
    try std.testing.expectEqual(before_rejected_exit_selftest.last_main_emitted_events, after_rejected_exit_selftest.last_main_emitted_events);
    try std.testing.expectEqual(before_rejected_exit_selftest.last_fn_emitted_events, after_rejected_exit_selftest.last_fn_emitted_events);
    try std.testing.expectEqual(before_rejected_exit_selftest.last_main_conditional_event_count, after_rejected_exit_selftest.last_main_conditional_event_count);
    try std.testing.expectEqual(before_rejected_exit_selftest.init_runs, after_rejected_exit_selftest.init_runs);
    try std.testing.expectEqual(before_rejected_exit_selftest.selftest_runs, after_rejected_exit_selftest.selftest_runs);
    try std.testing.expectEqual(before_rejected_exit_selftest.exit_runs, after_rejected_exit_selftest.exit_runs);
    try std.testing.expectEqual(before_rejected_exit_selftest.registration_depth, after_rejected_exit_selftest.registration_depth);
    try std.testing.expectEqual(before_rejected_exit_selftest.last_main_count, after_rejected_exit_selftest.last_main_count);
    try std.testing.expectEqual(before_rejected_exit_selftest.last_fn_count, after_rejected_exit_selftest.last_fn_count);
    try std.testing.expectEqual(before_rejected_exit_selftest.saw_conditional_path, after_rejected_exit_selftest.saw_conditional_path);
    try std.testing.expectEqualStrings(before_rejected_exit_selftest.last_register_label orelse return error.ExpectedFunctionPayload, after_rejected_exit_selftest.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_rejected_exit_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload, after_rejected_exit_selftest.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_rejected_exit_selftest.last_main_conditional_message orelse return error.ExpectedMainPayload, after_rejected_exit_selftest.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_rejected_exit_selftest.last_main_template_cond_message orelse return error.ExpectedMainPayload, after_rejected_exit_selftest.last_main_template_cond_message orelse return error.ExpectedMainPayload);
}
