const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(index: usize) usize {
    return @as(usize, 1) << @intCast(index);
}

test "causeway window keeps bitmap and cpumask summaries aligned across multiword tail noise" {
    const capacity = bitmap_view.word_bits + 6;
    const words = [_]usize{
        bit(0) | bit(bitmap_view.word_bits - 1),
        bit(2) | bit(5) | bit(20),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expect(bitmap.isSet(0));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits - 1));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 2));
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 5));
    try testing.expect(!bitmap.isSet(bitmap_view.word_bits + 1));

    try testing.expect(cpumask.hasCpu(0));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits - 1));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 2));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 5));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 1));

    try testing.expectEqual(@as(usize, 4), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
}

test "causeway window keeps subset and overlap checks bounded to the declared capacity" {
    const capacity = bitmap_view.word_bits + 6;
    const base_words = [_]usize{
        bit(2) | bit(bitmap_view.word_bits - 3),
        bit(1) | bit(4) | bit(17),
    };
    const superset_words = [_]usize{
        bit(0) | bit(2) | bit(bitmap_view.word_bits - 3),
        bit(1) | bit(4) | bit(5) | std.math.maxInt(usize),
    };
    const peer_words = [_]usize{
        bit(bitmap_view.word_bits - 3),
        bit(5),
    };
    const disjoint_words = [_]usize{
        bit(1),
        bit(2),
    };

    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], capacity);
    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const peer = cpumask_view.CpuMaskView.init(peer_words[0..], capacity);
    const disjoint = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try testing.expectEqual(@as(usize, 4), base_bitmap.countSetBits());
    try testing.expectEqual(@as(usize, 9), superset_bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 1), superset_bitmap.firstClearBit());

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(base));
    try testing.expect(base.intersects(superset));
    try testing.expect(base.intersects(peer));
    try testing.expect(!base.isSubsetOf(peer));
    try testing.expect(!base.intersects(disjoint));
}
