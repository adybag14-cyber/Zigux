const std = @import("std");
const sample = @import("kretprobe_example_sample");

test "phase 5 kretprobe sample stays in the reference-sample lane" {
    const descriptor = sample.KretprobeExampleSample.descriptor();

    try std.testing.expectEqualStrings("kretprobe_example", descriptor.name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
}

test "phase 5 kretprobe sample replays the bounded skip, return, and summary paths" {
    var module = sample.KretprobeExampleSample{};
    try module.init();
    const replay = try module.runAnchorReplay();

    try std.testing.expectEqualStrings("kernel_clone", replay.symbol_name);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expect(replay.skipped_kernel_thread_path_checked);
    try std.testing.expectEqual(module.privateDataSizeBytes(), replay.private_data_size_bytes);
    try std.testing.expectEqual(@as(usize, 42), replay.return_value);
    try std.testing.expectEqual(@as(i64, 75), replay.duration_ns);
    try std.testing.expectEqual(@as(usize, 1), replay.nmissed);
    try std.testing.expectEqual(module.maxactiveBudget(), replay.maxactive);
    try std.testing.expectEqual(@as(usize, sample.KretprobeExampleSample.default_maxactive), module.maxactiveBudget());
    try std.testing.expectEqual(@as(usize, 6), replay.checked_focus.len);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.replay_runs);
}

test "phase 5 kretprobe sample keeps symbol retargeting and handler boundaries explicit" {
    var module = sample.KretprobeExampleSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, module.entryHandler(true, 100));
    try std.testing.expectError(error.InvalidSymbolName, module.retargetSymbol(""));

    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    try std.testing.expectEqualStrings("do_sys_openat2", module.symbol_name);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), module.privateDataSizeBytes());
    try std.testing.expectEqual(@as(usize, sample.KretprobeExampleSample.default_maxactive), module.maxactiveBudget());
    try std.testing.expect(!(try module.entryHandler(false, 11)));
    try std.testing.expectEqual(@as(usize, 1), module.skipped_kernel_threads);
    try std.testing.expect(try module.entryHandler(true, 100));
    try std.testing.expectEqual(sample.SampleStage.armed, module.stage());
    try std.testing.expectError(error.OutstandingProbeInstance, module.entryHandler(true, 120));

    const result = try module.retHandler(37, 145);
    try std.testing.expectEqual(@as(usize, 37), result.retval);
    try std.testing.expectEqual(@as(i64, 45), result.duration_ns);
    try std.testing.expectEqual(@as(usize, 37), module.last_retval);
    try std.testing.expectEqual(@as(i64, 45), module.last_duration_ns);

    try module.recordMissedInstance();
    try std.testing.expectEqual(@as(usize, 1), module.nmissed);
}

test "phase 5 kretprobe sample ownership summary tracks lifecycle snapshots" {
    var module = sample.KretprobeExampleSample{};

    var summary = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.cold, summary.stage);
    try std.testing.expectEqual(module.maxactiveBudget(), summary.maxactive);
    try std.testing.expectEqual(@as(usize, 0), summary.active_instances);
    try std.testing.expectEqual(@as(usize, 0), summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), summary.nmissed);
    try std.testing.expect(!summary.entry_timestamp_armed);

    try module.init();
    summary = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.initialized, summary.stage);
    try std.testing.expectEqual(module.maxactiveBudget(), summary.maxactive);
    try std.testing.expectEqual(@as(usize, 1), summary.init_runs);

    _ = try module.entryHandler(false, 11);
    summary = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.initialized, summary.stage);
    try std.testing.expectEqual(module.maxactiveBudget(), summary.maxactive);
    try std.testing.expectEqual(@as(usize, 1), summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), summary.active_instances);

    try std.testing.expect(try module.entryHandler(true, 100));
    summary = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.armed, summary.stage);
    try std.testing.expectEqual(module.maxactiveBudget(), summary.maxactive);
    try std.testing.expectEqual(@as(usize, 1), summary.active_instances);
    try std.testing.expect(summary.entry_timestamp_armed);

    _ = try module.retHandler(42, 175);
    try module.recordMissedInstance();
    module.replay_runs += 1;
    module.stage_state = .replay_complete;

    summary = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.replay_complete, summary.stage);
    try std.testing.expectEqual(module.maxactiveBudget(), summary.maxactive);
    try std.testing.expectEqual(@as(usize, 0), summary.active_instances);
    try std.testing.expectEqual(@as(usize, 1), summary.nmissed);
    try std.testing.expectEqual(@as(usize, 1), summary.replay_runs);
    try std.testing.expect(!summary.entry_timestamp_armed);

    try module.exit();
    summary = module.ownershipSummary();
    try std.testing.expectEqual(sample.SampleStage.exited, summary.stage);
    try std.testing.expectEqual(module.maxactiveBudget(), summary.maxactive);
    try std.testing.expectEqual(@as(usize, 1), summary.exit_runs);
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
    try std.testing.expectEqual(@as(usize, 1), lifecycle_guards.init_runs);

    var module = sample.KretprobeExampleSample{};

    try std.testing.expectEqual(sample.SampleStage.cold, module.stage());
    try module.init();
    try std.testing.expectEqual(@as(usize, sample.KretprobeExampleSample.default_maxactive), module.maxactiveBudget());
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
    try std.testing.expect(try module.entryHandler(true, 200));
    try std.testing.expectError(error.OutstandingProbeInstance, module.exit());
    try std.testing.expectError(error.InvalidTimestampOrder, module.retHandler(9, 199));

    const recovered = try module.retHandler(9, 260);
    try std.testing.expectEqual(@as(i64, 60), recovered.duration_ns);
    try std.testing.expectEqual(@as(i64, -1), module.instance_data.entry_stamp_ns);
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());

    try module.exit();
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), module.active_instances);
    try std.testing.expectEqual(@as(i64, -1), module.instance_data.entry_stamp_ns);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.recordMissedInstance());
}
