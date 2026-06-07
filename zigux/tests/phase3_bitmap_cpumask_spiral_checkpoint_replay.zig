const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const word_bits = bitmap_view.word_bits;
const Word = usize;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn tailNoise(active_tail_bits: usize) Word {
    return ~@as(Word, 0) << @intCast(active_tail_bits);
}

fn bitmap(words: []const Word, capacity: usize) bitmap_view.BitmapView {
    return bitmap_view.BitmapView.init(words, capacity);
}

fn cpumask(words: []const Word, capacity: usize) cpumask_view.CpuMaskView {
    return cpumask_view.CpuMaskView.init(words, capacity);
}

fn expectMirror(words: []const Word, capacity: usize, count: usize, first_set: ?usize, first_clear: ?usize) !void {
    const b = bitmap(words, capacity);
    const c = cpumask(words, capacity);

    try testing.expectEqual(count, b.countSetBits());
    try testing.expectEqual(count, c.countPresentCpus());
    try testing.expectEqual(first_set, b.firstSetBit());
    try testing.expectEqual(first_set, c.firstCpu());
    try testing.expectEqual(first_clear, b.firstClearBit());
    try testing.expectEqual(first_clear, c.firstMissingCpu());
}

test "lane27 spiral checkpoint keeps staged relation mirrors aligned" {
    const capacity = (word_bits * 2) + 21;
    const outer_words = [_]Word{
        bit(1) | bit(8) | bit(15) | bit(22) | bit(31),
        bit(word_bits + 5) | bit(word_bits + 14) | bit(word_bits + 23) | bit(word_bits + 38),
        bit((word_bits * 2) + 4) | bit((word_bits * 2) + 13) | bit((word_bits * 2) + 20) | tailNoise(21),
    };
    const inner_words = [_]Word{
        bit(8) | bit(22),
        bit(word_bits + 14) | bit(word_bits + 38),
        bit((word_bits * 2) + 13) | tailNoise(21),
    };
    const bridge_words = [_]Word{
        bit(1) | bit(8) | bit(31),
        bit(word_bits + 5) | bit(word_bits + 14),
        bit((word_bits * 2) + 4) | bit((word_bits * 2) + 13) | tailNoise(21),
    };
    const outside_words = [_]Word{
        bit(3) | bit(10) | bit(18) | bit(27),
        bit(word_bits + 2) | bit(word_bits + 9) | bit(word_bits + 19) | bit(word_bits + 30),
        bit((word_bits * 2) + 1) | bit((word_bits * 2) + 9) | bit((word_bits * 2) + 17) | tailNoise(21),
    };

    const outer_bitmap = bitmap(outer_words[0..], capacity);
    const inner_bitmap = bitmap(inner_words[0..], capacity);
    const bridge_bitmap = bitmap(bridge_words[0..], capacity);
    const outside_bitmap = bitmap(outside_words[0..], capacity);
    const outer_mask = cpumask(outer_words[0..], capacity);
    const inner_mask = cpumask(inner_words[0..], capacity);
    const bridge_mask = cpumask(bridge_words[0..], capacity);
    const outside_mask = cpumask(outside_words[0..], capacity);

    try expectMirror(outer_words[0..], capacity, 12, 1, 0);
    try expectMirror(inner_words[0..], capacity, 5, 8, 0);
    try expectMirror(bridge_words[0..], capacity, 7, 1, 0);
    try expectMirror(outside_words[0..], capacity, 11, 3, 0);

    try testing.expect(inner_bitmap.isSubsetOf(outer_bitmap));
    try testing.expect(bridge_bitmap.isSubsetOf(outer_bitmap));
    try testing.expect(!outer_bitmap.isSubsetOf(bridge_bitmap));
    try testing.expect(bridge_bitmap.intersects(inner_bitmap));
    try testing.expect(!outside_bitmap.intersects(outer_bitmap));

    try testing.expect(inner_mask.isSubsetOf(outer_mask));
    try testing.expect(bridge_mask.isSubsetOf(outer_mask));
    try testing.expect(!outer_mask.isSubsetOf(bridge_mask));
    try testing.expect(bridge_mask.intersects(inner_mask));
    try testing.expect(!outside_mask.intersects(outer_mask));

    try testing.expectEqual(@as(?usize, 22), outer_bitmap.nextSetBit(16));
    try testing.expectEqual(@as(?usize, word_bits + 23), outer_bitmap.nextSetBit(word_bits + 15));
    try testing.expectEqual(@as(?usize, (word_bits * 2) + 20), outer_bitmap.nextSetBit((word_bits * 2) + 14));
    try testing.expectEqual(@as(?usize, null), outer_bitmap.nextClearBit((word_bits * 2) + 20));
    try testing.expectEqual(@as(?usize, 22), outer_mask.nextCpu(16));
    try testing.expectEqual(@as(?usize, word_bits + 23), outer_mask.nextCpu(word_bits + 15));
    try testing.expectEqual(@as(?usize, (word_bits * 2) + 20), outer_mask.nextCpu((word_bits * 2) + 14));
    try testing.expectEqual(@as(?usize, null), outer_mask.nextMissingCpu((word_bits * 2) + 20));
}

