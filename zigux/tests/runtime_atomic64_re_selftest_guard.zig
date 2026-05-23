const std = @import("std");
const sample = @import("runtime_atomic64_sample");

test "runtime atomic64 sample keeps rejected re-selftest rollback explicit at the module boundary" {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(23);
    _ = try module.runSelftest();

    const before_rejected_selftest_snapshot = module.lifecycleSnapshot();
    const before_rejected_selftest_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_rejected_selftest_snapshot.stage);
    try std.testing.expect(before_rejected_selftest_snapshot.allows_counter_ops);
    try std.testing.expectEqual(@as(i64, 23), before_rejected_selftest_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_rejected_selftest_summary.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    const after_rejected_selftest_snapshot = module.lifecycleSnapshot();
    const after_rejected_selftest_summary = module.summary();
    try std.testing.expectEqual(before_rejected_selftest_snapshot.stage, after_rejected_selftest_snapshot.stage);
    try std.testing.expectEqual(before_rejected_selftest_snapshot.init_runs, after_rejected_selftest_snapshot.init_runs);
    try std.testing.expectEqual(before_rejected_selftest_snapshot.selftest_runs, after_rejected_selftest_snapshot.selftest_runs);
    try std.testing.expectEqual(before_rejected_selftest_snapshot.exit_runs, after_rejected_selftest_snapshot.exit_runs);
    try std.testing.expectEqual(
        before_rejected_selftest_snapshot.allows_counter_ops,
        after_rejected_selftest_snapshot.allows_counter_ops,
    );
    try std.testing.expectEqual(
        before_rejected_selftest_summary.counter_snapshot,
        after_rejected_selftest_summary.counter_snapshot,
    );
    try std.testing.expectEqual(before_rejected_selftest_summary.init_runs, after_rejected_selftest_summary.init_runs);
    try std.testing.expectEqual(
        before_rejected_selftest_summary.selftest_runs,
        after_rejected_selftest_summary.selftest_runs,
    );
    try std.testing.expectEqual(before_rejected_selftest_summary.exit_runs, after_rejected_selftest_summary.exit_runs);

    try module.exit();

    const before_rejected_exit_selftest_snapshot = module.lifecycleSnapshot();
    const before_rejected_exit_selftest_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, before_rejected_exit_selftest_snapshot.stage);
    try std.testing.expect(!before_rejected_exit_selftest_snapshot.allows_counter_ops);
    try std.testing.expectEqual(@as(i64, 23), before_rejected_exit_selftest_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest_summary.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    const after_rejected_exit_selftest_snapshot = module.lifecycleSnapshot();
    const after_rejected_exit_selftest_summary = module.summary();
    try std.testing.expectEqual(before_rejected_exit_selftest_snapshot.stage, after_rejected_exit_selftest_snapshot.stage);
    try std.testing.expectEqual(before_rejected_exit_selftest_snapshot.init_runs, after_rejected_exit_selftest_snapshot.init_runs);
    try std.testing.expectEqual(before_rejected_exit_selftest_snapshot.selftest_runs, after_rejected_exit_selftest_snapshot.selftest_runs);
    try std.testing.expectEqual(before_rejected_exit_selftest_snapshot.exit_runs, after_rejected_exit_selftest_snapshot.exit_runs);
    try std.testing.expectEqual(
        before_rejected_exit_selftest_snapshot.allows_counter_ops,
        after_rejected_exit_selftest_snapshot.allows_counter_ops,
    );
    try std.testing.expectEqual(
        before_rejected_exit_selftest_summary.counter_snapshot,
        after_rejected_exit_selftest_summary.counter_snapshot,
    );
    try std.testing.expectEqual(
        before_rejected_exit_selftest_summary.init_runs,
        after_rejected_exit_selftest_summary.init_runs,
    );
    try std.testing.expectEqual(
        before_rejected_exit_selftest_summary.selftest_runs,
        after_rejected_exit_selftest_summary.selftest_runs,
    );
    try std.testing.expectEqual(
        before_rejected_exit_selftest_summary.exit_runs,
        after_rejected_exit_selftest_summary.exit_runs,
    );
}
