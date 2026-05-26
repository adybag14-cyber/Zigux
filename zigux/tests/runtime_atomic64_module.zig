const std = @import("std");
const sample = @import("runtime_atomic64_sample");

test "runtime atomic64 sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeAtomic64Sample.descriptor();
    try std.testing.expectEqualStrings("runtime_atomic64", descriptor.name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime atomic64 sample keeps selftest summary replay explicit at the module boundary" {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(0x1111_1111_2222_2222);
    const selftest_summary = try module.runSelftest();
    try std.testing.expectEqualStrings("lib/atomic64_test.c", selftest_summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), selftest_summary.operation_families.len);
    try std.testing.expectEqual(sample.OperationFamily.arithmetic, selftest_summary.operation_families[0]);
    try std.testing.expectEqual(sample.OperationFamily.bitwise, selftest_summary.operation_families[1]);
    try std.testing.expectEqual(sample.OperationFamily.returning_ops, selftest_summary.operation_families[2]);
    try std.testing.expectEqual(sample.OperationFamily.swap_ops, selftest_summary.operation_families[3]);
    try std.testing.expectEqual(sample.OperationFamily.guard_ops, selftest_summary.operation_families[4]);
    try std.testing.expect(selftest_summary.checked_returning_paths);
    try std.testing.expect(selftest_summary.checked_bitwise_paths);
    try std.testing.expect(selftest_summary.checked_guard_paths);
    const selftest_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, selftest_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), selftest_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_snapshot.exit_runs);
    try std.testing.expect(selftest_snapshot.allows_counter_ops);
}

test "runtime atomic64 sample keeps lifecycle snapshot replay explicit at the module boundary" {
    var module = sample.RuntimeAtomic64Sample{};
    const cold_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.cold, cold_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 0), cold_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_snapshot.exit_runs);
    try std.testing.expect(!cold_snapshot.allows_counter_ops);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addCounter(1));
    try module.init(7);
    const initialized_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.initialized, initialized_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.exit_runs);
    try std.testing.expect(initialized_snapshot.allows_counter_ops);
    _ = try module.runSelftest();
    const selftest_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, selftest_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), selftest_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_snapshot.exit_runs);
    try std.testing.expect(selftest_snapshot.allows_counter_ops);
    try module.exit();
    const exited_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.exit_runs);
    try std.testing.expect(!exited_snapshot.allows_counter_ops);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(9));
}

test "runtime atomic64 sample keeps initialized-stage exit replay explicit at the module boundary" {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(-17);
    const initialized_summary = module.summary();
    try std.testing.expectEqual(@as(i64, -17), initialized_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);
    try module.exit();
    const exited_snapshot = module.lifecycleSnapshot();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), exited_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.exit_runs);
    try std.testing.expect(!exited_snapshot.allows_counter_ops);
    try std.testing.expectEqual(@as(i64, -17), exited_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addCounter(1));
}

test "runtime atomic64 sample keeps captured initialized summary replay explicit across later selftest and exit at the module boundary" {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(41);
    const initialized_summary = module.summary();
    try std.testing.expectEqual(@as(i64, 41), initialized_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);
    _ = try module.runSelftest();
    try module.exit();
    const exited_snapshot = module.lifecycleSnapshot();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.exit_runs);
    try std.testing.expectEqual(@as(i64, 41), exited_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectEqual(@as(i64, 41), initialized_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);
}

