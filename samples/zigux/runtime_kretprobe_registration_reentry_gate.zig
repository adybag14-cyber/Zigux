const std = @import("std");
const runtime_kretprobe_sample = @import("runtime_kretprobe_sample");

const LifecycleSnapshot = runtime_kretprobe_sample.LifecycleSnapshot;
const ModuleStage = runtime_kretprobe_sample.ModuleStage;
const RuntimeKretprobeSample = runtime_kretprobe_sample.RuntimeKretprobeSample;

fn expectBalancedCycle(
    module: *RuntimeKretprobeSample,
    expected_stage: ModuleStage,
    expected_registration_runs: usize,
    expected_unregistration_runs: usize,
    expected_completed_instances: usize,
    retval: i32,
) !LifecycleSnapshot {
    try module.registerProbe();
    try module.recordEntry();
    try module.recordReturn(retval);
    try module.unregisterProbe();

    const snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(expected_stage, snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), snapshot.init_runs);
    try std.testing.expectEqual(expected_registration_runs, snapshot.registration_runs);
    try std.testing.expectEqual(expected_unregistration_runs, snapshot.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 0), snapshot.active_instances);
    try std.testing.expectEqual(expected_completed_instances, snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, retval), snapshot.last_retval);
    try std.testing.expect(!snapshot.probe_registered);
    return snapshot;
}

fn expectExitPreservesReplay(before_exit: LifecycleSnapshot, after_exit: LifecycleSnapshot) !void {
    try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(before_exit.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(before_exit.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqual(before_exit.registration_runs, after_exit.registration_runs);
    try std.testing.expectEqual(before_exit.unregistration_runs, after_exit.unregistration_runs);
    try std.testing.expectEqual(before_exit.active_instances, after_exit.active_instances);
    try std.testing.expectEqual(before_exit.completed_instances, after_exit.completed_instances);
    try std.testing.expectEqual(before_exit.last_retval, after_exit.last_retval);
    try std.testing.expectEqual(before_exit.probe_registered, after_exit.probe_registered);
}

fn expectSnapshotStable(before: LifecycleSnapshot, after: LifecycleSnapshot) !void {
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

test "runtime kretprobe registration reentry stays reusable before selftest" {
    var module = RuntimeKretprobeSample{};
    try module.init();

    const first_cycle = try expectBalancedCycle(
        &module,
        .initialized,
        1,
        1,
        1,
        11,
    );
    try std.testing.expectEqual(@as(usize, 0), first_cycle.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), first_cycle.exit_runs);

    const second_cycle = try expectBalancedCycle(
        &module,
        .initialized,
        2,
        2,
        2,
        23,
    );
    try std.testing.expectEqual(@as(usize, 0), second_cycle.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), second_cycle.exit_runs);

    try module.exit();
    try expectExitPreservesReplay(second_cycle, module.lifecycleSnapshot());
}

test "runtime kretprobe registration reentry stays reusable after selftest" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    _ = try module.runSelftest();

    const after_selftest = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.selftest_complete, after_selftest.stage);
    try std.testing.expectEqual(@as(usize, 1), after_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_selftest.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), after_selftest.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 1), after_selftest.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), after_selftest.last_retval);

    const second_cycle = try expectBalancedCycle(
        &module,
        .selftest_complete,
        2,
        2,
        2,
        17,
    );
    try std.testing.expectEqual(@as(usize, 1), second_cycle.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), second_cycle.exit_runs);

    const third_cycle = try expectBalancedCycle(
        &module,
        .selftest_complete,
        3,
        3,
        3,
        29,
    );
    try std.testing.expectEqual(@as(usize, 1), third_cycle.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), third_cycle.exit_runs);

    try module.exit();
    try expectExitPreservesReplay(third_cycle, module.lifecycleSnapshot());
}

test "runtime kretprobe registration reentry stays fail-closed after exit" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    _ = try expectBalancedCycle(&module, .initialized, 1, 1, 1, 11);
    try module.exit();

    const exited_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, exited_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), exited_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 0), exited_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 11), exited_snapshot.last_retval);
    try std.testing.expect(!exited_snapshot.probe_registered);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.registerProbe());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.recordEntry());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.recordReturn(31));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.unregisterProbe());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try expectSnapshotStable(exited_snapshot, module.lifecycleSnapshot());
}