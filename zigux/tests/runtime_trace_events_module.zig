const std = @import("std");
const sample = @import("runtime_trace_events_sample");

test "runtime trace-events sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeTraceEventsSample.descriptor();

    try std.testing.expectEqualStrings("runtime_trace_events", descriptor.name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime trace-events sample enforces lifecycle transitions and bounded event emission through the stable summary surface" {
    var module = sample.RuntimeTraceEventsSample{};

    try std.testing.expectEqual(sample.ModuleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(0));
    try std.testing.expectError(error.FunctionThreadNotRegistered, blk: {
        try module.init();
        break :blk module.emitFunctionIteration(0);
    });

    const initialized = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, initialized.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized.init_runs);

    const main_events = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 6), main_events);
    const after_main = module.summary();
    try std.testing.expectEqual(@as(usize, 1), after_main.main_iterations);
    try std.testing.expectEqual(@as(i32, 7), after_main.last_main_count);
    try std.testing.expect(after_main.saw_vararg_payload);
    try std.testing.expect(after_main.saw_rel_loc_payload);
    try std.testing.expect(after_main.saw_conditional_path);
    const main_payload = after_main.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("HELLO", main_payload.template_message);
    try std.testing.expectEqualStrings("Some times print", main_payload.conditional_message);
    try std.testing.expectEqualStrings("prints other times", main_payload.template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", main_payload.template_print_message);
    try std.testing.expectEqualStrings("Hello __rel_loc", main_payload.relative_location_message);
    try std.testing.expectEqualStrings("iter=%d", main_payload.format_template);

    try module.registerFunctionThread();
    try module.registerFunctionThread();
    try std.testing.expectEqual(@as(usize, 2), module.summary().registration_depth);
    try std.testing.expectEqual(@as(usize, 1), module.summary().registration_start_runs);
    const fn_events = try module.emitFunctionIteration(9);
    try std.testing.expectEqual(@as(usize, 2), fn_events);
    const after_function = module.summary();
    try std.testing.expectEqual(@as(usize, 1), after_function.fn_iterations);
    try std.testing.expectEqual(@as(usize, 2), after_function.registration_depth);
    try std.testing.expectEqual(@as(usize, 8), after_function.total_events);
    try std.testing.expectEqual(@as(i32, 9), after_function.last_fn_count);
    const fn_payload = after_function.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", fn_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", fn_payload.template_message);
    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 1), module.summary().registration_depth);
    try std.testing.expectEqual(@as(usize, 0), module.summary().registration_stop_runs);
    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 0), module.summary().registration_depth);
    try std.testing.expectEqual(@as(usize, 1), module.summary().registration_stop_runs);

    const selftest_summary = try module.runSelftest();
    const post_selftest = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, post_selftest.stage);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", selftest_summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), selftest_summary.event_families.len);
    try std.testing.expectEqual(@as(usize, 12), selftest_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), selftest_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 16), selftest_summary.total_events);
    try std.testing.expect(selftest_summary.conditional_paths_checked);
    try std.testing.expect(selftest_summary.registration_paths_checked);
    try std.testing.expectEqual(@as(usize, 0), post_selftest.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), post_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 3), post_selftest.register_runs);
    try std.testing.expectEqual(@as(usize, 3), post_selftest.unregister_runs);
    try std.testing.expectEqual(@as(usize, 2), post_selftest.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 2), post_selftest.registration_stop_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());

    try module.exit();
    const exited = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited.stage);
    try std.testing.expectEqual(@as(usize, 1), exited.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(0));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(0));
}

test "runtime trace-events sample keeps registration balance explicit" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());
    try module.registerFunctionThread();
    try module.registerFunctionThread();
    try std.testing.expectEqual(@as(usize, 2), module.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), module.registration_start_runs);
    try std.testing.expectError(error.OutstandingRegistration, module.exit());
    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 1), module.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), module.registration_stop_runs);
    try std.testing.expectError(error.OutstandingRegistration, module.exit());
    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 0), module.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), module.registration_stop_runs);
    try module.exit();
}

test "runtime trace-events sample keeps nested callback-registration rollback explicit through the module gate" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    try module.registerFunctionThread();
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(2);

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.register_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.unregister_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.registration_stop_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.total_events);
    try std.testing.expectEqual(@as(i32, -1), before_failed_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 2), before_failed_exit.last_fn_count);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.last_fn_emitted_events);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.exit_runs);
    const before_payload = before_failed_exit.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", before_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", before_payload.template_message);

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
    try std.testing.expectEqual(before_failed_exit.selftest_runs, after_failed_exit.selftest_runs);
    try std.testing.expectEqual(before_failed_exit.exit_runs, after_failed_exit.exit_runs);
    const after_payload = after_failed_exit.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", after_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", after_payload.template_message);

    try module.unregisterFunctionThread();
    const after_partial_drain = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, after_partial_drain.stage);
    try std.testing.expectEqual(@as(usize, 1), after_partial_drain.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), after_partial_drain.register_runs);
    try std.testing.expectEqual(@as(usize, 1), after_partial_drain.unregister_runs);
    try std.testing.expectEqual(@as(usize, 1), after_partial_drain.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 0), after_partial_drain.registration_stop_runs);
    try std.testing.expectEqual(before_failed_exit.total_events, after_partial_drain.total_events);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, after_partial_drain.last_fn_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_emitted_events, after_partial_drain.last_fn_emitted_events);
    try std.testing.expectEqual(before_failed_exit.selftest_runs, after_partial_drain.selftest_runs);
    try std.testing.expectEqual(before_failed_exit.exit_runs, after_partial_drain.exit_runs);
    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    try module.unregisterFunctionThread();
    const drained = module.summary();
    try std.testing.expectEqual(@as(usize, 0), drained.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), drained.unregister_runs);
    try std.testing.expectEqual(@as(usize, 1), drained.registration_stop_runs);
    try std.testing.expectEqual(before_failed_exit.total_events, drained.total_events);

    try module.exit();
    const exited = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited.stage);
    try std.testing.expectEqual(@as(usize, 0), exited.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), exited.register_runs);
    try std.testing.expectEqual(@as(usize, 2), exited.unregister_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.registration_start_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.registration_stop_runs);
    try std.testing.expectEqual(before_failed_exit.total_events, exited.total_events);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, exited.last_fn_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_emitted_events, exited.last_fn_emitted_events);
    try std.testing.expectEqual(@as(usize, 1), exited.exit_runs);
    const exited_payload = exited.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", exited_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", exited_payload.template_message);
}

test "runtime trace-events sample keeps initialized-stage failed-exit rollback explicit through the module gate" {
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
    try std.testing.expectEqual(sample.ModuleStage.initialized, after_failed_exit.stage);
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

test "runtime trace-events sample keeps selftest-ready failed-exit rollback explicit through the module gate" {
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
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, after_failed_exit.stage);
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

test "runtime trace-events sample keeps outstanding-registration selftest rollback explicit through the module gate" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.emitMainIteration(3);
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(4);

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
    try std.testing.expectEqual(@as(i32, 3), before_failed_selftest.last_main_count);
    try std.testing.expectEqual(@as(i32, 4), before_failed_selftest.last_fn_count);
    const before_main_payload = before_failed_selftest.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", before_main_payload.foo_bar_message);
    const before_function_payload = before_failed_selftest.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", before_function_payload.foo_bar_message);

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
    const after_main_payload = after_failed_selftest.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", after_main_payload.foo_bar_message);
    const after_function_payload = after_failed_selftest.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", after_function_payload.foo_bar_message);

    try module.unregisterFunctionThread();
    const summary = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 12), summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 16), summary.total_events);
}
