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

test "runtime kretprobe sample keeps reusable probe replay explicit after selftest at the module boundary" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();
    _ = try module.runSelftest();

    try module.registerProbe();
    try module.recordEntry();
    try module.recordReturn(17);
    try module.unregisterProbe();

    const before_exit = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), before_exit.registration_runs);
    try std.testing.expectEqual(@as(usize, 2), before_exit.unregistration_runs);
    try std.testing.expect(!before_exit.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_exit.active_instances);
    try std.testing.expectEqual(@as(usize, 2), before_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 17), before_exit.last_retval);

    try module.exit();

    const after_exit = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(before_exit.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(before_exit.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqual(before_exit.registration_runs, after_exit.registration_runs);
    try std.testing.expectEqual(before_exit.unregistration_runs, after_exit.unregistration_runs);
    try std.testing.expectEqual(before_exit.probe_registered, after_exit.probe_registered);
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

test "runtime kretprobe sample keeps duplicate registration and failed exit rollback explicit at the module boundary" {
    var initialized_module = sample.RuntimeKretprobeSample{};
    try initialized_module.init();
    try initialized_module.registerProbe();

    const before_initialized_duplicate_registration = initialized_module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_initialized_duplicate_registration.stage);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_duplicate_registration.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_duplicate_registration.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_duplicate_registration.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_duplicate_registration.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_duplicate_registration.unregistration_runs);
    try std.testing.expect(before_initialized_duplicate_registration.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_duplicate_registration.active_instances);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_duplicate_registration.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), before_initialized_duplicate_registration.last_retval);

    try std.testing.expectError(error.ProbeAlreadyRegistered, initialized_module.registerProbe());
    try expectSnapshotStable(
        before_initialized_duplicate_registration,
        initialized_module.lifecycleSnapshot(),
    );

    const before_initialized_failed_exit = initialized_module.lifecycleSnapshot();
    try std.testing.expectError(error.OutstandingRegistration, initialized_module.exit());
    try expectSnapshotStable(before_initialized_failed_exit, initialized_module.lifecycleSnapshot());

    try initialized_module.unregisterProbe();
    try initialized_module.exit();
    const initialized_after_exit = initialized_module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, initialized_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_after_exit.exit_runs);

    var selftested_module = sample.RuntimeKretprobeSample{};
    try selftested_module.init();
    _ = try selftested_module.runSelftest();
    try selftested_module.registerProbe();

    const before_selftested_duplicate_registration = selftested_module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_selftested_duplicate_registration.stage);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_duplicate_registration.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_duplicate_registration.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_duplicate_registration.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_duplicate_registration.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_duplicate_registration.unregistration_runs);
    try std.testing.expect(before_selftested_duplicate_registration.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_duplicate_registration.active_instances);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_duplicate_registration.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), before_selftested_duplicate_registration.last_retval);

    try std.testing.expectError(error.ProbeAlreadyRegistered, selftested_module.registerProbe());
    try expectSnapshotStable(
        before_selftested_duplicate_registration,
        selftested_module.lifecycleSnapshot(),
    );

    const before_selftested_failed_exit = selftested_module.lifecycleSnapshot();
    try std.testing.expectError(error.OutstandingRegistration, selftested_module.exit());
    try expectSnapshotStable(before_selftested_failed_exit, selftested_module.lifecycleSnapshot());

    try selftested_module.recordEntry();
    try selftested_module.recordReturn(42);
    try selftested_module.unregisterProbe();
    try selftested_module.exit();
    const selftested_after_exit = selftested_module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, selftested_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_after_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), selftested_after_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 42), selftested_after_exit.last_retval);
}

