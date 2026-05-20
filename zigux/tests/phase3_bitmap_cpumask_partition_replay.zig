const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn setBit(words: []usize, bit: usize) void {
    const word_index = bit / bitmap_view.word_bits;
    const shift = bit % bitmap_view.word_bits;
    words[word_index] |= (@as(usize, 1) << @intCast(shift));
}

fn addTailNoise(words: []usize, capacity: usize) void {
    for (capacity..(words.len * bitmap_view.word_bits)) |bit| {
        setBit(words, bit);
    }
}

fn bitmapSubsetOf(lhs: bitmap_view.BitmapView, rhs: bitmap_view.BitmapView) bool {
    std.debug.assert(lhs.bit_len == rhs.bit_len);
    for (0..lhs.bit_len) |bit| {
        if (lhs.isSet(bit) and !rhs.isSet(bit)) return false;
    }
    return true;
}

fn bitmapIntersects(lhs: bitmap_view.BitmapView, rhs: bitmap_view.BitmapView) bool {
    std.debug.assert(lhs.bit_len == rhs.bit_len);
    for (0..lhs.bit_len) |bit| {
        if (lhs.isSet(bit) and rhs.isSet(bit)) return true;
    }
    return false;
}

fn expectExhaustiveDisjointPartition(
    lhs_words: []const usize,
    rhs_words: []const usize,
    capacity: usize,
) !void {
    const lhs_bitmap = bitmap_view.BitmapView.init(lhs_words, capacity);
    const rhs_bitmap = bitmap_view.BitmapView.init(rhs_words, capacity);
    const lhs_cpumask = cpumask_view.CpuMaskView.init(lhs_words, capacity);
    const rhs_cpumask = cpumask_view.CpuMaskView.init(rhs_words, capacity);

    for (0..capacity) |bit| {
        const lhs_set = lhs_bitmap.isSet(bit);
        const rhs_set = rhs_bitmap.isSet(bit);

        try testing.expectEqual(lhs_set, lhs_cpumask.hasCpu(bit));
        try testing.expectEqual(rhs_set, rhs_cpumask.hasCpu(bit));
        try testing.expect(lhs_set != rhs_set);
    }

    try testing.expectEqual(capacity, lhs_bitmap.countSetBits() + rhs_bitmap.countSetBits());
    try testing.expectEqual(capacity, lhs_cpumask.countPresentCpus() + rhs_cpumask.countPresentCpus());

    try testing.expect(!bitmapIntersects(lhs_bitmap, rhs_bitmap));
    try testing.expect(!bitmapIntersects(rhs_bitmap, lhs_bitmap));
    try testing.expect(!lhs_cpumask.intersects(rhs_cpumask));
    try testing.expect(!rhs_cpumask.intersects(lhs_cpumask));

    try testing.expect(!bitmapSubsetOf(lhs_bitmap, rhs_bitmap));
    try testing.expect(!bitmapSubsetOf(rhs_bitmap, lhs_bitmap));
    try testing.expect(!lhs_cpumask.isSubsetOf(rhs_cpumask));
    try testing.expect(!rhs_cpumask.isSubsetOf(lhs_cpumask));
}

test "cross-word parity partitions stay exhaustive and disjoint" {
    const capacity = bitmap_view.word_bits + 5;
    var lhs_words = [_]usize{ 0, 0 };
    var rhs_words = [_]usize{ 0, 0 };

    for (0..capacity) |bit| {
        if (bit % 2 == 0) {
            setBit(lhs_words[0..], bit);
        } else {
            setBit(rhs_words[0..], bit);
        }
    }
    addTailNoise(lhs_words[0..], capacity);
    addTailNoise(rhs_words[0..], capacity);

    try expectExhaustiveDisjointPartition(lhs_words[0..], rhs_words[0..], capacity);

    try testing.expectEqual(@as(?usize, 0), bitmap_view.BitmapView.init(lhs_words[0..], capacity).firstSetBit());
    try testing.expectEqual(@as(?usize, 1), bitmap_view.BitmapView.init(rhs_words[0..], capacity).firstSetBit());
    try testing.expectEqual(@as(?usize, 1), cpumask_view.CpuMaskView.init(lhs_words[0..], capacity).firstMissingCpu());
    try testing.expectEqual(@as(?usize, 0), cpumask_view.CpuMaskView.init(rhs_words[0..], capacity).firstMissingCpu());
}

test "exact-word partitions ignore a fully out-of-range trailing word" {
    const capacity = bitmap_view.word_bits;
    var lhs_words = [_]usize{ 0, 0 };
    var rhs_words = [_]usize{ 0, 0 };

    for (0..capacity) |bit| {
        if (bit < (capacity / 2)) {
            setBit(lhs_words[0..], bit);
        } else {
            setBit(rhs_words[0..], bit);
        }
    }
    addTailNoise(lhs_words[0..], capacity);
    addTailNoise(rhs_words[0..], capacity);

    try expectExhaustiveDisjointPartition(lhs_words[0..], rhs_words[0..], capacity);

    try testing.expectEqual(@as(?usize, 0), cpumask_view.CpuMaskView.init(lhs_words[0..], capacity).firstCpu());
    try testing.expectEqual(@as(?usize, capacity / 2), cpumask_view.CpuMaskView.init(rhs_words[0..], capacity).firstCpu());
}

test "tail-heavy partitions keep the last active window reviewable" {
    const capacity = bitmap_view.word_bits + 3;
    var lhs_words = [_]usize{ 0, 0 };
    var rhs_words = [_]usize{ 0, 0 };

    for (0..capacity) |bit| {
        if (bit < bitmap_view.word_bits) {
            setBit(rhs_words[0..], bit);
        } else {
            setBit(lhs_words[0..], bit);
        }
    }
    addTailNoise(lhs_words[0..], capacity);
    addTailNoise(rhs_words[0..], capacity);

    try expectExhaustiveDisjointPartition(lhs_words[0..], rhs_words[0..], capacity);

    try testing.expectEqual(@as(?usize, bitmap_view.word_bits), bitmap_view.BitmapView.init(lhs_words[0..], capacity).firstSetBit());
    try testing.expectEqual(@as(?usize, 0), bitmap_view.BitmapView.init(rhs_words[0..], capacity).firstSetBit());
    try testing.expectEqual(@as(?usize, 0), cpumask_view.CpuMaskView.init(lhs_words[0..], capacity).firstMissingCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits), cpumask_view.CpuMaskView.init(rhs_words[0..], capacity).firstMissingCpu());
}
