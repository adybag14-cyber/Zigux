const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

test "checkerboard shift mirrors bitmap and cpumask cursors" {
    const capacity = word_bits * 2 + 9;
    const last_valid = word_bits * 2 + 8;
    const clipped_tail = word_bits * 2 + 12;

    const even_words = [_]Word{
        bit(0) | bit(2) | bit(word_bits - 2),
        bit(word_bits + 1) | bit(word_bits + 5),
        bit(last_valid) | bit(clipped_tail),
    };
    const shifted_words = [_]Word{
        bit(1) | bit(3) | bit(word_bits - 1),
        bit(word_bits + 2) | bit(word_bits + 6),
        bit(word_bits * 2 + 7),
    };
    const union_words = [_]Word{
        even_words[0] | shifted_words[0],
        even_words[1] | shifted_words[1],
        even_words[2] | shifted_words[2],
    };
    const outside_words = [_]Word{
        bit(5),
        bit(word_bits + 4),
        bit(word_bits * 2 + 1),
    };

    const even_bitmap = bitmap_view.BitmapView.init(even_words[0..], capacity);
    const even_cpus = cpumask_view.CpuMaskView.init(even_words[0..], capacity);
    const shifted_bitmap = bitmap_view.BitmapView.init(shifted_words[0..], capacity);
    const shifted_cpus = cpumask_view.CpuMaskView.init(shifted_words[0..], capacity);
    const union_bitmap = bitmap_view.BitmapView.init(union_words[0..], capacity);
    const union_cpus = cpumask_view.CpuMaskView.init(union_words[0..], capacity);
    const outside_bitmap = bitmap_view.BitmapView.init(outside_words[0..], capacity);
    const outside_cpus = cpumask_view.CpuMaskView.init(outside_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 6), even_bitmap.countSetBits());
    try std.testing.expectEqual(even_bitmap.countSetBits(), even_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 6), shifted_bitmap.countSetBits());
    try std.testing.expectEqual(shifted_bitmap.countSetBits(), shifted_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 12), union_bitmap.countSetBits());
    try std.testing.expectEqual(union_bitmap.countSetBits(), union_cpus.countPresentCpus());

    try std.testing.expect(even_bitmap.isSubsetOf(union_bitmap));
    try std.testing.expect(even_cpus.isSubsetOf(union_cpus));
    try std.testing.expect(shifted_bitmap.isSubsetOf(union_bitmap));
    try std.testing.expect(shifted_cpus.isSubsetOf(union_cpus));
    try std.testing.expect(!union_bitmap.isSubsetOf(even_bitmap));
    try std.testing.expect(!union_cpus.isSubsetOf(even_cpus));
    try std.testing.expect(!even_bitmap.intersects(shifted_bitmap));
    try std.testing.expect(!even_cpus.intersects(shifted_cpus));
    try std.testing.expect(!union_bitmap.intersects(outside_bitmap));
    try std.testing.expect(!union_cpus.intersects(outside_cpus));

    try std.testing.expectEqual(@as(?usize, 0), even_bitmap.firstSetBit());
    try std.testing.expectEqual(even_bitmap.firstSetBit(), even_cpus.firstCpu());
    try std.testing.expectEqual(@as(?usize, 2), even_bitmap.nextSetBit(1));
    try std.testing.expectEqual(even_bitmap.nextSetBit(1), even_cpus.nextCpu(1));
    try std.testing.expectEqual(@as(?usize, word_bits - 1), shifted_bitmap.nextSetBit(word_bits - 2));
    try std.testing.expectEqual(shifted_bitmap.nextSetBit(word_bits - 2), shifted_cpus.nextCpu(word_bits - 2));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), union_bitmap.nextSetBit(word_bits));
    try std.testing.expectEqual(union_bitmap.nextSetBit(word_bits), union_cpus.nextCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 7), union_bitmap.nextSetBit(word_bits * 2));
    try std.testing.expectEqual(union_bitmap.nextSetBit(word_bits * 2), union_cpus.nextCpu(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, last_valid), union_bitmap.nextSetBit(last_valid));
    try std.testing.expectEqual(union_bitmap.nextSetBit(last_valid), union_cpus.nextCpu(last_valid));
    try std.testing.expectEqual(@as(?usize, null), union_bitmap.nextSetBit(capacity));
    try std.testing.expectEqual(union_bitmap.nextSetBit(capacity), union_cpus.nextCpu(capacity));

    try std.testing.expectEqual(@as(?usize, 4), union_bitmap.firstClearBit());
    try std.testing.expectEqual(union_bitmap.firstClearBit(), union_cpus.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits), union_bitmap.nextClearBit(word_bits - 2));
    try std.testing.expectEqual(union_bitmap.nextClearBit(word_bits - 2), union_cpus.nextMissingCpu(word_bits - 2));
    try std.testing.expect(union_cpus.hasCpu(last_valid));
}

