const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

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

fn fillExactWindow(words: []usize) void {
    @memset(words, 0);
    applyRange(words, 0, 2);
    applyRange(words, bitmap_view.word_bits + 1, bitmap_view.word_bits + 4);
    applyRange(words, (2 * bitmap_view.word_bits) - 1, (2 * bitmap_view.word_bits) + 2);
    applyRange(words, (3 * bitmap_view.word_bits) - 2, 3 * bitmap_view.word_bits);
    words[words.len - 1] = std.math.maxInt(usize);
}

fn fillEdgePeer(words: []usize) void {
    @memset(words, 0);
    const edge_bits = [_]usize{
        0,
        bitmap_view.word_bits + 1,
        (2 * bitmap_view.word_bits) - 1,
        (3 * bitmap_view.word_bits) - 1,
    };
    for (edge_bits) |bit| {
        setBit(words, bit);
    }
    words[words.len - 1] = std.math.maxInt(usize);
}

fn fillGapPeer(words: []usize) void {
    @memset(words, 0);
    const gap_bits = [_]usize{
        2,
        bitmap_view.word_bits,
        bitmap_view.word_bits + 4,
        (2 * bitmap_view.word_bits) - 2,
        (2 * bitmap_view.word_bits) + 2,
        (3 * bitmap_view.word_bits) - 3,
    };
    for (gap_bits) |bit| {
        setBit(words, bit);
    }
    words[words.len - 1] = std.math.maxInt(usize);
}

test "exact-word-capacity windows keep bitmap and cpumask summaries aligned while ignoring inactive storage" {
    const capacity = 3 * bitmap_view.word_bits;
    var words = [_]usize{ 0, 0, 0, 0 };
    fillExactWindow(words[0..]);

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(usize, 10), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 2), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(bitmap_view.word_bits + 2));
    try testing.expect(cpumask.hasCpu((2 * bitmap_view.word_bits) + 1));
    try testing.expect(bitmap.isSet((3 * bitmap_view.word_bits) - 1));
    try testing.expect(cpumask.hasCpu((3 * bitmap_view.word_bits) - 2));
    try testing.expect(!bitmap.isSet(bitmap_view.word_bits));
    try testing.expect(!cpumask.hasCpu((2 * bitmap_view.word_bits) + 2));
}

test "exact-word edge peer stays a bounded subset through the final active bit" {
    const capacity = 3 * bitmap_view.word_bits;
    var full_words = [_]usize{ 0, 0, 0, 0 };
    var edge_words = [_]usize{ 0, 0, 0, 0 };
    fillExactWindow(full_words[0..]);
    fillEdgePeer(edge_words[0..]);

    const edge_bitmap = bitmap_view.BitmapView.init(edge_words[0..], capacity);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], capacity);
    const edge = cpumask_view.CpuMaskView.init(edge_words[0..], capacity);

    try testing.expectEqual(@as(usize, 4), edge_bitmap.countSetBits());
    try testing.expectEqual(edge_bitmap.countSetBits(), edge.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), edge_bitmap.firstSetBit());
    try testing.expectEqual(edge_bitmap.firstSetBit(), edge.firstCpu());
    try testing.expect(edge.isSubsetOf(full));
    try testing.expect(full.intersects(edge));
    try testing.expect(edge.intersects(full));
    try testing.expect(!full.isSubsetOf(edge));
    try testing.expect(edge.hasCpu((3 * bitmap_view.word_bits) - 1));
    try testing.expect(!edge.hasCpu(2));
}

test "exact-word disjoint peer stays separate while both masks remain bounded by a saturated full mask" {
    const capacity = 3 * bitmap_view.word_bits;
    var island_words = [_]usize{ 0, 0, 0, 0 };
    var gap_words = [_]usize{ 0, 0, 0, 0 };
    fillExactWindow(island_words[0..]);
    fillGapPeer(gap_words[0..]);

    const full_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        0,
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
    try testing.expect(gaps.hasCpu((3 * bitmap_view.word_bits) - 3));
    try testing.expect(!islands.hasCpu((3 * bitmap_view.word_bits) - 3));
}