test "runtime atomic64 sample keeps post-selftest mutation replay explicit at the module boundary" {
    var module = sample.RuntimeAtomic64Sample{};
    const seed = 0x0102_0304_0506_0708;
    try module.init(seed);
    _ = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    const add_result = try module.addCounter(0x10);
    try std.testing.expectEqual(seed, add_result.previous);
    try std.testing.expectEqual(seed + 0x10, add_result.final);
    const swap_result = try module.swapCounter(-5);
    try std.testing.expectEqual(seed + 0x10, swap_result);
    const compare_swap_result = try module.compareSwapCounter(-5, 11);
    try std.testing.expect(compare_swap_result.stored);
    try std.testing.expectEqual(@as(i64, -5), compare_swap_result.previous);
    const add_unless_result = try module.addUnlessCounter(4, 99);
    try std.testing.expect(add_unless_result.changed);
    try std.testing.expectEqual(@as(i64, 11), add_unless_result.previous);
    const and_not_result = try module.andNotCounter(0b0100);
    try std.testing.expectEqual(@as(i64, 15), and_not_result.previous);
    try std.testing.expectEqual(@as(i64, 11), and_not_result.final);
    const inc_not_zero_result = try module.incNotZeroCounter();
    try std.testing.expect(inc_not_zero_result.changed);
    const dec_if_positive_result = try module.decIfPositiveCounter();
    try std.testing.expect(dec_if_positive_result.changed);
    const post_selftest_summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), post_selftest_summary.exit_runs);
    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(i64, 11), exited_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
}

test "runtime atomic64 sample keeps post-selftest bitwise replay explicit at the module boundary" {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(0b1010_1100);
    _ = try module.runSelftest();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    const or_result = try module.orCounter(0b0101_0000);
    try std.testing.expectEqual(@as(i64, 0b1010_1100), or_result.previous);
    try std.testing.expectEqual(@as(i64, 0b1111_1100), or_result.final);
    try std.testing.expectEqual(@as(i64, 0b1111_1100), module.snapshotCounter());
    const and_result = try module.andCounter(0b1111_0110);
    try std.testing.expectEqual(@as(i64, 0b1111_1100), and_result.previous);
    try std.testing.expectEqual(@as(i64, 0b1111_0100), and_result.final);
    try std.testing.expectEqual(@as(i64, 0b1111_0100), module.snapshotCounter());
    const xor_result = try module.xorCounter(0b0011_0011);
    try std.testing.expectEqual(@as(i64, 0b1111_0100), xor_result.previous);
    try std.testing.expectEqual(@as(i64, 0b1100_0111), xor_result.final);
    try std.testing.expectEqual(@as(i64, 0b1100_0111), module.snapshotCounter());
    const and_not_result = try module.andNotCounter(0b0100_0101);
    try std.testing.expectEqual(@as(i64, 0b1100_0111), and_not_result.previous);
    try std.testing.expectEqual(@as(i64, 0b1000_0010), and_not_result.final);
    try std.testing.expectEqual(@as(i64, 0b1000_0010), module.snapshotCounter());
    const selftest_summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_summary.exit_runs);
    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(i64, 0b1000_0010), exited_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
}

test "runtime atomic64 sample keeps captured selftest summary replay explicit across later mutation and exit at the module boundary" {
    var module = sample.RuntimeAtomic64Sample{};
    try module.init(23);
    const selftest_summary = try module.runSelftest();
    try std.testing.expectEqual(@as(usize, 5), selftest_summary.operation_families.len);
    try std.testing.expect(selftest_summary.checked_returning_paths);
    try std.testing.expect(selftest_summary.checked_bitwise_paths);
    try std.testing.expect(selftest_summary.checked_guard_paths);
    const add_result = try module.addCounter(9);
    try std.testing.expectEqual(@as(i64, 23), add_result.previous);
    try std.testing.expectEqual(@as(i64, 32), add_result.final);
    try module.exit();
    const exited_snapshot = module.lifecycleSnapshot();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, exited_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectEqual(@as(i64, 32), exited_summary.counter_snapshot);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", selftest_summary.anchor);
    try std.testing.expectEqual(sample.OperationFamily.arithmetic, selftest_summary.operation_families[0]);
    try std.testing.expectEqual(sample.OperationFamily.bitwise, selftest_summary.operation_families[1]);
    try std.testing.expectEqual(sample.OperationFamily.returning_ops, selftest_summary.operation_families[2]);
    try std.testing.expectEqual(sample.OperationFamily.swap_ops, selftest_summary.operation_families[3]);
    try std.testing.expectEqual(sample.OperationFamily.guard_ops, selftest_summary.operation_families[4]);
}

