const std = @import("std");
const sample = @import("runtime_bitmap_sample");

fn expectSummaryStable(before: sample.RuntimeBitmapSummary, after: sample.RuntimeBitmapSummary) !void {
    try std.testing.expectEqual(before.first_set, after.first_set);
    try std.testing.expectEqual(before.first_zero, after.first_zero);
    try std.testing.expectEqual(before.weight, after.weight);
    try std.testing.expectEqual(before.nbits, after.nbits);
    try std.testing.expectEqual(before.init_runs, after.init_runs);
    try std.testing.expectEqual(before.selftest_runs, after.selftest_runs);
    try std.testing.expectEqual(before.exit_runs, after.exit_runs);
}

test "runtime bitmap sample advertises the bounded pilot-module contract" {
    const descriptor = sample.RuntimeBitmapSample.descriptor();
    const contract = sample.RuntimeBitmapSample.reviewContract();

    try std.testing.expectEqualStrings("runtime_bitmap", descriptor.name);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
    try std.testing.expectEqual(@as(usize, sample.sample_review_focus.len), contract.focus.len);
    try std.testing.expectEqual(@as(usize, sample.sample_review_non_goals.len), contract.non_goals.len);
}

test "runtime bitmap sample keeps selftest summary replay explicit at the module boundary" {
    var module = sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });

    const selftest_summary = try module.runSelftest();
    try std.testing.expectEqualStrings("lib/test_bitmap.c", selftest_summary.anchor);
    try std.testing.expectEqual(@as(usize, 4), selftest_summary.operation_families.len);
    try std.testing.expectEqual(sample.OperationFamily.clear_set, selftest_summary.operation_families[0]);
    try std.testing.expectEqual(sample.OperationFamily.copy, selftest_summary.operation_families[1]);
    try std.testing.expectEqual(sample.OperationFamily.parse_and_print, selftest_summary.operation_families[2]);
    try std.testing.expectEqual(sample.OperationFamily.iteration_and_ranges, selftest_summary.operation_families[3]);
    try std.testing.expect(selftest_summary.checked_range_mutations);
    try std.testing.expect(selftest_summary.checked_iteration_paths);

    const selftest_snapshot = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(u32, 0), selftest_snapshot.first_set);
    try std.testing.expectEqual(@as(u32, 1), selftest_snapshot.first_zero);
    try std.testing.expectEqual(@as(u32, 4), selftest_snapshot.weight);
    try std.testing.expectEqual(@as(usize, 1), selftest_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_snapshot.exit_runs);
}

test "runtime bitmap sample keeps lifecycle summary replay explicit at the module boundary" {
    var module = sample.RuntimeBitmapSample{};

    const cold_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.cold, module.stage());
    try std.testing.expectEqual(sample.RuntimeBitmapSample.bitmap_nbits, cold_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), cold_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), cold_summary.weight);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.setRange(1, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    try module.initWithSetBits(&.{ 1, 64 });
    const initialized_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(u32, 1), initialized_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), initialized_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 2), initialized_summary.weight);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);

    _ = try module.runSelftest();
    const selftest_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(initialized_summary.first_set, selftest_summary.first_set);
    try std.testing.expectEqual(initialized_summary.first_zero, selftest_summary.first_zero);
    try std.testing.expectEqual(initialized_summary.weight, selftest_summary.weight);
    try std.testing.expectEqual(initialized_summary.nbits, selftest_summary.nbits);
    try std.testing.expectEqual(initialized_summary.init_runs, selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_summary.exit_runs);

    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try expectSummaryStable(selftest_summary, .{
        .first_set = exited_summary.first_set,
        .first_zero = exited_summary.first_zero,
        .weight = exited_summary.weight,
        .nbits = exited_summary.nbits,
        .init_runs = exited_summary.init_runs,
        .selftest_runs = exited_summary.selftest_runs,
        .exit_runs = 0,
    });
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.setRange(1, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}

test "runtime bitmap sample keeps initialized-stage exit replay explicit at the module boundary" {
    var module = sample.RuntimeBitmapSample{};
    try module.initFromBitList("0, 63, 64, 127");

    const initialized_summary = module.summary();
    try std.testing.expectEqual(@as(u32, 0), initialized_summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), initialized_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), initialized_summary.weight);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);

    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(initialized_summary.first_set, exited_summary.first_set);
    try std.testing.expectEqual(initialized_summary.first_zero, exited_summary.first_zero);
    try std.testing.expectEqual(initialized_summary.weight, exited_summary.weight);
    try std.testing.expectEqual(initialized_summary.nbits, exited_summary.nbits);
    try std.testing.expectEqual(initialized_summary.init_runs, exited_summary.init_runs);
    try std.testing.expectEqual(initialized_summary.selftest_runs, exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
}

