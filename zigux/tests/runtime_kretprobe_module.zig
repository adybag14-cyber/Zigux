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
    const too_long_symbol = [_]u8{'x'} ** sample.RuntimeKretprobeSample.max_symbol_name_len;

    try std.testing.expectEqual(sample.ModuleStage.cold, module.stage());
    const cold_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.cold, cold_summary.stage);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.active_instances);
    try std.testing.expect(!cold_summary.entry_timestamp_armed);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.retHandler(1, 10));
    try std.testing.expectError(error.InvalidSymbolName, module.retargetSymbol(""));
    try std.testing.expectError(error.SymbolNameTooLong, module.retargetSymbol(too_long_symbol[0..]));

    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqualStrings("do_sys_openat2", module.symbol_name);
    try std.testing.expectEqual(sample.RuntimeKretprobeSample.default_maxactive, module.maxactive);
    const initialized_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, initialized_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);
    try std.testing.expectEqualStrings("do_sys_openat2", initialized_summary.symbol_name);
    try std.testing.expectEqual(sample.RuntimeKretprobeSample.default_maxactive, initialized_summary.maxactive);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.active_instances);
    try std.testing.expect(!initialized_summary.entry_timestamp_armed);

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
    const ready_to_exit = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, ready_to_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), ready_to_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), ready_to_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), ready_to_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), ready_to_exit.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), ready_to_exit.nmissed);
    try std.testing.expectEqual(@as(usize, 37), ready_to_exit.last_retval);
    try std.testing.expectEqual(@as(i64, 45), ready_to_exit.last_duration_ns);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.nmissed);
    try std.testing.expectEqual(@as(usize, 37), exited_summary.last_retval);
    try std.testing.expectEqual(@as(i64, 45), exited_summary.last_duration_ns);
    try std.testing.expect(!exited_summary.entry_timestamp_armed);
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
    const selftest_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, selftest_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_summary.exit_runs);
    try std.testing.expectEqualStrings(sample.RuntimeKretprobeSample.default_symbol_name, selftest_summary.symbol_name);
    try std.testing.expectEqual(sample.RuntimeKretprobeSample.default_maxactive, selftest_summary.maxactive);
    try std.testing.expectEqual(@as(usize, 0), selftest_summary.active_instances);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.nmissed);
    try std.testing.expectEqual(@as(usize, 42), selftest_summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), selftest_summary.last_duration_ns);
    try std.testing.expect(!selftest_summary.entry_timestamp_armed);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.nmissed);
    try std.testing.expectEqual(@as(usize, 42), exited_summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), exited_summary.last_duration_ns);
    try std.testing.expect(!exited_summary.entry_timestamp_armed);

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

test "runtime kretprobe sample keeps the Linux KSYM_NAME_LEN symbol cap explicit" {
    const too_long_symbol = [_]u8{'k'} ** sample.RuntimeKretprobeSample.max_symbol_name_len;

    var cold_module = sample.RuntimeKretprobeSample{};
    try std.testing.expectError(error.SymbolNameTooLong, cold_module.retargetSymbol(too_long_symbol[0..]));

    var preset_symbol_module = sample.RuntimeKretprobeSample{
        .symbol_name = too_long_symbol[0..],
    };
    try std.testing.expectError(error.SymbolNameTooLong, preset_symbol_module.init());
}
