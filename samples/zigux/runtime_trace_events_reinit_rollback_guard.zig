const std = @import("std");
const trace_events = @import("runtime_trace_events.zig");

const ModuleStage = trace_events.ModuleStage;
const RuntimeTraceEventsSummary = trace_events.RuntimeTraceEventsSummary;
const RuntimeTraceEventsSample = trace_events.RuntimeTraceEventsSample;

fn expectSummaryStable(before: RuntimeTraceEventsSummary, after: RuntimeTraceEventsSummary) !void {
    try std.testing.expect(std.meta.eql(before, after));
}

test "phase9 trace-events sample keeps re-init rollback explicit across initialized, selftest-complete, and exited states" {
    var initialized_module = RuntimeTraceEventsSample{};
    try initialized_module.init();
    const initialized_main = try initialized_module.emitMainIteration(7);
    try std.testing.expectEqual(@as(usize, 4), initialized_main);
    try initialized_module.registerFunctionThread();

    const before_initialized_reinit = initialized_module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, before_initialized_reinit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.main_iterations);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 4), before_initialized_reinit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 4), before_initialized_reinit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.register_transitions);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.unregister_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit.exit_runs);
    try std.testing.expectEqual(@as(i32, 7), before_initialized_reinit.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), before_initialized_reinit.last_fn_count);
    try std.testing.expect(before_initialized_reinit.saw_vararg_payload);
    try std.testing.expect(before_initialized_reinit.saw_rel_loc_payload);
    try std.testing.expect(!before_initialized_reinit.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", before_initialized_reinit.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqual(@as(?[]const u8, null), before_initialized_reinit.last_unregister_label);

    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init());

    const after_initialized_reinit = initialized_module.summary();
    try expectSummaryStable(before_initialized_reinit, after_initialized_reinit);

    var selftested_module = RuntimeTraceEventsSample{};
    try selftested_module.init();
    _ = try selftested_module.runSelftest();
    const selftested_main = try selftested_module.emitMainIteration(40);
    try std.testing.expectEqual(@as(usize, 6), selftested_main);

    const before_selftested_reinit = selftested_module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_selftested_reinit.stage);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_reinit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_reinit.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 12), before_selftested_reinit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_reinit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), before_selftested_reinit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit.register_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit.unregister_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_reinit.exit_runs);
    try std.testing.expectEqual(@as(i32, 40), before_selftested_reinit.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), before_selftested_reinit.last_fn_count);
    try std.testing.expect(before_selftested_reinit.saw_vararg_payload);
    try std.testing.expect(before_selftested_reinit.saw_rel_loc_payload);
    try std.testing.expect(before_selftested_reinit.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", before_selftested_reinit.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_selftested_reinit.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("Some times print", before_selftested_reinit.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", before_selftested_reinit.last_main_template_cond_message orelse return error.ExpectedMainPayload);

    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init());

    const after_selftested_reinit = selftested_module.summary();
    try expectSummaryStable(before_selftested_reinit, after_selftested_reinit);

    var exited_module = RuntimeTraceEventsSample{};
    try exited_module.init();
    _ = try exited_module.runSelftest();
    const exited_main = try exited_module.emitMainIteration(3);
    try std.testing.expectEqual(@as(usize, 4), exited_main);
    try exited_module.exit();

    const before_exited_reinit = exited_module.summary();
    try std.testing.expectEqual(ModuleStage.exited, before_exited_reinit.stage);
    try std.testing.expectEqual(@as(usize, 0), before_exited_reinit.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), before_exited_reinit.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), before_exited_reinit.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), before_exited_reinit.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 12), before_exited_reinit.total_events);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.register_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.unregister_transitions);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit.exit_runs);
    try std.testing.expectEqual(@as(i32, 3), before_exited_reinit.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), before_exited_reinit.last_fn_count);
    try std.testing.expect(before_exited_reinit.saw_vararg_payload);
    try std.testing.expect(before_exited_reinit.saw_rel_loc_payload);
    try std.testing.expect(before_exited_reinit.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", before_exited_reinit.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", before_exited_reinit.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqual(@as(?[]const u8, null), before_exited_reinit.last_main_conditional_message);
    try std.testing.expectEqual(@as(?[]const u8, null), before_exited_reinit.last_main_template_cond_message);

    try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.init());

    const after_exited_reinit = exited_module.summary();
    try expectSummaryStable(before_exited_reinit, after_exited_reinit);
}
