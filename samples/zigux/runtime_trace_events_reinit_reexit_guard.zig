const std = @import("std");
const trace_events = @import("runtime_trace_events.zig");

const ModuleStage = trace_events.ModuleStage;
const RuntimeTraceEventsSummary = trace_events.RuntimeTraceEventsSummary;
const RuntimeTraceEventsSample = trace_events.RuntimeTraceEventsSample;

fn expectSummaryStable(
    before: RuntimeTraceEventsSummary,
    after: RuntimeTraceEventsSummary,
) !void {
    try std.testing.expect(std.meta.eql(before, after));
}

test "phase9 trace-events sample keeps initialized direct-activity summary explicit across clean exit" {
    var module = RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.emitMainIteration(5);
    try module.registerFunctionThread();
    _ = try module.emitFunctionIteration(7);
    try module.unregisterFunctionThread();

    const before_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, before_exit.stage);
    try std.testing.expectEqual(@as(usize, 0), before_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), before_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), before_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 4), before_exit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), before_exit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 6), before_exit.total_events);
    try std.testing.expectEqual(@as(?usize, 4), before_exit.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), before_exit.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, 0), before_exit.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(usize, 1), before_exit.register_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_exit.unregister_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), before_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 7), before_exit.last_fn_count);
    try std.testing.expect(before_exit.saw_vararg_payload);
    try std.testing.expect(before_exit.saw_rel_loc_payload);
    try std.testing.expect(!before_exit.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", before_exit.main_thread_label orelse return error.ExpectedMainThreadLabel);
    try std.testing.expectEqualStrings("event-sample-fn", before_exit.function_thread_label orelse return error.ExpectedFunctionThreadLabel);
    try std.testing.expectEqualStrings("foo_bar_reg", before_exit.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_exit.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("hello", before_exit.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Mother Goose", before_exit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 0), before_exit.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(before_exit.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", before_exit.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), before_exit.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), before_exit.last_main_template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", before_exit.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", before_exit.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", before_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", before_exit.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("iter=%d", before_exit.last_format_template orelse return error.ExpectedMainPayload);

    try module.exit();

    const after_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(before_exit.registration_depth, after_exit.registration_depth);
    try std.testing.expectEqual(before_exit.main_iterations, after_exit.main_iterations);
    try std.testing.expectEqual(before_exit.fn_iterations, after_exit.fn_iterations);
    try std.testing.expectEqual(before_exit.main_thread_events, after_exit.main_thread_events);
    try std.testing.expectEqual(before_exit.fn_thread_events, after_exit.fn_thread_events);
    try std.testing.expectEqual(before_exit.total_events, after_exit.total_events);
    try std.testing.expectEqual(before_exit.last_main_emitted_events, after_exit.last_main_emitted_events);
    try std.testing.expectEqual(before_exit.last_fn_emitted_events, after_exit.last_fn_emitted_events);
    try std.testing.expectEqual(before_exit.last_main_conditional_event_count, after_exit.last_main_conditional_event_count);
    try std.testing.expectEqual(before_exit.register_transitions, after_exit.register_transitions);
    try std.testing.expectEqual(before_exit.unregister_transitions, after_exit.unregister_transitions);
    try std.testing.expectEqual(before_exit.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(before_exit.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqual(before_exit.last_main_count, after_exit.last_main_count);
    try std.testing.expectEqual(before_exit.last_fn_count, after_exit.last_fn_count);
    try std.testing.expectEqual(before_exit.saw_vararg_payload, after_exit.saw_vararg_payload);
    try std.testing.expectEqual(before_exit.saw_rel_loc_payload, after_exit.saw_rel_loc_payload);
    try std.testing.expectEqual(before_exit.saw_conditional_path, after_exit.saw_conditional_path);
    try std.testing.expectEqualStrings(before_exit.main_thread_label orelse return error.ExpectedMainThreadLabel, after_exit.main_thread_label orelse return error.ExpectedMainThreadLabel);
    try std.testing.expectEqualStrings(before_exit.function_thread_label orelse return error.ExpectedFunctionThreadLabel, after_exit.function_thread_label orelse return error.ExpectedFunctionThreadLabel);
    try std.testing.expectEqualStrings(before_exit.last_register_label orelse return error.ExpectedRegisterLabel, after_exit.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings(before_exit.last_unregister_label orelse return error.ExpectedUnregisterLabel, after_exit.last_unregister_label orelse return error.ExpectedUnregisterLabel);
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

test "phase9 trace-events sample keeps re-init rollback explicit after initialized, selftest-complete, and exited replay" {
    var initialized_module = RuntimeTraceEventsSample{};
    try initialized_module.init();
    _ = try initialized_module.emitMainIteration(5);
    try initialized_module.registerFunctionThread();
    _ = try initialized_module.emitFunctionIteration(7);
    try initialized_module.unregisterFunctionThread();

    const before_initialized_reinit = initialized_module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, before_initialized_reinit.stage);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 4), before_initialized_reinit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), before_initialized_reinit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 6), before_initialized_reinit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), before_initialized_reinit.last_main_count);
    try std.testing.expectEqual(@as(i32, 7), before_initialized_reinit.last_fn_count);
    try std.testing.expect(before_initialized_reinit.saw_vararg_payload);
    try std.testing.expect(before_initialized_reinit.saw_rel_loc_payload);
    try std.testing.expect(!before_initialized_reinit.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", before_initialized_reinit.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_initialized_reinit.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("Mother Goose", before_initialized_reinit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", before_initialized_reinit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);

    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init());
    try expectSummaryStable(before_initialized_reinit, initialized_module.summary());

    var selftested_module = RuntimeTraceEventsSample{};
    try selftested_module.init();
    _ = try selftested_module.runSelftest();
    _ = try selftested_module.emitMainIteration(5);
    try selftested_module.registerFunctionThread();
    _ = try selftested_module.emitFunctionIteration(11);
    try selftested_module.unregisterFunctionThread();

    const before_selftested_reinit = selftested_module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_selftested_reinit.stage);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_reinit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_reinit.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_reinit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), before_selftested_reinit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), before_selftested_reinit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), before_selftested_reinit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_reinit.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), before_selftested_reinit.last_main_count);
    try std.testing.expectEqual(@as(i32, 11), before_selftested_reinit.last_fn_count);
    try std.testing.expect(before_selftested_reinit.saw_vararg_payload);
    try std.testing.expect(before_selftested_reinit.saw_rel_loc_payload);
    try std.testing.expect(before_selftested_reinit.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", before_selftested_reinit.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_selftested_reinit.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("Mother Goose", before_selftested_reinit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", before_selftested_reinit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);

    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init());
    try expectSummaryStable(before_selftested_reinit, selftested_module.summary());

    var exited_module = RuntimeTraceEventsSample{};
    try exited_module.init();
    _ = try exited_module.runSelftest();
    _ = try exited_module.emitMainIteration(5);
    try exited_module.registerFunctionThread();
    _ = try exited_module.emitFunctionIteration(11);
    try exited_module.unregisterFunctionThread();
    try exited_module.exit();

    const before_exited_reinit = exited_module.summary();
    try std.testing.expectEqual(ModuleStage.exited, before_exited_reinit.stage);
    try std.testing.expectEqual(@as(usize, 0), before_exited_reinit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_exited_reinit.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), before_exited_reinit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), before_exited_reinit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), before_exited_reinit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), before_exited_reinit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), before_exited_reinit.last_main_count);
    try std.testing.expectEqual(@as(i32, 11), before_exited_reinit.last_fn_count);
    try std.testing.expect(before_exited_reinit.saw_vararg_payload);
    try std.testing.expect(before_exited_reinit.saw_rel_loc_payload);
    try std.testing.expect(before_exited_reinit.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", before_exited_reinit.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_exited_reinit.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("Mother Goose", before_exited_reinit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", before_exited_reinit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);

    try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.init());
    try expectSummaryStable(before_exited_reinit, exited_module.summary());
}

