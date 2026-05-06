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

    const add_unless_blocked = try module.addUnlessCounter(5, 17);
    try std.testing.expect(!add_unless_blocked.changed);
    try std.testing.expectEqual(@as(i64, 17), add_unless_blocked.previous);
    try std.testing.expectEqual(@as(i64, 17), module.snapshotCounter());

    const add_unless_changed = try module.addUnlessCounter(-4, 99);
    try std.testing.expect(add_unless_changed.changed);
    try std.testing.expectEqual(@as(i64, 17), add_unless_changed.previous);
    try std.testing.expectEqual(@as(i64, 13), module.snapshotCounter());

    const and_previous = try module.andCounter(0b0110);
    try std.testing.expectEqual(@as(i64, 13), and_previous);
    try std.testing.expectEqual(@as(i64, 4), module.snapshotCounter());

    const or_previous = try module.orCounter(0b1_0000);
    try std.testing.expectEqual(@as(i64, 4), or_previous);
    try std.testing.expectEqual(@as(i64, 20), module.snapshotCounter());

    const xor_previous = try module.xorCounter(0b0_0111);
    try std.testing.expectEqual(@as(i64, 20), xor_previous);
    try std.testing.expectEqual(@as(i64, 19), module.snapshotCounter());

    const summary = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings("lib/atomic64_test.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), summary.operation_families.len);
    try std.testing.expect(summary.checked_returning_paths);
    try std.testing.expect(summary.checked_bitwise_paths);
    try std.testing.expect(summary.checked_guard_paths);
    try std.testing.expectEqual(@as(i64, 19), module.snapshotCounter());
    try std.testing.expectEqual(@as(usize, 1), module.selftest_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init(23));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.andCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.orCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.xorCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.compareSwapCounter(17, 19));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addUnlessCounter(1, 13));
}

test "runtime atomic64 sample allows exit from initialized state without claiming selftest completion" {
    var module = sample.RuntimeAtomic64Sample{};

    try module.init(-5);
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(i64, -5), module.snapshotCounter());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expectEqual(@as(usize, 0), module.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), module.exit_runs);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), module.selftest_runs);
    try std.testing.expectEqual(@as(i64, -5), module.snapshotCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.compareSwapCounter(-5, 9));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addUnlessCounter(1, -5));
}
