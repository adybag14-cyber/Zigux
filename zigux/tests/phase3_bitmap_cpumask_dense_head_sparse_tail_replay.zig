const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn validTailMask(valid_tail_bits: usize) usize {
    return (@as(usize, 1) << @intCast(valid_tail_bits)) - 1;
}

test "bitmap cpumask dense head sparse tail replay keeps tail gaps explicit" {
    const capacity = bitmap_view.word_bits + 7;
    const words = [_]usize{
        std.math.maxInt(usize),
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 3) |
            (@as(usize, 1) << 6) |
            (@as(usize, 1) << 17),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, bitmap_view.word_bits + 3), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 6));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 5));
}

test "bitmap cpumask dense head sparse tail replay keeps tail-only noise empty" {
    const capacity = bitmap_view.word_bits + 7;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 3) |
            (@as(usize, 1) << 6),
    };
    const noise_only_words = [_]usize{
        0,
        ~validTailMask(7),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const noise_only = cpumask_view.CpuMaskView.init(noise_only_words[0..], capacity);

    try testing.expectEqual(@as(usize, 0), noise_only.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), noise_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), noise_only.firstMissingCpu());
    try testing.expect(noise_only.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(noise_only));
    try testing.expect(!base.intersects(noise_only));
}

test "bitmap cpumask dense head sparse tail replay keeps bounded peer relations aligned" {
    const capacity = bitmap_view.word_bits + 7;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 3) |
            (@as(usize, 1) << 6) |
            (@as(usize, 1) << 19),
    };
    const superset_words = [_]usize{
        std.math.maxInt(usize),
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 3) |
            (@as(usize, 1) << 5) |
            (@as(usize, 1) << 6) |
            (@as(usize, 1) << 21),
    };
    const disjoint_words = [_]usize{
        0,
        (@as(usize, 1) << 1) |
            (@as(usize, 1) << 2) |
            (@as(usize, 1) << 14),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(base.intersects(superset));
    try testing.expect(!base.intersects(disjoint));
}
