const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(offset: usize) usize {
    return @as(usize, 1) << @intCast(offset);
}

test "bitmap and cpumask shared backing observes word mutations" {
    const word_bits = bitmap_view.word_bits;
    const capacity = word_bits * 2 + 5;
    var shared_words = [_]usize{ 0, 0, ~@as(usize, 0) << 5 };

    const bitmap = bitmap_view.BitmapView.init(shared_words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(shared_words[0..], capacity);

    shared_words[0] = bit(3) | bit(8);
    shared_words[1] = bit(0) | bit(word_bits - 1);
    shared_words[2] |= bit(1);

    try testing.expectEqual(@as(usize, 5), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expect(bitmap.isSet(3));
    try testing.expect(cpumask.hasCpu(3));
    try testing.expect(bitmap.isSet(word_bits));
    try testing.expect(cpumask.hasCpu(word_bits));
    try testing.expect(bitmap.isSet(word_bits * 2 + 1));
    try testing.expect(cpumask.hasCpu(word_bits * 2 + 1));

    try testing.expectEqual(@as(?usize, 3), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expectEqual(@as(?usize, 8), bitmap.nextSetBit(4));
    try testing.expectEqual(bitmap.nextSetBit(4), cpumask.nextCpu(4));
    try testing.expectEqual(@as(?usize, word_bits * 2 - 1), bitmap.nextSetBit(word_bits + 1));
    try testing.expectEqual(bitmap.nextSetBit(word_bits + 1), cpumask.nextCpu(word_bits + 1));
    try testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(word_bits * 2 + 2));
    try testing.expectEqual(bitmap.nextSetBit(word_bits * 2 + 2), cpumask.nextCpu(word_bits * 2 + 2));

    var superset_words = shared_words;
    superset_words[0] |= bit(0);
    superset_words[2] |= bit(4);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], capacity);
    const superset_cpumask = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);

    const disjoint_words = [_]usize{ bit(1), bit(1), bit(3) };
    const disjoint_bitmap = bitmap_view.BitmapView.init(disjoint_words[0..], capacity);
    const disjoint_cpumask = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try testing.expect(bitmap.isSubsetOf(superset_bitmap));
    try testing.expect(cpumask.isSubsetOf(superset_cpumask));
    try testing.expect(!superset_bitmap.isSubsetOf(bitmap));
    try testing.expect(!superset_cpumask.isSubsetOf(cpumask));
    try testing.expect(bitmap.intersects(superset_bitmap));
    try testing.expect(cpumask.intersects(superset_cpumask));
    try testing.expect(!bitmap.intersects(disjoint_bitmap));
    try testing.expect(!cpumask.intersects(disjoint_cpumask));
}

test "bitmap and cpumask ignore tail-only mutation noise until active bits change" {
    const word_bits = bitmap_view.word_bits;
    const capacity = word_bits + 3;
    var shared_words = [_]usize{ bit(0), 0 };

    const bitmap = bitmap_view.BitmapView.init(shared_words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(shared_words[0..], capacity);

    shared_words[1] = ~@as(usize, 0) << 3;
    try testing.expectEqual(@as(usize, 1), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(word_bits));
    try testing.expectEqual(bitmap.nextSetBit(word_bits), cpumask.nextCpu(word_bits));
    try testing.expectEqual(@as(?usize, word_bits), bitmap.nextClearBit(word_bits));
    try testing.expectEqual(bitmap.nextClearBit(word_bits), cpumask.nextMissingCpu(word_bits));

    shared_words[1] |= bit(2);
    try testing.expectEqual(@as(usize, 2), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, word_bits + 2), bitmap.nextSetBit(word_bits));
    try testing.expectEqual(bitmap.nextSetBit(word_bits), cpumask.nextCpu(word_bits));
    try testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(word_bits + 3));
    try testing.expectEqual(bitmap.nextSetBit(word_bits + 3), cpumask.nextCpu(word_bits + 3));
}