test "runtime atomic64 sample keeps zero and negative guard-return replay explicit after selftest at the module boundary" {
    var zero_guard = sample.RuntimeAtomic64Sample{};
    try zero_guard.init(0);
    _ = try zero_guard.runSelftest();
    const zero_inc_not_zero = try zero_guard.incNotZeroCounter();
    try std.testing.expect(!zero_inc_not_zero.changed);
    try std.testing.expectEqual(@as(i64, 0), zero_inc_not_zero.previous);
    const zero_dec_if_positive = try zero_guard.decIfPositiveCounter();
    try std.testing.expect(!zero_dec_if_positive.changed);
    try std.testing.expectEqual(@as(i64, -1), zero_dec_if_positive.result);
    var negative_guard = sample.RuntimeAtomic64Sample{};
    try negative_guard.init(-1);
    _ = try negative_guard.runSelftest();
    const negative_dec_if_positive = try negative_guard.decIfPositiveCounter();
    try std.testing.expect(!negative_dec_if_positive.changed);
    try std.testing.expectEqual(@as(i64, -2), negative_dec_if_positive.result);
}

test "runtime atomic64 sample keeps rejected re-init rollback explicit at the module boundary" {
    var initialized_module = sample.RuntimeAtomic64Sample{};
    try initialized_module.init(91);

    const before_initialized_reinit_snapshot = initialized_module.lifecycleSnapshot();
    const before_initialized_reinit_summary = initialized_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, before_initialized_reinit_snapshot.stage);
    try std.testing.expect(before_initialized_reinit_snapshot.allows_counter_ops);
    try std.testing.expectEqual(@as(i64, 91), before_initialized_reinit_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reinit_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reinit_summary.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.init(7));

    const after_initialized_reinit_snapshot = initialized_module.lifecycleSnapshot();
    const after_initialized_reinit_summary = initialized_module.summary();
    try std.testing.expectEqual(before_initialized_reinit_snapshot.stage, after_initialized_reinit_snapshot.stage);
    try std.testing.expectEqual(before_initialized_reinit_snapshot.init_runs, after_initialized_reinit_snapshot.init_runs);
    try std.testing.expectEqual(before_initialized_reinit_snapshot.selftest_runs, after_initialized_reinit_snapshot.selftest_runs);
    try std.testing.expectEqual(before_initialized_reinit_snapshot.exit_runs, after_initialized_reinit_snapshot.exit_runs);
    try std.testing.expectEqual(before_initialized_reinit_snapshot.allows_counter_ops, after_initialized_reinit_snapshot.allows_counter_ops);
    try std.testing.expectEqual(before_initialized_reinit_summary.counter_snapshot, after_initialized_reinit_summary.counter_snapshot);
    try std.testing.expectEqual(before_initialized_reinit_summary.init_runs, after_initialized_reinit_summary.init_runs);
    try std.testing.expectEqual(before_initialized_reinit_summary.selftest_runs, after_initialized_reinit_summary.selftest_runs);
    try std.testing.expectEqual(before_initialized_reinit_summary.exit_runs, after_initialized_reinit_summary.exit_runs);

    var selftested_module = sample.RuntimeAtomic64Sample{};
    try selftested_module.init(-12);
    _ = try selftested_module.runSelftest();

    const before_selftested_reinit_snapshot = selftested_module.lifecycleSnapshot();
    const before_selftested_reinit_summary = selftested_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, before_selftested_reinit_snapshot.stage);
    try std.testing.expect(before_selftested_reinit_snapshot.allows_counter_ops);
    try std.testing.expectEqual(@as(i64, -12), before_selftested_reinit_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reinit_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_reinit_summary.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.init(5));

    const after_selftested_reinit_snapshot = selftested_module.lifecycleSnapshot();
    const after_selftested_reinit_summary = selftested_module.summary();
    try std.testing.expectEqual(before_selftested_reinit_snapshot.stage, after_selftested_reinit_snapshot.stage);
    try std.testing.expectEqual(before_selftested_reinit_snapshot.init_runs, after_selftested_reinit_snapshot.init_runs);
    try std.testing.expectEqual(before_selftested_reinit_snapshot.selftest_runs, after_selftested_reinit_snapshot.selftest_runs);
    try std.testing.expectEqual(before_selftested_reinit_snapshot.exit_runs, after_selftested_reinit_snapshot.exit_runs);
    try std.testing.expectEqual(before_selftested_reinit_snapshot.allows_counter_ops, after_selftested_reinit_snapshot.allows_counter_ops);
    try std.testing.expectEqual(before_selftested_reinit_summary.counter_snapshot, after_selftested_reinit_summary.counter_snapshot);
    try std.testing.expectEqual(before_selftested_reinit_summary.init_runs, after_selftested_reinit_summary.init_runs);
    try std.testing.expectEqual(before_selftested_reinit_summary.selftest_runs, after_selftested_reinit_summary.selftest_runs);
    try std.testing.expectEqual(before_selftested_reinit_summary.exit_runs, after_selftested_reinit_summary.exit_runs);

    var exited_module = sample.RuntimeAtomic64Sample{};
    try exited_module.init(33);
    _ = try exited_module.runSelftest();
    try exited_module.exit();

    const before_exited_reinit_snapshot = exited_module.lifecycleSnapshot();
    const before_exited_reinit_summary = exited_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, before_exited_reinit_snapshot.stage);
    try std.testing.expect(!before_exited_reinit_snapshot.allows_counter_ops);
    try std.testing.expectEqual(@as(i64, 33), before_exited_reinit_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exited_reinit_summary.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.init(2));

    const after_exited_reinit_snapshot = exited_module.lifecycleSnapshot();
    const after_exited_reinit_summary = exited_module.summary();
    try std.testing.expectEqual(before_exited_reinit_snapshot.stage, after_exited_reinit_snapshot.stage);
    try std.testing.expectEqual(before_exited_reinit_snapshot.init_runs, after_exited_reinit_snapshot.init_runs);
    try std.testing.expectEqual(before_exited_reinit_snapshot.selftest_runs, after_exited_reinit_snapshot.selftest_runs);
    try std.testing.expectEqual(before_exited_reinit_snapshot.exit_runs, after_exited_reinit_snapshot.exit_runs);
    try std.testing.expectEqual(before_exited_reinit_snapshot.allows_counter_ops, after_exited_reinit_snapshot.allows_counter_ops);
    try std.testing.expectEqual(before_exited_reinit_summary.counter_snapshot, after_exited_reinit_summary.counter_snapshot);
    try std.testing.expectEqual(before_exited_reinit_summary.init_runs, after_exited_reinit_summary.init_runs);
    try std.testing.expectEqual(before_exited_reinit_summary.selftest_runs, after_exited_reinit_summary.selftest_runs);
    try std.testing.expectEqual(before_exited_reinit_summary.exit_runs, after_exited_reinit_summary.exit_runs);
}

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
    try std.testing.expectEqual(before_rejected_selftest_snapshot.allows_counter_ops, after_rejected_selftest_snapshot.allows_counter_ops);
    try std.testing.expectEqual(before_rejected_selftest_summary.counter_snapshot, after_rejected_selftest_summary.counter_snapshot);
    try std.testing.expectEqual(before_rejected_selftest_summary.init_runs, after_rejected_selftest_summary.init_runs);
    try std.testing.expectEqual(before_rejected_selftest_summary.selftest_runs, after_rejected_selftest_summary.selftest_runs);
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
    try std.testing.expectEqual(before_rejected_exit_selftest_snapshot.allows_counter_ops, after_rejected_exit_selftest_snapshot.allows_counter_ops);
    try std.testing.expectEqual(before_rejected_exit_selftest_summary.counter_snapshot, after_rejected_exit_selftest_summary.counter_snapshot);
    try std.testing.expectEqual(before_rejected_exit_selftest_summary.init_runs, after_rejected_exit_selftest_summary.init_runs);
    try std.testing.expectEqual(before_rejected_exit_selftest_summary.selftest_runs, after_rejected_exit_selftest_summary.selftest_runs);
    try std.testing.expectEqual(before_rejected_exit_selftest_summary.exit_runs, after_rejected_exit_selftest_summary.exit_runs);
}

