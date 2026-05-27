const std = @import("std");
const sample = @import("runtime_kretprobe_sample");

fn expectSnapshotStable(before: sample.LifecycleSnapshot, after: sample.LifecycleSnapshot) !void {
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

test "runtime kretprobe sample keeps rejected return-before-entry timestamp rollback explicit across initialized and selftested stages" {
    var initialized = sample.RuntimeKretprobeSample{};
    try initialized.init();
    try initialized.registerProbe();
    try initialized.recordEntryAt(40);

    const before_initialized_rejected_return_timestamp = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(
        sample.ModuleStage.initialized,
        before_initialized_rejected_return_timestamp.stage,
    );
    try std.testing.expectEqual(@as(usize, 1), before_initialized_rejected_return_timestamp.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return_timestamp.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return_timestamp.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_rejected_return_timestamp.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return_timestamp.unregistration_runs);
    try std.testing.expect(before_initialized_rejected_return_timestamp.probe_registered);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_rejected_return_timestamp.active_instances);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return_timestamp.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), before_initialized_rejected_return_timestamp.last_retval);
    try std.testing.expectEqual(@as(?i64, 40), before_initialized_rejected_return_timestamp.last_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, null), before_initialized_rejected_return_timestamp.last_return_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, null), before_initialized_rejected_return_timestamp.last_duration_ns);
    try std.testing.expectEqual(@as(?i64, 40), before_initialized_rejected_return_timestamp.oldest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 40), before_initialized_rejected_return_timestamp.newest_active_entry_timestamp_ns);

    try std.testing.expectError(
        error.ReturnBeforeEntryTimestamp,
        initialized.recordReturnAt(7, 39),
    );
    try expectSnapshotStable(
        before_initialized_rejected_return_timestamp,
        initialized.lifecycleSnapshot(),
    );

    try initialized.recordReturnAt(7, 90);
    try initialized.unregisterProbe();
    try initialized.exit();
    const initialized_after_exit = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, initialized_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_after_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_after_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 7), initialized_after_exit.last_retval);
    try std.testing.expectEqual(@as(?i64, 90), initialized_after_exit.last_return_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 50), initialized_after_exit.last_duration_ns);

    var selftested = sample.RuntimeKretprobeSample{};
    try selftested.init();
    _ = try selftested.runSelftest();
    try selftested.registerProbe();
    try selftested.recordEntryAt(120);

    const before_selftested_rejected_return_timestamp = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(
        sample.ModuleStage.selftest_complete,
        before_selftested_rejected_return_timestamp.stage,
    );
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return_timestamp.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return_timestamp.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_rejected_return_timestamp.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_rejected_return_timestamp.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return_timestamp.unregistration_runs);
    try std.testing.expect(before_selftested_rejected_return_timestamp.probe_registered);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return_timestamp.active_instances);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return_timestamp.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), before_selftested_rejected_return_timestamp.last_retval);
    try std.testing.expectEqual(@as(?i64, 120), before_selftested_rejected_return_timestamp.last_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 20), before_selftested_rejected_return_timestamp.last_return_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 10), before_selftested_rejected_return_timestamp.last_duration_ns);
    try std.testing.expectEqual(@as(?i64, 120), before_selftested_rejected_return_timestamp.oldest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 120), before_selftested_rejected_return_timestamp.newest_active_entry_timestamp_ns);

    try std.testing.expectError(
        error.ReturnBeforeEntryTimestamp,
        selftested.recordReturnAt(17, 119),
    );
    try expectSnapshotStable(
        before_selftested_rejected_return_timestamp,
        selftested.lifecycleSnapshot(),
    );

    try selftested.recordReturnAt(42, 150);
    try selftested.unregisterProbe();
    try selftested.exit();
    const selftested_after_exit = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, selftested_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_after_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), selftested_after_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 42), selftested_after_exit.last_retval);
    try std.testing.expectEqual(@as(?i64, 150), selftested_after_exit.last_return_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 30), selftested_after_exit.last_duration_ns);
}
