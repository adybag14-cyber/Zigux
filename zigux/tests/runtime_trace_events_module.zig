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
    try std.testing.expectEqual(@as(usize, 0), cold_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.total_events);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.exit_runs);
    try std.testing.expectEqual(@as(i32, -1), cold_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), cold_summary.last_fn_count);
    try std.testing.expect(!cold_summary.saw_vararg_payload);
    try std.testing.expect(!cold_summary.saw_rel_loc_payload);
    try std.testing.expect(!cold_summary.saw_conditional_path);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.main_thread_label);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.function_thread_label);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_register_label);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_unregister_label);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_foo_bar_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_random_choice_message);
    try std.testing.expectEqual(@as(?usize, null), cold_summary.last_main_vararg_array_length);
    try std.testing.expectEqual(@as(?bool, null), cold_summary.last_main_vararg_array_terminator_zero);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_template_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_template_cond_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_template_print_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_main_relative_location_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_function_template_message);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_summary.last_function_foo_bar_message);
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
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.total_events);
    try std.testing.expect(!initialized_summary.saw_vararg_payload);
    try std.testing.expect(!initialized_summary.saw_rel_loc_payload);
    try std.testing.expect(!initialized_summary.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", initialized_summary.main_thread_label orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("event-sample-fn", initialized_summary.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), initialized_summary.last_register_label);
    try std.testing.expectEqual(@as(?[]const u8, null), initialized_summary.last_unregister_label);

    const main_events = try module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 6), main_events);
    const main_summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), main_summary.main_iterations);
    try std.testing.expectEqual(@as(usize, 6), main_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), main_summary.fn_thread_events);
    try std.testing.expectEqual(@as(i32, 7), main_summary.last_main_count);
    try std.testing.expect(main_summary.saw_vararg_payload);
    try std.testing.expect(main_summary.saw_rel_loc_payload);
    try std.testing.expect(main_summary.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", main_summary.main_thread_label orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("event-sample-fn", main_summary.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), main_summary.last_register_label);
    try std.testing.expectEqual(@as(?[]const u8, null), main_summary.last_unregister_label);
    try std.testing.expectEqualStrings("hello", main_summary.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Gandalf", main_summary.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 2), main_summary.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(main_summary.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", main_summary.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Some times print", main_summary.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", main_summary.last_main_template_cond_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("I have to be different", main_summary.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", main_summary.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("iter=%d", main_summary.last_format_template orelse return error.ExpectedMainPayload);

    try module.registerFunctionThread();
    const fn_events = try module.emitFunctionIteration(9);
    try std.testing.expectEqual(@as(usize, 2), fn_events);
    const function_summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), function_summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 6), function_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), function_summary.fn_thread_events);
    try std.testing.expectEqual(@as(i32, 9), function_summary.last_fn_count);
    try std.testing.expectEqual(@as(usize, 1), function_summary.registration_depth);
    try std.testing.expectEqualStrings("event-sample", function_summary.main_thread_label orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("event-sample-fn", function_summary.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_reg", function_summary.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), function_summary.last_unregister_label);
    try std.testing.expectEqualStrings("Look at me", function_summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", function_summary.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try module.unregisterFunctionThread();
    try std.testing.expectEqual(@as(usize, 0), module.summary().registration_depth);
    try std.testing.expectEqualStrings("foo_bar_unreg", module.summary().last_unregister_label orelse return error.ExpectedFunctionPayload);

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
    try std.testing.expectEqual(@as(usize, 12), selftest_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), selftest_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 16), selftest_summary.total_events);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(i32, 0), selftest_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), selftest_summary.last_fn_count);
    try std.testing.expect(selftest_summary.saw_vararg_payload);
    try std.testing.expect(selftest_summary.saw_rel_loc_payload);
    try std.testing.expect(selftest_summary.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", selftest_summary.main_thread_label orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("event-sample-fn", selftest_summary.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_reg", selftest_summary.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", selftest_summary.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("hello", selftest_summary.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Mother Goose", selftest_summary.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 0), selftest_summary.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(selftest_summary.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", selftest_summary.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Some times print", selftest_summary.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", selftest_summary.last_main_template_cond_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("I have to be different", selftest_summary.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", selftest_summary.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", selftest_summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", selftest_summary.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("iter=%d", selftest_summary.last_format_template orelse return error.ExpectedMainPayload);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());

    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(sample.ModuleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 12), exited_summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), exited_summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 16), exited_summary.total_events);
    try std.testing.expectEqual(@as(i32, 0), exited_summary.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), exited_summary.last_fn_count);
    try std.testing.expect(exited_summary.saw_vararg_payload);
    try std.testing.expect(exited_summary.saw_rel_loc_payload);
    try std.testing.expect(exited_summary.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", exited_summary.main_thread_label orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("event-sample-fn", exited_summary.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_reg", exited_summary.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", exited_summary.last_unregister_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("hello", exited_summary.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Mother Goose", exited_summary.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 0), exited_summary.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(exited_summary.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", exited_summary.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Some times print", exited_summary.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", exited_summary.last_main_template_cond_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("I have to be different", exited_summary.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", exited_summary.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", exited_summary.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", exited_summary.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("iter=%d", exited_summary.last_format_template orelse return error.ExpectedMainPayload);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(0));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(0));
}

test "runtime trace-events sample keeps registration balance explicit" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();

    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());
    try module.registerFunctionThread();
    try std.testing.expectEqualStrings("foo_bar_reg", module.summary().last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectError(error.OutstandingRegistration, module.exit());
    try module.unregisterFunctionThread();
    try std.testing.expectEqualStrings("foo_bar_unreg", module.summary().last_unregister_label orelse return error.ExpectedFunctionPayload);
    try module.exit();
}

