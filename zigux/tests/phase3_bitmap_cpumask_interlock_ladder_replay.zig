const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

test "interlock ladder mirrors bitmap and cpumask relation cursors" {
    const capacity = word_bits * 2 + 13;
    const rung_a = word_bits - 3;
    const rung_b = word_bits;
    const rung_c = word_bits + 6;
    const rung_d = word_bits * 2 + 12;
    const clipped_tail = word_bits * 2 + 14;

    const left_words = [_]Word{
        bit(2) | bit(rung_a),
        bit(rung_b) | bit(rung_c),
        bit(rung_d) | bit(clipped_tail),
    };
    const right_words = [_]Word{
        bit(5) | bit(rung_a),
        bit(rung_b + 2) | bit(rung_c),
        bit(rung_d),
    };
    const ladder_words = [_]Word{
        left_words[0] | right_words[0],
        left_words[1] | right_words[1],
        left_words[2] | right_words[2],
    };
    const outside_words = [_]Word{
        bit(0) | bit(word_bits - 1),
        bit(word_bits + 4) | bit(word_bits + 11),
        0,
    };

    const left_bitmap = bitmap_view.BitmapView.init(left_words[0..], capacity);
    const left_cpus = cpumask_view.CpuMaskView.init(left_words[0..], capacity);
    const right_bitmap = bitmap_view.BitmapView.init(right_words[0..], capacity);
    const right_cpus = cpumask_view.CpuMaskView.init(right_words[0..], capacity);
    const ladder_bitmap = bitmap_view.BitmapView.init(ladder_words[0..], capacity);
    const ladder_cpus = cpumask_view.CpuMaskView.init(ladder_words[0..], capacity);
    const outside_bitmap = bitmap_view.BitmapView.init(outside_words[0..], capacity);
    const outside_cpus = cpumask_view.CpuMaskView.init(outside_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 5), left_bitmap.countSetBits());
    try std.testing.expectEqual(left_bitmap.countSetBits(), left_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 5), right_bitmap.countSetBits());
    try std.testing.expectEqual(right_bitmap.countSetBits(), right_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 7), ladder_bitmap.countSetBits());
    try std.testing.expectEqual(ladder_bitmap.countSetBits(), ladder_cpus.countPresentCpus());

    try std.testing.expect(left_bitmap.isSubsetOf(ladder_bitmap));
    try std.testing.expect(left_cpus.isSubsetOf(ladder_cpus));
    try std.testing.expect(right_bitmap.isSubsetOf(ladder_bitmap));
    try std.testing.expect(right_cpus.isSubsetOf(ladder_cpus));
    try std.testing.expect(!ladder_bitmap.isSubsetOf(left_bitmap));
    try std.testing.expect(!ladder_cpus.isSubsetOf(left_cpus));
    try std.testing.expect(left_bitmap.intersects(right_bitmap));
    try std.testing.expect(left_cpus.intersects(right_cpus));
    try std.testing.expect(!ladder_bitmap.intersects(outside_bitmap));
    try std.testing.expect(!ladder_cpus.intersects(outside_cpus));

    try std.testing.expectEqual(@as(?usize, 2), left_bitmap.firstSetBit());
    try std.testing.expectEqual(left_bitmap.firstSetBit(), left_cpus.firstCpu());
    try std.testing.expectEqual(@as(?usize, rung_a), ladder_bitmap.nextSetBit(rung_a - 1));
    try std.testing.expectEqual(ladder_bitmap.nextSetBit(rung_a - 1), ladder_cpus.nextCpu(rung_a - 1));
    try std.testing.expectEqual(@as(?usize, rung_b), ladder_bitmap.nextSetBit(rung_b));
    try std.testing.expectEqual(ladder_bitmap.nextSetBit(rung_b), ladder_cpus.nextCpu(rung_b));
    try std.testing.expectEqual(@as(?usize, rung_d), ladder_bitmap.nextSetBit(word_bits * 2));
    try std.testing.expectEqual(ladder_bitmap.nextSetBit(word_bits * 2), ladder_cpus.nextCpu(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, null), ladder_bitmap.nextSetBit(capacity));
    try std.testing.expectEqual(ladder_bitmap.nextSetBit(capacity), ladder_cpus.nextCpu(capacity));

    try std.testing.expectEqual(@as(?usize, 0), ladder_bitmap.firstClearBit());
    try std.testing.expectEqual(ladder_bitmap.firstClearBit(), ladder_cpus.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 1), ladder_bitmap.nextClearBit(word_bits));
    try std.testing.expectEqual(ladder_bitmap.nextClearBit(word_bits), ladder_cpus.nextMissingCpu(word_bits));
}

test "interlock ladder clips tail noise through declared cpu capacity" {
    const capacity = word_bits + 7;
    const last_valid = word_bits + 6;
    const clipped_tail = word_bits + 8;

    const noisy_words = [_]Word{
        bit(1) | bit(word_bits - 1),
        bit(word_bits) | bit(last_valid) | bit(clipped_tail),
    };
    const widened_words = [_]Word{
        noisy_words[0] | bit(3),
        noisy_words[1],
    };

    const noisy_bitmap = bitmap_view.BitmapView.init(noisy_words[0..], capacity);
    const noisy_cpus = cpumask_view.CpuMaskView.init(noisy_words[0..], capacity);
    const widened_bitmap = bitmap_view.BitmapView.init(widened_words[0..], capacity);
    const widened_cpus = cpumask_view.CpuMaskView.init(widened_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 4), noisy_bitmap.countSetBits());
    try std.testing.expectEqual(noisy_bitmap.countSetBits(), noisy_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, last_valid), noisy_bitmap.nextSetBit(word_bits + 1));
    try std.testing.expectEqual(noisy_bitmap.nextSetBit(word_bits + 1), noisy_cpus.nextCpu(word_bits + 1));
    try std.testing.expectEqual(@as(?usize, null), noisy_bitmap.nextSetBit(last_valid + 1));
    try std.testing.expectEqual(noisy_bitmap.nextSetBit(last_valid + 1), noisy_cpus.nextCpu(last_valid + 1));

    try std.testing.expect(noisy_bitmap.isSubsetOf(widened_bitmap));
    try std.testing.expect(noisy_cpus.isSubsetOf(widened_cpus));
    try std.testing.expect(!widened_bitmap.isSubsetOf(noisy_bitmap));
    try std.testing.expect(!widened_cpus.isSubsetOf(noisy_cpus));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), noisy_bitmap.nextClearBit(word_bits));
    try std.testing.expectEqual(noisy_bitmap.nextClearBit(word_bits), noisy_cpus.nextMissingCpu(word_bits));
}