test "runtime kretprobe sample keeps failed unregister rollback explicit while a return instance is still active at the module boundary" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();
    try module.registerProbe();
    try module.recordEntry();

    const before_failed_unregister = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_failed_unregister.stage);
    try std.testing.expectEqual(@as(usize, 1), before_failed_unregister.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_unregister.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_unregister.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_unregister.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_unregister.unregistration_runs);
    try std.testing.expect(before_failed_unregister.probe_registered);
    try std.testing.expectEqual(@as(usize, 1), before_failed_unregister.active_instances);
    try std.testing.expectEqual(@as(usize, 0), before_failed_unregister.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), before_failed_unregister.last_retval);

    try std.testing.expectError(error.OutstandingReturnInstance, module.unregisterProbe());
    try expectSnapshotStable(before_failed_unregister, module.lifecycleSnapshot());

    try module.recordReturn(21);

    const before_cleanup = module.lifecycleSnapshot();
    try std.testing.expect(before_cleanup.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_cleanup.active_instances);
    try std.testing.expectEqual(@as(usize, 1), before_cleanup.completed_instances);
    try std.testing.expectEqual(@as(?i32, 21), before_cleanup.last_retval);

    try module.unregisterProbe();
    try module.exit();

    const after_exit = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(before_cleanup.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(before_cleanup.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqual(before_cleanup.registration_runs, after_exit.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.unregistration_runs);
    try std.testing.expectEqual(before_cleanup.completed_instances, after_exit.completed_instances);
    try std.testing.expectEqual(before_cleanup.last_retval, after_exit.last_retval);
}

test "runtime kretprobe sample keeps rejected entry-without-registration rollback explicit at the module boundary" {
    var initialized_module = sample.RuntimeKretprobeSample{};
    try initialized_module.init();

    const before_initialized_rejected_entry = initialized_module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_initialized_rejected_entry.stage);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_rejected_entry.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_entry.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_entry.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_entry.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_entry.unregistration_runs);
    try std.testing.expect(!before_initialized_rejected_entry.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_entry.active_instances);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_entry.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), before_initialized_rejected_entry.last_retval);

    try std.testing.expectError(error.ProbeNotRegistered, initialized_module.recordEntry());
    try expectSnapshotStable(
        before_initialized_rejected_entry,
        initialized_module.lifecycleSnapshot(),
    );

    try initialized_module.exit();
    const initialized_after_exit = initialized_module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, initialized_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_after_exit.exit_runs);

    var selftested_module = sample.RuntimeKretprobeSample{};
    try selftested_module.init();
    _ = try selftested_module.runSelftest();

    const before_selftested_rejected_entry = selftested_module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_selftested_rejected_entry.stage);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_entry.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_entry.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_rejected_entry.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_entry.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_entry.unregistration_runs);
    try std.testing.expect(!before_selftested_rejected_entry.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_rejected_entry.active_instances);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_entry.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), before_selftested_rejected_entry.last_retval);

    try std.testing.expectError(error.ProbeNotRegistered, selftested_module.recordEntry());
    try expectSnapshotStable(
        before_selftested_rejected_entry,
        selftested_module.lifecycleSnapshot(),
    );

    try selftested_module.exit();
    const selftested_after_exit = selftested_module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, selftested_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_after_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_after_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), selftested_after_exit.last_retval);
}

test "runtime kretprobe sample keeps rejected return-without-entry rollback explicit at the module boundary" {
    var initialized_module = sample.RuntimeKretprobeSample{};
    try initialized_module.init();
    try initialized_module.registerProbe();

    const before_initialized_rejected_return = initialized_module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_initialized_rejected_return.stage);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_rejected_return.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_rejected_return.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return.unregistration_runs);
    try std.testing.expect(before_initialized_rejected_return.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return.active_instances);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), before_initialized_rejected_return.last_retval);

    try std.testing.expectError(error.ReturnWithoutEntry, initialized_module.recordReturn(7));
    try expectSnapshotStable(
        before_initialized_rejected_return,
        initialized_module.lifecycleSnapshot(),
    );

    try initialized_module.unregisterProbe();
    try initialized_module.exit();
    const initialized_after_exit = initialized_module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, initialized_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_after_exit.exit_runs);

    var selftested_module = sample.RuntimeKretprobeSample{};
    try selftested_module.init();
    _ = try selftested_module.runSelftest();
    try selftested_module.registerProbe();

    const before_selftested_rejected_return = selftested_module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_selftested_rejected_return.stage);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_rejected_return.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_rejected_return.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return.unregistration_runs);
    try std.testing.expect(before_selftested_rejected_return.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_rejected_return.active_instances);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), before_selftested_rejected_return.last_retval);

    try std.testing.expectError(error.ReturnWithoutEntry, selftested_module.recordReturn(11));
    try expectSnapshotStable(
        before_selftested_rejected_return,
        selftested_module.lifecycleSnapshot(),
    );

    try selftested_module.recordEntry();
    try selftested_module.recordReturn(42);
    try selftested_module.unregisterProbe();
    try selftested_module.exit();
    const selftested_after_exit = selftested_module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, selftested_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_after_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), selftested_after_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 42), selftested_after_exit.last_retval);
}
