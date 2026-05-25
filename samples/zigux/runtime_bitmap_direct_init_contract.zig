const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

const ModuleStage = runtime_bitmap_sample.ModuleStage;
const RuntimeBitmapSample = runtime_bitmap_sample.RuntimeBitmapSample;

test "runtime bitmap sample normalizes unsorted duplicate direct init bits without inflating summaries" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 70, 5, 0, 64, 70, 5 });

    const summary = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.exit_runs);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(70));
    try std.testing.expectEqual(@as(?u32, 0), module.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, 5), module.nthSetBit(1));
    try std.testing.expectEqual(@as(?u32, 64), module.nthSetBit(2));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(4));
    try std.testing.expectEqual(@as(u32, 2), try module.countSetBitsInRange(64, 7));

    const formatted = try module.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);
    try std.testing.expectEqualStrings("0,5,64,70", formatted);
}
