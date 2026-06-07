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

test "phase3 bitmap cpumask shift lattice mirrors staged projections" {
    const bit_len = word_bits * 2 + 11;

    const low: Word = bit(1) | bit(5) | bit(9);
    const shifted_low: Word = bit(4) | bit(8) | bit(12);
    const bridge: Word = bit(word_bits - 2) | bit(word_bits - 1);
    const mid: Word = bit(2) | bit(6) | bit(10);
    const shifted_mid: Word = bit(5) | bit(9) | bit(13);
    const high: Word = bit(1) | bit(7);
    const shifted_high: Word = bit(4) | bit(10);
    const tail_noise: Word = bit(11) | bit(13) | bit(17);

    const lattice_words = [_]Word{
        low | bridge,
        mid,
        high | tail_noise,
    };
    const shifted_words = [_]Word{
        shifted_low | bridge,
        shifted_mid,
        shifted_high | tail_noise,
    };
    const bridge_words = [_]Word{
        bridge,
        bit(6),
        tail_noise,
    };
    const disjoint_words = [_]Word{
        bit(14),
        bit(15),
        bit(3),
    };

    const lattice = bitmap_view.BitmapView.init(lattice_words[0..], bit_len);
    const shifted = bitmap_view.BitmapView.init(shifted_words[0..], bit_len);
    const bridge_only = bitmap_view.BitmapView.init(bridge_words[0..], bit_len);
    const disjoint = bitmap_view.BitmapView.init(disjoint_words[0..], bit_len);

    const lattice_cpus = cpumask_view.CpuMaskView.init(lattice_words[0..], bit_len);
    const shifted_cpus = cpumask_view.CpuMaskView.init(shifted_words[0..], bit_len);
    const bridge_cpus = cpumask_view.CpuMaskView.init(bridge_words[0..], bit_len);
    const disjoint_cpus = cpumask_view.CpuMaskView.init(disjoint_words[0..], bit_len);

    try expectBitmapCpuMirror(lattice_words[0..], bit_len, 10, 1, 0);
    try expectBitmapCpuMirror(shifted_words[0..], bit_len, 10, 4, 0);
    try expectBitmapCpuMirror(bridge_words[0..], bit_len, 3, word_bits - 2, 0);

    try std.testing.expect(bridge_only.isSubsetOf(lattice));
    try std.testing.expect(bridge_cpus.isSubsetOf(lattice_cpus));
    try std.testing.expect(bridge_only.intersects(shifted));
    try std.testing.expect(bridge_cpus.intersects(shifted_cpus));
    try std.testing.expect(!lattice.isSubsetOf(shifted));
    try std.testing.expect(!lattice_cpus.isSubsetOf(shifted_cpus));
    try std.testing.expect(!lattice.intersects(disjoint));
    try std.testing.expect(!lattice_cpus.intersects(disjoint_cpus));

    try std.testing.expectEqual(@as(?usize, word_bits - 2), lattice.nextSetBit(word_bits - 4));
    try std.testing.expectEqual(@as(?usize, word_bits - 2), lattice_cpus.nextCpu(word_bits - 4));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), lattice.nextSetBit(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), lattice_cpus.nextCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 1), lattice.nextSetBit(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 1), lattice_cpus.nextCpu(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 7), lattice.nextSetBit(word_bits * 2 + 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 7), lattice_cpus.nextCpu(word_bits * 2 + 2));

    try std.testing.expectEqual(@as(?usize, null), lattice.nextSetBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), lattice_cpus.nextCpu(bit_len));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), lattice.nextClearBit(word_bits * 2 + 8));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), lattice_cpus.nextMissingCpu(word_bits * 2 + 8));
}

test "phase3 bitmap cpumask shift lattice recomputes after bridge removal" {
    const bit_len = word_bits + 29;
    const before_words = [_]Word{
        bit(2) | bit(6) | bit(word_bits - 1),
        bit(1) |
            bit(6) |
            bit(18) |
            bit(24),
    };
    const after_words = [_]Word{
        bit(5) | bit(9),
        bit(4) |
            bit(9) |
            bit(18) |
            bit(21) |
            bit(26),
    };
    const anchor_words = [_]Word{
        0,
        bit(18) |
            bit(23) |
            bit(27),
    };

    const before = bitmap_view.BitmapView.init(before_words[0..], bit_len);
    const after = bitmap_view.BitmapView.init(after_words[0..], bit_len);
    const anchor = bitmap_view.BitmapView.init(anchor_words[0..], bit_len);
    const before_cpus = cpumask_view.CpuMaskView.init(before_words[0..], bit_len);
    const after_cpus = cpumask_view.CpuMaskView.init(after_words[0..], bit_len);
    const anchor_cpus = cpumask_view.CpuMaskView.init(anchor_words[0..], bit_len);

    try expectBitmapCpuMirror(before_words[0..], bit_len, 7, 2, 0);
    try expectBitmapCpuMirror(after_words[0..], bit_len, 7, 5, 0);

    try std.testing.expect(before.intersects(after));
    try std.testing.expect(before_cpus.intersects(after_cpus));
    try std.testing.expect(anchor.intersects(after));
    try std.testing.expect(anchor_cpus.intersects(after_cpus));
    try std.testing.expect(!anchor.isSubsetOf(after));
    try std.testing.expect(!anchor_cpus.isSubsetOf(after_cpus));
    try std.testing.expect(!after.isSubsetOf(before));
    try std.testing.expect(!after_cpus.isSubsetOf(before_cpus));

    try std.testing.expectEqual(@as(?usize, word_bits + 18), after.nextSetBit(word_bits + 10));
    try std.testing.expectEqual(@as(?usize, word_bits + 18), after_cpus.nextCpu(word_bits + 10));
    try std.testing.expectEqual(@as(?usize, null), after.nextSetBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), after_cpus.nextCpu(bit_len));
}
