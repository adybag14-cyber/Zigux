const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn inactiveTailNoise(bit_len: usize) usize {
    const remainder = bit_len % bitmap_view.word_bits;
    if (remainder == 0) return 0;
    return ~((@as(usize, 1) << @intCast(remainder)) - 1);
}

fn setBit(words: []usize, bit: usize) void {
    const word_index = bit / bitmap_view.word_bits;
    const bit_index = bit % bitmap_view.word_bits;
    words[word_index] |= @as(usize, 1) << @intCast(bit_index);
}

fn applyRange(words: []usize, start: usize, end: usize) void {
    var bit = start;
    while (bit < end) : (bit += 1) {
        setBit(words, bit);
    }
}

fn fillThreeIslands(words: []usize, capacity: usize) void {
    @memset(words, 0);
    applyRange(words, 1, 4);
    applyRange(words, bitmap_view.word_bits - 1, bitmap_view.word_bits + 2);
    applyRange(words, (2 * bitmap_view.word_bits) + 1, (2 * bitmap_view.word_bits) + 4);
    words[words.len - 1] |= inactiveTailNoise(capacity);
}

fn fillMiddleIsland(words: []usize, capacity: usize) void {
    @memset(words, 0);
    applyRange(words, bitmap_view.word_bits - 1, bitmap_view.word_bits + 2);
    words[words.len - 1] |= inactiveTailNoise(capacity);
}

fn fillGapPeer(words: []usize, capacity: usize) void {
    @memset(words, 0);
    const gap_bits = [_]usize{
        0,
        5,
        bitmap_view.word_bits - 2,
        bitmap_view.word_bits + 3,
        2 * bitmap_view.word_bits,
        (2 * bitmap_view.word_bits) + 4,
    };
    for (gap_bits) |bit| {
        setBit(words, bit);
    }
    words[words.len - 1] |= inactiveTailNoise(capacity);
}

test "three-island windows keep bitmap and cpumask summaries aligned under noisy tails" {
    const capacity = (2 * bitmap_view.word_bits) + 5;
    var words = [_]usize{ 0, 0, 0 };
    fillThreeIslands(words[0..], capacity);

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 9), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(bitmap_view.word_bits - 1));
    try testing.expect(cpumask.hasCpu(bitmap_view.word_bits));
    try testing.expect(bitmap.isSet((2 * bitmap_view.word_bits) + 3));
    try testing.expect(cpumask.hasCpu((2 * bitmap_view.word_bits) + 1));
    try testing.expect(!bitmap.isSet(0));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 3));
    try testing.expect(!bitmap.isSet((2 * bitmap_view.word_bits) + 4));
}

test "middle island peer stays a bounded subset of the full three-island window" {
    const capacity = (2 * bitmap_view.word_bits) + 5;
    var full_words = [_]usize{ 0, 0, 0 };
    var middle_words = [_]usize{ 0, 0, 0 };
    fillThreeIslands(full_words[0..], capacity);
    fillMiddleIsland(middle_words[0..], capacity);

    const full_bitmap = bitmap_view.BitmapView.init(full_words[0..], capacity);
    const middle_bitmap = bitmap_view.BitmapView.init(middle_words[0..], capacity);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], capacity);
    const middle = cpumask_view.CpuMaskView.init(middle_words[0..], capacity);

    try testing.expectEqual(@as(usize, 3), middle_bitmap.countSetBits());
    try testing.expectEqual(middle_bitmap.countSetBits(), middle.countPresentCpus());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits - 1), middle_bitmap.firstSetBit());
    try testing.expectEqual(middle_bitmap.firstSetBit(), middle.firstCpu());
    try testing.expect(middle.isSubsetOf(full));
    try testing.expect(full.intersects(middle));
    try testing.expect(middle.intersects(full));
    try testing.expect(!full.isSubsetOf(middle));
    try testing.expect(middle.hasCpu(bitmap_view.word_bits));
    try testing.expect(!middle.hasCpu(1));
    try testing.expect(full_bitmap.isSet((2 * bitmap_view.word_bits) + 1));
}

test "gap peer stays disjoint while both masks remain subset-bounded inside a full union" {
    const capacity = (2 * bitmap_view.word_bits) + 5;
    var island_words = [_]usize{ 0, 0, 0 };
    var gap_words = [_]usize{ 0, 0, 0 };
    fillThreeIslands(island_words[0..], capacity);
    fillGapPeer(gap_words[0..], capacity);

    const full_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
    };

    const islands = cpumask_view.CpuMaskView.init(island_words[0..], capacity);
    const gaps = cpumask_view.CpuMaskView.init(gap_words[0..], capacity);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], capacity);

    try testing.expect(!islands.intersects(gaps));
    try testing.expect(!gaps.intersects(islands));
    try testing.expect(!gaps.isSubsetOf(islands));
    try testing.expect(islands.isSubsetOf(full));
    try testing.expect(gaps.isSubsetOf(full));
    try testing.expectEqual(@as(usize, capacity), full.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), full.firstCpu());
    try testing.expectEqual(@as(?usize, null), full.firstMissingCpu());
    try testing.expect(gaps.hasCpu((2 * bitmap_view.word_bits) + 4));
    try testing.expect(!islands.hasCpu((2 * bitmap_view.word_bits) + 4));
}
