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
    try std.testing.expectEqualStrings("foo_bar_reg", replay.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", replay.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("hello", replay.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Frodo", replay.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 3), replay.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(replay.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), replay.last_main_template_cond_message);
    try std.testing.expectEqualStrings("Look at me", replay.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", replay.last_function_template_message orelse return error.ExpectedFunctionPayload);
}

test "runtime trace-events sample keeps registration balance and failed-exit rollback explicit" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());
    try module.registerFunctionThread();
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
    try std.testing.expectEqual(@as(?[]const u8, null), before_failed_exit.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), before_failed_exit.last_main_template_cond_message);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(before_failed_exit.registration_depth, after_failed_exit.registration_depth);
    try std.testing.expectEqual(before_failed_exit.main_thread_events, after_failed_exit.main_thread_events);
    try std.testing.expectEqual(before_failed_exit.fn_thread_events, after_failed_exit.fn_thread_events);
    try std.testing.expectEqual(before_failed_exit.total_events, after_failed_exit.total_events);
    try std.testing.expectEqual(before_failed_exit.last_main_count, after_failed_exit.last_main_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, after_failed_exit.last_fn_count);

    try module.unregisterFunctionThread();
    try std.testing.expectEqualStrings("foo_bar_unreg", module.summary().last_unregister_label orelse return error.ExpectedFunctionPayload);
    const selftest = try module.runSelftest();
    try std.testing.expectEqual(@as(usize, 10), selftest.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), selftest.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), selftest.total_events);
    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.summary().exit_runs);
}

test "runtime trace-events sample keeps selftest replay explicit after direct pilot activity" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    _ = try module.emitMainIteration(7);
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(9);
    try module.unregisterFunctionThread();

    const summary = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), summary.event_families.len);
    try std.testing.expectEqual(@as(usize, 10), summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), summary.total_events);
    try std.testing.expect(summary.conditional_paths_checked);
    try std.testing.expect(summary.registration_paths_checked);

    const replay = module.summary();
    try std.testing.expectEqual(@as(usize, 2), replay.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), replay.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), replay.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), replay.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), replay.total_events);
    try std.testing.expectEqual(@as(usize, 1), replay.selftest_runs);
    try std.testing.expectEqual(@as(i32, 0), replay.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), replay.last_fn_count);
    try std.testing.expect(replay.saw_conditional_path);
    try std.testing.expectEqualStrings("Some times print", replay.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", replay.last_main_template_cond_message orelse return error.ExpectedMainPayload);
}
