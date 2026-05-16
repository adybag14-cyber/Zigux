const std = @import("std");
const trace_events = @import("runtime_trace_events.zig");

const ModuleStage = trace_events.ModuleStage;
const RuntimeTraceEventsSample = trace_events.RuntimeTraceEventsSample;

test "phase9 trace-events sample keeps unregistered function-thread failures fail-closed" {
    var module = RuntimeTraceEventsSample{};
    try module.init();

    const initialized_before = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, initialized_before.stage);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.main_iterations);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.fn_iterations);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.main_thread_events);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.total_events);
    try std.testing.expectEqual(@as(?usize, null), initialized_before.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), initialized_before.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, null), initialized_before.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(usize, 1), initialized_before.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.exit_runs);
    try std.testing.expectEqual(@as(i32, -1), initialized_before.last_main_count);
    try std.testing.expectEqual(@as(i32, -1), initialized_before.last_fn_count);
    try std.testing.expectEqual(@as(?[]const u8, null), initialized_before.last_register_label);
    try std.testing.expectEqual(@as(?[]const u8, null), initialized_before.last_unregister_label);

    try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(3));
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());

    const initialized_after = module.summary();
    try std.testing.expectEqual(initialized_before.stage, initialized_after.stage);
    try std.testing.expectEqual(initialized_before.registration_depth, initialized_after.registration_depth);
    try std.testing.expectEqual(initialized_before.main_iterations, initialized_after.main_iterations);
    try std.testing.expectEqual(initialized_before.fn_iterations, initialized_after.fn_iterations);
    try std.testing.expectEqual(initialized_before.main_thread_events, initialized_after.main_thread_events);
    try std.testing.expectEqual(initialized_before.fn_thread_events, initialized_after.fn_thread_events);
    try std.testing.expectEqual(initialized_before.total_events, initialized_after.total_events);
    try std.testing.expectEqual(initialized_before.last_main_emitted_events, initialized_after.last_main_emitted_events);
    try std.testing.expectEqual(initialized_before.last_fn_emitted_events, initialized_after.last_fn_emitted_events);
    try std.testing.expectEqual(initialized_before.last_main_conditional_event_count, initialized_after.last_main_conditional_event_count);
    try std.testing.expectEqual(initialized_before.init_runs, initialized_after.init_runs);
    try std.testing.expectEqual(initialized_before.selftest_runs, initialized_after.selftest_runs);
    try std.testing.expectEqual(initialized_before.exit_runs, initialized_after.exit_runs);
    try std.testing.expectEqual(initialized_before.last_main_count, initialized_after.last_main_count);
    try std.testing.expectEqual(initialized_before.last_fn_count, initialized_after.last_fn_count);
    try std.testing.expectEqual(initialized_before.last_register_label, initialized_after.last_register_label);
    try std.testing.expectEqual(initialized_before.last_unregister_label, initialized_after.last_unregister_label);

    _ = try module.runSelftest();
    _ = try module.emitMainIteration(5);

    const selftest_complete_before = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_complete_before.stage);
    try std.testing.expectEqual(@as(usize, 0), selftest_complete_before.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), selftest_complete_before.main_iterations);
    try std.testing.expectEqual(@as(usize, 1), selftest_complete_before.fn_iterations);
    try std.testing.expectEqual(@as(usize, 10), selftest_complete_before.main_thread_events);
    try std.testing.expectEqual(@as(usize, 2), selftest_complete_before.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 12), selftest_complete_before.total_events);
    try std.testing.expectEqual(@as(?usize, 4), selftest_complete_before.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), selftest_complete_before.last_fn_emitted_events);
    try std.testing.expectEqual(@as(?usize, 0), selftest_complete_before.last_main_conditional_event_count);
    try std.testing.expectEqual(@as(usize, 1), selftest_complete_before.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_complete_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_complete_before.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), selftest_complete_before.last_main_count);
    try std.testing.expectEqual(@as(i32, 1), selftest_complete_before.last_fn_count);
    try std.testing.expect(selftest_complete_before.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", selftest_complete_before.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", selftest_complete_before.last_unregister_label orelse return error.ExpectedUnregisterLabel);

    try std.testing.expectError(error.FunctionThreadNotRegistered, module.emitFunctionIteration(7));
    try std.testing.expectError(error.RegistrationUnderflow, module.unregisterFunctionThread());

    const selftest_complete_after = module.summary();
    try std.testing.expectEqual(selftest_complete_before.stage, selftest_complete_after.stage);
    try std.testing.expectEqual(selftest_complete_before.registration_depth, selftest_complete_after.registration_depth);
    try std.testing.expectEqual(selftest_complete_before.main_iterations, selftest_complete_after.main_iterations);
    try std.testing.expectEqual(selftest_complete_before.fn_iterations, selftest_complete_after.fn_iterations);
    try std.testing.expectEqual(selftest_complete_before.main_thread_events, selftest_complete_after.main_thread_events);
    try std.testing.expectEqual(selftest_complete_before.fn_thread_events, selftest_complete_after.fn_thread_events);
    try std.testing.expectEqual(selftest_complete_before.total_events, selftest_complete_after.total_events);
    try std.testing.expectEqual(selftest_complete_before.last_main_emitted_events, selftest_complete_after.last_main_emitted_events);
    try std.testing.expectEqual(selftest_complete_before.last_fn_emitted_events, selftest_complete_after.last_fn_emitted_events);
    try std.testing.expectEqual(selftest_complete_before.last_main_conditional_event_count, selftest_complete_after.last_main_conditional_event_count);
    try std.testing.expectEqual(selftest_complete_before.init_runs, selftest_complete_after.init_runs);
    try std.testing.expectEqual(selftest_complete_before.selftest_runs, selftest_complete_after.selftest_runs);
    try std.testing.expectEqual(selftest_complete_before.exit_runs, selftest_complete_after.exit_runs);
    try std.testing.expectEqual(selftest_complete_before.last_main_count, selftest_complete_after.last_main_count);
    try std.testing.expectEqual(selftest_complete_before.last_fn_count, selftest_complete_after.last_fn_count);
    try std.testing.expectEqual(selftest_complete_before.saw_conditional_path, selftest_complete_after.saw_conditional_path);
    try std.testing.expectEqualStrings(selftest_complete_before.last_register_label orelse return error.ExpectedRegisterLabel, selftest_complete_after.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings(selftest_complete_before.last_unregister_label orelse return error.ExpectedUnregisterLabel, selftest_complete_after.last_unregister_label orelse return error.ExpectedUnregisterLabel);
}
