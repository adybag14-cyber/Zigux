const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const word_count = 3;
const capacity = word_bits * 2 + 11;

const Partition = struct {
    lower: [word_count]Word,
    upper: [word_count]Word,
};

fn bitMask(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn setBit(words: *[word_count]Word, bit_index: usize) void {
    words[bit_index / word_bits] |= bitMask(bit_index);
}

fn tailNoise() Word {
    return ~((@as(Word, 1) << 11) - 1);
}

fn partitionWords(base: [word_count]Word, split_bit: usize) Partition {
    var partition = Partition{
        .lower = [_]Word{0} ** word_count,
        .upper = [_]Word{0} ** word_count,
    };

    for (0..capacity) |bit| {
        if ((base[bit / word_bits] & bitMask(bit)) == 0) continue;
        if (bit < split_bit) {
            setBit(&partition.lower, bit);
        } else {
            setBit(&partition.upper, bit);
        }
    }
    return partition;
}

fn recombine(lower: [word_count]Word, upper: [word_count]Word) [word_count]Word {
    var result: [word_count]Word = undefined;
    for (0..word_count) |index| {
        result[index] = lower[index] | upper[index];
    }
    return result;
}

fn expectMirroredView(words: []const Word, expected_count: usize, first_set: ?usize, first_clear: ?usize) !void {
    const bitmap = bitmap_view.BitmapView.init(words, capacity);
    const mask = cpumask_view.CpuMaskView.init(words, capacity);

    try testing.expectEqual(expected_count, bitmap.countSetBits());
    try testing.expectEqual(expected_count, mask.countPresentCpus());
    try testing.expectEqual(first_set, bitmap.firstSetBit());
    try testing.expectEqual(first_set, mask.firstCpu());
    try testing.expectEqual(first_clear, bitmap.firstClearBit());
    try testing.expectEqual(first_clear, mask.firstMissingCpu());
}

test "bitmap and cpumask agree across lower and upper partition masks" {
    var base_words = [_]Word{ 0, 0, tailNoise() };
    for ([_]usize{ 0, 3, word_bits - 2, word_bits + 1, word_bits + 9, word_bits * 2, word_bits * 2 + 10 }) |bit| {
        setBit(&base_words, bit);
    }

    const split_bit = word_bits + 2;
    var partition = partitionWords(base_words, split_bit);
    partition.upper[2] |= tailNoise();

    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const lower_bitmap = bitmap_view.BitmapView.init(partition.lower[0..], capacity);
    const upper_bitmap = bitmap_view.BitmapView.init(partition.upper[0..], capacity);
    const lower_mask = cpumask_view.CpuMaskView.init(partition.lower[0..], capacity);
    const upper_mask = cpumask_view.CpuMaskView.init(partition.upper[0..], capacity);
    const recombined = recombine(partition.lower, partition.upper);
    const recombined_bitmap = bitmap_view.BitmapView.init(recombined[0..], capacity);

    try expectMirroredView(partition.lower[0..], 4, 0, 1);
    try expectMirroredView(partition.upper[0..], 3, word_bits + 9, 0);
    try testing.expect(lower_bitmap.isSubsetOf(base_bitmap));
    try testing.expect(upper_mask.isSubsetOf(cpumask_view.CpuMaskView.init(base_words[0..], capacity)));
    try testing.expect(!lower_bitmap.intersects(upper_bitmap));
    try testing.expect(!lower_mask.intersects(upper_mask));
    try testing.expect(recombined_bitmap.isSubsetOf(base_bitmap));
    try testing.expect(base_bitmap.isSubsetOf(recombined_bitmap));
    try testing.expectEqual(@as(?usize, word_bits + 9), upper_mask.nextCpu(split_bit));
    try testing.expectEqual(@as(?usize, split_bit), upper_bitmap.nextClearBit(split_bit));
}

test "moving the partition boundary preserves mirrored cursor semantics" {
    var base_words = [_]Word{ 0, 0, tailNoise() };
    for ([_]usize{ 1, word_bits - 1, word_bits, word_bits + 3, word_bits * 2 + 2, word_bits * 2 + 9 }) |bit| {
        setBit(&base_words, bit);
    }

    const first_partition = partitionWords(base_words, word_bits);
    const second_partition = partitionWords(base_words, word_bits + 4);

    const first_lower = cpumask_view.CpuMaskView.init(first_partition.lower[0..], capacity);
    const first_upper = cpumask_view.CpuMaskView.init(first_partition.upper[0..], capacity);
    const second_lower = cpumask_view.CpuMaskView.init(second_partition.lower[0..], capacity);
    const second_upper_bitmap = bitmap_view.BitmapView.init(second_partition.upper[0..], capacity);
    const second_recombined = bitmap_view.BitmapView.init(recombine(second_partition.lower, second_partition.upper)[0..], capacity);
    const base_bitmap = bitmap_view.BitmapView.init(base_words[0..], capacity);

    try expectMirroredView(first_partition.lower[0..], 2, 1, 0);
    try expectMirroredView(first_partition.upper[0..], 4, word_bits, 0);
    try testing.expect(!first_lower.hasCpu(word_bits));
    try testing.expect(first_upper.hasCpu(word_bits));

    try expectMirroredView(second_partition.lower[0..], 4, 1, 0);
    try expectMirroredView(second_partition.upper[0..], 2, word_bits * 2 + 2, 0);
    try testing.expect(second_lower.hasCpu(word_bits));
    try testing.expect(second_lower.hasCpu(word_bits + 3));
    try testing.expectEqual(@as(?usize, word_bits * 2 + 2), second_upper_bitmap.nextSetBit(word_bits + 4));
    try testing.expectEqual(@as(?usize, word_bits + 4), second_upper_bitmap.nextClearBit(word_bits + 4));
    try testing.expect(base_bitmap.isSubsetOf(second_recombined));
    try testing.expect(second_recombined.isSubsetOf(base_bitmap));
}
