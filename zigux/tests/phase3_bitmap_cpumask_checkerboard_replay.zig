const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn setBit(words: []usize, bit: usize) void {
    const word_index = bit / bitmap_view.word_bits;
    const bit_index = bit % bitmap_view.word_bits;
    words[word_index] |= @as(usize, 1) << @intCast(bit_index);
}

fn addNoise(words: []usize, capacity: usize) void {
    const active_word_len = if (capacity == 0) 0 else (capacity + (bitmap_view.word_bits - 1)) / bitmap_view.word_bits;
    if (active_word_len == 0) return;

    const remainder = capacity % bitmap_view.word_bits;
    if (remainder != 0) {
        const valid_mask = (@as(usize, 1) << @intCast(remainder)) - 1;
        words[active_word_len - 1] |= ~valid_mask;
    }
    if (words.len > active_word_len) {
        words[active_word_len] = std.math.maxInt(usize);
    }
}

fn fillCheckerboard(words: []usize, capacity: usize, parity: usize) void {
    @memset(words, 0);
    var bit = parity;
    while (bit < capacity) : (bit += 2) {
        setBit(words, bit);
    }
    addNoise(words, capacity);
}

fn fillStrideFour(words: []usize, capacity: usize, start: usize) void {
    @memset(words, 0);
    var bit = start;
    while (bit < capacity) : (bit += 4) {
        setBit(words, bit);
    }
    addNoise(words, capacity);
}

test "checkerboard window keeps bitmap and cpumask summaries aligned under tail noise" {
    const capacity = (2 * bitmap_view.word_bits) + 9;
    var words = [_]usize{ 0, 0, 0, 0 };
    fillCheckerboard(words[0..], capacity, 0);

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, (capacity + 1) / 2), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(0));
    try testing.expect(bitmap.isSet(capacity - 1));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits + 2));
    try testing.expect(!cpumask.hasCpu(1));
    try testing.expect(!cpumask.hasCpu(capacity - 2));
}

test "checkerboard complements stay disjoint while the bounded full window still contains both" {
    const capacity = (2 * bitmap_view.word_bits) + 9;
    var even_words = [_]usize{ 0, 0, 0, 0 };
    var odd_words = [_]usize{ 0, 0, 0, 0 };
    fillCheckerboard(even_words[0..], capacity, 0);
    fillCheckerboard(odd_words[0..], capacity, 1);

    const full_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
    };

    const even = cpumask_view.CpuMaskView.init(even_words[0..], capacity);
    const odd = cpumask_view.CpuMaskView.init(odd_words[0..], capacity);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], capacity);

    try testing.expect(!even.intersects(odd));
    try testing.expect(!odd.intersects(even));
    try testing.expect(!even.isSubsetOf(odd));
    try testing.expect(!odd.isSubsetOf(even));
    try testing.expect(even.isSubsetOf(full));
    try testing.expect(odd.isSubsetOf(full));
    try testing.expectEqual(capacity, full.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), full.firstCpu());
    try testing.expectEqual(@as(?usize, null), full.firstMissingCpu());
}

test "sparser checkerboard peer remains a bounded subset without inheriting tail noise" {
    const capacity = (2 * bitmap_view.word_bits) + 9;
    var even_words = [_]usize{ 0, 0, 0, 0 };
    var sparse_words = [_]usize{ 0, 0, 0, 0 };
    fillCheckerboard(even_words[0..], capacity, 0);
    fillStrideFour(sparse_words[0..], capacity, 0);

    const sparse_bitmap = bitmap_view.BitmapView.init(sparse_words[0..], capacity);
    const even = cpumask_view.CpuMaskView.init(even_words[0..], capacity);
    const sparse = cpumask_view.CpuMaskView.init(sparse_words[0..], capacity);

    try testing.expectEqual(@as(usize, ((capacity - 1) / 4) + 1), sparse_bitmap.countSetBits());
    try testing.expectEqual(sparse_bitmap.countSetBits(), sparse.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), sparse_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 1), sparse_bitmap.firstClearBit());
    try testing.expect(sparse.isSubsetOf(even));
    try testing.expect(even.intersects(sparse));
    try testing.expect(sparse.intersects(even));
    try testing.expect(!even.isSubsetOf(sparse));
    try testing.expect(sparse.hasCpu(capacity - 1));
    try testing.expect(!sparse.hasCpu(capacity - 4));
}
