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
    const cold_summary = module.summary();
    try std.testing.expectEqual(@as(i64, 0), cold_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    try module.init(0x1111_1111_2222_2222);
    const initialized_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2222), module.snapshotCounter());
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2222), initialized_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);

    const subtract_result = try module.subCounter(0x22);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2222), subtract_result.previous);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2200), subtract_result.final);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2200), module.snapshotCounter());

    const bitwise_or = try module.orCounter(0x00ff_0000_0000_00ff);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2200), bitwise_or.previous);
    try std.testing.expectEqual(@as(i64, 0x11ff_1111_2222_22ff), bitwise_or.final);
    try std.testing.expectEqual(@as(i64, 0x11ff_1111_2222_22ff), module.snapshotCounter());

    const bitwise_and = try module.andCounter(0x0fff_ffff_ffff_ff0f);
    try std.testing.expectEqual(@as(i64, 0x11ff_1111_2222_22ff), bitwise_and.previous);
    try std.testing.expectEqual(@as(i64, 0x01ff_1111_2222_220f), bitwise_and.final);
    try std.testing.expectEqual(@as(i64, 0x01ff_1111_2222_220f), module.snapshotCounter());

    const bitwise_xor = try module.xorCounter(0x0000_00ff_0000_00f0);
    try std.testing.expectEqual(@as(i64, 0x01ff_1111_2222_220f), bitwise_xor.previous);
    try std.testing.expectEqual(@as(i64, 0x01ff_11ee_2222_22ff), bitwise_xor.final);
    try std.testing.expectEqual(@as(i64, 0x01ff_11ee_2222_22ff), module.snapshotCounter());

    const bitwise_andnot = try module.andNotCounter(0x0000_0000_0000_00ff);
    try std.testing.expectEqual(@as(i64, 0x01ff_11ee_2222_22ff), bitwise_andnot.previous);
    try std.testing.expectEqual(@as(i64, 0x01ff_11ee_2222_2200), bitwise_andnot.final);
    try std.testing.expectEqual(@as(i64, 0x01ff_11ee_2222_2200), module.snapshotCounter());

    const previous = try module.swapCounter(-9);
    try std.testing.expectEqual(@as(i64, 0x01ff_11ee_2222_2200), previous);
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

    const inc_not_zero_changed = try module.incNotZeroCounter();
    try std.testing.expect(inc_not_zero_changed.changed);
    try std.testing.expectEqual(@as(i64, 13), inc_not_zero_changed.previous);
    try std.testing.expectEqual(@as(i64, 14), module.snapshotCounter());

    var zero_guard = sample.RuntimeAtomic64Sample{};
    try zero_guard.init(0);
    const inc_not_zero_blocked = try zero_guard.incNotZeroCounter();
    try std.testing.expect(!inc_not_zero_blocked.changed);
    try std.testing.expectEqual(@as(i64, 0), inc_not_zero_blocked.previous);
    try std.testing.expectEqual(@as(i64, 0), zero_guard.snapshotCounter());

    const dec_if_positive_changed = try module.decIfPositiveCounter();
    try std.testing.expect(dec_if_positive_changed.changed);
    try std.testing.expectEqual(@as(i64, 13), dec_if_positive_changed.result);
    try std.testing.expectEqual(@as(i64, 13), module.snapshotCounter());

    const dec_if_positive_zero = try zero_guard.decIfPositiveCounter();
    try std.testing.expect(!dec_if_positive_zero.changed);
    try std.testing.expectEqual(@as(i64, -1), dec_if_positive_zero.result);
    try std.testing.expectEqual(@as(i64, 0), zero_guard.snapshotCounter());

    var negative_guard = sample.RuntimeAtomic64Sample{};
    try negative_guard.init(-1);
    const dec_if_positive_negative = try negative_guard.decIfPositiveCounter();
    try std.testing.expect(!dec_if_positive_negative.changed);
    try std.testing.expectEqual(@as(i64, -2), dec_if_positive_negative.result);
    try std.testing.expectEqual(@as(i64, -1), negative_guard.snapshotCounter());

    const summary = try module.runSelftest();
    const post_selftest_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings("lib/atomic64_test.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), summary.operation_families.len);
    try std.testing.expect(summary.checked_returning_paths);
    try std.testing.expect(summary.checked_guard_paths);
    try std.testing.expectEqual(@as(i64, 13), module.snapshotCounter());
    try std.testing.expectEqual(@as(i64, 13), post_selftest_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), post_selftest_summary.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(i64, 13), exited_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init(23));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.compareSwapCounter(17, 19));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.subCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.orCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.andCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.xorCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.andNotCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addUnlessCounter(1, 13));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.incNotZeroCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.decIfPositiveCounter());
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
    try std.testing.expectEqual(seed + 0x10, module.snapshotCounter());

    const swap_result = try module.swapCounter(-5);
    try std.testing.expectEqual(seed + 0x10, swap_result);
    try std.testing.expectEqual(@as(i64, -5), module.snapshotCounter());

    const compare_swap_result = try module.compareSwapCounter(-5, 11);
    try std.testing.expect(compare_swap_result.stored);
    try std.testing.expectEqual(@as(i64, -5), compare_swap_result.previous);
    try std.testing.expectEqual(@as(i64, 11), module.snapshotCounter());

    const add_unless_result = try module.addUnlessCounter(4, 99);
    try std.testing.expect(add_unless_result.changed);
    try std.testing.expectEqual(@as(i64, 11), add_unless_result.previous);
    try std.testing.expectEqual(@as(i64, 15), module.snapshotCounter());

    const inc_not_zero_result = try module.incNotZeroCounter();
    try std.testing.expect(inc_not_zero_result.changed);
    try std.testing.expectEqual(@as(i64, 15), inc_not_zero_result.previous);
    try std.testing.expectEqual(@as(i64, 16), module.snapshotCounter());

    const dec_if_positive_result = try module.decIfPositiveCounter();
    try std.testing.expect(dec_if_positive_result.changed);
    try std.testing.expectEqual(@as(i64, 15), dec_if_positive_result.result);
    try std.testing.expectEqual(@as(i64, 15), module.snapshotCounter());

    const post_selftest_summary = module.summary();
    try std.testing.expectEqual(@as(i64, 15), post_selftest_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), post_selftest_summary.exit_runs);

    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(i64, 15), exited_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.compareSwapCounter(15, 19));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addUnlessCounter(1, 15));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.incNotZeroCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.decIfPositiveCounter());
}

