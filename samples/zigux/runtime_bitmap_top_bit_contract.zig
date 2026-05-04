const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

test "runtime bitmap sample keeps the highest valid bit explicit in the direct sample leg" {
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    var direct = runtime_bitmap_sample.RuntimeBitmapSample{};
    try direct.initWithSetBits(&.{top_bit});

    const direct_summary = direct.summary();
    try std.testing.expectEqual(top_bit, direct_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), direct_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 1), direct_summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, direct_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), direct_summary.init_runs);
    try std.testing.expect(direct.isSet(top_bit));
    try std.testing.expect(!direct.isSet(top_bit - 1));
    try std.testing.expectEqual(@as(?u32, top_bit), direct.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), direct.nthSetBit(1));
    try std.testing.expectEqual(@as(u32, 1), try direct.countSetBitsInRange(top_bit, 1));

    const direct_formatted = try direct.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(direct_formatted);
    try std.testing.expectEqualStrings("127", direct_formatted);

    var parsed = runtime_bitmap_sample.RuntimeBitmapSample{};
    try parsed.initFromBitList("127");

    const parsed_summary = parsed.summary();
    try std.testing.expectEqual(direct_summary.first_set, parsed_summary.first_set);
    try std.testing.expectEqual(direct_summary.first_zero, parsed_summary.first_zero);
    try std.testing.expectEqual(direct_summary.weight, parsed_summary.weight);
    try std.testing.expectEqual(direct_summary.nbits, parsed_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), parsed_summary.init_runs);
    try std.testing.expect(parsed.isSet(top_bit));
    try std.testing.expect(!parsed.isSet(top_bit - 1));
    try std.testing.expectEqual(@as(?u32, top_bit), parsed.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), parsed.nthSetBit(1));
    try std.testing.expectEqual(@as(u32, 1), try parsed.countSetBitsInRange(top_bit, 1));

    const parsed_formatted = try parsed.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(parsed_formatted);
    try std.testing.expectEqualStrings("127", parsed_formatted);
}

test "runtime bitmap sample keeps top-bit lifecycle mutation explicit in the direct sample leg" {
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{top_bit});
    _ = try module.runSelftest();

    try module.clearRange(top_bit, 1);

    const cleared_summary = module.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, cleared_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), cleared_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), cleared_summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, cleared_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), cleared_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), cleared_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cleared_summary.exit_runs);
    try std.testing.expect(!module.isSet(top_bit));
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(0));
    try std.testing.expectEqual(@as(u32, 0), try module.countSetBitsInRange(top_bit, 1));

    const cleared_formatted = try module.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(cleared_formatted);
    try std.testing.expectEqualStrings("", cleared_formatted);

    try module.setRange(top_bit, 1);

    const restored_summary = module.summary();
    try std.testing.expectEqual(@as(u32, top_bit), restored_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), restored_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 1), restored_summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, restored_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), restored_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), restored_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), restored_summary.exit_runs);
    try std.testing.expect(module.isSet(top_bit));
    try std.testing.expect(!module.isSet(top_bit - 1));
    try std.testing.expectEqual(@as(?u32, top_bit), module.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(1));
    try std.testing.expectEqual(@as(u32, 1), try module.countSetBitsInRange(top_bit, 1));

    const restored_formatted = try module.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(restored_formatted);
    try std.testing.expectEqualStrings("127", restored_formatted);

    var mirror = runtime_bitmap_sample.RuntimeBitmapSample{};
    try mirror.initWithSetBits(&.{});
    try mirror.copyFrom(&module);

    const mirror_summary = mirror.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, mirror.stage());
    try std.testing.expectEqual(restored_summary.first_set, mirror_summary.first_set);
    try std.testing.expectEqual(restored_summary.first_zero, mirror_summary.first_zero);
    try std.testing.expectEqual(restored_summary.weight, mirror_summary.weight);
    try std.testing.expectEqual(restored_summary.nbits, mirror_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), mirror_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), mirror_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), mirror_summary.exit_runs);
    try std.testing.expect(mirror.isSet(top_bit));
    try std.testing.expect(!mirror.isSet(top_bit - 1));

    try module.exit();

    const exited_summary = module.summary();
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(restored_summary.first_set, exited_summary.first_set);
    try std.testing.expectEqual(restored_summary.first_zero, exited_summary.first_zero);
    try std.testing.expectEqual(restored_summary.weight, exited_summary.weight);
    try std.testing.expectEqual(restored_summary.nbits, exited_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expect(module.isSet(top_bit));
    try std.testing.expect(!module.isSet(top_bit - 1));
    try std.testing.expectEqual(@as(u32, 1), try module.countSetBitsInRange(top_bit, 1));
}
