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

test "phase 5 kretprobe sample keeps sample-owned retarget replay explicit" {
    var module = sample.KretprobeExampleSample{};
    const replay = try module.runRetargetReplay("do_sys_openat2");

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", replay.anchor);
    try std.testing.expectEqualStrings(sample.KretprobeExampleSample.default_symbol_name, replay.symbol_before_retarget);
    try std.testing.expectEqualStrings("do_sys_openat2", replay.symbol_after_retarget);
    try std.testing.expectEqual(sample.SampleStage.cold, replay.stage_before_retarget);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_after_init);
    try std.testing.expect(replay.empty_symbol_rejected);
    try std.testing.expect(replay.post_init_retarget_rejected);
    try std.testing.expectEqual(@as(usize, 1), replay.init_runs);
    try std.testing.expectEqualStrings("do_sys_openat2", module.symbol_name);
    try std.testing.expectEqual(sample.SampleStage.initialized, module.stage());
}

test "phase 5 kretprobe sample keeps sample-owned handler boundary replay explicit" {
    var module = sample.KretprobeExampleSample{};
    const replay = try module.runHandlerBoundaryReplay();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", replay.anchor);
    try std.testing.expectEqualStrings(sample.KretprobeExampleSample.default_symbol_name, replay.symbol_name);
    try std.testing.expectEqual(sample.SampleStage.cold, replay.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expect(replay.skipped_kernel_thread_path_checked);
    try std.testing.expect(replay.outstanding_instance_rejected);
    try std.testing.expectEqual(@as(usize, 37), replay.return_value);
    try std.testing.expectEqual(@as(i64, 45), replay.duration_ns);
    try std.testing.expectEqual(@as(usize, 1), replay.nmissed);
    try std.testing.expectEqual(module.maxactiveBudget(), replay.maxactive);
    try std.testing.expectEqual(@as(usize, sample.KretprobeExampleSample.default_maxactive), replay.maxactive);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.replay_runs);
}

test "phase 5 kretprobe sample ownership replay keeps lifecycle snapshots explicit" {
    var module = sample.KretprobeExampleSample{};
    const replay = try module.runOwnershipReplay();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", replay.anchor);
    try std.testing.expectEqualStrings(sample.KretprobeExampleSample.default_symbol_name, replay.symbol_name);
    try std.testing.expectEqual(sample.SampleStage.cold, replay.stage_snapshots[0].stage);
    try std.testing.expectEqual(sample.SampleStage.initialized, replay.stage_snapshots[1].stage);
    try std.testing.expectEqual(sample.SampleStage.armed, replay.stage_snapshots[2].stage);
    try std.testing.expectEqual(sample.SampleStage.replay_complete, replay.stage_snapshots[3].stage);
    try std.testing.expectEqual(sample.SampleStage.exited, replay.stage_snapshots[4].stage);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[0].active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[1].active_instances);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[2].active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[3].active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[4].active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[0].skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[1].skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[3].skipped_kernel_threads);
    try std.testing.expect(replay.stage_snapshots[2].entry_timestamp_armed);
    try std.testing.expect(!replay.stage_snapshots[3].entry_timestamp_armed);
    try std.testing.expect(!replay.stage_snapshots[4].entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[1].init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[3].replay_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[4].exit_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[3].nmissed);
    try std.testing.expect(replay.skipped_kernel_thread_path_checked);
    try std.testing.expectEqual(@as(usize, 42), replay.replay_return_value);
    try std.testing.expectEqual(@as(i64, 75), replay.replay_duration_ns);
    try std.testing.expectEqual(sample.SampleStage.exited, module.stage());
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
    const recovery = try module.runRecoveryReplay("do_sys_openat2");
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", recovery.anchor);
    try std.testing.expectEqualStrings("do_sys_openat2", recovery.symbol_name);
    try std.testing.expectEqual(sample.SampleStage.cold, recovery.stage_before_replay);
    try std.testing.expectEqual(sample.SampleStage.exited, recovery.stage_after_replay);
    try std.testing.expect(recovery.outstanding_exit_rejected);
    try std.testing.expect(recovery.invalid_timestamp_rejected);
    try std.testing.expectEqual(@as(i64, 60), recovery.recovered_duration_ns);
    try std.testing.expect(recovery.post_exit_record_rejected);
    try std.testing.expect(recovery.post_exit_entry_rejected);
    try std.testing.expect(recovery.post_exit_ret_rejected);
    try std.testing.expectEqual(@as(usize, 1), recovery.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), module.active_instances);
    try std.testing.expectEqual(@as(i64, -1), module.instance_data.entry_stamp_ns);
}
