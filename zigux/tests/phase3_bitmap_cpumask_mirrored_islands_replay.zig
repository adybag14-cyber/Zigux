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

fn fillMirroredIslands(words: []usize, capacity: usize, offsets: []const usize) void {
    std.debug.assert(words.len * bitmap_view.word_bits >= capacity);
    @memset(words, 0);

    for (offsets) |offset| {
        std.debug.assert(offset < capacity);
        setBit(words, offset);
        setBit(words, capacity - 1 - offset);
    }

    if (words.len != 0) {
        words[words.len - 1] |= inactiveTailNoise(capacity);
    }
}

test "mirrored islands keep bitmap and cpumask summaries aligned under noisy tails" {
    const capacity = bitmap_view.word_bits + 9;
    var mirrored_words = [_]usize{ 0, 0 };
    fillMirroredIslands(mirrored_words[0..], capacity, &.{ 0, 2, 4 });

    const bitmap = bitmap_view.BitmapView.init(mirrored_words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(mirrored_words[0..], capacity);

    try testing.expectEqual(@as(usize, 6), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(4));
    try testing.expect(cpumask.hasCpu(4));
    try testing.expect(bitmap.isSet(capacity - 5));
    try testing.expect(cpumask.hasCpu(capacity - 5));
    try testing.expect(!bitmap.isSet(1));
    try testing.expect(!cpumask.hasCpu(1));
    try testing.expect(!bitmap.isSet(capacity - 2));
    try testing.expect(!cpumask.hasCpu(capacity - 2));
}

test "mirrored islands stay subset-bounded while gap-only peers remain disjoint" {
    const capacity = bitmap_view.word_bits + 9;
    var mirrored_words = [_]usize{ 0, 0 };
    var superset_words = [_]usize{ 0, 0 };
    var outsider_words = [_]usize{ 0, 0 };
    fillMirroredIslands(mirrored_words[0..], capacity, &.{ 0, 2, 4 });
    fillMirroredIslands(superset_words[0..], capacity, &.{ 0, 2, 4 });
    setBit(superset_words[0..], 6);
    setBit(superset_words[0..], bitmap_view.word_bits + 1);

    setBit(outsider_words[0..], 1);
    setBit(outsider_words[0..], 3);
    setBit(outsider_words[0..], bitmap_view.word_bits + 1);
    outsider_words[outsider_words.len - 1] |= inactiveTailNoise(capacity);

    const mirrored = cpumask_view.CpuMaskView.init(mirrored_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const outsider = cpumask_view.CpuMaskView.init(outsider_words[0..], capacity);

    try testing.expect(mirrored.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(mirrored));
    try testing.expect(mirrored.intersects(superset));
    try testing.expect(!mirrored.intersects(outsider));
    try testing.expect(!outsider.isSubsetOf(mirrored));
}

test "mirrored islands and their bounded complement partition the full window" {
    const capacity = bitmap_view.word_bits + 9;
    var mirrored_words = [_]usize{ 0, 0 };
    fillMirroredIslands(mirrored_words[0..], capacity, &.{ 0, 2, 4 });

    const gap_words = [_]usize{
        ~mirrored_words[0],
        ~mirrored_words[1],
    };
    const full_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
    };

    const mirrored_bitmap = bitmap_view.BitmapView.init(mirrored_words[0..], capacity);
    const gap_bitmap = bitmap_view.BitmapView.init(gap_words[0..], capacity);
    const mirrored = cpumask_view.CpuMaskView.init(mirrored_words[0..], capacity);
    const gap = cpumask_view.CpuMaskView.init(gap_words[0..], capacity);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], capacity);

    try testing.expectEqual(capacity, mirrored_bitmap.countSetBits() + gap_bitmap.countSetBits());
    try testing.expect(mirrored.isSubsetOf(full));
    try testing.expect(gap.isSubsetOf(full));
    try testing.expect(!mirrored.intersects(gap));
    try testing.expectEqual(@as(usize, capacity), full.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), gap.firstCpu());
    try testing.expectEqual(@as(?usize, null), full.firstMissingCpu());
}