test "runtime bitmap sample keeps captured initialized summary replay explicit across later selftest and exit at the module boundary" {
    var module = sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 10, 64, 90 });

    const initialized_summary = module.summary();
    try std.testing.expectEqual(@as(u32, 10), initialized_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), initialized_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 3), initialized_summary.weight);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);

    _ = try module.runSelftest();
    try module.exit();

    const exited_summary = module.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(u32, 10), initialized_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), initialized_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 3), initialized_summary.weight);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);
    try std.testing.expectEqual(@as(u32, 10), exited_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), exited_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 3), exited_summary.weight);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
}

test "runtime bitmap sample keeps post-selftest mutation and copy replay explicit at the module boundary" {
    var source = sample.RuntimeBitmapSample{};
    try source.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try source.runSelftest();

    try source.clearRange(64, 1);
    try source.setRange(9, 4);
    const formatted = try source.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);
    try std.testing.expectEqualStrings("0,5,9,10,11,12,70", formatted);

    const source_after_mutation = source.summary();
    try std.testing.expectEqual(sample.ModuleStage.selftest_complete, source.stage());
    try std.testing.expectEqual(@as(u32, 0), source_after_mutation.first_set);
    try std.testing.expectEqual(@as(u32, 1), source_after_mutation.first_zero);
    try std.testing.expectEqual(@as(u32, 7), source_after_mutation.weight);
    try std.testing.expectEqual(@as(usize, 1), source_after_mutation.init_runs);
    try std.testing.expectEqual(@as(usize, 1), source_after_mutation.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), source_after_mutation.exit_runs);

    var target = sample.RuntimeBitmapSample{};
    try target.initWithSetBits(&.{127});
    try target.copyFrom(&source);

    const target_after_copy = target.summary();
    try std.testing.expectEqual(sample.ModuleStage.initialized, target.stage());
    try std.testing.expectEqual(source_after_mutation.first_set, target_after_copy.first_set);
    try std.testing.expectEqual(source_after_mutation.first_zero, target_after_copy.first_zero);
    try std.testing.expectEqual(source_after_mutation.weight, target_after_copy.weight);
    try std.testing.expectEqual(source_after_mutation.nbits, target_after_copy.nbits);
    try std.testing.expectEqual(@as(usize, 1), target_after_copy.init_runs);
    try std.testing.expectEqual(@as(usize, 0), target_after_copy.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), target_after_copy.exit_runs);
    try std.testing.expect(target.isSet(70));
    try std.testing.expect(!target.isSet(64));
    try std.testing.expectEqual(@as(?u32, 70), target.nthSetBit(6));
    try std.testing.expectEqual(@as(u32, 4), try target.countSetBitsInRange(9, 4));
}

test "runtime bitmap sample keeps source and target lifecycle guards explicit at the module boundary" {
    var cold_source = sample.RuntimeBitmapSample{};

    var target = sample.RuntimeBitmapSample{};
    try target.initWithSetBits(&.{0});
    const target_before = target.summary();

    try std.testing.expectError(error.InvalidSourceLifecycle, target.copyFrom(&cold_source));
    const target_after_cold_source = target.summary();
    try expectSummaryStable(target_before, target_after_cold_source);

    var exited_source = sample.RuntimeBitmapSample{};
    try exited_source.initWithSetBits(&.{127});
    try exited_source.exit();
    try std.testing.expectError(error.InvalidSourceLifecycle, target.copyFrom(&exited_source));
    const target_after_exited_source = target.summary();
    try expectSummaryStable(target_before, target_after_exited_source);

    try target.exit();
    const exited_target = target.summary();
    try std.testing.expectEqual(sample.ModuleStage.exited, target.stage());

    var initialized_source = sample.RuntimeBitmapSample{};
    try initialized_source.initWithSetBits(&.{10});
    try std.testing.expectError(error.InvalidLifecycleTransition, target.copyFrom(&initialized_source));
    const target_after_exited_copy = target.summary();
    try expectSummaryStable(exited_target, target_after_exited_copy);
}
