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

    const bitwise_or = try module.orCounter(0x00ff_0000_0000_00ff);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2222), bitwise_or.previous);
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
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings("lib/atomic64_test.c", summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), summary.operation_families.len);
    try std.testing.expect(summary.checked_returning_paths);
    try std.testing.expect(summary.checked_guard_paths);
    try std.testing.expectEqual(@as(i64, 13), module.snapshotCounter());
    try std.testing.expectEqual(@as(usize, 1), module.selftest_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    try module.exit();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.init(23));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.compareSwapCounter(17, 19));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.orCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.andCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.xorCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.andNotCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addUnlessCounter(1, 13));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.incNotZeroCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.decIfPositiveCounter());
}
