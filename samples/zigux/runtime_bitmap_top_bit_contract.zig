const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");

test "runtime bitmap top-bit contract keeps the highest valid bit explicit" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    try module.initWithSetBits(&.{top_bit});

    const summary = module.summary();
    try std.testing.expect(module.isSet(top_bit));
    try std.testing.expect(!module.isSet(top_bit - 1));
    try std.testing.expectEqual(top_bit, summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 1), summary.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, summary.nbits);
}

test "runtime bitmap top-bit contract keeps boundary mutation and bounds checks reviewable" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    const top_bit = runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits - 1;

    try module.initWithSetBits(&.{});
    try module.setRange(top_bit, 1);
    try std.testing.expect(module.isSet(top_bit));

    try module.clearRange(top_bit, 1);
    try std.testing.expect(!module.isSet(top_bit));
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, module.stage());

    try std.testing.expectError(error.BitRangeOutOfBounds, module.setRange(top_bit + 1, 1));
    try std.testing.expectError(error.BitRangeOutOfBounds, module.clearRange(top_bit + 1, 1));
    try std.testing.expectEqual(runtime_bitmap_sample.ModuleStage.initialized, module.stage());
}
