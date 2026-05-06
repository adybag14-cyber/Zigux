const std = @import("std");
const sample = @import("runtime_trace_events_sample");

test "runtime trace-events sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeTraceEventsSample.descriptor();

    try std.testing.expectEqualStrings("runtime_trace_events", descriptor.name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime trace-events sample enforces lifecycle transitions and bounded event emission" {
    var module = sample.RuntimeTraceEventsSample{};

    try std.testing.expectEqual(sample.ModuleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(0));
    try std.testing.expectError(error.FunctionThreadNotRegistered, blk: {
        try module.init();
        break :blk module.emitFunctionIteration(0);
    });

    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);

    const main_events = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 6), main_events);
    try std.testing.expectEqual(@as(usize, 1), module.main_iterations);
    try std.testing.expectEqual(@as(i32, 7), module.last_main_count);
    try std.testing.expect(module.saw_vararg_payload);
    try std.testing.expect(module.saw_rel_loc_payload);
    try std.testing.expect(module.saw_conditional_path);
    const main_payload = module.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("HELLO", main_payload.template_message);
    try std.testing.expectEqualStrings("Some times print", main_payload.conditional_message);
    try std.testing.expectEqualStrings("prints other times", main_payload.template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", main_payload.template_print_message);
    try std.testing.expectEqualStrings("Hello __rel_loc", main_payload.relative_location_message);
    try std.testing.expectEqualStrings("iter=%d", main_payload.format_template);

    try module.registerFunctionThread();
    try std.testing.expectError(error.FunctionThreadAlreadyRegistered, module.registerFunctionThread());
    const fn_events = try module.emitFunctionIteration(9);
    try std.testing.expectEqual(@as(usize, 2), fn_events);
    try std.testing.expectEqual(@as(usize, 1), module.fn_iterations);
    try std.testing.expectEqual(@as(i32, 9), module.last_fn_count);
    try std.testing.expectEqual(@as(usize, 1), module.registration_depth);
    const fn_payload = module.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", fn_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", fn_payload.template_message);
    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 0), module.registration_depth);

    const summary = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), summary.event_families.len);
    try std.testing.expectEqual(@as(usize, 12), summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 16), summary.total_events);
    try std.testing.expect(summary.conditional_paths_checked);
    try std.testing.expect(summary.registration_paths_checked);
    try std.testing.expectEqual(@as(usize, 0), module.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), module.selftest_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(0));
}

test "runtime trace-events sample keeps registration balance explicit" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());
    try module.registerFunctionThread();
    try std.testing.expectError(error.FunctionThreadAlreadyRegistered, module.registerFunctionThread());
    try std.testing.expectError(error.OutstandingRegistration, module.exit());
    try module.unregisterFunctionThread();
    try module.exit();
}

test "runtime trace-events sample preserves failed-exit summary state until registration is balanced" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    _ = try module.emitMainIteration(4);
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(6);

    const summary_before_failed_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, summary_before_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), summary_before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), summary_before_failed_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), summary_before_failed_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 8), summary_before_failed_exit.total_events);
    try std.testing.expectEqual(@as(usize, 6), summary_before_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(@as(usize, 2), summary_before_failed_exit.last_fn_emitted_events);
    try std.testing.expectEqual(@as(i32, 4), summary_before_failed_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 6), summary_before_failed_exit.last_fn_count);
    try std.testing.expectEqual(@as(usize, 0), summary_before_failed_exit.exit_runs);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const summary_after_failed_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, summary_after_failed_exit.stage);
    try std.testing.expectEqual(summary_before_failed_exit.registration_depth, summary_after_failed_exit.registration_depth);
    try std.testing.expectEqual(summary_before_failed_exit.main_iterations, summary_after_failed_exit.main_iterations);
    try std.testing.expectEqual(summary_before_failed_exit.fn_iterations, summary_after_failed_exit.fn_iterations);
    try std.testing.expectEqual(summary_before_failed_exit.total_events, summary_after_failed_exit.total_events);
    try std.testing.expectEqual(summary_before_failed_exit.last_main_emitted_events, summary_after_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(summary_before_failed_exit.last_fn_emitted_events, summary_after_failed_exit.last_fn_emitted_events);
    try std.testing.expectEqual(summary_before_failed_exit.last_main_count, summary_after_failed_exit.last_main_count);
    try std.testing.expectEqual(summary_before_failed_exit.last_fn_count, summary_after_failed_exit.last_fn_count);
    try std.testing.expectEqual(summary_before_failed_exit.exit_runs, summary_after_failed_exit.exit_runs);

    const main_payload = summary_after_failed_exit.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", main_payload.format_template);
    const function_payload = summary_after_failed_exit.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", function_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", function_payload.template_message);

    try module.unregisterFunctionThread();
    try module.exit();

    const summary_after_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, summary_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 0), summary_after_exit.registration_depth);
    try std.testing.expectEqual(summary_before_failed_exit.main_iterations, summary_after_exit.main_iterations);
    try std.testing.expectEqual(summary_before_failed_exit.fn_iterations, summary_after_exit.fn_iterations);
    try std.testing.expectEqual(summary_before_failed_exit.total_events, summary_after_exit.total_events);
    try std.testing.expectEqual(summary_before_failed_exit.last_main_emitted_events, summary_after_exit.last_main_emitted_events);
    try std.testing.expectEqual(summary_before_failed_exit.last_fn_emitted_events, summary_after_exit.last_fn_emitted_events);
    try std.testing.expectEqual(summary_before_failed_exit.last_main_count, summary_after_exit.last_main_count);
    try std.testing.expectEqual(summary_before_failed_exit.last_fn_count, summary_after_exit.last_fn_count);
    try std.testing.expectEqual(@as(usize, 1), summary_after_exit.exit_runs);
}

