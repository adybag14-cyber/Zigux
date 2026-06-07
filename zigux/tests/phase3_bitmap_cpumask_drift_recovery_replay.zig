const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const bit_len = word_bits * 4 + 9;

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
        word_bits - 1,
        word_bits,
        word_bits + 3,
        word_bits * 2 - 2,
        word_bits * 2,
        word_bits * 3 + 5,
        word_bits * 4,
        bit_len - 1,
        bit_len,
    };

    for (starts) |start| {
        try std.testing.expectEqual(bitmap.nextSetBit(start), cpumask.nextCpu(start));
        try std.testing.expectEqual(bitmap.nextClearBit(start), cpumask.nextMissingCpu(start));
    }
}

test "drift recovery preserves bitmap and cpumask mirrors across staged edits" {
    var anchor_words = [_]Word{ 0, 0, 0, 0, 0 };
    var drift_words = [_]Word{ 0, 0, 0, 0, 0 };
    var recovered_words = [_]Word{ 0, 0, 0, 0, 0 };
    var noisy_recovered_words = [_]Word{ 0, 0, 0, 0, 0 };

    const anchors = [_]usize{
        0,
        3,
        word_bits - 1,
        word_bits,
        word_bits + 2,
        word_bits * 2 + 7,
        word_bits * 3 + 11,
        word_bits * 4 + 2,
    };
    for (anchors) |index| {
        setBit(anchor_words[0..], index);
    }

    @memcpy(drift_words[0..], anchor_words[0..]);
    @memcpy(recovered_words[0..], anchor_words[0..]);
    @memcpy(noisy_recovered_words[0..], anchor_words[0..]);

    clearBit(drift_words[0..], word_bits);
    clearBit(drift_words[0..], word_bits * 3 + 11);
    setBit(drift_words[0..], word_bits + 5);
    setBit(drift_words[0..], word_bits * 3 + 12);

    setBit(recovered_words[0..], word_bits * 4 + 6);
    setBit(noisy_recovered_words[0..], word_bits * 4 + 6);
    setBit(noisy_recovered_words[0..], bit_len + 3);
    setBit(noisy_recovered_words[0..], bit_len + 6);

    try expectMirrors(anchor_words[0..]);
    try expectMirrors(drift_words[0..]);
    try expectMirrors(recovered_words[0..]);
    try expectMirrors(noisy_recovered_words[0..]);

    const anchor_bitmap = view(anchor_words[0..]);
    const drift_bitmap = view(drift_words[0..]);
    const recovered_bitmap = view(recovered_words[0..]);
    const noisy_bitmap = view(noisy_recovered_words[0..]);
    const anchor_mask = mask(anchor_words[0..]);
    const drift_mask = mask(drift_words[0..]);
    const recovered_mask = mask(recovered_words[0..]);
    const noisy_mask = mask(noisy_recovered_words[0..]);

    try std.testing.expectEqual(@as(usize, 8), anchor_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 8), drift_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 9), recovered_bitmap.countSetBits());
    try std.testing.expectEqual(recovered_bitmap.countSetBits(), noisy_bitmap.countSetBits());

    try std.testing.expect(anchor_bitmap.intersects(drift_bitmap));
    try std.testing.expect(!anchor_bitmap.isSubsetOf(drift_bitmap));
    try std.testing.expect(!drift_mask.isSubsetOf(anchor_mask));
    try std.testing.expect(anchor_mask.isSubsetOf(recovered_mask));
    try std.testing.expect(recovered_bitmap.isSubsetOf(noisy_bitmap));
    try std.testing.expect(noisy_mask.isSubsetOf(recovered_mask));

    try std.testing.expect(anchor_mask.hasCpu(word_bits));
    try std.testing.expect(!drift_mask.hasCpu(word_bits));
    try std.testing.expect(drift_mask.hasCpu(word_bits + 5));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), drift_mask.nextCpu(word_bits + 1));
    try std.testing.expectEqual(@as(?usize, word_bits), drift_mask.nextMissingCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits * 4 + 6), recovered_mask.nextCpu(word_bits * 4 + 3));
    try std.testing.expectEqual(@as(?usize, null), noisy_mask.nextCpu(bit_len));
}

test "drift rollback keeps disjoint gaps and cross-word cursors stable" {
    var left_words = [_]Word{ 0, 0, 0, 0, 0 };
    var right_words = [_]Word{ 0, 0, 0, 0, 0 };
    var rollback_words = [_]Word{ 0, 0, 0, 0, 0 };
    var bridge_words = [_]Word{ 0, 0, 0, 0, 0 };

    const left = [_]usize{
        2,
        word_bits - 2,
        word_bits + 9,
        word_bits * 2 + 1,
        word_bits * 3 + 8,
    };
    const right = [_]usize{
        5,
        word_bits + 12,
        word_bits * 2 + 4,
        word_bits * 3 + 19,
        word_bits * 4 + 8,
    };

    for (left) |index| {
        setBit(left_words[0..], index);
        setBit(rollback_words[0..], index);
        setBit(bridge_words[0..], index);
    }
    for (right) |index| {
        setBit(right_words[0..], index);
        setBit(bridge_words[0..], index);
    }

    clearBit(rollback_words[0..], word_bits + 9);
    clearBit(rollback_words[0..], word_bits * 3 + 8);
    setBit(rollback_words[0..], word_bits + 10);
    setBit(rollback_words[0..], word_bits * 3 + 9);

    try expectMirrors(left_words[0..]);
    try expectMirrors(right_words[0..]);
    try expectMirrors(rollback_words[0..]);
    try expectMirrors(bridge_words[0..]);

    const left_bitmap = view(left_words[0..]);
    const right_bitmap = view(right_words[0..]);
    const rollback_bitmap = view(rollback_words[0..]);
    const bridge_bitmap = view(bridge_words[0..]);
    const left_mask = mask(left_words[0..]);
    const right_mask = mask(right_words[0..]);
    const rollback_mask = mask(rollback_words[0..]);
    const bridge_mask = mask(bridge_words[0..]);

    try std.testing.expectEqual(@as(usize, 5), left_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 5), right_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 10), bridge_bitmap.countSetBits());

    try std.testing.expect(!left_bitmap.intersects(right_bitmap));
    try std.testing.expect(left_mask.isSubsetOf(bridge_mask));
    try std.testing.expect(right_bitmap.isSubsetOf(bridge_bitmap));
    try std.testing.expect(!rollback_mask.isSubsetOf(left_mask));
    try std.testing.expect(!left_bitmap.isSubsetOf(rollback_bitmap));
    try std.testing.expect(rollback_bitmap.intersects(bridge_bitmap));

    try std.testing.expectEqual(@as(?usize, 5), right_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 0), bridge_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits + 10), rollback_mask.nextCpu(word_bits + 10));
    try std.testing.expectEqual(@as(?usize, word_bits + 8), rollback_mask.nextMissingCpu(word_bits + 8));
    try std.testing.expectEqual(@as(?usize, word_bits * 4 + 8), bridge_mask.nextCpu(word_bits * 4));
}
