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
    const cold_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.cold, cold_summary.stage);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.total_events);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.registration_depth);
    try std.testing.expectEqual(@as(i32, -1), cold_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), cold_summary.last_fn_count);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_template_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_function_template_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_format_template);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(0));
    try std.testing.expectError(error.FunctionThreadNotRegistered, blk: {
        try module.init();
        break :blk module.emitFunctionIteration(0);
    });

    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    const initialized_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, initialized_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.total_events);

    const main_events = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 6), main_events);
    const main_summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), main_summary.main_iterations);
    try std.testing.expectEqual(@as(i32, 7), main_summary.last_main_count);
    try std.testing.expect(main_summary.saw_vararg_payload);
    try std.testing.expect(main_summary.saw_rel_loc_payload);
    try std.testing.expect(main_summary.saw_conditional_path);
    try std.testing.expectEqualStrings("HELLO", main_summary.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("iter=%d", main_summary.last_format_template orelse return error.ExpectedMainPayload);
    const main_payload = module.last_main_payload orelse return error.ExpectedMainPayload;
    try std.testing.expectEqualStrings("hello", main_payload.foo_bar_message);
    try std.testing.expectEqualStrings("HELLO", main_payload.template_message);
    try std.testing.expectEqualStrings("Some times print", main_payload.conditional_message);
    try std.testing.expectEqualStrings("prints other times", main_payload.template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", main_payload.template_print_message);
    try std.testing.expectEqualStrings("Hello __rel_loc", main_payload.relative_location_message);
    try std.testing.expectEqualStrings("iter=%d", main_payload.format_template);

    try module.registerFunctionThread();
    const fn_events = try module.emitFunctionIteration(9);
    try std.testing.expectEqual(@as(usize, 2), fn_events);
    const function_summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), function_summary.fn_iterations);
    try std.testing.expectEqual(@as(i32, 9), function_summary.last_fn_count);
    try std.testing.expectEqual(@as(usize, 1), function_summary.registration_depth);
    try std.testing.expectEqualStrings("Look at me too", function_summary.last_function_template_message orelse return error.ExpectedFunctionPayload);
    const fn_payload = module.last_function_payload orelse return error.ExpectedFunctionPayload;
    try std.testing.expectEqualStrings("Look at me", fn_payload.foo_bar_message);
    try std.testing.expectEqualStrings("Look at me too", fn_payload.template_message);
    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 0), module.summary().registration_depth);

    const summary = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), summary.event_families.len);
    try std.testing.expectEqual(@as(usize, 12), summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 16), summary.total_events);
    try std.testing.expect(summary.conditional_paths_checked);
    try std.testing.expect(summary.registration_paths_checked);
    const selftest_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, selftest_summary.stage);
    try std.testing.expectEqual(@as(usize, 0), selftest_summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), selftest_summary.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), selftest_summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 16), selftest_summary.total_events);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.selftest_runs);
    try std.testing.expectEqualStrings("HELLO", selftest_summary.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me too", selftest_summary.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());

    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(sample.ModuleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 16), exited_summary.total_events);
    try std.testing.expectEqualStrings("HELLO", exited_summary.last_main_template_message orelse return error.ExpectedMainPayload);
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
    try std.testing.expectError(error.OutstandingRegistration, module.exit());
    try module.unregisterFunctionThread();
    try module.exit();
}
