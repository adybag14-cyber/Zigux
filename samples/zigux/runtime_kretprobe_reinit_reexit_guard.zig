const std = @import("std");
const kretprobe = @import("runtime_kretprobe.zig");

const LifecycleSnapshot = kretprobe.LifecycleSnapshot;
const ModuleStage = kretprobe.ModuleStage;
const RuntimeKretprobeSample = kretprobe.RuntimeKretprobeSample;

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
    try std.testing.expectEqual(before.last_entry_timestamp_ns, after.last_entry_timestamp_ns);
    try std.testing.expectEqual(before.last_return_timestamp_ns, after.last_return_timestamp_ns);
    try std.testing.expectEqual(before.last_duration_ns, after.last_duration_ns);
    try std.testing.expectEqual(
        before.oldest_active_entry_timestamp_ns,
        after.oldest_active_entry_timestamp_ns,
    );
    try std.testing.expectEqual(
        before.newest_active_entry_timestamp_ns,
        after.newest_active_entry_timestamp_ns,
    );
}

test "phase9 kretprobe sample keeps paired rejected re-init and re-exit rollback explicit after initialized direct activity" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    try module.registerProbe();
    try module.recordEntry();
    try module.recordReturn(13);
    try module.unregisterProbe();

    const before_reinit = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.initialized, before_reinit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_reinit.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_reinit.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), before_reinit.unregistration_runs);
    try std.testing.expect(!before_reinit.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_reinit.active_instances);
    try std.testing.expectEqual(@as(usize, 1), before_reinit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 13), before_reinit.last_retval);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());
    try expectSnapshotStable(before_reinit, module.lifecycleSnapshot());

    try module.exit();

    const before_reexit = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, before_reexit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_reexit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_reexit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_reexit.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_reexit.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), before_reexit.unregistration_runs);
    try std.testing.expect(!before_reexit.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_reexit.active_instances);
    try std.testing.expectEqual(@as(usize, 1), before_reexit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 13), before_reexit.last_retval);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try expectSnapshotStable(before_reexit, module.lifecycleSnapshot());
}

test "phase9 kretprobe sample keeps paired rejected re-init and re-exit rollback explicit after selftest-ready replay" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    _ = try module.runSelftest();
    try module.registerProbe();
    try module.recordEntry();
    try module.recordReturn(42);
    try module.unregisterProbe();

    const before_reinit = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_reinit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_reinit.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), before_reinit.registration_runs);
    try std.testing.expectEqual(@as(usize, 2), before_reinit.unregistration_runs);
    try std.testing.expect(!before_reinit.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_reinit.active_instances);
    try std.testing.expectEqual(@as(usize, 2), before_reinit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 42), before_reinit.last_retval);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.init());
    try expectSnapshotStable(before_reinit, module.lifecycleSnapshot());

    try module.exit();

    const before_reexit = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, before_reexit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_reexit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_reexit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_reexit.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), before_reexit.registration_runs);
    try std.testing.expectEqual(@as(usize, 2), before_reexit.unregistration_runs);
    try std.testing.expect(!before_reexit.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_reexit.active_instances);
    try std.testing.expectEqual(@as(usize, 2), before_reexit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 42), before_reexit.last_retval);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try expectSnapshotStable(before_reexit, module.lifecycleSnapshot());
}
