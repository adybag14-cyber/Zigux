const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn inactiveTailNoise(bit_len: usize) usize {
    const remainder = bit_len % bitmap_view.word_bits;
    if (remainder == 0) return 0;
    return ~((@as(usize, 1) << @intCast(remainder)) - 1);
}

test "dual clusters stay aligned for bitmap and cpumask views" {
    const capacity = bitmap_view.word_bits + 7;
    const tail_start = bitmap_view.word_bits + 2;
    const words = [_]usize{
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 1) |
            (@as(usize, 1) << 2),
        (@as(usize, 1) << 2) |
            (@as(usize, 1) << 4) |
            inactiveTailNoise(capacity),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 5), bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 3), bitmap.firstClearBit());
    try testing.expect(bitmap.isSet(tail_start));
    try testing.expect(!bitmap.isSet(tail_start + 1));

    try testing.expectEqual(@as(usize, 5), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 3), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(tail_start));
    try testing.expect(!cpumask.hasCpu(tail_start + 1));
}

test "dual clusters keep subset and overlap checks focused on active bits" {
    const capacity = bitmap_view.word_bits + 7;
    const leading_cluster = [_]usize{
        (@as(usize, 1) << 0) |
            (@as(usize, 1) << 1) |
            (@as(usize, 1) << 2),
        inactiveTailNoise(capacity),
    };
    const trailing_cluster = [_]usize{
        0,
        (@as(usize, 1) << 2) |
            (@as(usize, 1) << 4) |
            inactiveTailNoise(capacity),
    };
    const combined_clusters = [_]usize{
        leading_cluster[0],
        trailing_cluster[1],
    };

    const leading = cpumask_view.CpuMaskView.init(leading_cluster[0..], capacity);
    const trailing = cpumask_view.CpuMaskView.init(trailing_cluster[0..], capacity);
    const combined = cpumask_view.CpuMaskView.init(combined_clusters[0..], capacity);

    try testing.expect(leading.isSubsetOf(combined));
    try testing.expect(trailing.isSubsetOf(combined));
    try testing.expect(!combined.isSubsetOf(leading));
    try testing.expect(!leading.intersects(trailing));
    try testing.expect(combined.intersects(trailing));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 2), trailing.firstCpu());
    try testing.expectEqual(@as(?usize, 0), trailing.firstMissingCpu());
    try testing.expectEqual(@as(usize, 2), trailing.countPresentCpus());
}
