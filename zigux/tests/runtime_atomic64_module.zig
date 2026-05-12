const std = @import("std");
const sample = @import("runtime_atomic64_sample");

test "runtime atomic64 sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeAtomic64Sample.descriptor();
    try std.testing.expectEqualStrings("runtime_atomic64", descriptor.name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
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
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
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
