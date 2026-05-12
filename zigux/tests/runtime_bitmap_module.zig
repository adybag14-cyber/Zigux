const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

test "runtime bitmap module gate replays current lifecycle and selftest behavior directly" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    const second_word_base = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits / 2;

    const cold = module.lifecycleSnapshot();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.cold, cold.stage);
    try std.testing.expectEqual(@as(usize, 0), cold.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold.exit_runs);
    try std.testing.expect(!cold.allows_mutation);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    try module.initWithSetBits(&.{ 0, 5, second_word_base, second_word_base + 6 });

    const initialized = module.lifecycleSnapshot();
    const summary_before_selftest = module.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, initialized.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized.exit_runs);
    try std.testing.expect(initialized.allows_mutation);
    try std.testing.expectEqual(@as(u32, 0), summary_before_selftest.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary_before_selftest.first_zero);
    try std.testing.expectEqual(@as(u32, 4), summary_before_selftest.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, summary_before_selftest.nbits);
    try std.testing.expect(module.isSet(second_word_base));
    try std.testing.expect(module.isSet(second_word_base + 6));

    const selftest = try module.runSelftest();
    const selftested = module.lifecycleSnapshot();
    const summary_after_selftest = module.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, selftested.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftested.exit_runs);
    try std.testing.expect(selftested.allows_mutation);
    try std.testing.expectEqualStrings(runtime_bitmap_sample.RuntimeBitmapSample.descriptor().anchor, selftest.anchor);
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expectEqual(runtime_bitmap_sample.OperationFamily.clear_set, selftest.operation_families[0]);
    try std.testing.expectEqual(runtime_bitmap_sample.OperationFamily.copy, selftest.operation_families[1]);
    try std.testing.expectEqual(runtime_bitmap_sample.OperationFamily.summary, selftest.operation_families[2]);
    try std.testing.expectEqual(runtime_bitmap_sample.OperationFamily.lifecycle, selftest.operation_families[3]);
    try std.testing.expect(selftest.checked_range_mutations);
    try std.testing.expect(selftest.checked_lifecycle_paths);
    try std.testing.expectEqual(summary_before_selftest.first_set, summary_after_selftest.first_set);
    try std.testing.expectEqual(summary_before_selftest.first_zero, summary_after_selftest.first_zero);
    try std.testing.expectEqual(summary_before_selftest.weight, summary_after_selftest.weight);
    try std.testing.expectEqual(summary_before_selftest.nbits, summary_after_selftest.nbits);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    try module.clearRange(second_word_base, 1);
    try module.setRange(9, 4);

    const mutated_summary = module.summary();
    try std.testing.expectEqual(@as(u32, 0), mutated_summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), mutated_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 7), mutated_summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, mutated_summary.nbits);
    try std.testing.expect(!module.isSet(second_word_base));
    try std.testing.expect(module.isSet(second_word_base + 6));
    try std.testing.expect(module.isSet(12));

    var mirror = runtime_bitmap_sample.RuntimeBitmapSample{};
    try mirror.initWithSetBits(&.{});
    try mirror.copyFrom(&module);

    const mirrored_summary = mirror.summary();
    const mirrored_state = mirror.lifecycleSnapshot();
    try std.testing.expectEqual(mutated_summary.first_set, mirrored_summary.first_set);
    try std.testing.expectEqual(mutated_summary.first_zero, mirrored_summary.first_zero);
    try std.testing.expectEqual(mutated_summary.weight, mirrored_summary.weight);
    try std.testing.expectEqual(mutated_summary.nbits, mirrored_summary.nbits);
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, mirrored_state.stage);
    try std.testing.expectEqual(@as(usize, 1), mirrored_state.init_runs);
    try std.testing.expectEqual(@as(usize, 0), mirrored_state.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), mirrored_state.exit_runs);
    try std.testing.expect(mirrored_state.allows_mutation);
    try std.testing.expect(!mirror.isSet(second_word_base));
    try std.testing.expect(mirror.isSet(second_word_base + 6));
    try std.testing.expect(mirror.isSet(12));

    try module.exit();

    const exited = module.lifecycleSnapshot();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.exited, exited.stage);
    try std.testing.expectEqual(@as(usize, 1), exited.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.exit_runs);
    try std.testing.expect(!exited.allows_mutation);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.setRange(1, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.clearRange(1, 1));

    var source = runtime_bitmap_sample.RuntimeBitmapSample{};
    try source.initWithSetBits(&.{ 2, 9 });
    try std.testing.expectError(error.InvalidLifecycleTransition, module.copyFrom(&source));
}
