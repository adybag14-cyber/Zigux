const std = @import("std");
const trace_events = @import("runtime_trace_events.zig");

const ModuleStage = trace_events.ModuleStage;
const RuntimeTraceEventsSample = trace_events.RuntimeTraceEventsSample;

test "phase9 trace-events sample keeps registration reentry reusable across initialized and selftest_complete stages" {
    var module = RuntimeTraceEventsSample{};
    try module.init();

    const initialized_before = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, initialized_before.stage);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.registration_depth);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.fn_iterations);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.total_events);

    try module.registerFunctionThread();
    const initialized_replay = try module.emitFunctionIteration(3);
    try std.testing.expectEqual(@as(usize, 2), initialized_replay);
    try module.unregisterFunctionThread();

    const initialized_after = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, initialized_after.stage);
    try std.testing.expectEqual(@as(usize, 0), initialized_after.registration_depth);
    try std.testing.expectEqual(@as(usize, 1), initialized_after.fn_iterations);
    try std.testing.expectEqual(@as(usize, 2), initialized_after.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 2), initialized_after.total_events);
    try std.testing.expectEqual(@as(?usize, 2), initialized_after.last_fn_emitted_events);
    try std.testing.expectEqual(@as(i32, 3), initialized_after.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", initialized_after.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", initialized_after.last_unregister_label orelse return error.ExpectedUnregisterLabel);

    _ = try module.runSelftest();

    const selftest_before = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_before.stage);
    try std.testing.expectEqual(@as(usize, 0), selftest_before.registration_depth);
    try std.testing.expectEqual(@as(usize, 2), selftest_before.fn_iterations);
    try std.testing.expectEqual(@as(usize, 4), selftest_before.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 10), selftest_before.total_events);
    try std.testing.expectEqual(@as(usize, 1), selftest_before.selftest_runs);
    try std.testing.expectEqual(@as(i32, 1), selftest_before.last_fn_count);

    try module.registerFunctionThread();
    const selftest_replay = try module.emitFunctionIteration(11);
    try std.testing.expectEqual(@as(usize, 2), selftest_replay);
    try module.unregisterFunctionThread();

    const selftest_after = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftest_after.stage);
    try std.testing.expectEqual(@as(usize, 0), selftest_after.registration_depth);
    try std.testing.expectEqual(@as(usize, 3), selftest_after.fn_iterations);
    try std.testing.expectEqual(@as(usize, 6), selftest_after.fn_thread_events);
    try std.testing.expectEqual(@as(usize, 12), selftest_after.total_events);
    try std.testing.expectEqual(@as(usize, 1), selftest_after.selftest_runs);
    try std.testing.expectEqual(@as(?usize, 2), selftest_after.last_fn_emitted_events);
    try std.testing.expectEqual(@as(i32, 11), selftest_after.last_fn_count);
    try std.testing.expectEqualStrings("foo_bar_reg", selftest_after.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", selftest_after.last_unregister_label orelse return error.ExpectedUnregisterLabel);
}
