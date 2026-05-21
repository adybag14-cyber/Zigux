const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn inactiveTailNoise(bit_len: usize) usize {
    const remainder = bit_len % bitmap_view.word_bits;
    if (remainder == 0) return 0;
    return ~((@as(usize, 1) << @intCast(remainder)) - 1);
}

fn fillParityWords(words: []usize, capacity: usize, start_bit: usize) void {
    @memset(words, 0);

    var bit = start_bit;
    while (bit < capacity) : (bit += 2) {
        const word_index = bit / bitmap_view.word_bits;
        const bit_index = bit % bitmap_view.word_bits;
        words[word_index] |= @as(usize, 1) << @intCast(bit_index);
    }

    if (words.len != 0) {
        words[words.len - 1] |= inactiveTailNoise(capacity);
    }
}

test "parity windows keep bitmap and cpumask summaries aligned under noisy tails" {
    const capacity = bitmap_view.word_bits + 5;
    var even_words = [_]usize{ 0, 0 };
    fillParityWords(even_words[0..], capacity, 0);

    const bitmap = bitmap_view.BitmapView.init(even_words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(even_words[0..], capacity);

    try testing.expectEqual(@as(usize, (capacity + 1) / 2), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 4));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 4));
    try testing.expect(!bitmap.isSet(bitmap_view.word_bits + 3));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 3));
}

test "opposite parity windows stay disjoint inside the bounded range" {
    const capacity = bitmap_view.word_bits + 5;
    var even_words = [_]usize{ 0, 0 };
    var odd_words = [_]usize{ 0, 0 };
    fillParityWords(even_words[0..], capacity, 0);
    fillParityWords(odd_words[0..], capacity, 1);

    const even = cpumask_view.CpuMaskView.init(even_words[0..], capacity);
    const odd = cpumask_view.CpuMaskView.init(odd_words[0..], capacity);

    try testing.expectEqual(@as(usize, (capacity + 1) / 2), even.countPresentCpus());
    try testing.expectEqual(@as(usize, capacity / 2), odd.countPresentCpus());
    try testing.expect(!even.intersects(odd));
    try testing.expect(!odd.intersects(even));
    try testing.expect(!even.isSubsetOf(odd));
    try testing.expect(!odd.isSubsetOf(even));
    try testing.expect(even.hasCpu(0));
    try testing.expect(!odd.hasCpu(0));
    try testing.expect(odd.hasCpu(1));
    try testing.expect(!even.hasCpu(1));
}

test "full parity union keeps each peer subset-bounded without tail leakage" {
    const capacity = bitmap_view.word_bits + 5;
    var even_words = [_]usize{ 0, 0 };
    var odd_words = [_]usize{ 0, 0 };
    fillParityWords(even_words[0..], capacity, 0);
    fillParityWords(odd_words[0..], capacity, 1);

    const full_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
    };

    const even = cpumask_view.CpuMaskView.init(even_words[0..], capacity);
    const odd = cpumask_view.CpuMaskView.init(odd_words[0..], capacity);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], capacity);

    try testing.expect(even.isSubsetOf(full));
    try testing.expect(odd.isSubsetOf(full));
    try testing.expect(full.intersects(even));
    try testing.expect(full.intersects(odd));
    try testing.expectEqual(@as(usize, capacity), full.countPresentCpus());
    try testing.expectEqual(@as(?usize, null), full.firstMissingCpu());
    try testing.expectEqual(@as(?usize, 0), full.firstCpu());
}
