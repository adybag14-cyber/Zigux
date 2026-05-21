const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

const ModuleStage = runtime_bitmap_sample.ModuleStage;
const RuntimeBitmapSample = runtime_bitmap_sample.RuntimeBitmapSample;
const RuntimeBitmapSummary = runtime_bitmap_sample.RuntimeBitmapSummary;

const LoadPlan = struct {
    name: []const u8,
    source_bit_list: []const u8,
    formatted_bit_list: []const u8,
    expected_weight: u32,
    expected_first_set: u32,
};

const load_plan = LoadPlan{
    .name = "runtime_bitmap",
    .source_bit_list = "0, 63, 64, 127",
    .formatted_bit_list = "0,63,64,127",
    .expected_weight = 4,
    .expected_first_set = 0,
};

fn expectSummaryStable(before: RuntimeBitmapSummary, after: RuntimeBitmapSummary) !void {
    try std.testing.expectEqual(before.first_set, after.first_set);
    try std.testing.expectEqual(before.first_zero, after.first_zero);
    try std.testing.expectEqual(before.weight, after.weight);
    try std.testing.expectEqual(before.nbits, after.nbits);
    try std.testing.expectEqual(before.init_runs, after.init_runs);
}

test "runtime bitmap loader keeps loader-facing bitmap payload explicit" {
    const descriptor = RuntimeBitmapSample.descriptor();
    try std.testing.expectEqualStrings(load_plan.name, descriptor.name);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    var module = RuntimeBitmapSample{};
    try module.initFromBitList(load_plan.source_bit_list);

    const summary = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(load_plan.expected_first_set, summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary.first_zero);
    try std.testing.expectEqual(load_plan.expected_weight, summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);
    try std.testing.expect(module.isSet(63));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(127));

    const formatted = try module.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);
    try std.testing.expectEqualStrings(load_plan.formatted_bit_list, formatted);
}

test "runtime bitmap loader keeps loaded cross-word summary stable through selftest and exit" {
    var module = RuntimeBitmapSample{};
    try module.initFromBitList(load_plan.source_bit_list);

    const initialized = module.summary();
    const selftest = try module.runSelftest();
    try std.testing.expectEqualStrings("lib/test_bitmap.c", selftest.anchor);
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expect(selftest.checked_range_mutations);
    try std.testing.expect(selftest.checked_iteration_paths);

    const after_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try expectSummaryStable(initialized, after_selftest);
    try std.testing.expectEqual(@as(usize, 1), after_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), after_selftest.exit_runs);

    try module.exit();
    const after_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(initialized.first_set, after_exit.first_set);
    try std.testing.expectEqual(initialized.first_zero, after_exit.first_zero);
    try std.testing.expectEqual(initialized.weight, after_exit.weight);
    try std.testing.expectEqual(initialized.nbits, after_exit.nbits);
    try std.testing.expectEqual(initialized.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(63));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(127));
}

test "runtime bitmap loader keeps initialized loaded summary stable across direct exit without selftest" {
    var module = RuntimeBitmapSample{};
    try module.initFromBitList(load_plan.source_bit_list);

    const before_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(load_plan.expected_first_set, before_exit.first_set);
    try std.testing.expectEqual(@as(u32, 1), before_exit.first_zero);
    try std.testing.expectEqual(load_plan.expected_weight, before_exit.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, before_exit.nbits);
    try std.testing.expectEqual(@as(usize, 1), before_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);

    try module.exit();

    const after_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try expectSummaryStable(before_exit, after_exit);
    try std.testing.expectEqual(@as(usize, 0), after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(63));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(127));
    try std.testing.expectEqual(@as(?u32, 0), module.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, 63), module.nthSetBit(1));
    try std.testing.expectEqual(@as(?u32, 64), module.nthSetBit(2));
    try std.testing.expectEqual(@as(?u32, 127), module.nthSetBit(3));
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(4));
    try std.testing.expectEqual(@as(u32, 4), try module.countSetBitsInRange(0, RuntimeBitmapSample.bitmap_nbits));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.setRange(5, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.clearRange(63, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}

test "runtime bitmap loader rejects malformed loader payloads without leaving initialized state" {
    var invalid = RuntimeBitmapSample{};
    try std.testing.expectError(error.InvalidBitList, invalid.initFromBitList("0,,64"));
    try std.testing.expectEqual(ModuleStage.cold, invalid.stage());
    const invalid_summary = invalid.summary();
    try std.testing.expectEqual(@as(u32, RuntimeBitmapSample.bitmap_nbits), invalid_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), invalid_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), invalid_summary.weight);
    try std.testing.expectEqual(@as(usize, 0), invalid_summary.init_runs);
    try std.testing.expect(!invalid.isSet(0));

    var out_of_bounds = RuntimeBitmapSample{};
    try std.testing.expectError(error.BitRangeOutOfBounds, out_of_bounds.initFromBitList("128"));
    try std.testing.expectEqual(ModuleStage.cold, out_of_bounds.stage());
    const out_of_bounds_summary = out_of_bounds.summary();
    try std.testing.expectEqual(@as(u32, RuntimeBitmapSample.bitmap_nbits), out_of_bounds_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), out_of_bounds_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), out_of_bounds_summary.weight);
    try std.testing.expectEqual(@as(usize, 0), out_of_bounds_summary.init_runs);
}
