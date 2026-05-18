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

    const replayed_fn_after_failed_exit = try module.emitFunctionIteration(17);
    try std.testing.expectEqual(@as(usize, 2), replayed_fn_after_failed_exit);

    const before_unregister = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_unregister.stage);
    try std.testing.expectEqual(@as(usize, 1), before_unregister.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_unregister.main_iterations);
    try std.testing.expectEqual(@as(usize, 3), before_unregister.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), before_unregister.main_thread_events);
    try std.testing.expectEqual(@as(usize, 6), before_unregister.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 16), before_unregister.total_events);
    try std.testing.expectEqual(@as(usize, 2), before_unregister.register_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_unregister.unregister_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_unregister.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_unregister.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), before_unregister.last_main_count);
    try std.testing.expectEqual(@as(i32, 17), before_unregister.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", before_unregister.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_unregister.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("Look at me", before_unregister.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", before_unregister.last_function_template_message orelse return error.ExpectedFunctionPayload);

    try module.unregisterFunctionThread();
    const before_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_exit.stage);
    try std.testing.expectEqual(@as(usize, 0), before_exit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_exit.unregister_transitions);
    try std.testing.expectEqual(@as(usize, 16), before_exit.total_events);
    try std.testing.expectEqual(@as(usize, 3), before_exit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 6), before_exit.fn_thread_events);
    try std.testing.expectEqual(@as(?usize, 2), before_exit.last_fn_emitted_events);
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
