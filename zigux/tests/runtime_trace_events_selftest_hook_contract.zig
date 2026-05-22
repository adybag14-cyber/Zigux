const std = @import("std");
const trace_events = @import("../../samples/zigux/runtime_trace_events.zig");

const EventFamily = trace_events.EventFamily;
const ModuleStage = trace_events.ModuleStage;
const RuntimeTraceEventsSample = trace_events.RuntimeTraceEventsSample;
const RuntimeTraceEventsSummary = trace_events.RuntimeTraceEventsSummary;

fn expectSummaryStable(before: RuntimeTraceEventsSummary, after: RuntimeTraceEventsSummary) !void {
    try std.testing.expect(std.meta.eql(before, after));
}

test "phase9 trace-events descriptor keeps selftest hook contract explicit" {
    const descriptor = RuntimeTraceEventsSample.descriptor();
    try std.testing.expectEqualStrings("runtime_trace_events", descriptor.name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    var module = RuntimeTraceEventsSample{};
    const cold_before = module.summary();
    try std.testing.expectEqual(ModuleStage.cold, cold_before.stage);
    try std.testing.expectEqual(@as(usize, 0), cold_before.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_before.exit_runs);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_before.main_thread_label);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_before.function_thread_label);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_before.last_register_label);
    try std.testing.expectEqual(@as(?[]const u8, null), cold_before.last_unregister_label);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());

    const cold_after = module.summary();
    try expectSummaryStable(cold_before, cold_after);

    try module.init();
    const selftest = try module.runSelftest();
    try std.testing.expectEqualStrings(descriptor.anchor, selftest.anchor);
    try std.testing.expectEqual(@as(usize, 5), selftest.event_families.len);
    try std.testing.expectEqual(EventFamily.foo_bar, selftest.event_families[0]);
    try std.testing.expectEqual(EventFamily.template, selftest.event_families[1]);
    try std.testing.expectEqual(EventFamily.conditional, selftest.event_families[2]);
    try std.testing.expectEqual(EventFamily.relative_location, selftest.event_families[3]);
    try std.testing.expectEqual(EventFamily.function_callback, selftest.event_families[4]);
    try std.testing.expect(selftest.conditional_paths_checked);
    try std.testing.expect(selftest.registration_paths_checked);

    const after_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, after_selftest.stage);
    try std.testing.expectEqual(@as(usize, 1), after_selftest.init_runs);
    try std.testing.expectEqual(@as(usize, 1), after_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), after_selftest.exit_runs);
    try std.testing.expectEqual(selftest.main_thread_events, after_selftest.main_thread_events);
    try std.testing.expectEqual(selftest.fn_thread_events, after_selftest.fn_thread_events);
    try std.testing.expectEqual(selftest.total_events, after_selftest.total_events);
    try std.testing.expectEqual(selftest.conditional_paths_checked, after_selftest.saw_conditional_path);
    try std.testing.expectEqualStrings("event-sample", after_selftest.main_thread_label orelse return error.ExpectedMainThreadLabel);
    try std.testing.expectEqualStrings("event-sample-fn", after_selftest.function_thread_label orelse return error.ExpectedFunctionThreadLabel);
    try std.testing.expectEqualStrings("foo_bar_reg", after_selftest.last_register_label orelse return error.ExpectedRegisterLabel);
    try std.testing.expectEqualStrings("foo_bar_unreg", after_selftest.last_unregister_label orelse return error.ExpectedUnregisterLabel);

    try module.exit();
    const exited_before_retry = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, exited_before_retry.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_before_retry.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    const exited_after_retry = module.summary();
    try expectSummaryStable(exited_before_retry, exited_after_retry);
}
