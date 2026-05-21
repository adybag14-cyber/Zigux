const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

test "bitmap and cpumask stay aligned across split clusters and tail noise" {
    const bit_len = word_bits + 10;
    const words = [_]Word{
        bit(0) | bit(1) | bit(2) | bit(6) | bit(word_bits - 1),
        bit(word_bits + 1) | bit(word_bits + 4) | bit(word_bits + 9) | bit(word_bits + 10) | bit(word_bits + 21),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try std.testing.expectEqual(@as(usize, 8), bitmap.countSetBits());
    try std.testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 3), bitmap.firstClearBit());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try std.testing.expect(bitmap.isSet(word_bits - 1));
    try std.testing.expect(bitmap.isSet(word_bits + 9));
    try std.testing.expect(cpumask.hasCpu(word_bits - 1));
    try std.testing.expect(cpumask.hasCpu(word_bits + 9));
    try std.testing.expect(!bitmap.isSet(5));
    try std.testing.expect(!cpumask.hasCpu(5));
}

test "cpumask subset and disjoint checks stay bounded inside the split cluster window" {
    const bit_len = word_bits + 10;
    const base_words = [_]Word{
        bit(0) | bit(1) | bit(2) | bit(6) | bit(word_bits - 1),
        bit(word_bits + 1) | bit(word_bits + 4) | bit(word_bits + 9) | bit(word_bits + 12),
    };
    const peer_words = [_]Word{
        bit(1) | bit(2) | bit(word_bits - 1),
        bit(word_bits + 4) | bit(word_bits + 9) | bit(word_bits + 18),
    };
    const hole_words = [_]Word{
        bit(6),
        bit(word_bits + 1) | bit(word_bits + 19),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], bit_len);
    const peer = cpumask_view.CpuMaskView.init(peer_words[0..], bit_len);
    const hole = cpumask_view.CpuMaskView.init(hole_words[0..], bit_len);

    try std.testing.expect(peer.isSubsetOf(base));
    try std.testing.expect(hole.isSubsetOf(base));
    try std.testing.expect(base.intersects(peer));
    try std.testing.expect(base.intersects(hole));
    try std.testing.expect(!peer.intersects(hole));
}

test "full-window bitmap and cpumask keep the split-cluster peers bounded" {
    const bit_len = word_bits + 10;
    const full_words = [_]Word{
        std.math.maxInt(Word),
        std.math.maxInt(Word),
    };
    const peer_words = [_]Word{
        bit(1) | bit(2) | bit(word_bits - 1),
        bit(word_bits + 4) | bit(word_bits + 9) | bit(word_bits + 25),
    };
    const hole_words = [_]Word{
        bit(6),
        bit(word_bits + 1) | bit(word_bits + 14),
    };

    const bitmap = bitmap_view.BitmapView.init(full_words[0..], bit_len);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], bit_len);
    const peer = cpumask_view.CpuMaskView.init(peer_words[0..], bit_len);
    const hole = cpumask_view.CpuMaskView.init(hole_words[0..], bit_len);

    try std.testing.expectEqual(bit_len, bitmap.countSetBits());
    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, null), bitmap.firstClearBit());
    try std.testing.expectEqual(bit_len, full.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, 0), full.firstCpu());
    try std.testing.expectEqual(@as(?usize, null), full.firstMissingCpu());
    try std.testing.expect(peer.isSubsetOf(full));
    try std.testing.expect(hole.isSubsetOf(full));
}
