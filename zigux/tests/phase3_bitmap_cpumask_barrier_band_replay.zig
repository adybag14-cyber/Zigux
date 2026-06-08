const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

test "barrier band mirrors word-boundary bitmap and cpumask cursors" {
    const capacity = word_bits * 2 + 9;
    const left_barrier = word_bits - 1;
    const bridge_start = word_bits;
    const right_barrier = word_bits + 8;
    const tail_noise = word_bits + 11;

    const band_words = [_]Word{
        bit(0) | bit(left_barrier),
        bit(bridge_start) | bit(word_bits + 3) | bit(right_barrier),
        bit(tail_noise),
    };
    const guard_words = [_]Word{
        bit(1) | bit(word_bits - 2),
        bit(word_bits + 2) | bit(word_bits + 7),
        std.math.maxInt(Word),
    };
    const superset_words = [_]Word{
        band_words[0] | bit(4),
        band_words[1] | bit(word_bits + 6),
        std.math.maxInt(Word),
    };

    const band_bitmap = bitmap_view.BitmapView.init(band_words[0..], capacity);
    const band_cpus = cpumask_view.CpuMaskView.init(band_words[0..], capacity);
    const guard_bitmap = bitmap_view.BitmapView.init(guard_words[0..], capacity);
    const guard_cpus = cpumask_view.CpuMaskView.init(guard_words[0..], capacity);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], capacity);
    const superset_cpus = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 5), band_bitmap.countSetBits());
    try std.testing.expectEqual(band_bitmap.countSetBits(), band_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 0), band_bitmap.firstSetBit());
    try std.testing.expectEqual(band_bitmap.firstSetBit(), band_cpus.firstCpu());
    try std.testing.expectEqual(@as(?usize, left_barrier), band_bitmap.nextSetBit(left_barrier));
    try std.testing.expectEqual(band_bitmap.nextSetBit(left_barrier), band_cpus.nextCpu(left_barrier));
    try std.testing.expectEqual(@as(?usize, bridge_start), band_bitmap.nextSetBit(bridge_start));
    try std.testing.expectEqual(band_bitmap.nextSetBit(bridge_start), band_cpus.nextCpu(bridge_start));
    try std.testing.expectEqual(@as(?usize, null), band_bitmap.nextSetBit(right_barrier + 1));
    try std.testing.expectEqual(band_bitmap.nextSetBit(right_barrier + 1), band_cpus.nextCpu(right_barrier + 1));

    try std.testing.expectEqual(@as(?usize, 1), band_bitmap.firstClearBit());
    try std.testing.expectEqual(band_bitmap.firstClearBit(), band_cpus.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 1), band_bitmap.nextClearBit(bridge_start));
    try std.testing.expectEqual(band_bitmap.nextClearBit(bridge_start), band_cpus.nextMissingCpu(bridge_start));

    try std.testing.expect(band_bitmap.isSubsetOf(superset_bitmap));
    try std.testing.expect(band_cpus.isSubsetOf(superset_cpus));
    try std.testing.expect(!superset_bitmap.isSubsetOf(band_bitmap));
    try std.testing.expect(!superset_cpus.isSubsetOf(band_cpus));
    try std.testing.expect(!band_bitmap.intersects(guard_bitmap));
    try std.testing.expect(!band_cpus.intersects(guard_cpus));
}

test "barrier band clips noisy storage beyond declared cpu capacity" {
    const capacity = word_bits + 5;
    const last_valid = word_bits + 4;
    const clipped_tail = word_bits + 6;

    const clipped_words = [_]Word{
        bit(word_bits - 1),
        bit(word_bits) | bit(last_valid) | bit(clipped_tail),
    };
    const widened_words = [_]Word{
        clipped_words[0] | bit(2),
        clipped_words[1],
    };

    const clipped_bitmap = bitmap_view.BitmapView.init(clipped_words[0..], capacity);
    const clipped_cpus = cpumask_view.CpuMaskView.init(clipped_words[0..], capacity);
    const widened_bitmap = bitmap_view.BitmapView.init(widened_words[0..], capacity);
    const widened_cpus = cpumask_view.CpuMaskView.init(widened_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 3), clipped_bitmap.countSetBits());
    try std.testing.expectEqual(clipped_bitmap.countSetBits(), clipped_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, word_bits - 1), clipped_bitmap.firstSetBit());
    try std.testing.expectEqual(clipped_bitmap.firstSetBit(), clipped_cpus.firstCpu());
    try std.testing.expectEqual(@as(?usize, last_valid), clipped_bitmap.nextSetBit(last_valid));
    try std.testing.expectEqual(clipped_bitmap.nextSetBit(last_valid), clipped_cpus.nextCpu(last_valid));

    try std.testing.expect(clipped_bitmap.isSubsetOf(widened_bitmap));
    try std.testing.expect(clipped_cpus.isSubsetOf(widened_cpus));
    try std.testing.expectEqual(@as(?usize, null), clipped_bitmap.nextSetBit(last_valid + 1));
    try std.testing.expectEqual(clipped_bitmap.nextSetBit(last_valid + 1), clipped_cpus.nextCpu(last_valid + 1));
    try std.testing.expectEqual(@as(?usize, null), clipped_bitmap.nextClearBit(capacity));
    try std.testing.expectEqual(clipped_bitmap.nextClearBit(capacity), clipped_cpus.nextMissingCpu(capacity));
}
