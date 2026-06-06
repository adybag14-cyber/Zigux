const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn collectSetBits(view: bitmap_view.BitmapView, out: []usize) []usize {
    var count: usize = 0;
    var cursor = view.firstSetBit();
    while (cursor) |index| {
        out[count] = index;
        count += 1;
        cursor = view.nextSetBit(index + 1);
    }
    return out[0..count];
}

fn expectCpuMaskMirrorsBitmap(bitmap: bitmap_view.BitmapView, cpumask: cpumask_view.CpuMaskView) !void {
    try std.testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    for (0..bitmap.bit_len) |index| {
        try std.testing.expectEqual(bitmap.isSet(index), cpumask.hasCpu(index));
        try std.testing.expectEqual(bitmap.nextSetBit(index), cpumask.nextCpu(index));
        try std.testing.expectEqual(bitmap.nextClearBit(index), cpumask.nextMissingCpu(index));
    }
}

test "bitmap and cpumask agree on symmetric difference partitions" {
    const bit_len = word_bits * 2 + 9;
    const tail_noise: Word = ~((@as(Word, 1) << 9) - 1);
    const left_words = [_]Word{
        bit(0) | bit(3) | bit(7) | bit(13),
        bit(word_bits + 2) | bit(word_bits + 6) | bit(word_bits + 10),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 7) | tail_noise,
    };
    const right_words = [_]Word{
        bit(3) | bit(5) | bit(7) | bit(12),
        bit(word_bits + 6) | bit(word_bits + 11) | bit(word_bits + 15),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 8) | tail_noise,
    };

    var left_only_words: [3]Word = undefined;
    var right_only_words: [3]Word = undefined;
    var either_only_words: [3]Word = undefined;
    var shared_words: [3]Word = undefined;
    var recombined_words: [3]Word = undefined;

    for (0..left_only_words.len) |index| {
        left_only_words[index] = left_words[index] & ~right_words[index];
        right_only_words[index] = right_words[index] & ~left_words[index];
        either_only_words[index] = left_words[index] ^ right_words[index];
        shared_words[index] = left_words[index] & right_words[index];
        recombined_words[index] = either_only_words[index] | shared_words[index];
    }

    const left = bitmap_view.BitmapView.init(left_words[0..], bit_len);
    const right = bitmap_view.BitmapView.init(right_words[0..], bit_len);
    const left_only = bitmap_view.BitmapView.init(left_only_words[0..], bit_len);
    const right_only = bitmap_view.BitmapView.init(right_only_words[0..], bit_len);
    const either_only = bitmap_view.BitmapView.init(either_only_words[0..], bit_len);
    const shared = bitmap_view.BitmapView.init(shared_words[0..], bit_len);
    const recombined = bitmap_view.BitmapView.init(recombined_words[0..], bit_len);

    const either_cpu = cpumask_view.CpuMaskView.init(either_only_words[0..], bit_len);
    const shared_cpu = cpumask_view.CpuMaskView.init(shared_words[0..], bit_len);

    try expectCpuMaskMirrorsBitmap(either_only, either_cpu);
    try expectCpuMaskMirrorsBitmap(shared, shared_cpu);
    try std.testing.expect(left_only.isSubsetOf(left));
    try std.testing.expect(right_only.isSubsetOf(right));
    try std.testing.expect(!left_only.intersects(right));
    try std.testing.expect(!right_only.intersects(left));
    try std.testing.expect(!either_only.intersects(shared));
    try std.testing.expect(either_only.intersects(left));
    try std.testing.expect(either_only.intersects(right));

    try std.testing.expectEqual(left.countSetBits() + right.countSetBits() - shared.countSetBits(), recombined.countSetBits());
    try std.testing.expectEqual(@as(usize, 10), either_only.countSetBits());
    try std.testing.expectEqual(@as(usize, 4), shared.countSetBits());

    var seen: [16]usize = undefined;
    try std.testing.expectEqualSlices(
        usize,
        &[_]usize{ 0, 5, 12, 13, word_bits + 2, word_bits + 10, word_bits + 11, word_bits + 15, word_bits * 2 + 7, word_bits * 2 + 8 },
        collectSetBits(either_only, seen[0..]),
    );
}

test "symmetric difference cursors react to shared-bit mutation" {
    const bit_len = word_bits + 6;
    const tail_noise: Word = ~((@as(Word, 1) << 6) - 1);
    var left_words = [_]Word{ bit(1) | bit(4), bit(2) | bit(5) | tail_noise };
    var right_words = [_]Word{ bit(4) | bit(9), bit(2) | tail_noise };
    var symmetric_words: [2]Word = undefined;

    for (0..symmetric_words.len) |index| {
        symmetric_words[index] = left_words[index] ^ right_words[index];
    }

    var symmetric = bitmap_view.BitmapView.init(symmetric_words[0..], bit_len);
    var symmetric_cpu = cpumask_view.CpuMaskView.init(symmetric_words[0..], bit_len);
    try expectCpuMaskMirrorsBitmap(symmetric, symmetric_cpu);
    try std.testing.expectEqual(@as(?usize, 1), symmetric.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 9), symmetric.nextSetBit(2));
    try std.testing.expectEqual(@as(?usize, word_bits + 5), symmetric.nextSetBit(word_bits + 3));
    try std.testing.expect(!symmetric.isSet(4));
    try std.testing.expect(!symmetric.isSet(word_bits + 2));

    right_words[0] ^= bit(1);
    left_words[1] ^= bit(2);
    for (0..symmetric_words.len) |index| {
        symmetric_words[index] = left_words[index] ^ right_words[index];
    }

    symmetric = bitmap_view.BitmapView.init(symmetric_words[0..], bit_len);
    symmetric_cpu = cpumask_view.CpuMaskView.init(symmetric_words[0..], bit_len);
    try expectCpuMaskMirrorsBitmap(symmetric, symmetric_cpu);
    try std.testing.expect(!symmetric.isSet(1));
    try std.testing.expect(symmetric.isSet(word_bits + 2));
    try std.testing.expectEqual(@as(?usize, 9), symmetric.firstSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits + 2), symmetric.nextSetBit(10));
}
