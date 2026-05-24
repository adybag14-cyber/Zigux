const std = @import("std");
const sample = @import("runtime_kretprobe_sample");

fn expectSnapshotStable(
    before: sample.LifecycleSnapshot,
    after: sample.LifecycleSnapshot,
) !void {
    try std.testing.expectEqual(before.stage, after.stage);
    try std.testing.expectEqual(before.init_runs, after.init_runs);
    try std.testing.expectEqual(before.selftest_runs, after.selftest_runs);
    try std.testing.expectEqual(before.exit_runs, after.exit_runs);
    try std.testing.expectEqual(before.registration_runs, after.registration_runs);
    try std.testing.expectEqual(before.unregistration_runs, after.unregistration_runs);
    try std.testing.expectEqual(before.probe_registered, after.probe_registered);
    try std.testing.expectEqual(before.active_instances, after.active_instances);
    try std.testing.expectEqual(before.completed_instances, after.completed_instances);
    try std.testing.expectEqual(before.last_retval, after.last_retval);
}

test "runtime kretprobe sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeKretprobeSample.descriptor();
    try std.testing.expectEqualStrings("runtime_kretprobe", descriptor.name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime kretprobe sample keeps selftest summary replay explicit at the module boundary" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();

    const selftest_summary = try module.runSelftest();
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", selftest_summary.anchor);
    try std.testing.expect(selftest_summary.checked_registration_paths);
    try std.testing.expect(selftest_summary.checked_return_paths);
    try std.testing.expect(selftest_summary.checked_lifecycle_guards);

    const snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), snapshot.unregistration_runs);
    try std.testing.expect(!snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 1), snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), snapshot.last_retval);
}

test "runtime kretprobe sample keeps lifecycle snapshot replay explicit at the module boundary" {
    var module = sample.RuntimeKretprobeSample{};

    const cold_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.cold, cold_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 0), cold_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_snapshot.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 0), cold_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), cold_snapshot.last_retval);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerProbe());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.recordEntry());

    try module.init();
    const initialized_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.initialized, initialized_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.unregistration_runs);

    _ = try module.runSelftest();
    const selftested_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, selftested_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftested_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_snapshot.unregistration_runs);

    try module.exit();
    const exited_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 0), exited_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), exited_snapshot.last_retval);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerProbe());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.recordReturn(9));
}

test "runtime kretprobe sample keeps initialized-stage exit replay explicit at the module boundary" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();

    const before_exit = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.active_instances);
    try std.testing.expectEqual(@as(usize, 0), before_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), before_exit.last_retval);

    try module.exit();

    const after_exit = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(before_exit.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(before_exit.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqual(before_exit.registration_runs, after_exit.registration_runs);
    try std.testing.expectEqual(before_exit.unregistration_runs, after_exit.unregistration_runs);
    try std.testing.expectEqual(before_exit.active_instances, after_exit.active_instances);
    try std.testing.expectEqual(before_exit.completed_instances, after_exit.completed_instances);
    try std.testing.expectEqual(before_exit.last_retval, after_exit.last_retval);
}

test "runtime kretprobe sample keeps rejected re-init rollback explicit at the module boundary" {
    var initialized_module = sample.RuntimeKretprobeSample{};
    try initialized_module.init();
    const before_initialized_reinit = initialized_module.lifecycleSnapshot();
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init());
    try expectSnapshotStable(before_initialized_reinit, initialized_module.lifecycleSnapshot());

    var selftested_module = sample.RuntimeKretprobeSample{};
    try selftested_module.init();
    _ = try selftested_module.runSelftest();
    const before_selftested_reinit = selftested_module.lifecycleSnapshot();
    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init());
    try expectSnapshotStable(before_selftested_reinit, selftested_module.lifecycleSnapshot());

    var exited_module = sample.RuntimeKretprobeSample{};
    try exited_module.init();
    _ = try exited_module.runSelftest();
    try exited_module.exit();
    const before_exited_reinit = exited_module.lifecycleSnapshot();
    try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.init());
    try expectSnapshotStable(before_exited_reinit, exited_module.lifecycleSnapshot());
}

test "runtime kretprobe sample keeps rejected re-selftest rollback explicit at the module boundary" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();
    _ = try module.runSelftest();

    const before_rejected_selftest = module.lifecycleSnapshot();
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try expectSnapshotStable(before_rejected_selftest, module.lifecycleSnapshot());

    try module.exit();

    const before_rejected_exit_selftest = module.lifecycleSnapshot();
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try expectSnapshotStable(before_rejected_exit_selftest, module.lifecycleSnapshot());
}

test "runtime kretprobe sample keeps rejected re-exit rollback explicit at the module boundary" {
    var initialized_module = sample.RuntimeKretprobeSample{};
    try initialized_module.init();
    try initialized_module.exit();

    const before_initialized_reexit = initialized_module.lifecycleSnapshot();
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.exit());
    try expectSnapshotStable(before_initialized_reexit, initialized_module.lifecycleSnapshot());

    var selftested_module = sample.RuntimeKretprobeSample{};
    try selftested_module.init();
    _ = try selftested_module.runSelftest();
    try selftested_module.exit();

    const before_selftested_reexit = selftested_module.lifecycleSnapshot();
    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.exit());
    try expectSnapshotStable(before_selftested_reexit, selftested_module.lifecycleSnapshot());
}
