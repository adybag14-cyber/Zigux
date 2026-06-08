const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn tailNoiseFrom(comptime first_invalid_tail_bit: usize) Word {
    return ~((@as(Word, 1) << @as(std.math.Log2Int(Word), @intCast(first_invalid_tail_bit))) - 1);
}

fn expectBitmapCpuAgreement(words: []const Word, bit_len: usize) !void {
    const bitmap = BitmapView.init(words, bit_len);
    const cpumask = CpuMaskView.init(words, bit_len);

    try std.testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try std.testing.expectEqual(bitmap.lastSetBit(), cpumask.lastCpu());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try std.testing.expectEqual(bitmap.lastClearBit(), cpumask.lastMissingCpu());

    var cursor: usize = 0;
    while (cursor <= bit_len) : (cursor += 11) {
        try std.testing.expectEqual(bitmap.nextSetBit(cursor), cpumask.nextCpu(cursor));
        try std.testing.expectEqual(bitmap.nextClearBit(cursor), cpumask.nextMissingCpu(cursor));
    }
}

fn expectHasCpus(words: []const Word, bit_len: usize, cpus: []const usize) !void {
    const bitmap = BitmapView.init(words, bit_len);
    const cpumask = CpuMaskView.init(words, bit_len);

    for (cpus) |cpu| {
        try std.testing.expect(bitmap.isSet(cpu));
        try std.testing.expect(cpumask.hasCpu(cpu));
    }
}

test "bitmap and cpumask views agree across a zipper bridge" {
    const capacity = word_bits * 2 + 9;
    const left_words = [_]Word{
        bit(2) | bit(10) | bit(18) | bit(26) | bit(word_bits - 1),
        bit(word_bits + 3) | bit(word_bits + 11) | bit(word_bits + 19) | bit(word_bits + 27),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 7),
    };
    const right_words = [_]Word{
        bit(5) | bit(13) | bit(21) | bit(29),
        bit(word_bits + 6) | bit(word_bits + 14) | bit(word_bits + 22) | bit(word_bits + 30),
        bit(word_bits * 2 + 3) | bit(word_bits * 2 + 8),
    };
    const zipper_words = [_]Word{
        left_words[0] | right_words[0],
        left_words[1] | right_words[1],
        left_words[2] | right_words[2],
    };
    const outside_words = [_]Word{
        bit(0),
        bit(word_bits + 2),
        bit(word_bits * 2 + 5),
    };

    const left = BitmapView.init(left_words[0..], capacity);
    const right = BitmapView.init(right_words[0..], capacity);
    const zipper = BitmapView.init(zipper_words[0..], capacity);
    const outside = BitmapView.init(outside_words[0..], capacity);
    const cpu_left = CpuMaskView.init(left_words[0..], capacity);
    const cpu_right = CpuMaskView.init(right_words[0..], capacity);
    const cpu_zipper = CpuMaskView.init(zipper_words[0..], capacity);
    const cpu_outside = CpuMaskView.init(outside_words[0..], capacity);

    try std.testing.expect(left.isSubsetOf(zipper));
    try std.testing.expect(right.isSubsetOf(zipper));
    try std.testing.expect(!zipper.isSubsetOf(left));
    try std.testing.expect(!zipper.isSubsetOf(right));
    try std.testing.expect(!left.intersects(right));
    try std.testing.expect(!zipper.intersects(outside));

    try std.testing.expect(cpu_left.isSubsetOf(cpu_zipper));
    try std.testing.expect(cpu_right.isSubsetOf(cpu_zipper));
    try std.testing.expect(!cpu_zipper.isSubsetOf(cpu_left));
    try std.testing.expect(!cpu_zipper.isSubsetOf(cpu_right));
    try std.testing.expect(!cpu_left.intersects(cpu_right));
    try std.testing.expect(!cpu_zipper.intersects(cpu_outside));

    try std.testing.expectEqual(@as(usize, 11), left.countSetBits());
    try std.testing.expectEqual(@as(usize, 10), right.countSetBits());
    try std.testing.expectEqual(@as(usize, 21), zipper.countSetBits());
    try std.testing.expectEqual(@as(?usize, 2), zipper.firstSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), zipper.lastSetBit());
    try std.testing.expectEqual(@as(?usize, 0), zipper.firstClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 6), zipper.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits + 27), zipper.nextSetBit(word_bits + 23));
    try std.testing.expectEqual(@as(?usize, null), zipper.nextClearBit(capacity - 1));

    try expectBitmapCpuAgreement(zipper_words[0..], capacity);
    try expectHasCpus(zipper_words[0..], capacity, &.{
        2,
        word_bits - 1,
        word_bits + 30,
        word_bits * 2 + 8,
    });
}

test "zipper bridge masks noisy storage past declared cpu capacity" {
    const capacity = word_bits * 2 + 9;
    const clean_words = [_]Word{
        bit(1) | bit(9) | bit(17) | bit(25),
        bit(word_bits + 4) | bit(word_bits + 12) | bit(word_bits + 20) | bit(word_bits + 28),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 4) | bit(word_bits * 2 + 8),
    };
    const noisy_words = [_]Word{
        clean_words[0],
        clean_words[1],
        clean_words[2] | tailNoiseFrom(9),
    };
    const released_words = [_]Word{
        bit(9) | bit(25),
        bit(word_bits + 12) | bit(word_bits + 28),
        bit(word_bits * 2 + 8) | tailNoiseFrom(9),
    };

    const clean = BitmapView.init(clean_words[0..], capacity);
    const noisy = BitmapView.init(noisy_words[0..], capacity);
    const released = BitmapView.init(released_words[0..], capacity);
    const cpu_clean = CpuMaskView.init(clean_words[0..], capacity);
    const cpu_noisy = CpuMaskView.init(noisy_words[0..], capacity);
    const cpu_released = CpuMaskView.init(released_words[0..], capacity);

    try std.testing.expectEqual(clean.countSetBits(), noisy.countSetBits());
    try std.testing.expectEqual(clean.firstSetBit(), noisy.firstSetBit());
    try std.testing.expectEqual(clean.lastSetBit(), noisy.lastSetBit());
    try std.testing.expectEqual(clean.lastClearBit(), noisy.lastClearBit());
    try std.testing.expect(released.isSubsetOf(noisy));
    try std.testing.expect(!noisy.isSubsetOf(released));

    try std.testing.expectEqual(cpu_clean.countPresentCpus(), cpu_noisy.countPresentCpus());
    try std.testing.expectEqual(cpu_clean.firstCpu(), cpu_noisy.firstCpu());
    try std.testing.expectEqual(cpu_clean.lastCpu(), cpu_noisy.lastCpu());
    try std.testing.expectEqual(cpu_clean.lastMissingCpu(), cpu_noisy.lastMissingCpu());
    try std.testing.expect(cpu_released.isSubsetOf(cpu_noisy));
    try std.testing.expect(!cpu_noisy.isSubsetOf(cpu_released));

    try std.testing.expectEqual(@as(usize, 11), noisy.countSetBits());
    try std.testing.expectEqual(@as(usize, 5), released.countSetBits());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), noisy.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 7), noisy.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), released.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 7), cpu_released.lastMissingCpu());

    try expectBitmapCpuAgreement(noisy_words[0..], capacity);
    try expectBitmapCpuAgreement(released_words[0..], capacity);
}
