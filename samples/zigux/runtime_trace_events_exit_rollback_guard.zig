const std = @import("std");
const trace_events = @import("runtime_trace_events.zig");

const ModuleStage = trace_events.ModuleStage;
const RuntimeTraceEventsSummary = trace_events.RuntimeTraceEventsSummary;
const RuntimeTraceEventsSample = trace_events.RuntimeTraceEventsSample;

fn expectSummaryStable(before: RuntimeTraceEventsSummary, after: RuntimeTraceEventsSummary) !void {
    try std.testing.expect(std.meta.eql(before, after));
}

test "phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay" {
    var module = RuntimeTraceEventsSample{};
    try module.init();
    _ = try module.runSelftest();

    const replayed_main = try module.emitMainIteration(5);
    try std.testing.expectEqual(@as(usize, 4), replayed_main);
    try module.registerFunctionThread();
    const replayed_fn = try module.emitFunctionIteration(15);
    try std.testing.expectEqual(@as(usize, 2), replayed_fn);

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), before_failed_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), before_failed_exit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), before_failed_exit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), before_failed_exit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), before_failed_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 15), before_failed_exit.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", before_failed_exit.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_failed_exit.last_unregister_label orelse return error.ExpectedUnregisterLabel);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());

    const after_failed_exit = module.summary();
    try expectSummaryStable(before_failed_exit, after_failed_exit);

    const replayed_main_after_failed_exit = try module.emitMainIteration(9);
    try std.testing.expectEqual(@as(usize, 4), replayed_main_after_failed_exit);

    const after_failed_exit_main_replay = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, after_failed_exit_main_replay.stage);
    try std.testing.expectEqual(@as(usize, 1), after_failed_exit_main_replay.registration_depth);
    try std.testing.expectEqual(@as(usize, 3), after_failed_exit_main_replay.main_iterations);
    try std.testing.expectEqual(before_failed_exit.fn_iterations, after_failed_exit_main_replay.fn_iterations);
    try std.testing.expectEqual(@as(usize, 14), after_failed_exit_main_replay.main_thread_events);
    try std.testing.expectEqual(before_failed_exit.fn_thread_events, after_failed_exit_main_replay.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 18), after_failed_exit_main_replay.total_events);
    try std.testing.expectEqual(@as(?usize, 4), after_failed_exit_main_replay.last_main_emitted_events);
    try std.testing.expectEqual(before_failed_exit.last_fn_emitted_events, after_failed_exit_main_replay.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, 0), after_failed_exit_main_replay.last_main_conditional_event_count);
    try std.testing.expectEqual(before_failed_exit.register_transitions, after_failed_exit_main_replay.register_transitions);
    try std.testing.expectEqual(before_failed_exit.unregister_transitions, after_failed_exit_main_replay.unregister_transitions);
    try std.testing.expectEqual(before_failed_exit.init_runs, after_failed_exit_main_replay.init_runs);
    try std.testing.expectEqual(before_failed_exit.selftest_runs, after_failed_exit_main_replay.selftest_runs);
    try std.testing.expectEqual(before_failed_exit.exit_runs, after_failed_exit_main_replay.exit_runs);
    try std.testing.expectEqual(@as(i32, 9), after_failed_exit_main_replay.last_main_count);
    try std.testing.expectEqual(before_failed_exit.last_fn_count, after_failed_exit_main_replay.last_fn_count);
    try std.testing.expectEqual(before_failed_exit.saw_vararg_payload, after_failed_exit_main_replay.saw_vararg_payload);
    try std.testing.expectEqual(before_failed_exit.saw_rel_loc_payload, after_failed_exit_main_replay.saw_rel_loc_payload);
    try std.testing.expectEqual(before_failed_exit.saw_conditional_path, after_failed_exit_main_replay.saw_conditional_path);
    try std.testing.expectEqualStrings(before_failed_exit.main_thread_label orelse return error.ExpectedMainThreadLabel, after_failed_exit_main_replay.main_thread_label orelse return error.ExpectedMainThreadLabel);
    try std.testing.expectEqualStrings(before_failed_exit.function_thread_label orelse return error.ExpectedFunctionThreadLabel, after_failed_exit_main_replay.function_thread_label orelse return error.ExpectedFunctionThreadLabel);
    try std.testing.expectEqualStrings(before_failed_exit.last_register_label orelse return error.ExpectedRegisterLabel, after_failed_exit_main_replay.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings(before_failed_exit.last_unregister_label orelse return error.ExpectedUnregisterLabel, after_failed_exit_main_replay.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("hello", after_failed_exit_main_replay.last_main_foo_bar_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("One ring to rule them all", after_failed_exit_main_replay.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 4), after_failed_exit_main_replay.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expect(after_failed_exit_main_replay.last_main_vararg_array_terminator_zero orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("HELLO", after_failed_exit_main_replay.last_main_template_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit_main_replay.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), after_failed_exit_main_replay.last_main_template_cond_message);
    try std.testing.expectEqualStrings("I have to be different", after_failed_exit_main_replay.last_main_template_print_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Hello __rel_loc", after_failed_exit_main_replay.last_main_relative_location_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload, after_failed_exit_main_replay.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings(before_failed_exit.last_function_template_message orelse return error.ExpectedFunctionPayload, after_failed_exit_main_replay.last_function_template_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("iter=%d", after_failed_exit_main_replay.last_format_template orelse return error.ExpectedMainPayload);

    const replayed_fn_after_failed_exit = try module.emitFunctionIteration(17);
    try std.testing.expectEqual(@as(usize, 2), replayed_fn_after_failed_exit);

    const before_unregister = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_unregister.stage);
    try std.testing.expectEqual(@as(usize, 1), before_unregister.registration_depth);
    try std.testing.expectEqual(@as(usize, 3), before_unregister.main_iterations);
    try std.testing.expectEqual(@as(usize, 3), before_unregister.fn_iterations);
    try std.testing.expectEqual(@as(usize, 14), before_unregister.main_thread_events);
    try std.testing.expectEqual(@as(usize, 6), before_unregister.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 20), before_unregister.total_events);
    try std.testing.expectEqual(@as(usize, 2), before_unregister.register_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_unregister.unregister_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_unregister.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_unregister.exit_runs);
    try std.testing.expectEqual(@as(i32, 9), before_unregister.last_main_count);
    try std.testing.expectEqual(@as(i32, 17), before_unregister.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", before_unregister.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_unregister.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("One ring to rule them all", before_unregister.last_main_random_choice_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqual(@as(usize, 4), before_unregister.last_main_vararg_array_length orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", before_unregister.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", before_unregister.last_function_template_message orelse return error.ExpectedFunctionPayload);

    try module.unregisterFunctionThread();
    const before_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_exit.stage);
    try std.testing.expectEqual(@as(usize, 0), before_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_exit.unregister_transitions);
    try std.testing.expectEqual(@as(usize, 20), before_exit.total_events);
    try std.testing.expectEqual(@as(usize, 3), before_exit.main_iterations);
    try std.testing.expectEqual(@as(usize, 3), before_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 14), before_exit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 6), before_exit.fn_thread_events);
    try std.testing.expectEqual(@as(?usize, 4), before_exit.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), before_exit.last_fn_emitted_events);
    try std.testing.expectEqual(@as(i32, 9), before_exit.last_main_count);
    try std.testing.expectEqual(@as(i32, 17), before_exit.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", before_exit.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_exit.last_unregister_label orelse return error.ExpectedUnregisterLabel);

    try module.exit();

    const after_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
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
    try std.testing.expectEqual(before_exit.last_main_count, after_exit.last_main_count);
    try std.testing.expectEqual(before_exit.last_fn_count, after_exit.last_fn_count);
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

    const exited_before_rejected_ops = module.summary();
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(17));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.emitFunctionIteration(19));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterFunctionThread());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());

    const exited_after_rejected_ops = module.summary();
    try expectSummaryStable(exited_before_rejected_ops, exited_after_rejected_ops);
}