test "runtime trace-events sample preserves selftest-ready failed-exit summary state until registration is balanced" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();
    const selftest_summary = try module.runSelftest();

    try std.testing.expectEqual(@as(usize, 6), selftest_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), selftest_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), selftest_summary.total_events);

    try module.registerFunctionThread();
    _ = try module.emitMainIteration(4);
    _ = try module.emitFunctionIteration(6);

    const summary_before_failed_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, summary_before_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), summary_before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), summary_before_failed_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), summary_before_failed_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 16), summary_before_failed_exit.total_events);
    try std.testing.expectEqual(@as(usize, 6), summary_before_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(@as(usize, 2), summary_before_failed_exit.last_fn_emitted_events);
    try std.testing.expectEqual(@as(i32, 4), summary_before_failed_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 6), summary_before_failed_exit.last_fn_count);
    try std.testing.expectEqual(@as(usize, 1), summary_before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), summary_before_failed_exit.exit_runs);

    const main_payload_before_failed_exit = summary_before_failed_exit.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", main_payload_before_failed_exit.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", main_payload_before_failed_exit.format_template);
    const function_payload_before_failed_exit = summary_before_failed_exit.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", function_payload_before_failed_exit.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", function_payload_before_failed_exit.template_message);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const summary_after_failed_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, summary_after_failed_exit.stage);
    try std.testing.expectEqual(summary_before_failed_exit.registration_depth, summary_after_failed_exit.registration_depth);
    try std.testing.expectEqual(summary_before_failed_exit.main_iterations, summary_after_failed_exit.main_iterations);
    try std.testing.expectEqual(summary_before_failed_exit.fn_iterations, summary_after_failed_exit.fn_iterations);
    try std.testing.expectEqual(summary_before_failed_exit.total_events, summary_after_failed_exit.total_events);
    try std.testing.expectEqual(summary_before_failed_exit.last_main_emitted_events, summary_after_failed_exit.last_main_emitted_events);
    try std.testing.expectEqual(summary_before_failed_exit.last_fn_emitted_events, summary_after_failed_exit.last_fn_emitted_events);
    try std.testing.expectEqual(summary_before_failed_exit.last_main_count, summary_after_failed_exit.last_main_count);
    try std.testing.expectEqual(summary_before_failed_exit.last_fn_count, summary_after_failed_exit.last_fn_count);
    try std.testing.expectEqual(summary_before_failed_exit.selftest_runs, summary_after_failed_exit.selftest_runs);
    try std.testing.expectEqual(summary_before_failed_exit.exit_runs, summary_after_failed_exit.exit_runs);

    const main_payload_after_failed_exit = summary_after_failed_exit.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", main_payload_after_failed_exit.foo_bar_message);
    try std.testing.expectEqualStrings("iter=%d", main_payload_after_failed_exit.format_template);
    const function_payload_after_failed_exit = summary_after_failed_exit.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", function_payload_after_failed_exit.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", function_payload_after_failed_exit.template_message);

    try module.unregisterFunctionThread();
    try module.exit();

    const summary_after_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, summary_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 0), summary_after_exit.registration_depth);
    try std.testing.expectEqual(summary_before_failed_exit.main_iterations, summary_after_exit.main_iterations);
    try std.testing.expectEqual(summary_before_failed_exit.fn_iterations, summary_after_exit.fn_iterations);
    try std.testing.expectEqual(summary_before_failed_exit.total_events, summary_after_exit.total_events);
    try std.testing.expectEqual(summary_before_failed_exit.last_main_emitted_events, summary_after_exit.last_main_emitted_events);
    try std.testing.expectEqual(summary_before_failed_exit.last_fn_emitted_events, summary_after_exit.last_fn_emitted_events);
    try std.testing.expectEqual(summary_before_failed_exit.last_main_count, summary_after_exit.last_main_count);
    try std.testing.expectEqual(summary_before_failed_exit.last_fn_count, summary_after_exit.last_fn_count);
    try std.testing.expectEqual(summary_before_failed_exit.selftest_runs, summary_after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), summary_after_exit.exit_runs);
}
