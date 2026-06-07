const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const bit_len = word_bits * 3 + 11;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn setBit(words: []Word, bit_index: usize) void {
    words[bit_index / word_bits] |= bit(bit_index);
}

fn clearBit(words: []Word, bit_index: usize) void {
    words[bit_index / word_bits] &= ~bit(bit_index);
}

fn view(words: []const Word) bitmap_view.BitmapView {
    return bitmap_view.BitmapView.init(words, bit_len);
}

fn mask(words: []const Word) cpumask_view.CpuMaskView {
    return cpumask_view.CpuMaskView.init(words, bit_len);
}

fn expectMirrors(words: []const Word) !void {
    const bitmap = view(words);
    const cpumask = mask(words);

    try std.testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    const starts = [_]usize{
        0,
        1,
        word_bits - 3,
        word_bits,
        word_bits + 6,
        word_bits * 2 - 1,
        word_bits * 2,
        word_bits * 3,
        bit_len - 1,
        bit_len,
    };

    for (starts) |start| {
        try std.testing.expectEqual(bitmap.nextSetBit(start), cpumask.nextCpu(start));
        try std.testing.expectEqual(bitmap.nextClearBit(start), cpumask.nextMissingCpu(start));
    }
}

test "interleaved quorum lanes survive merge and tail masking" {
    var odd_words = [_]Word{ 0, 0, 0, 0 };
    var even_words = [_]Word{ 0, 0, 0, 0 };
    var quorum_words = [_]Word{ 0, 0, 0, 0 };
    var tail_noise_words = [_]Word{ 0, 0, 0, 0 };

    const odd_lanes = [_]usize{
        1,
        5,
        word_bits + 7,
        word_bits + 15,
        word_bits * 2 + 21,
        word_bits * 3 + 3,
    };
    const even_lanes = [_]usize{
        2,
        6,
        word_bits + 8,
        word_bits + 16,
        word_bits * 2 + 22,
        word_bits * 3 + 4,
    };

    for (odd_lanes) |index| {
        setBit(odd_words[0..], index);
        setBit(quorum_words[0..], index);
    }
    for (even_lanes) |index| {
        setBit(even_words[0..], index);
        setBit(quorum_words[0..], index);
    }

    @memcpy(tail_noise_words[0..], quorum_words[0..]);
    setBit(tail_noise_words[0..], bit_len + 5);
    setBit(tail_noise_words[0..], bit_len + 9);

    try expectMirrors(odd_words[0..]);
    try expectMirrors(even_words[0..]);
    try expectMirrors(quorum_words[0..]);
    try expectMirrors(tail_noise_words[0..]);

    const odd_bitmap = view(odd_words[0..]);
    const even_bitmap = view(even_words[0..]);
    const quorum_bitmap = view(quorum_words[0..]);
    const noise_bitmap = view(tail_noise_words[0..]);
    const odd_mask = mask(odd_words[0..]);
    const even_mask = mask(even_words[0..]);
    const quorum_mask = mask(quorum_words[0..]);
    const noise_mask = mask(tail_noise_words[0..]);

    try std.testing.expectEqual(@as(usize, 6), odd_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 6), even_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 6), even_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 12), quorum_bitmap.countSetBits());
    try std.testing.expectEqual(quorum_bitmap.countSetBits(), noise_bitmap.countSetBits());

    try std.testing.expect(odd_bitmap.isSubsetOf(quorum_bitmap));
    try std.testing.expect(even_mask.isSubsetOf(quorum_mask));
    try std.testing.expect(!quorum_bitmap.isSubsetOf(odd_bitmap));
    try std.testing.expect(!odd_mask.intersects(even_mask));
    try std.testing.expect(quorum_mask.intersects(odd_mask));
    try std.testing.expect(quorum_bitmap.isSubsetOf(noise_bitmap));
    try std.testing.expect(noise_mask.isSubsetOf(quorum_mask));

    try std.testing.expect(odd_mask.hasCpu(word_bits * 3 + 3));
    try std.testing.expect(!odd_mask.hasCpu(word_bits * 3 + 4));
    try std.testing.expect(even_mask.hasCpu(word_bits * 3 + 4));
    try std.testing.expectEqual(@as(?usize, 1), quorum_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 0), quorum_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 4), quorum_mask.nextCpu(word_bits * 3 + 4));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 5), quorum_mask.nextMissingCpu(word_bits * 3 + 4));
}

test "interleaved quorum loss and recovery preserve relation mirrors" {
    var full_words = [_]Word{ 0, 0, 0, 0 };
    var loss_words = [_]Word{ 0, 0, 0, 0 };
    var recovery_words = [_]Word{ 0, 0, 0, 0 };
    var sentinel_words = [_]Word{ 0, 0, 0, 0 };

    const quorum = [_]usize{
        1,
        2,
        5,
        6,
        word_bits + 7,
        word_bits + 8,
        word_bits + 15,
        word_bits + 16,
        word_bits * 2 + 21,
        word_bits * 2 + 22,
        word_bits * 3 + 3,
        word_bits * 3 + 4,
    };

    for (quorum) |index| {
        setBit(full_words[0..], index);
    }
    @memcpy(loss_words[0..], full_words[0..]);
    @memcpy(recovery_words[0..], full_words[0..]);
    @memcpy(sentinel_words[0..], full_words[0..]);

    clearBit(loss_words[0..], word_bits + 16);
    clearBit(loss_words[0..], word_bits * 3 + 3);
    setBit(recovery_words[0..], word_bits * 3 + 7);
    setBit(sentinel_words[0..], word_bits * 3 + 9);

    try expectMirrors(loss_words[0..]);
    try expectMirrors(recovery_words[0..]);
    try expectMirrors(sentinel_words[0..]);

    const full_bitmap = view(full_words[0..]);
    const loss_bitmap = view(loss_words[0..]);
    const recovery_bitmap = view(recovery_words[0..]);
    const sentinel_bitmap = view(sentinel_words[0..]);
    const full_mask = mask(full_words[0..]);
    const loss_mask = mask(loss_words[0..]);
    const recovery_mask = mask(recovery_words[0..]);
    const sentinel_mask = mask(sentinel_words[0..]);

    try std.testing.expectEqual(@as(usize, 10), loss_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 13), recovery_mask.countPresentCpus());
    try std.testing.expect(loss_bitmap.isSubsetOf(full_bitmap));
    try std.testing.expect(!full_mask.isSubsetOf(loss_mask));
    try std.testing.expect(full_bitmap.isSubsetOf(recovery_bitmap));
    try std.testing.expect(!recovery_mask.isSubsetOf(full_mask));
    try std.testing.expect(recovery_bitmap.intersects(sentinel_bitmap));
    try std.testing.expect(sentinel_mask.intersects(loss_mask));

    try std.testing.expectEqual(@as(?usize, word_bits + 16), loss_mask.nextMissingCpu(word_bits + 16));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 7), recovery_mask.nextCpu(word_bits * 3 + 5));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 9), sentinel_mask.nextCpu(word_bits * 3 + 8));
    try std.testing.expectEqual(@as(?usize, null), sentinel_mask.nextCpu(bit_len));
}
