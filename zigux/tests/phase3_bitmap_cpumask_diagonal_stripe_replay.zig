const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn expectBitmapCpuMirror(words: []const Word, bit_len: usize, expected_count: usize, first_set: ?usize, first_clear: ?usize) !void {
    const bitmap = bitmap_view.BitmapView.init(words, bit_len);
    const cpus = cpumask_view.CpuMaskView.init(words, bit_len);

    try std.testing.expectEqual(expected_count, bitmap.countSetBits());
    try std.testing.expectEqual(expected_count, cpus.countPresentCpus());
    try std.testing.expectEqual(first_set, bitmap.firstSetBit());
    try std.testing.expectEqual(first_set, cpus.firstCpu());
    try std.testing.expectEqual(first_clear, bitmap.firstClearBit());
    try std.testing.expectEqual(first_clear, cpus.firstMissingCpu());

    var cursor: usize = 0;
    while (cursor < bit_len) : (cursor += 1) {
        try std.testing.expectEqual(bitmap.nextSetBit(cursor), cpus.nextCpu(cursor));
        try std.testing.expectEqual(bitmap.nextClearBit(cursor), cpus.nextMissingCpu(cursor));
        try std.testing.expectEqual(bitmap.isSet(cursor), cpus.hasCpu(cursor));
    }
}

test "phase3 bitmap cpumask diagonal stripe mirrors stripe promotion" {
    const bit_len = word_bits * 3 + 17;

    const stripe_a_words = [_]Word{
        bit(0) | bit(9) | bit(18) | bit(word_bits - 1),
        bit(7) | bit(16) | bit(25),
        bit(5) | bit(14) | bit(23),
        bit(3) | bit(12) | bit(17) | bit(28) | bit(35),
    };
    const stripe_b_words = [_]Word{
        bit(4) | bit(13) | bit(22),
        bit(2) | bit(11) | bit(20) | bit(word_bits - 1),
        bit(0) | bit(9) | bit(18),
        bit(7) | bit(16) | bit(22) | bit(31),
    };
    const promoted_words = [_]Word{
        bit(0) | bit(4) | bit(9) | bit(13) | bit(18) | bit(22) | bit(word_bits - 1),
        bit(2) | bit(7) | bit(11) | bit(16) | bit(20) | bit(25) | bit(word_bits - 1),
        bit(0) | bit(5) | bit(9) | bit(14) | bit(18) | bit(23),
        bit(3) | bit(7) | bit(12) | bit(16) | bit(17) | bit(22) | bit(28) | bit(35),
    };
    const shared_anchor_words = [_]Word{
        bit(0) | bit(22),
        bit(20),
        bit(23),
        bit(16) | bit(40),
    };
    const disjoint_words = [_]Word{
        bit(31),
        bit(31),
        bit(31),
        bit(1) | bit(33),
    };

    const stripe_a = bitmap_view.BitmapView.init(stripe_a_words[0..], bit_len);
    const stripe_b = bitmap_view.BitmapView.init(stripe_b_words[0..], bit_len);
    const promoted = bitmap_view.BitmapView.init(promoted_words[0..], bit_len);
    const shared_anchor = bitmap_view.BitmapView.init(shared_anchor_words[0..], bit_len);
    const disjoint = bitmap_view.BitmapView.init(disjoint_words[0..], bit_len);

    const stripe_a_cpus = cpumask_view.CpuMaskView.init(stripe_a_words[0..], bit_len);
    const stripe_b_cpus = cpumask_view.CpuMaskView.init(stripe_b_words[0..], bit_len);
    const promoted_cpus = cpumask_view.CpuMaskView.init(promoted_words[0..], bit_len);
    const shared_anchor_cpus = cpumask_view.CpuMaskView.init(shared_anchor_words[0..], bit_len);
    const disjoint_cpus = cpumask_view.CpuMaskView.init(disjoint_words[0..], bit_len);

    try expectBitmapCpuMirror(stripe_a_words[0..], bit_len, 12, 0, 1);
    try expectBitmapCpuMirror(stripe_b_words[0..], bit_len, 12, 4, 0);
    try expectBitmapCpuMirror(promoted_words[0..], bit_len, 24, 0, 1);

    try std.testing.expect(stripe_a.isSubsetOf(promoted));
    try std.testing.expect(stripe_a_cpus.isSubsetOf(promoted_cpus));
    try std.testing.expect(stripe_b.isSubsetOf(promoted));
    try std.testing.expect(stripe_b_cpus.isSubsetOf(promoted_cpus));
    try std.testing.expect(shared_anchor.isSubsetOf(promoted));
    try std.testing.expect(shared_anchor_cpus.isSubsetOf(promoted_cpus));
    try std.testing.expect(stripe_a.intersects(shared_anchor));
    try std.testing.expect(stripe_a_cpus.intersects(shared_anchor_cpus));
    try std.testing.expect(stripe_b.intersects(shared_anchor));
    try std.testing.expect(stripe_b_cpus.intersects(shared_anchor_cpus));
    try std.testing.expect(!promoted.intersects(disjoint));
    try std.testing.expect(!promoted_cpus.intersects(disjoint_cpus));

    try std.testing.expectEqual(@as(?usize, word_bits - 1), promoted.nextSetBit(word_bits - 2));
    try std.testing.expectEqual(@as(?usize, word_bits - 1), promoted_cpus.nextCpu(word_bits - 2));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), promoted.nextSetBit(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), promoted_cpus.nextCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits * 2), promoted.nextSetBit(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2), promoted_cpus.nextCpu(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 16), promoted.nextSetBit(word_bits * 3 + 13));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 16), promoted_cpus.nextCpu(word_bits * 3 + 13));
    try std.testing.expectEqual(@as(?usize, null), promoted.nextSetBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), promoted_cpus.nextCpu(bit_len));
}

