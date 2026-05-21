const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

test "offset bridge replay keeps bitmap and cpumask summaries aligned" {
    const capacity = bitmap_view.word_bits + 10;
    const tail_valid_mask = (@as(usize, 1) << 10) - 1;
    const words = [_]usize{
        (@as(usize, 1) << 2) |
            (@as(usize, 1) << (bitmap_view.word_bits - 2)) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 1) |
            (@as(usize, 1) << 5) |
            (@as(usize, 1) << 9) |
            ~tail_valid_mask,
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 7), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 2), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(2));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits - 1));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 2));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 5));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 9));
}

test "offset bridge replay keeps subset and overlap checks bounded" {
    const capacity = bitmap_view.word_bits + 10;
    const tail_valid_mask = (@as(usize, 1) << 10) - 1;
    const bridge_words = [_]usize{
        (@as(usize, 1) << 2) |
            (@as(usize, 1) << (bitmap_view.word_bits - 2)) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 1) |
            (@as(usize, 1) << 5) |
            (@as(usize, 1) << 9) |
            ~tail_valid_mask,
    };
    const superset_words = [_]usize{
        bridge_words[0] | (@as(usize, 1) << 7),
        bridge_words[1] | (@as(usize, 1) << 7),
    };
    const disjoint_words = [_]usize{
        (@as(usize, 1) << 3) |
            (@as(usize, 1) << 8),
        (@as(usize, 1) << 3) |
            (@as(usize, 1) << 6) |
            ~tail_valid_mask,
    };

    const bridge = cpumask_view.CpuMaskView.init(bridge_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try testing.expect(bridge.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(bridge));
    try testing.expect(bridge.intersects(superset));
    try testing.expect(!bridge.intersects(disjoint));
}

test "offset bridge replay ignores tail-only storage outside the bounded window" {
    const capacity = bitmap_view.word_bits + 10;
    const words = [_]usize{
        0,
        ~((@as(usize, 1) << 10) - 1),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 0), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}
