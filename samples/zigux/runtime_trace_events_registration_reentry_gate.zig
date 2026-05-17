const std = @import("std");
const trace_events = @import("runtime_trace_events.zig");

const ModuleStage = trace_events.ModuleStage;
const RuntimeTraceEventsSample = trace_events.RuntimeTraceEventsSample;

test "phase9 trace-events sample keeps balanced registration reusable before and after selftest" {
    var module = RuntimeTraceEventsSample{};
    try module.init();

    try module.registerFunctionThread();
    try std.testing.expectEqual(@as(usize, 2), try module.emitFunctionIteration(3));
    try module.unregisterFunctionThread();

    try module.registerFunctionThread();
    try std.testing.expectEqual(@as(usize, 2), try module.emitFunctionIteration(5));
    try module.unregisterFunctionThread();

    const initialized_reentry = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, initialized_reentry.stage);
    try std.testing.expectEqual(@as(usize, 0), initialized_reentry.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), initialized_reentry.main_iterations);
    try std.testing.expectEqual(@as(usize, 2), initialized_reentry.fn_iterations);
    try std.testing.expectEqual(@as(usize, 0), initialized_reentry.main_thread_events);
    try std.testing.expectEqual(@as(usize, 4), initialized_reentry.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 4), initialized_reentry.total_events);
    try std.testing.expectEqual(@as(?usize, null), initialized_reentry.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), initialized_reentry.last_fn_emitted_events);
    try std.testing.expectEqual(@as(usize, 1), initialized_reentry.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_reentry.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_reentry.exit_runs);
    try std.testing.expectEqual(@as(i32, 5), initialized_reentry.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", initialized_reentry.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", initialized_reentry.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("Look at me", initialized_reentry.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", initialized_reentry.last_function_template_message orelse return error.ExpectedFunctionPayload);

    _ = try module.runSelftest();

    try module.registerFunctionThread();
    try std.testing.expectEqual(@as(usize, 2), try module.emitFunctionIteration(7));
    try module.unregisterFunctionThread();

    const selftest_reentry = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_reentry.stage);
    try std.testing.expectEqual(@as(usize, 0), selftest_reentry.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), selftest_reentry.main_iterations);
    try std.testing.expectEqual(@as(usize, 4), selftest_reentry.fn_iterations);
    try std.testing.expectEqual(@as(usize, 6), selftest_reentry.main_thread_events);
    try std.testing.expectEqual(@as(usize, 8), selftest_reentry.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 14), selftest_reentry.total_events);
    try std.testing.expectEqual(@as(?usize, 6), selftest_reentry.last_main_emitted_events);
    try std.testing.expectEqual(@as(?usize, 2), selftest_reentry.last_fn_emitted_events);
    try std.testing.expectEqual(@as(usize, 1), selftest_reentry.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_reentry.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_reentry.exit_runs);
    try std.testing.expectEqual(@as(i32, 0), selftest_reentry.last_main_count);
    try std.testing.expectEqual(@as(i32, 7), selftest_reentry.last_fn_count);
    try std.testing.expect(selftest_reentry.saw_conditional_path);
    try std.testing.expectEqualStrings("foo_bar_reg", selftest_reentry.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", selftest_reentry.last_unregister_label orelse return error.ExpectedUnregisterLabel);
    try std.testing.expectEqualStrings("Some times print", selftest_reentry.last_main_conditional_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("prints other times", selftest_reentry.last_main_template_cond_message orelse return error.ExpectedMainPayload);
    try std.testing.expectEqualStrings("Look at me", selftest_reentry.last_function_foo_bar_message orelse return error.ExpectedFunctionPayload);
    try std.testing.expectEqualStrings("Look at me too", selftest_reentry.last_function_template_message orelse return error.ExpectedFunctionPayload);
}