test "phase9 trace-events sample keeps re-exit rollback explicit after initialized and selftest-complete replay" {
    var initialized_module = RuntimeTraceEventsSample{};
    try initialized_module.init();
    _ = try initialized_module.emitMainIteration(5);
    try initialized_module.registerFunctionThread();
    _ = try initialized_module.emitFunctionIteration(7);
    try initialized_module.unregisterFunctionThread();
    try initialized_module.exit();

    const before_initialized_reexit = initialized_module.summary();
    try std.testing.expectEqual(ModuleStage.exited, before_initialized_reexit.stage);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reexit.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reexit.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reexit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 4), before_initialized_reexit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), before_initialized_reexit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 6), before_initialized_reexit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reexit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reexit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reexit.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), before_initialized_reexit.last_main_count);
    try std.testing.expectEqual(@as(i32, 7), before_initialized_reexit.last_fn_count);
    try std.testing.expect(before_initialized_reexit.saw_vararg_payload);
    try std.testing.expect(before_initialized_reexit.saw_rel_loc_payload);
    try std.testing.expect(!before_initialized_reexit.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", before_initialized_reexit.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_initialized_reexit.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("Mother Goose", before_initialized_reexit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", before_initialized_reexit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);

    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.exit());
    try expectSummaryStable(before_initialized_reexit, initialized_module.summary());

    var selftested_module = RuntimeTraceEventsSample{};
    try selftested_module.init();
    _ = try selftested_module.runSelftest();
    _ = try selftested_module.emitMainIteration(5);
    try selftested_module.registerFunctionThread();
    _ = try selftested_module.emitFunctionIteration(11);
    try selftested_module.unregisterFunctionThread();
    try selftested_module.exit();

    const before_selftested_reexit = selftested_module.summary();
    try std.testing.expectEqual(ModuleStage.exited, before_selftested_reexit.stage);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_reexit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_reexit.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_reexit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), before_selftested_reexit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), before_selftested_reexit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), before_selftested_reexit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), before_selftested_reexit.last_main_count);
    try std.testing.expectEqual(@as(i32, 11), before_selftested_reexit.last_fn_count);
    try std.testing.expect(before_selftested_reexit.saw_vararg_payload);
    try std.testing.expect(before_selftested_reexit.saw_rel_loc_payload);
    try std.testing.expect(before_selftested_reexit.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", before_selftested_reexit.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_selftested_reexit.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("Mother Goose", before_selftested_reexit.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", before_selftested_reexit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);

    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.exit());
    try expectSummaryStable(before_selftested_reexit, selftested_module.summary());
}
