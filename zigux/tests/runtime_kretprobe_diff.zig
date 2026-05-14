const std = @import("std");
const sample = @import("runtime_kretprobe_sample");

test "runtime kretprobe diff gate keeps maxactive pressure and nmissed explicit" {
    var module = sample.RuntimeKretprobeSample{ .maxactive = 1 };
    try module.init();

    try std.testing.expect(try module.entryHandler(true, 200));

    const armed = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, armed.stage);
    try std.testing.expectEqual(@as(usize, 1), armed.maxactive);
    try std.testing.expectEqual(@as(usize, 1), armed.active_instances);
    try std.testing.expect(armed.entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 0), armed.nmissed);
    try std.testing.expectEqual(@as(usize, 0), armed.last_retval);
    try std.testing.expectEqual(@as(i64, 0), armed.last_duration_ns);

    try std.testing.expectError(error.MaxactiveExceeded, module.entryHandler(true, 220));

    const pressured = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, pressured.stage);
    try std.testing.expectEqual(@as(usize, 1), pressured.maxactive);
    try std.testing.expectEqual(@as(usize, 1), pressured.active_instances);
    try std.testing.expect(pressured.entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 1), pressured.nmissed);
    try std.testing.expectEqual(@as(usize, 0), pressured.last_retval);
    try std.testing.expectEqual(@as(i64, 0), pressured.last_duration_ns);

    const recovered = try module.retHandler(5, 260);
    try std.testing.expectEqual(@as(usize, 5), recovered.retval);
    try std.testing.expectEqual(@as(i64, 60), recovered.duration_ns);

    const drained = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, drained.stage);
    try std.testing.expectEqual(@as(usize, 0), drained.active_instances);
    try std.testing.expect(!drained.entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 1), drained.nmissed);
    try std.testing.expectEqual(@as(usize, 5), drained.last_retval);
    try std.testing.expectEqual(@as(i64, 60), drained.last_duration_ns);

    const exit_report = try module.exit();
    try std.testing.expectEqualStrings(sample.RuntimeKretprobeSample.default_symbol_name, exit_report.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), exit_report.missed_instances);
    try std.testing.expectEqual(@as(usize, 5), exit_report.last_retval);
    try std.testing.expectEqual(@as(i64, 60), exit_report.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 0), exit_report.selftest_runs);
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
}

test "runtime kretprobe diff gate keeps overlapping entry stamps distinct under concurrent load" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();

    try std.testing.expect(try module.entryHandler(true, 100));
    try std.testing.expect(try module.entryHandler(true, 140));

    const armed = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, armed.stage);
    try std.testing.expectEqual(@as(usize, 2), armed.active_instances);
    try std.testing.expect(armed.entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 0), armed.nmissed);
    try std.testing.expectEqual(@as(usize, 0), armed.selftest_runs);

    const inner = try module.retHandler(7, 170);
    try std.testing.expectEqual(@as(usize, 7), inner.retval);
    try std.testing.expectEqual(@as(i64, 30), inner.duration_ns);

    const after_inner = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, after_inner.stage);
    try std.testing.expectEqual(@as(usize, 1), after_inner.active_instances);
    try std.testing.expect(after_inner.entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 0), after_inner.nmissed);
    try std.testing.expectEqual(@as(usize, 7), after_inner.last_retval);
    try std.testing.expectEqual(@as(i64, 30), after_inner.last_duration_ns);

    const outer = try module.retHandler(11, 240);
    try std.testing.expectEqual(@as(usize, 11), outer.retval);
    try std.testing.expectEqual(@as(i64, 140), outer.duration_ns);

    const drained = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, drained.stage);
    try std.testing.expectEqual(@as(usize, 0), drained.active_instances);
    try std.testing.expect(!drained.entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 0), drained.nmissed);
    try std.testing.expectEqual(@as(usize, 11), drained.last_retval);
    try std.testing.expectEqual(@as(i64, 140), drained.last_duration_ns);

    const exit_report = try module.exit();
    try std.testing.expectEqualStrings(sample.RuntimeKretprobeSample.default_symbol_name, exit_report.symbol_name);
    try std.testing.expectEqual(@as(usize, 0), exit_report.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), exit_report.missed_instances);
    try std.testing.expectEqual(@as(usize, 11), exit_report.last_retval);
    try std.testing.expectEqual(@as(i64, 140), exit_report.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 0), exit_report.selftest_runs);
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
}

test "runtime kretprobe diff gate keeps skipped-kernel-thread and selftest summary cues explicit" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();

    const selftest = try module.runSelftest();
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", selftest.anchor);
    try std.testing.expectEqualStrings(sample.RuntimeKretprobeSample.default_symbol_name, selftest.symbol_name);
    try std.testing.expectEqual(@as(usize, 4), selftest.probe_focus.len);
    try std.testing.expect(selftest.skipped_kernel_thread_path_checked);
    try std.testing.expect(selftest.duration_path_checked);
    try std.testing.expect(selftest.missed_instance_path_checked);
    try std.testing.expectEqual(@as(usize, 42), selftest.last_retval);
    try std.testing.expectEqual(@as(i64, 75), selftest.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), selftest.nmissed);
    try std.testing.expectEqual(sample.RuntimeKretprobeSample.default_maxactive, selftest.maxactive);

    const summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, summary.stage);
    try std.testing.expectEqual(@as(usize, 0), summary.active_instances);
    try std.testing.expect(!summary.entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 1), summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), summary.nmissed);
    try std.testing.expectEqual(@as(usize, 42), summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), summary.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), summary.selftest_runs);

    const exit_report = try module.exit();
    try std.testing.expectEqual(@as(usize, 1), exit_report.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), exit_report.missed_instances);
    try std.testing.expectEqual(@as(usize, 42), exit_report.last_retval);
    try std.testing.expectEqual(@as(i64, 75), exit_report.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), exit_report.selftest_runs);
}
