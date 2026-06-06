const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const word_bits = bitmap_view.word_bits;
const Word = bitmap_view.Word;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

test "bitmap and cpumask diagonal braid mirrors cursor and relation state" {
    const capacity = word_bits * 3 + 9;
    const diagonal_words = [_]Word{
        bit(2),
        bit(word_bits + 5),
        bit(word_bits * 2 + 8),
        bit(word_bits * 3 + 1) | (~@as(Word, 0) << 9),
    };
    const subset_words = [_]Word{
        bit(2),
        0,
        bit(word_bits * 2 + 8),
        bit(word_bits * 3 + 1) | (~@as(Word, 0) << 9),
    };
    const disjoint_words = [_]Word{
        bit(4),
        bit(word_bits + 7),
        bit(word_bits * 2 + 2),
        bit(word_bits * 3 + 3) | (~@as(Word, 0) << 9),
    };

    const bitmap = bitmap_view.BitmapView.init(diagonal_words[0..], capacity);
    const cpus = cpumask_view.CpuMaskView.init(diagonal_words[0..], capacity);
    const subset_bitmap = bitmap_view.BitmapView.init(subset_words[0..], capacity);
    const subset_cpus = cpumask_view.CpuMaskView.init(subset_words[0..], capacity);
    const disjoint_bitmap = bitmap_view.BitmapView.init(disjoint_words[0..], capacity);
    const disjoint_cpus = cpumask_view.CpuMaskView.init(disjoint_words[0..], capacity);

    try testing.expectEqual(@as(usize, 4), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpus.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpus.firstCpu());
    try testing.expectEqual(@as(?usize, 2), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), cpus.firstMissingCpu());
    try testing.expectEqual(@as(?usize, word_bits + 5), bitmap.nextSetBit(3));
    try testing.expectEqual(bitmap.nextSetBit(word_bits + 1), cpus.nextCpu(word_bits + 1));
    try testing.expectEqual(@as(?usize, word_bits * 3 + 1), cpus.nextCpu(word_bits * 2 + 9));
    try testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(capacity));
    try testing.expectEqual(@as(?usize, null), cpus.nextCpu(capacity));

    try testing.expect(subset_bitmap.isSubsetOf(bitmap));
    try testing.expect(subset_cpus.isSubsetOf(cpus));
    try testing.expect(bitmap.intersects(subset_bitmap));
    try testing.expect(cpus.intersects(subset_cpus));
    try testing.expect(!bitmap.intersects(disjoint_bitmap));
    try testing.expect(!cpus.intersects(disjoint_cpus));
}

test "bitmap and cpumask diagonal braid clips high-word noise to capacity" {
    const capacity = word_bits * 2 + 6;
    const clipped_words = [_]Word{
        bit(1) | bit(9),
        bit(word_bits + 4),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 8) | (~@as(Word, 0) << 10),
    };
    const exact_subset_words = [_]Word{
        bit(1),
        bit(word_bits + 4),
        bit(word_bits * 2 + 1) | (~@as(Word, 0) << 10),
    };
    const tail_only_noise_words = [_]Word{
        0,
        0,
        bit(word_bits * 2 + 8) | (~@as(Word, 0) << 10),
    };

    const bitmap = bitmap_view.BitmapView.init(clipped_words[0..], capacity);
    const cpus = cpumask_view.CpuMaskView.init(clipped_words[0..], capacity);
    const subset_bitmap = bitmap_view.BitmapView.init(exact_subset_words[0..], capacity);
    const subset_cpus = cpumask_view.CpuMaskView.init(exact_subset_words[0..], capacity);
    const tail_noise_bitmap = bitmap_view.BitmapView.init(tail_only_noise_words[0..], capacity);
    const tail_noise_cpus = cpumask_view.CpuMaskView.init(tail_only_noise_words[0..], capacity);

    try testing.expectEqual(@as(usize, 4), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpus.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), cpus.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(@as(?usize, word_bits * 2 + 1), bitmap.nextSetBit(word_bits * 2));
    try testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(word_bits * 2 + 2));
    try testing.expectEqual(bitmap.nextSetBit(word_bits * 2), cpus.nextCpu(word_bits * 2));
    try testing.expectEqual(bitmap.nextClearBit(word_bits * 2 + 2), cpus.nextMissingCpu(word_bits * 2 + 2));

    try testing.expect(subset_bitmap.isSubsetOf(bitmap));
    try testing.expect(subset_cpus.isSubsetOf(cpus));
    try testing.expect(!bitmap.isSubsetOf(subset_bitmap));
    try testing.expect(!cpus.isSubsetOf(subset_cpus));
    try testing.expectEqual(@as(usize, 0), tail_noise_bitmap.countSetBits());
    try testing.expectEqual(@as(usize, 0), tail_noise_cpus.countPresentCpus());
    try testing.expect(!bitmap.intersects(tail_noise_bitmap));
    try testing.expect(!cpus.intersects(tail_noise_cpus));
}