test "runtime atomic64 sample keeps rejected re-exit rollback explicit at the module boundary" {
    var initialized_module = sample.RuntimeAtomic64Sample{};
    try initialized_module.init(17);
    try initialized_module.exit();

    const before_initialized_reexit_snapshot = initialized_module.lifecycleSnapshot();
    const before_initialized_reexit_summary = initialized_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, before_initialized_reexit_snapshot.stage);
    try std.testing.expect(!before_initialized_reexit_snapshot.allows_counter_ops);
    try std.testing.expectEqual(@as(i64, 17), before_initialized_reexit_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reexit_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_reexit_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_reexit_summary.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, initialized_module.exit());

    const after_initialized_reexit_snapshot = initialized_module.lifecycleSnapshot();
    const after_initialized_reexit_summary = initialized_module.summary();
    try std.testing.expectEqual(before_initialized_reexit_snapshot.stage, after_initialized_reexit_snapshot.stage);
    try std.testing.expectEqual(before_initialized_reexit_snapshot.init_runs, after_initialized_reexit_snapshot.init_runs);
    try std.testing.expectEqual(before_initialized_reexit_snapshot.selftest_runs, after_initialized_reexit_snapshot.selftest_runs);
    try std.testing.expectEqual(before_initialized_reexit_snapshot.exit_runs, after_initialized_reexit_snapshot.exit_runs);
    try std.testing.expectEqual(before_initialized_reexit_snapshot.allows_counter_ops, after_initialized_reexit_snapshot.allows_counter_ops);
    try std.testing.expectEqual(before_initialized_reexit_summary.counter_snapshot, after_initialized_reexit_summary.counter_snapshot);
    try std.testing.expectEqual(before_initialized_reexit_summary.init_runs, after_initialized_reexit_summary.init_runs);
    try std.testing.expectEqual(before_initialized_reexit_summary.selftest_runs, after_initialized_reexit_summary.selftest_runs);
    try std.testing.expectEqual(before_initialized_reexit_summary.exit_runs, after_initialized_reexit_summary.exit_runs);

    var selftested_module = sample.RuntimeAtomic64Sample{};
    try selftested_module.init(-8);
    _ = try selftested_module.runSelftest();
    try selftested_module.exit();

    const before_selftested_reexit_snapshot = selftested_module.lifecycleSnapshot();
    const before_selftested_reexit_summary = selftested_module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, before_selftested_reexit_snapshot.stage);
    try std.testing.expect(!before_selftested_reexit_snapshot.allows_counter_ops);
    try std.testing.expectEqual(@as(i64, -8), before_selftested_reexit_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_reexit_summary.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, selftested_module.exit());

    const after_selftested_reexit_snapshot = selftested_module.lifecycleSnapshot();
    const after_selftested_reexit_summary = selftested_module.summary();
    try std.testing.expectEqual(before_selftested_reexit_snapshot.stage, after_selftested_reexit_snapshot.stage);
    try std.testing.expectEqual(before_selftested_reexit_snapshot.init_runs, after_selftested_reexit_snapshot.init_runs);
    try std.testing.expectEqual(before_selftested_reexit_snapshot.selftest_runs, after_selftested_reexit_snapshot.selftest_runs);
    try std.testing.expectEqual(before_selftested_reexit_snapshot.exit_runs, after_selftested_reexit_snapshot.exit_runs);
    try std.testing.expectEqual(before_selftested_reexit_snapshot.allows_counter_ops, after_selftested_reexit_snapshot.allows_counter_ops);
    try std.testing.expectEqual(before_selftested_reexit_summary.counter_snapshot, after_selftested_reexit_summary.counter_snapshot);
    try std.testing.expectEqual(before_selftested_reexit_summary.init_runs, after_selftested_reexit_summary.init_runs);
    try std.testing.expectEqual(before_selftested_reexit_summary.selftest_runs, after_selftested_reexit_summary.selftest_runs);
    try std.testing.expectEqual(before_selftested_reexit_summary.exit_runs, after_selftested_reexit_summary.exit_runs);
}

