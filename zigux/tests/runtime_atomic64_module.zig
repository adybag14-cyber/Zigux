const std = @import("std");
const sample = @import("runtime_atomic64_sample");

test "runtime atomic64 sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeAtomic64Sample.descriptor();

    try std.testing.expectEqualStrings("runtime_atomic64", descriptor.name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime atomic64 sample enforces lifecycle transitions and keeps a 64-bit counter" {
    var module = sample.RuntimeAtomic64Sample{};

    try std.testing.expectEqual(sample.ModuleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    try module.init(0x1111_1111_2222_2222);
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2222), module.snapshotCounter());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);

    const previous = try module.swapCounter(-9);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2222), previous);
    try std.testing.expectEqual(@as(i64, -9), module.snapshotCounter());

    const compare_success = try module.compareSwapCounter(-9, 17);
    try std.testing.expect(compare_success.stored);
    try std.testing.expectEqual(@as(i64, -9), compare_success.previous);
    try std.testing.expectEqual(@as(i64, 17), module.snapshotCounter());

    const compare_mismatch = try module.compareSwapCounter(-9, 33);
    try std.testing.expect(!compare_mismatch.stored);
    try std.testing.expectEqual(@as(i64, 17), compare_mismatch.previous);
    try std.testing.expectEqual(@as(i64, 17), module.snapshotCounter());

    const summary = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings("lib/atomic64_test.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), summary.operation_families.len);
    try std.testing.expect(summary.checked_returning_paths);
    try std.testing.expect(summary.checked_guard_paths);
    try std.testing.expectEqual(@as(usize, 1), module.selftest_runs);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.compareSwapCounter(17, 19));
}
