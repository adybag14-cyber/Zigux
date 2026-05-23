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
