const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const bit_len = word_bits + 19;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn setBit(words: []Word, index: usize) void {
    words[index / word_bits] |= bit(index);
}

fn clearBit(words: []Word, index: usize) void {
    words[index / word_bits] &= ~bit(index);
}

fn makeWords(indices: []const usize, tail_noise: Word) [2]Word {
    var words = [_]Word{ 0, tail_noise };
    for (indices) |index| {
        setBit(words[0..], index);
    }
    return words;
}

fn maskByRange(source: [2]Word, start: usize, end: usize) [2]Word {
    var out = [_]Word{ 0, 0 };
    var index = start;
    while (index < end) : (index += 1) {
        if ((source[index / word_bits] & bit(index)) != 0) {
            setBit(out[0..], index);
        }
    }
    return out;
}

fn mergeWords(left: [2]Word, right: [2]Word, tail_noise: Word) [2]Word {
    return .{
        left[0] | right[0],
        left[1] | right[1] | tail_noise,
    };
}

fn expectViewsAgree(words: [2]Word) !void {
    const bitmap = bitmap_view.BitmapView.init(words[0..], bit_len);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], bit_len);

    try std.testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    var cursor: usize = 0;
    while (cursor <= bit_len) : (cursor += 1) {
        try std.testing.expectEqual(bitmap.nextSetBit(cursor), cpumask.nextCpu(cursor));
        try std.testing.expectEqual(bitmap.nextClearBit(cursor), cpumask.nextMissingCpu(cursor));
    }
}

test "bitmap and cpumask preserve prefix suffix split and join" {
    const prefix_indices = [_]usize{ 0, 3, 8, 13, word_bits - 1 };
    const suffix_indices = [_]usize{ word_bits, word_bits + 4, word_bits + 9, word_bits + 18 };
    const tail_noise = bit(word_bits + 20) | bit(word_bits + 33);

    const base = makeWords(prefix_indices[0..] ++ suffix_indices[0..], tail_noise);
    const prefix = maskByRange(base, 0, word_bits);
    const suffix = maskByRange(base, word_bits, bit_len);
    const joined = mergeWords(prefix, suffix, tail_noise);

    const base_bitmap = bitmap_view.BitmapView.init(base[0..], bit_len);
    const prefix_bitmap = bitmap_view.BitmapView.init(prefix[0..], bit_len);
    const suffix_bitmap = bitmap_view.BitmapView.init(suffix[0..], bit_len);
    const joined_bitmap = bitmap_view.BitmapView.init(joined[0..], bit_len);

    const base_cpumask = cpumask_view.CpuMaskView.init(base[0..], bit_len);
    const prefix_cpumask = cpumask_view.CpuMaskView.init(prefix[0..], bit_len);
    const suffix_cpumask = cpumask_view.CpuMaskView.init(suffix[0..], bit_len);
    const joined_cpumask = cpumask_view.CpuMaskView.init(joined[0..], bit_len);

    try expectViewsAgree(base);
    try expectViewsAgree(prefix);
    try expectViewsAgree(suffix);
    try expectViewsAgree(joined);

    try std.testing.expect(prefix_bitmap.isSubsetOf(base_bitmap));
    try std.testing.expect(prefix_cpumask.isSubsetOf(base_cpumask));
    try std.testing.expect(suffix_bitmap.isSubsetOf(base_bitmap));
    try std.testing.expect(suffix_cpumask.isSubsetOf(base_cpumask));
    try std.testing.expect(!prefix_bitmap.intersects(suffix_bitmap));
    try std.testing.expect(!prefix_cpumask.intersects(suffix_cpumask));

    try std.testing.expectEqual(base_bitmap.countSetBits(), joined_bitmap.countSetBits());
    try std.testing.expectEqual(base_cpumask.countPresentCpus(), joined_cpumask.countPresentCpus());
    try std.testing.expectEqual(base_bitmap.nextSetBit(word_bits - 2), joined_bitmap.nextSetBit(word_bits - 2));
    try std.testing.expectEqual(base_cpumask.nextCpu(word_bits - 2), joined_cpumask.nextCpu(word_bits - 2));
    try std.testing.expectEqual(@as(?usize, null), joined_bitmap.nextSetBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), joined_cpumask.nextCpu(bit_len));
}

test "bitmap and cpumask update joined prefix suffix after boundary migration" {
    const indices = [_]usize{ 1, 6, 11, word_bits - 2, word_bits + 2, word_bits + 5, word_bits + 12 };
    var migrated = makeWords(indices[0..], bit(word_bits + 27));

    clearBit(migrated[0..], word_bits - 2);
    setBit(migrated[0..], word_bits - 1);
    clearBit(migrated[0..], word_bits + 2);
    setBit(migrated[0..], word_bits + 17);

    const prefix = maskByRange(migrated, 0, word_bits);
    const suffix = maskByRange(migrated, word_bits, bit_len);
    const rejoined = mergeWords(prefix, suffix, bit(word_bits + 40));

    const migrated_bitmap = bitmap_view.BitmapView.init(migrated[0..], bit_len);
    const rejoined_bitmap = bitmap_view.BitmapView.init(rejoined[0..], bit_len);
    const migrated_cpumask = cpumask_view.CpuMaskView.init(migrated[0..], bit_len);
    const rejoined_cpumask = cpumask_view.CpuMaskView.init(rejoined[0..], bit_len);

    try expectViewsAgree(migrated);
    try expectViewsAgree(rejoined);
    try std.testing.expectEqual(@as(?usize, word_bits - 1), rejoined_bitmap.nextSetBit(word_bits - 3));
    try std.testing.expectEqual(@as(?usize, word_bits - 1), rejoined_cpumask.nextCpu(word_bits - 3));
    try std.testing.expectEqual(@as(?usize, word_bits + 17), rejoined_bitmap.nextSetBit(word_bits + 13));
    try std.testing.expectEqual(@as(?usize, word_bits + 17), rejoined_cpumask.nextCpu(word_bits + 13));
    try std.testing.expectEqual(migrated_bitmap.countSetBits(), rejoined_bitmap.countSetBits());
    try std.testing.expectEqual(migrated_cpumask.countPresentCpus(), rejoined_cpumask.countPresentCpus());
    try std.testing.expect(migrated_bitmap.isSubsetOf(rejoined_bitmap));
    try std.testing.expect(migrated_cpumask.isSubsetOf(rejoined_cpumask));
}
