const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn tailNoiseMask(valid_tail_bits: usize) usize {
    if (valid_tail_bits >= bitmap_view.word_bits) return 0;
    const WideWord = std.meta.Int(.unsigned, bitmap_view.word_bits);
    var mask: WideWord = 0;
    var bit = valid_tail_bits;
    while (bit < bitmap_view.word_bits) : (bit += 1) {
        const shift: std.math.Log2Int(WideWord) = @intCast(bit);
        mask |= @as(WideWord, 1) << shift;
    }
    return @as(usize, @intCast(mask));
}

test "bitmap interior island replay keeps middle occupancy bounded away from both edges" {
    const capacity = bitmap_view.word_bits + 7;
    const trailing_noise = tailNoiseMask(7);
    const words = [_]usize{
        (@as(usize, 1) << 5) |
            (@as(usize, 1) << 6) |
            (@as(usize, 1) << (bitmap_view.word_bits - 2)) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        trailing_noise |
            (@as(usize, 1) << 0) |
            (@as(usize, 1) << 1) |
            (@as(usize, 1) << 2),
    };
    const view = bitmap_view.BitmapView.init(words[0..], capacity);

    try testing.expect(!view.isSet(0));
    try testing.expect(!view.isSet(4));
    try testing.expect(view.isSet(5));
    try testing.expect(view.isSet(bitmap_view.word_bits + 2));
    try testing.expect(!view.isSet(capacity - 1));
    try testing.expectEqual(@as(usize, 7), view.countSetBits());
    try testing.expectEqual(@as(?usize, 5), view.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), view.firstClearBit());
}

test "cpumask interior island replay keeps subset and overlap checks centered on the valid band" {
    const capacity = bitmap_view.word_bits + 7;
    const trailing_noise = tailNoiseMask(7);

    const base_words = [_]usize{
        (@as(usize, 1) << 5) |
            (@as(usize, 1) << 6) |
            (@as(usize, 1) << (bitmap_view.word_bits - 2)) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        trailing_noise |
            (@as(usize, 1) << 0) |
            (@as(usize, 1) << 1) |
            (@as(usize, 1) << 2),
    };
    const superset_words = [_]usize{
        (@as(usize, 1) << 4) |
            (@as(usize, 1) << 5) |
            (@as(usize, 1) << 6) |
            (@as(usize, 1) << (bitmap_view.word_bits - 2)) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        trailing_noise |
            (@as(usize, 1) << 0) |
            (@as(usize, 1) << 1) |
            (@as(usize, 1) << 2) |
            (@as(usize, 1) << 6),
    };
    const disjoint_words = [_]usize{
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 4) |
            (@as(usize, 1) << (bitmap_view.word_bits - 3)),
        trailing_noise | (@as(usize, 1) << 6),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try testing.expect(!base.hasCpu(0));
    try testing.expect(base.hasCpu(5));
    try testing.expect(base.hasCpu(bitmap_view.word_bits + 2));
    try testing.expectEqual(@as(usize, 7), base.countPresentCpus());
    try testing.expectEqual(@as(?usize, 5), base.firstCpu());
    try testing.expectEqual(@as(?usize, 0), base.firstMissingCpu());
    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(base.intersects(superset));
    try testing.expect(!base.intersects(disjoint));
}

test "bitmap and cpumask interior island replay stay in lockstep on shared storage" {
    const capacity = bitmap_view.word_bits + 7;
    const trailing_noise = tailNoiseMask(7);
    const words = [_]usize{
        (@as(usize, 1) << 5) |
            (@as(usize, 1) << 6) |
            (@as(usize, 1) << (bitmap_view.word_bits - 2)) |
            (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        trailing_noise |
            (@as(usize, 1) << 0) |
            (@as(usize, 1) << 1) |
            (@as(usize, 1) << 2),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}