test "runtime atomic64 sample keeps guard-returning counter APIs rejected outside active lifecycle states without disturbing summaries" {
    var cold_module = sample.RuntimeAtomic64Sample{};
    const cold_snapshot = cold_module.lifecycleSnapshot();
    const cold_summary = cold_module.summary();

    try std.testing.expectError(error.InvalidLifecycleTransition, cold_module.addUnlessCounter(4, 99));
    try std.testing.expectError(error.InvalidLifecycleTransition, cold_module.incNotZeroCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, cold_module.decIfPositiveCounter());

    const cold_snapshot_after = cold_module.lifecycleSnapshot();
    const cold_summary_after = cold_module.summary();
    try std.testing.expectEqual(cold_snapshot.stage, cold_snapshot_after.stage);
    try std.testing.expectEqual(cold_snapshot.init_runs, cold_snapshot_after.init_runs);
    try std.testing.expectEqual(cold_snapshot.selftest_runs, cold_snapshot_after.selftest_runs);
    try std.testing.expectEqual(cold_snapshot.exit_runs, cold_snapshot_after.exit_runs);
    try std.testing.expectEqual(cold_snapshot.allows_counter_ops, cold_snapshot_after.allows_counter_ops);
    try std.testing.expectEqual(cold_summary.counter_snapshot, cold_summary_after.counter_snapshot);
    try std.testing.expectEqual(cold_summary.init_runs, cold_summary_after.init_runs);
    try std.testing.expectEqual(cold_summary.selftest_runs, cold_summary_after.selftest_runs);
    try std.testing.expectEqual(cold_summary.exit_runs, cold_summary_after.exit_runs);

    var exited_module = sample.RuntimeAtomic64Sample{};
    try exited_module.init(55);
    _ = try exited_module.runSelftest();
    try exited_module.exit();

    const exited_snapshot = exited_module.lifecycleSnapshot();
    const exited_summary = exited_module.summary();

    try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.addUnlessCounter(8, 99));
    try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.incNotZeroCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, exited_module.decIfPositiveCounter());

    const exited_snapshot_after = exited_module.lifecycleSnapshot();
    const exited_summary_after = exited_module.summary();
    try std.testing.expectEqual(exited_snapshot.stage, exited_snapshot_after.stage);
    try std.testing.expectEqual(exited_snapshot.init_runs, exited_snapshot_after.init_runs);
    try std.testing.expectEqual(exited_snapshot.selftest_runs, exited_snapshot_after.selftest_runs);
    try std.testing.expectEqual(exited_snapshot.exit_runs, exited_snapshot_after.exit_runs);
    try std.testing.expectEqual(exited_snapshot.allows_counter_ops, exited_snapshot_after.allows_counter_ops);
    try std.testing.expectEqual(exited_summary.counter_snapshot, exited_summary_after.counter_snapshot);
    try std.testing.expectEqual(exited_summary.init_runs, exited_summary_after.init_runs);
    try std.testing.expectEqual(exited_summary.selftest_runs, exited_summary_after.selftest_runs);
    try std.testing.expectEqual(exited_summary.exit_runs, exited_summary_after.exit_runs);
}