test "checkerboard shift replay keeps rollback and tail masking aligned" {
    const capacity = word_bits + 11;
    const bridge = word_bits + 3;
    const last_valid = word_bits + 10;
    const clipped_tail = word_bits + 12;

    const base_words = [_]Word{
        bit(4) | bit(8) | bit(word_bits - 4),
        bit(word_bits + 1) | bit(bridge) | bit(last_valid) | bit(clipped_tail),
    };
    const rollback_words = [_]Word{
        bit(4) | bit(word_bits - 4),
        bit(bridge),
    };
    const promoted_words = [_]Word{
        base_words[0] | bit(6),
        base_words[1] | bit(word_bits + 7),
    };
    const gap_words = [_]Word{
        bit(0) | bit(2),
        bit(word_bits + 5),
    };

    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const base_cpus = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const rollback_bitmap = bitmap_view.BitmapView.init(rollback_words[0..], capacity);
    const rollback_cpus = cpumask_view.CpuMaskView.init(rollback_words[0..], capacity);
    const promoted_bitmap = bitmap_view.BitmapView.init(promoted_words[0..], capacity);
    const promoted_cpus = cpumask_view.CpuMaskView.init(promoted_words[0..], capacity);
    const gap_bitmap = bitmap_view.BitmapView.init(gap_words[0..], capacity);
    const gap_cpus = cpumask_view.CpuMaskView.init(gap_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 6), base_bitmap.countSetBits());
    try std.testing.expectEqual(base_bitmap.countSetBits(), base_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 3), rollback_bitmap.countSetBits());
    try std.testing.expectEqual(rollback_bitmap.countSetBits(), rollback_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 8), promoted_bitmap.countSetBits());
    try std.testing.expectEqual(promoted_bitmap.countSetBits(), promoted_cpus.countPresentCpus());

    try std.testing.expect(rollback_bitmap.isSubsetOf(base_bitmap));
    try std.testing.expect(rollback_cpus.isSubsetOf(base_cpus));
    try std.testing.expect(base_bitmap.isSubsetOf(promoted_bitmap));
    try std.testing.expect(base_cpus.isSubsetOf(promoted_cpus));
    try std.testing.expect(!promoted_bitmap.isSubsetOf(base_bitmap));
    try std.testing.expect(!promoted_cpus.isSubsetOf(base_cpus));
    try std.testing.expect(base_bitmap.intersects(rollback_bitmap));
    try std.testing.expect(base_cpus.intersects(rollback_cpus));
    try std.testing.expect(!base_bitmap.intersects(gap_bitmap));
    try std.testing.expect(!base_cpus.intersects(gap_cpus));

    try std.testing.expectEqual(@as(?usize, word_bits + 1), base_bitmap.nextSetBit(word_bits));
    try std.testing.expectEqual(base_bitmap.nextSetBit(word_bits), base_cpus.nextCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, bridge), base_bitmap.nextSetBit(word_bits + 2));
    try std.testing.expectEqual(base_bitmap.nextSetBit(word_bits + 2), base_cpus.nextCpu(word_bits + 2));
    try std.testing.expectEqual(@as(?usize, last_valid), base_bitmap.nextSetBit(bridge + 1));
    try std.testing.expectEqual(base_bitmap.nextSetBit(bridge + 1), base_cpus.nextCpu(bridge + 1));
    try std.testing.expectEqual(@as(?usize, null), base_bitmap.nextSetBit(last_valid + 1));
    try std.testing.expectEqual(base_bitmap.nextSetBit(last_valid + 1), base_cpus.nextCpu(last_valid + 1));
    try std.testing.expectEqual(@as(?usize, word_bits), base_bitmap.nextClearBit(word_bits));
    try std.testing.expectEqual(base_bitmap.nextClearBit(word_bits), base_cpus.nextMissingCpu(word_bits));
    try std.testing.expect(!base_cpus.hasCpu(word_bits));
}
