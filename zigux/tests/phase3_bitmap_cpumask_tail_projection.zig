const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view_helper");
const cpumask_view = @import("cpumask_view_helper");

test "tail-masked bitmap and cpumask projections stay aligned on the same bounded words" {
    var backing = [_]usize{
        ~@as(usize, 0),
        bitmap_view.lastWordMask(bitmap_view.bits_per_word + 11),
    };
    const nbits = bitmap_view.bits_per_word + 11;
    const bitmap = bitmap_view.viewFromWords(backing[0..], nbits);
    const cpumask = cpumask_view.viewFromWords(backing[0..], nbits);
    const bitmap_summary = bitmap_view.summarize(bitmap);
    const cpumask_summary = cpumask_view.summarize(cpumask);

    try testing.expect(bitmap_view.isValid(bitmap));
    try testing.expect(cpumask_view.isValid(cpumask));
    try testing.expectEqual(bitmap_summary.first_set, cpumask_summary.first_set);
    try testing.expectEqual(bitmap_summary.first_zero, cpumask_summary.first_zero);
    try testing.expectEqual(bitmap_summary.weight, cpumask_summary.weight);
    try testing.expectEqual(bitmap_view.firstSet(bitmap), cpumask_view.firstCpu(cpumask));
    try testing.expectEqual(bitmap_view.firstZero(bitmap), cpumask_view.firstAbsentCpu(cpumask));
    try testing.expectEqual(bitmap_view.weight(bitmap), cpumask_view.weight(cpumask));
    try testing.expectEqual(
        bitmap_view.testBit(bitmap, bitmap_view.bits_per_word + 10),
        cpumask_view.cpuIsSet(cpumask, bitmap_view.bits_per_word + 10),
    );
    try testing.expectEqual(
        bitmap_view.testBit(bitmap, bitmap_view.bits_per_word + 11),
        cpumask_view.cpuIsSet(cpumask, bitmap_view.bits_per_word + 11),
    );
    try testing.expect(bitmap_view.testBit(bitmap, bitmap_view.bits_per_word + 10));
    try testing.expect(!bitmap_view.testBit(bitmap, bitmap_view.bits_per_word + 11));
}
