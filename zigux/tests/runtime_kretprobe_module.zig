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
    try std.testing.expectError(error.InvalidMaxactive, module.configureMaxactive(0));
    try std.testing.expectError(error.InvalidMaxactive, module.configureMaxactive(sample.RuntimeKretprobeSample.default_maxactive + 1));

    try module.retargetSymbol("do_sys_openat2");
    try module.configureMaxactive(3);
    try module.init();
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqualStrings("do_sys_openat2", module.symbol_name);
    try std.testing.expectEqual(@as(usize, 3), module.maxactive);
    const initialized_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, initialized_summary.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);
    try std.testing.expectEqualStrings("do_sys_openat2", initialized_summary.symbol_name);
    try std.testing.expectEqual(@as(usize, 3), initialized_summary.maxactive);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.active_instances);
    try std.testing.expect(!initialized_summary.entry_timestamp_armed);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.configureMaxactive(2));

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
    try outstanding.configureMaxactive(1);
    try outstanding.init();
    const failed_exit_replay = try outstanding.runFailedExitRecoveryReplay();
    try std.testing.expectEqual(sample.ModuleStage.exited, outstanding.stage());
    try std.testing.expectEqual(sample.ModuleStage.initialized, failed_exit_replay.before_failed_exit.stage);
    try std.testing.expectEqualStrings(sample.RuntimeKretprobeSample.default_symbol_name, failed_exit_replay.before_failed_exit.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), failed_exit_replay.before_failed_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), failed_exit_replay.before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), failed_exit_replay.before_failed_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), failed_exit_replay.before_failed_exit.maxactive);
    try std.testing.expectEqual(@as(usize, 1), failed_exit_replay.before_failed_exit.active_instances);
    try std.testing.expect(failed_exit_replay.before_failed_exit.entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 0), failed_exit_replay.before_failed_exit.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), failed_exit_replay.before_failed_exit.nmissed);
    try std.testing.expectEqual(@as(usize, 0), failed_exit_replay.before_failed_exit.last_retval);
    try std.testing.expectEqual(@as(i64, 0), failed_exit_replay.before_failed_exit.last_duration_ns);
    try std.testing.expectEqual(sample.ModuleStage.initialized, failed_exit_replay.after_failed_exit.stage);
    try std.testing.expectEqualStrings(failed_exit_replay.before_failed_exit.symbol_name, failed_exit_replay.after_failed_exit.symbol_name);
    try std.testing.expectEqual(failed_exit_replay.before_failed_exit.init_runs, failed_exit_replay.after_failed_exit.init_runs);
    try std.testing.expectEqual(failed_exit_replay.before_failed_exit.selftest_runs, failed_exit_replay.after_failed_exit.selftest_runs);
    try std.testing.expectEqual(failed_exit_replay.before_failed_exit.exit_runs, failed_exit_replay.after_failed_exit.exit_runs);
    try std.testing.expectEqual(failed_exit_replay.before_failed_exit.maxactive, failed_exit_replay.after_failed_exit.maxactive);
    try std.testing.expectEqual(failed_exit_replay.before_failed_exit.active_instances, failed_exit_replay.after_failed_exit.active_instances);
    try std.testing.expectEqual(failed_exit_replay.before_failed_exit.entry_timestamp_armed, failed_exit_replay.after_failed_exit.entry_timestamp_armed);
    try std.testing.expectEqual(failed_exit_replay.before_failed_exit.skipped_kernel_threads, failed_exit_replay.after_failed_exit.skipped_kernel_threads);
    try std.testing.expectEqual(failed_exit_replay.before_failed_exit.nmissed, failed_exit_replay.after_failed_exit.nmissed);
    try std.testing.expectEqual(failed_exit_replay.before_failed_exit.last_retval, failed_exit_replay.after_failed_exit.last_retval);
    try std.testing.expectEqual(failed_exit_replay.before_failed_exit.last_duration_ns, failed_exit_replay.after_failed_exit.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 17), failed_exit_replay.recovered.retval);
    try std.testing.expectEqual(@as(i64, 80), failed_exit_replay.recovered.duration_ns);
    try std.testing.expect(failed_exit_replay.selftest.skipped_kernel_thread_path_checked);
    try std.testing.expect(failed_exit_replay.selftest.duration_path_checked);
    try std.testing.expect(failed_exit_replay.selftest.missed_instance_path_checked);
    try std.testing.expectEqual(@as(usize, 42), failed_exit_replay.selftest.last_retval);
    try std.testing.expectEqual(@as(i64, 75), failed_exit_replay.selftest.last_duration_ns);
    try std.testing.expectEqual(sample.ModuleStage.exited, failed_exit_replay.final_summary.stage);
    try std.testing.expectEqualStrings(sample.RuntimeKretprobeSample.default_symbol_name, failed_exit_replay.final_summary.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), failed_exit_replay.final_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), failed_exit_replay.final_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), failed_exit_replay.final_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), failed_exit_replay.final_summary.maxactive);
    try std.testing.expectEqual(@as(usize, 1), failed_exit_replay.final_summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), failed_exit_replay.final_summary.nmissed);
    try std.testing.expectEqual(@as(usize, 42), failed_exit_replay.final_summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), failed_exit_replay.final_summary.last_duration_ns);
    try std.testing.expect(!failed_exit_replay.final_summary.entry_timestamp_armed);
}

test "runtime kretprobe sample keeps post-selftest replay explicit at the module boundary" {
    var module = sample.RuntimeKretprobeSample{};
    try module.retargetSymbol("do_exit");
    try module.init();

    _ = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());

    try std.testing.expect(try module.entryHandler(true, 500));
    const replay = try module.retHandler(23, 575);
    try std.testing.expectEqual(@as(usize, 23), replay.retval);
    try std.testing.expectEqual(@as(i64, 75), replay.duration_ns);
    try module.recordMissedInstance();

    const summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, summary.stage);
    try std.testing.expectEqualStrings("do_exit", summary.symbol_name);
    try std.testing.expectEqual(sample.RuntimeKretprobeSample.default_maxactive, summary.maxactive);
    try std.testing.expectEqual(@as(usize, 0), summary.active_instances);
    try std.testing.expectEqual(@as(usize, 1), summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 2), summary.nmissed);
    try std.testing.expectEqual(@as(usize, 23), summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), summary.last_duration_ns);
    try std.testing.expect(!summary.entry_timestamp_armed);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.entryHandler(true, 640));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.retHandler(1, 700));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.recordMissedInstance());
}

test "runtime kretprobe sample rejects maxactive values outside the bounded starter contract" {
    var module = sample.RuntimeKretprobeSample{};
    try std.testing.expectError(error.InvalidMaxactive, module.configureMaxactive(0));
    try std.testing.expectError(error.InvalidMaxactive, module.configureMaxactive(sample.RuntimeKretprobeSample.default_maxactive + 1));
}

test "runtime kretprobe sample keeps maxactive configuration explicit before init" {
    var module = sample.RuntimeKretprobeSample{};
    try module.configureMaxactive(1);
    try std.testing.expectEqual(@as(usize, 1), module.maxactive);

    try module.init();
    const initialized_summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.maxactive);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.configureMaxactive(2));
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
