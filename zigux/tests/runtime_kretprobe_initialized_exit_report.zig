const std = @import("std");
const sample = @import("runtime_kretprobe_sample");

test "runtime kretprobe initialized clean exit keeps zeroed report and summary explicit" {
    var module = sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try module.init();

    const before_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);
    try std.testing.expectEqualStrings("do_sys_openat2", before_exit.symbol_name);
    try std.testing.expectEqual(sample.RuntimeKretprobeSample.default_maxactive, before_exit.maxactive);
    try std.testing.expectEqual(@as(usize, 0), before_exit.active_instances);
    try std.testing.expectEqual(@as(usize, 0), before_exit.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), before_exit.nmissed);
    try std.testing.expectEqual(@as(usize, 0), before_exit.last_retval);
    try std.testing.expectEqual(@as(i64, 0), before_exit.last_duration_ns);
    try std.testing.expect(!before_exit.entry_timestamp_armed);

    const exit_report = try module.exit();
    try std.testing.expectEqualStrings("do_sys_openat2", exit_report.symbol_name);
    try std.testing.expectEqual(@as(usize, 0), exit_report.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), exit_report.missed_instances);
    try std.testing.expectEqual(@as(usize, 0), exit_report.last_retval);
    try std.testing.expectEqual(@as(i64, 0), exit_report.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 0), exit_report.selftest_runs);

    const after_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), after_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqualStrings("do_sys_openat2", after_exit.symbol_name);
    try std.testing.expectEqual(sample.RuntimeKretprobeSample.default_maxactive, after_exit.maxactive);
    try std.testing.expectEqual(@as(usize, 0), after_exit.active_instances);
    try std.testing.expectEqual(@as(usize, 0), after_exit.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), after_exit.nmissed);
    try std.testing.expectEqual(@as(usize, 0), after_exit.last_retval);
    try std.testing.expectEqual(@as(i64, 0), after_exit.last_duration_ns);
    try std.testing.expect(!after_exit.entry_timestamp_armed);
}
