const std = @import("std");
const sample = @import("runtime_atomic64_sample");

test "runtime atomic64 sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeAtomic64Sample.descriptor();

    try std.testing.expectEqualStrings("runtime_atomic64", descriptor.name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime atomic64 sample exposes lifecycle snapshots across stage transitions" {
    var module = sample.RuntimeAtomic64Sample{};

    const cold = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.cold, cold.stage);
    try std.testing.expectEqual(@as(usize, 0), cold.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold.exit_runs);
    try std.testing.expect(!cold.allows_counter_ops);

    try module.init(23);
    const initialized = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.initialized, initialized.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized.exit_runs);
    try std.testing.expect(initialized.allows_counter_ops);

    _ = try module.runSelftest();
    const selftested = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, selftested.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftested.exit_runs);
    try std.testing.expect(selftested.allows_counter_ops);

    try module.exit();
    const exited = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited.stage);
    try std.testing.expectEqual(@as(usize, 1), exited.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.exit_runs);
    try std.testing.expect(!exited.allows_counter_ops);
}

test "runtime atomic64 sample enforces lifecycle transitions and keeps a 64-bit counter" {
    var module = sample.RuntimeAtomic64Sample{};

    try std.testing.expectEqual(sample.ModuleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    try module.init(0x1111_1111_2222_2222);
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2222), module.snapshotCounter());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);

    try module.addCounter(4);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2226), module.snapshotCounter());
    try module.subCounter(2);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2224), module.snapshotCounter());

    const previous_add = try module.fetchAddCounter(-3);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2224), previous_add);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2221), module.snapshotCounter());

    const previous_sub = try module.fetchSubCounter(5);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2221), previous_sub);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_221c), module.snapshotCounter());

    const added = try module.addReturnCounter(6);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2222), added);
    const subtracted = try module.subReturnCounter(4);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_221e), subtracted);
    const incremented = try module.incReturnCounter();
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_221f), incremented);
    const decremented = try module.decReturnCounter();
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_221e), decremented);
    try module.incCounter();
    try module.decCounter();
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_221e), module.snapshotCounter());

    const previous = try module.swapCounter(-9);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_221e), previous);
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
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.subCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.fetchAddCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.fetchSubCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addReturnCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.subReturnCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.incCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.decCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.incReturnCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.decReturnCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.andCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.orCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.xorCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.compareSwapCounter(17, 19));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addUnlessCounter(1, 13));
}

test "runtime atomic64 sample keeps post-selftest replay local to the module packet" {
    var module = sample.RuntimeAtomic64Sample{};

    try module.init(11);
    const selftest = try module.runSelftest();

    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 5), selftest.operation_families.len);
    try std.testing.expectEqual(@as(usize, 1), module.selftest_runs);
    try std.testing.expectEqual(@as(i64, 11), module.snapshotCounter());

    const replay_swap = try module.swapCounter(17);
    try std.testing.expectEqual(@as(i64, 11), replay_swap);
    try std.testing.expectEqual(@as(i64, 17), module.snapshotCounter());

    const replay_compare = try module.compareSwapCounter(17, 31);
    try std.testing.expect(replay_compare.stored);
    try std.testing.expectEqual(@as(i64, 17), replay_compare.previous);
    try std.testing.expectEqual(@as(i64, 31), module.snapshotCounter());

    const replay_add_unless = try module.addUnlessCounter(4, 99);
    try std.testing.expect(replay_add_unless.changed);
    try std.testing.expectEqual(@as(i64, 31), replay_add_unless.previous);
    try std.testing.expectEqual(@as(i64, 35), module.snapshotCounter());

    const replay_and = try module.andCounter(0b1_1111);
    try std.testing.expectEqual(@as(i64, 35), replay_and);
    try std.testing.expectEqual(@as(i64, 3), module.snapshotCounter());

    const replay_xor = try module.xorCounter(0b1_0010);
    try std.testing.expectEqual(@as(i64, 3), replay_xor);
    try std.testing.expectEqual(@as(i64, 17), module.snapshotCounter());
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.selftest_runs);

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addUnlessCounter(1, 17));
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
