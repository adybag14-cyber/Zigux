const std = @import("std");
const sample = @import("kretprobe_example_sample");

test "phase 5 kretprobe sample stays in the reference-sample lane" {
    const descriptor = sample.KretprobeExampleSample.descriptor();
    const contract = sample.KretprobeExampleSample.reviewContract();
    const expected_focus = [_]sample.SampleFocus{
        .symbol_selection,
        .entry_timestamp,
        .private_data_shape,
        .return_duration,
        .maxactive_budget,
        .missed_summary,
        .ownership_and_lifetime,
    };
    const expected_non_goals = [_][]const u8{
        "register_kretprobe parity",
        "unregister_kretprobe parity",
        "pt_regs or regs_return_value parity",
        "loadable module wiring",
    };

    try std.testing.expectEqualStrings("kretprobe_example", descriptor.name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
    try std.testing.expectEqualSlices(sample.SampleFocus, &expected_focus, contract.focus);
    try std.testing.expectEqual(@as(usize, expected_non_goals.len), contract.non_goals.len);
    for (expected_non_goals, contract.non_goals) |expected, actual| {
        try std.testing.expectEqualStrings(expected, actual);
    }
}

test "phase 5 kretprobe sample replays the bounded skip, return, and summary paths" {
    const expected_focus = [_]sample.SampleFocus{
        .symbol_selection,
        .entry_timestamp,
        .private_data_shape,
        .return_duration,
        .maxactive_budget,
        .missed_summary,
        .ownership_and_lifetime,
    };

    var module = sample.KretprobeExampleSample{};
    try module.init();
    const replay = try module.runAnchorReplay();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", replay.anchor);
    try std.testing.expectEqualStrings("kernel_clone", replay.symbol_name);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expect(replay.skipped_kernel_thread_path_checked);
    try std.testing.expectEqual(module.privateDataSizeBytes(), replay.private_data_size_bytes);
    try std.testing.expectEqual(@as(usize, 42), replay.return_value);
    try std.testing.expectEqual(@as(i64, 75), replay.duration_ns);
    try std.testing.expectEqual(@as(usize, 1), replay.nmissed);
    try std.testing.expectEqual(module.maxactiveBudget(), replay.maxactive);
    try std.testing.expectEqualSlices(sample.SampleFocus, &expected_focus, replay.checked_focus);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.replay_runs);
}

test "phase 5 kretprobe sample keeps symbol retargeting and handler boundaries explicit" {
    var module = sample.KretprobeExampleSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, module.entryHandler(true, 100));
    try std.testing.expectError(error.InvalidSymbolName, module.retargetSymbol(""));

    const replay = try module.runRetargetRecoveryReplay();
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", replay.anchor);
    try std.testing.expectEqualStrings("do_sys_openat2", replay.symbol_name);
    try std.testing.expect(replay.skipped_kernel_thread_path_checked);
    try std.testing.expectEqual(@as(i64, 199), replay.rejected_timestamp_ns);
    try std.testing.expectEqual(@as(usize, 9), replay.return_value);
    try std.testing.expectEqual(@as(i64, 60), replay.duration_ns);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), replay.private_data_size_bytes);
    try std.testing.expectEqual(sample.KretprobeExampleSample.default_maxactive, replay.maxactive);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_after_recovery);
    try std.testing.expectEqualStrings("do_sys_openat2", module.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), module.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 9), module.last_retval);
    try std.testing.expectEqual(@as(i64, 60), module.last_duration_ns);
    try std.testing.expectEqual(@as(i64, -1), module.instance_data.entry_stamp_ns);

    try module.recordMissedInstance();
    try std.testing.expectEqual(@as(usize, 1), module.nmissed);
}

test "phase 5 kretprobe sample keeps the maxactive ceiling immutable" {
    var module = sample.KretprobeExampleSample{};
    const replay = try module.runMaxactiveBudgetReplay();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", replay.anchor);
    try std.testing.expectEqualStrings(sample.KretprobeExampleSample.default_symbol_name, replay.symbol_name);
    try std.testing.expectEqual(sample.KretprobeExampleSample.default_maxactive, replay.budget_before_init);
    try std.testing.expectEqual(sample.KretprobeExampleSample.default_maxactive, replay.budget_after_init);
    try std.testing.expectEqual(sample.KretprobeExampleSample.default_maxactive, replay.replay_budget);
    try std.testing.expectEqual(sample.KretprobeExampleSample.default_maxactive, replay.budget_after_replay);
    try std.testing.expectEqual(@as(usize, 1), replay.missed_instances);
    try std.testing.expectEqual(@as(usize, 1), replay.replay_runs);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expectEqual(sample.KretprobeExampleSample.default_maxactive, module.maxactiveBudget());
}

test "phase 5 kretprobe sample makes ownership and teardown boundaries explicit" {
    var guard_module = sample.KretprobeExampleSample{};
    const lifecycle_guards = try guard_module.runLifecycleGuardReplay();
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", lifecycle_guards.anchor);
    try std.testing.expectEqualStrings(sample.KretprobeExampleSample.default_symbol_name, lifecycle_guards.symbol_name);
    try std.testing.expectEqual(sample.SampleStage.cold, lifecycle_guards.stage_before_init);
    try std.testing.expectEqual(sample.SampleStage.initialized, lifecycle_guards.stage_after_init);
    try std.testing.expect(lifecycle_guards.pre_init_anchor_rejected);
    try std.testing.expect(lifecycle_guards.pre_init_exit_rejected);
    try std.testing.expect(lifecycle_guards.double_init_rejected);
    try std.testing.expect(lifecycle_guards.post_init_retarget_rejected);
    try std.testing.expect(lifecycle_guards.post_init_recovery_rejected);
    try std.testing.expectEqual(@as(usize, 1), lifecycle_guards.init_runs);

    var module = sample.KretprobeExampleSample{};
    const replay = try module.runOwnershipBoundaryReplay();
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", replay.anchor);
    try std.testing.expectEqualStrings(sample.KretprobeExampleSample.default_symbol_name, replay.symbol_name);
    try std.testing.expect(replay.armed_exit_rejected);
    try std.testing.expectEqual(@as(i64, 199), replay.rejected_timestamp_ns);
    try std.testing.expectEqual(@as(i64, 60), replay.recovered_duration_ns);
    try std.testing.expectEqual(sample.SampleStage.exited, replay.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 1), replay.exit_runs);
    try std.testing.expect(replay.post_exit_record_missed_rejected);
    try std.testing.expect(replay.post_exit_entry_rejected);
    try std.testing.expect(replay.post_exit_ret_rejected);
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), module.active_instances);
    try std.testing.expectEqual(@as(i64, -1), module.instance_data.entry_stamp_ns);
}
