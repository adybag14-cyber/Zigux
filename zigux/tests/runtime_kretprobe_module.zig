const std = @import("std");
const sample = @import("runtime_kretprobe_sample");

test "runtime kretprobe sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeKretprobeSample.descriptor();

    try std.testing.expectEqualStrings("runtime_kretprobe", descriptor.name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime kretprobe sample enforces lifecycle transitions and return-probe bookkeeping" {
    var module = sample.RuntimeKretprobeSample{};

    try std.testing.expectEqual(sample.ModuleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.retHandler(1, 10));
    try std.testing.expectError(error.InvalidSymbolName, module.retargetSymbol(""));

    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqualStrings("do_sys_openat2", module.symbol_name);
    try std.testing.expectEqual(sample.RuntimeKretprobeSample.default_maxactive, module.maxactive);

    try std.testing.expect(!(try module.entryHandler(false, 11)));
    try std.testing.expectEqual(@as(usize, 1), module.skipped_kernel_threads);
    try std.testing.expect(try module.entryHandler(true, 100));
    try std.testing.expectEqual(@as(usize, 1), module.active_instances);

    const result = try module.retHandler(37, 145);
    try std.testing.expectEqual(@as(usize, 37), result.retval);
    try std.testing.expectEqual(@as(i64, 45), result.duration_ns);
    try std.testing.expectEqual(@as(usize, 0), module.active_instances);
    try std.testing.expectEqual(@as(usize, 37), module.last_retval);
    try std.testing.expectEqual(@as(i64, 45), module.last_duration_ns);

    try module.recordMissedInstance();
    try std.testing.expectEqual(@as(usize, 1), module.nmissed);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.entryHandler(true, 200));
}

test "runtime kretprobe sample keeps bounded per-instance timestamps for concurrent probes" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();

    try std.testing.expect(try module.entryHandler(true, 100));
    try std.testing.expect(try module.entryHandler(true, 160));
    try std.testing.expectEqual(@as(usize, 2), module.active_instances);
    try std.testing.expect(module.summary().entry_timestamp_armed);

    const second = try module.retHandler(12, 210);
    try std.testing.expectEqual(@as(usize, 12), second.retval);
    try std.testing.expectEqual(@as(i64, 50), second.duration_ns);
    try std.testing.expectEqual(@as(usize, 1), module.active_instances);
    try std.testing.expect(module.summary().entry_timestamp_armed);

    const first = try module.retHandler(7, 260);
    try std.testing.expectEqual(@as(usize, 7), first.retval);
    try std.testing.expectEqual(@as(i64, 160), first.duration_ns);
    try std.testing.expectEqual(@as(usize, 0), module.active_instances);
    try std.testing.expect(!module.summary().entry_timestamp_armed);
}

test "runtime kretprobe sample keeps selftest and outstanding-instance paths explicit" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();

    const summary = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", summary.anchor);
    try std.testing.expectEqualStrings(sample.RuntimeKretprobeSample.default_symbol_name, summary.symbol_name);
    try std.testing.expectEqual(@as(usize, 4), summary.probe_focus.len);
    try std.testing.expect(summary.skipped_kernel_thread_path_checked);
    try std.testing.expect(summary.duration_path_checked);
    try std.testing.expect(summary.missed_instance_path_checked);
    try std.testing.expectEqual(@as(usize, 42), summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), summary.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), summary.nmissed);
    try std.testing.expectEqual(sample.RuntimeKretprobeSample.default_maxactive, summary.maxactive);
    try std.testing.expectEqual(@as(usize, 1), module.selftest_runs);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());

    var outstanding = sample.RuntimeKretprobeSample{};
    try outstanding.init();
    try std.testing.expect(try outstanding.entryHandler(true, 200));
    try std.testing.expectError(error.OutstandingProbeInstance, outstanding.exit());
    try std.testing.expectError(error.InvalidTimestampOrder, outstanding.retHandler(9, 199));
    const recovered = try outstanding.retHandler(9, 260);
    try std.testing.expectEqual(@as(i64, 60), recovered.duration_ns);
    try outstanding.exit();
}

test "runtime kretprobe sample rejects maxactive values outside the bounded starter contract" {
    var module = sample.RuntimeKretprobeSample{ .maxactive = sample.RuntimeKretprobeSample.default_maxactive + 1 };
    try std.testing.expectError(error.InvalidMaxactive, module.init());
}
