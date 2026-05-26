const std = @import("std");
const kretprobe = @import("runtime_kretprobe.zig");

const ModuleStage = kretprobe.ModuleStage;
const RuntimeKretprobeSample = kretprobe.RuntimeKretprobeSample;

test "phase9 kretprobe sample keeps captured initialized snapshot replay explicit across later selftest and exit" {
    var module = RuntimeKretprobeSample{};
    try module.init();

    const initialized_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.initialized, initialized_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.unregistration_runs);
    try std.testing.expect(!initialized_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), initialized_snapshot.last_retval);

    _ = try module.runSelftest();
    try module.exit();

    const exited_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(ModuleStage.initialized, initialized_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.unregistration_runs);
    try std.testing.expect(!initialized_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), initialized_snapshot.last_retval);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.unregistration_runs);
    try std.testing.expect(!exited_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), exited_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), exited_snapshot.last_retval);
}

test "phase9 kretprobe sample keeps captured initialized direct-activity snapshot replay explicit across later selftest and exit" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    try module.registerProbe();
    try module.recordEntry();
    try module.recordReturn(13);
    try module.unregisterProbe();

    const initialized_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.initialized, initialized_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.unregistration_runs);
    try std.testing.expect(!initialized_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 13), initialized_snapshot.last_retval);

    _ = try module.runSelftest();
    try module.exit();

    const exited_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(ModuleStage.initialized, initialized_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.unregistration_runs);
    try std.testing.expect(!initialized_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 13), initialized_snapshot.last_retval);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_snapshot.unregistration_runs);
    try std.testing.expect(!exited_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), exited_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 2), exited_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), exited_snapshot.last_retval);
}