test "lane27 spiral checkpoint tracks promotion and rollback without tail noise drift" {
    const capacity = word_bits + 19;
    const baseline_words = [_]Word{
        bit(2) | bit(7) | bit(16) | bit(29),
        bit(word_bits + 3) | bit(word_bits + 11) | bit(word_bits + 18) | tailNoise(19),
    };
    const checkpoint_words = [_]Word{
        bit(2) | bit(7) | bit(16) | bit(20) | bit(29) | bit(42),
        bit(word_bits + 3) | bit(word_bits + 7) | bit(word_bits + 11) | bit(word_bits + 15) | bit(word_bits + 18) | tailNoise(19),
    };
    const rollback_words = [_]Word{
        bit(2) | bit(7) | bit(29),
        bit(word_bits + 3) | bit(word_bits + 11) | bit(word_bits + 18) | tailNoise(19),
    };
    const checkpoint_only_words = [_]Word{
        bit(20) | bit(42),
        bit(word_bits + 7) | bit(word_bits + 15) | tailNoise(19),
    };
    const tail_noise_only_words = [_]Word{
        0,
        tailNoise(19),
    };

    const baseline_bitmap = bitmap(baseline_words[0..], capacity);
    const checkpoint_bitmap = bitmap(checkpoint_words[0..], capacity);
    const rollback_bitmap = bitmap(rollback_words[0..], capacity);
    const checkpoint_only_bitmap = bitmap(checkpoint_only_words[0..], capacity);
    const noise_bitmap = bitmap(tail_noise_only_words[0..], capacity);
    const baseline_mask = cpumask(baseline_words[0..], capacity);
    const checkpoint_mask = cpumask(checkpoint_words[0..], capacity);
    const rollback_mask = cpumask(rollback_words[0..], capacity);
    const checkpoint_only_mask = cpumask(checkpoint_only_words[0..], capacity);
    const noise_mask = cpumask(tail_noise_only_words[0..], capacity);

    try expectMirror(baseline_words[0..], capacity, 7, 2, 0);
    try expectMirror(checkpoint_words[0..], capacity, 11, 2, 0);
    try expectMirror(rollback_words[0..], capacity, 6, 2, 0);
    try expectMirror(checkpoint_only_words[0..], capacity, 4, 20, 0);
    try expectMirror(tail_noise_only_words[0..], capacity, 0, null, 0);

    try testing.expect(baseline_bitmap.isSubsetOf(checkpoint_bitmap));
    try testing.expect(rollback_bitmap.isSubsetOf(baseline_bitmap));
    try testing.expect(!baseline_bitmap.isSubsetOf(rollback_bitmap));
    try testing.expect(!checkpoint_only_bitmap.intersects(baseline_bitmap));
    try testing.expect(checkpoint_only_bitmap.intersects(checkpoint_bitmap));
    try testing.expect(!noise_bitmap.intersects(checkpoint_bitmap));

    try testing.expect(baseline_mask.isSubsetOf(checkpoint_mask));
    try testing.expect(rollback_mask.isSubsetOf(baseline_mask));
    try testing.expect(!baseline_mask.isSubsetOf(rollback_mask));
    try testing.expect(!checkpoint_only_mask.intersects(baseline_mask));
    try testing.expect(checkpoint_only_mask.intersects(checkpoint_mask));
    try testing.expect(!noise_mask.intersects(checkpoint_mask));

    try testing.expectEqual(@as(?usize, 29), baseline_bitmap.nextSetBit(17));
    try testing.expectEqual(@as(?usize, 20), checkpoint_bitmap.nextSetBit(17));
    try testing.expectEqual(@as(?usize, 16), rollback_bitmap.nextClearBit(16));
    try testing.expectEqual(@as(?usize, word_bits + 18), checkpoint_bitmap.nextSetBit(word_bits + 16));
    try testing.expectEqual(@as(?usize, 29), baseline_mask.nextCpu(17));
    try testing.expectEqual(@as(?usize, 20), checkpoint_mask.nextCpu(17));
    try testing.expectEqual(@as(?usize, 16), rollback_mask.nextMissingCpu(16));
    try testing.expectEqual(@as(?usize, word_bits + 18), checkpoint_mask.nextCpu(word_bits + 16));
}