test "runtime atomic64 sample keeps zero and negative guard-return replay explicit after selftest at the module boundary" {
    var zero_guard = sample.RuntimeAtomic64Sample{};
    try zero_guard.init(0);
    _ = try zero_guard.runSelftest();

    const zero_inc_not_zero = try zero_guard.incNotZeroCounter();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, zero_guard.stage());
    try std.testing.expect(!zero_inc_not_zero.changed);
    try std.testing.expectEqual(@as(i64, 0), zero_inc_not_zero.previous);
    try std.testing.expectEqual(@as(i64, 0), zero_guard.snapshotCounter());

    const zero_dec_if_positive = try zero_guard.decIfPositiveCounter();
    try std.testing.expect(!zero_dec_if_positive.changed);
    try std.testing.expectEqual(@as(i64, -1), zero_dec_if_positive.result);
    try std.testing.expectEqual(@as(i64, 0), zero_guard.snapshotCounter());

    const zero_summary = zero_guard.summary();
    try std.testing.expectEqual(@as(i64, 0), zero_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), zero_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), zero_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), zero_summary.exit_runs);

    var negative_guard = sample.RuntimeAtomic64Sample{};
    try negative_guard.init(-1);
    _ = try negative_guard.runSelftest();

    const negative_dec_if_positive = try negative_guard.decIfPositiveCounter();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, negative_guard.stage());
    try std.testing.expect(!negative_dec_if_positive.changed);
    try std.testing.expectEqual(@as(i64, -2), negative_dec_if_positive.result);
    try std.testing.expectEqual(@as(i64, -1), negative_guard.snapshotCounter());

    const negative_inc_not_zero = try negative_guard.incNotZeroCounter();
    try std.testing.expect(negative_inc_not_zero.changed);
    try std.testing.expectEqual(@as(i64, -1), negative_inc_not_zero.previous);
    try std.testing.expectEqual(@as(i64, 0), negative_guard.snapshotCounter());

    const negative_summary = negative_guard.summary();
    try std.testing.expectEqual(@as(i64, 0), negative_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), negative_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), negative_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), negative_summary.exit_runs);
}