test "phase3 bitmap cpumask diagonal stripe clips declared tail noise" {
    const bit_len = word_bits * 2 + 9;

    const active_words = [_]Word{
        bit(6) | bit(15) | bit(24) | bit(33),
        bit(3) | bit(12) | bit(21) | bit(30),
        bit(0) | bit(8) | bit(9) | bit(18) | bit(27),
    };
    const narrowed_words = [_]Word{
        bit(15) | bit(24),
        bit(12) | bit(21),
        bit(8) | bit(9) | bit(18) | bit(27),
    };
    const high_noise_words = [_]Word{
        bit(6) | bit(15) | bit(24) | bit(33),
        bit(3) | bit(12) | bit(21) | bit(30),
        bit(0) | bit(8) | bit(10) | bit(11) | bit(50),
    };

    const active = bitmap_view.BitmapView.init(active_words[0..], bit_len);
    const narrowed = bitmap_view.BitmapView.init(narrowed_words[0..], bit_len);
    const high_noise = bitmap_view.BitmapView.init(high_noise_words[0..], bit_len);
    const active_cpus = cpumask_view.CpuMaskView.init(active_words[0..], bit_len);
    const narrowed_cpus = cpumask_view.CpuMaskView.init(narrowed_words[0..], bit_len);
    const high_noise_cpus = cpumask_view.CpuMaskView.init(high_noise_words[0..], bit_len);

    try expectBitmapCpuMirror(active_words[0..], bit_len, 10, 6, 0);
    try expectBitmapCpuMirror(narrowed_words[0..], bit_len, 5, 15, 0);
    try expectBitmapCpuMirror(high_noise_words[0..], bit_len, 10, 6, 0);

    try std.testing.expect(narrowed.isSubsetOf(active));
    try std.testing.expect(narrowed_cpus.isSubsetOf(active_cpus));
    try std.testing.expect(active.intersects(high_noise));
    try std.testing.expect(active_cpus.intersects(high_noise_cpus));
    try std.testing.expect(!active.isSubsetOf(narrowed));
    try std.testing.expect(!active_cpus.isSubsetOf(narrowed_cpus));

    try std.testing.expectEqual(@as(?usize, word_bits * 2), active.nextSetBit(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2), active_cpus.nextCpu(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), active.nextSetBit(word_bits * 2 + 1));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), active_cpus.nextCpu(word_bits * 2 + 1));
    try std.testing.expectEqual(@as(?usize, null), active.nextSetBit(word_bits * 2 + 9));
    try std.testing.expectEqual(@as(?usize, null), active_cpus.nextCpu(word_bits * 2 + 9));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 1), high_noise.nextClearBit(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 1), high_noise_cpus.nextMissingCpu(word_bits * 2));
}