test "runtime trace-events sample keeps failed-exit rollback summary state explicit" {
    var module = sample.RuntimeTraceEventsSample{};
    try module.init();
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(5);
    _ = try module.emitMainIteration(3);

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 6), before_failed_exit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 8), before_failed_exit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.exit_runs);
    try std.testing.expectEqual(@as(i32, 3), before_failed_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 5), before_failed_exit.last_fn_count);
    try std.testing.expect(before_failed_exit.saw_vararg_payload);
    try std.testing.expect(before_failed_exit.saw_rel_loc_payload);
    try std.testing.expect(before_failed_exit.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", before_failed_exit.main_thread_label orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("event-sample-fn", before_failed_exit.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_reg", before_failed_exit.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), before_failed_exit.last_unregister_label);
    try std.testing.expectEqualStrings("hello", before_failed_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Frodo", before_failed_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 3), before_failed_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(before_failed_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", before_failed_exit.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Some times print", before_failed_exit.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", before_failed_exit.last_main_template_cond_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("I have to be different", before_failed_exit.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", before_failed_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", before_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", before_failed_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("iter=%d", before_failed_exit.last_format_template orelse return error.ExpectedMainPayload);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(sample.ModuleStage.initialized, after_failed_exit.stage);
    try std.testing.expectEqual(before_failed_exit.registration_depth, after_failed_exit.registration_depth);
    try std.testing.expectEqual(before_failed_exit.main_iterations, after_failed_exit.main_iterations);
    try std.testing.expectEqual(before_failed_exit.fn_iterations, after_failed_exit.fn_iterations);
    try std.testing.expectEqual(before_failed_exit.main_thread_events, after_failed_exit.main_thread_events);
    try std.testing.expectEqual(before_failed_exit.fn_thread_events, after_failed_exit.fn_thread_events);
    try std.testing.expectEqual(before_failed_exit.total_events, after_failed_exit.total_events);
    try std.testing.expectEqual(before_failed_exit.init_runs, after_failed_exit.init_runs);
    try std.testing.expectEqual(before_failed_exit.selftest_runs, after_failed_exit.selftest_runs);
    try std.testing.expectEqual(before_failed_exit.exit_runs, after_failed_exit.exit_runs);
    try std.testing.expectEqual(before_failed_exit.last_main_count, after_failed_exit.last_main_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, after_failed_exit.last_fn_count);
    try std.testing.expectEqual(before_failed_exit.saw_vararg_payload, after_failed_exit.saw_vararg_payload);
    try std.testing.expectEqual(before_failed_exit.saw_rel_loc_payload, after_failed_exit.saw_rel_loc_payload);
    try std.testing.expectEqual(before_failed_exit.saw_conditional_path, after_failed_exit.saw_conditional_path);
    try std.testing.expectEqualStrings(
        before_failed_exit.main_thread_label orelse return error.ExpectedMainPayload,
        after_failed_exit.main_thread_label orelse return error.ExpectedMainPayload,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.function_thread_label orelse return error.ExpectedFunctionPayload,
        after_failed_exit.function_thread_label orelse return error.ExpectedFunctionPayload,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.last_register_label orelse return error.ExpectedFunctionPayload,
        after_failed_exit.last_register_label orelse return error.ExpectedFunctionPayload,
    );
    try std.testing.expectEqual(
        before_failed_exit.last_unregister_label,
        after_failed_exit.last_unregister_label,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload,
        after_failed_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload,
        after_failed_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload,
    );
    try std.testing.expectEqual(
        before_failed_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload,
        after_failed_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload,
    );
    try std.testing.expectEqual(
        before_failed_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload,
        after_failed_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.last_main_template_message orelse return error.ExpectedMainPayload,
        after_failed_exit.last_main_template_message orelse return error.ExpectedMainPayload,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.last_main_conditional_message orelse return error.ExpectedMainPayload,
        after_failed_exit.last_main_conditional_message orelse return error.ExpectedMainPayload,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.last_main_template_cond_message orelse return error.ExpectedMainPayload,
        after_failed_exit.last_main_template_cond_message orelse return error.ExpectedMainPayload,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.last_main_template_print_message orelse return error.ExpectedMainPayload,
        after_failed_exit.last_main_template_print_message orelse return error.ExpectedMainPayload,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload,
        after_failed_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload,
        after_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.last_function_template_message orelse return error.ExpectedFunctionPayload,
        after_failed_exit.last_function_template_message orelse return error.ExpectedFunctionPayload,
    );
    try std.testing.expectEqualStrings(
        before_failed_exit.last_format_template orelse return error.ExpectedMainPayload,
        after_failed_exit.last_format_template orelse return error.ExpectedMainPayload,
    );

    try module.unregisterFunctionThread();
    const summary = try module.runSelftest();
    try std.testing.expectEqual(@as(usize, 12), summary.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), summary.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 16), summary.total_events);
    try module.exit();

    const final_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, final_summary.stage);
    try std.testing.expectEqual(@as(usize, 2), final_summary.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), final_summary.fn_iterations);
    try std.testing.expectEqual(@as(usize, 16), final_summary.total_events);
    try std.testing.expectEqual(@as(usize, 1), final_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), final_summary.exit_runs);
    try std.testing.expectEqualStrings("event-sample", final_summary.main_thread_label orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("event-sample-fn", final_summary.function_thread_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_reg", final_summary.last_register_label orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("foo_bar_unreg", final_summary.last_unregister_label orelse return error.ExpectedFunctionPayload);
}
