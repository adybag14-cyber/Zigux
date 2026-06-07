const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const word_bits = bitmap_view.word_bits;
const Word = usize;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn makeView(words: []const Word, capacity: usize) bitmap_view.BitmapView {
    return bitmap_view.BitmapView.init(words, capacity);
}

fn makeMask(words: []const Word, capacity: usize) cpumask_view.CpuMaskView {
    return cpumask_view.CpuMaskView.init(words, capacity);
}

fn expectBitmapCpuMirror(words: []const Word, capacity: usize, expected_count: usize, first_missing: ?usize) !void {
    const bitmap = makeView(words, capacity);
    const cpumask = makeMask(words, capacity);

    try testing.expectEqual(expected_count, bitmap.countSetBits());
    try testing.expectEqual(expected_count, cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expectEqual(first_missing, bitmap.firstClearBit());
    try testing.expectEqual(first_missing, cpumask.firstMissingCpu());
}

test "lane27 nested bridge keeps split bitmap and cpumask relations aligned" {
    const capacity = (word_bits * 2) + 9;
    const outer_words = [_]Word{
        bit(1) | bit(3) | bit(9) | bit(15) | bit(31),
        bit(word_bits + 2) | bit(word_bits + 7) | bit(word_bits + 11) | bit(word_bits + 23),
        bit((word_bits * 2) + 1) | bit((word_bits * 2) + 4) | bit((word_bits * 2) + 8) | (~@as(Word, 0) << 9),
    };
    const inner_words = [_]Word{
        bit(3) | bit(9),
        bit(word_bits + 7) | bit(word_bits + 11),
        bit((word_bits * 2) + 4) | (~@as(Word, 0) << 9),
    };
    const bridge_words = [_]Word{
        bit(15),
        bit(word_bits + 2) | bit(word_bits + 23),
        bit((word_bits * 2) + 1) | (~@as(Word, 0) << 9),
    };
    const disjoint_words = [_]Word{
        bit(0) | bit(2) | bit(4),
        bit(word_bits + 5),
        bit((word_bits * 2) + 6) | (~@as(Word, 0) << 9),
    };

    const outer_bitmap = makeView(outer_words[0..], capacity);
    const inner_bitmap = makeView(inner_words[0..], capacity);
    const bridge_bitmap = makeView(bridge_words[0..], capacity);
    const disjoint_bitmap = makeView(disjoint_words[0..], capacity);
    const outer_mask = makeMask(outer_words[0..], capacity);
    const inner_mask = makeMask(inner_words[0..], capacity);
    const bridge_mask = makeMask(bridge_words[0..], capacity);
    const disjoint_mask = makeMask(disjoint_words[0..], capacity);

    try expectBitmapCpuMirror(outer_words[0..], capacity, 12, 0);
    try expectBitmapCpuMirror(inner_words[0..], capacity, 5, 0);
    try expectBitmapCpuMirror(bridge_words[0..], capacity, 4, 0);

    try testing.expect(inner_bitmap.isSubsetOf(outer_bitmap));
    try testing.expect(bridge_bitmap.isSubsetOf(outer_bitmap));
    try testing.expect(!outer_bitmap.isSubsetOf(inner_bitmap));
    try testing.expect(!bridge_bitmap.intersects(inner_bitmap));
    try testing.expect(!outer_bitmap.intersects(disjoint_bitmap));

    try testing.expect(inner_mask.isSubsetOf(outer_mask));
    try testing.expect(bridge_mask.isSubsetOf(outer_mask));
    try testing.expect(!outer_mask.isSubsetOf(inner_mask));
    try testing.expect(!bridge_mask.intersects(inner_mask));
    try testing.expect(!outer_mask.intersects(disjoint_mask));

    try testing.expectEqual(@as(?usize, 1), outer_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 3), outer_bitmap.nextSetBit(2));
    try testing.expectEqual(@as(?usize, word_bits + 2), outer_bitmap.nextSetBit(word_bits));
    try testing.expectEqual(@as(?usize, (word_bits * 2) + 8), outer_bitmap.nextSetBit((word_bits * 2) + 5));
    try testing.expectEqual(@as(?usize, null), outer_bitmap.nextSetBit(capacity));

    try testing.expectEqual(@as(?usize, 1), outer_mask.firstCpu());
    try testing.expectEqual(@as(?usize, 3), outer_mask.nextCpu(2));
    try testing.expectEqual(@as(?usize, word_bits + 2), outer_mask.nextCpu(word_bits));
    try testing.expectEqual(@as(?usize, (word_bits * 2) + 8), outer_mask.nextCpu((word_bits * 2) + 5));
    try testing.expectEqual(@as(?usize, null), outer_mask.nextCpu(capacity));
}

test "lane27 nested bridge catches rollback drift before rejoin" {
    const capacity = word_bits + 6;
    const base_words = [_]Word{
        bit(5) | bit(8) | bit(13) | bit(21),
        bit(word_bits + 1) | bit(word_bits + 3) | bit(word_bits + 5) | (~@as(Word, 0) << 6),
    };
    const drift_words = [_]Word{
        bit(5) | bit(8) | bit(21),
        bit(word_bits + 1) | bit(word_bits + 5) | (~@as(Word, 0) << 6),
    };
    const rejoin_words = [_]Word{
        bit(5) | bit(8) | bit(13) | bit(21),
        bit(word_bits + 1) | bit(word_bits + 3) | bit(word_bits + 5) | (~@as(Word, 0) << 6),
    };
    const missing_bridge_words = [_]Word{
        bit(13),
        bit(word_bits + 3) | (~@as(Word, 0) << 6),
    };

    const base_bitmap = makeView(base_words[0..], capacity);
    const drift_bitmap = makeView(drift_words[0..], capacity);
    const rejoin_bitmap = makeView(rejoin_words[0..], capacity);
    const missing_bridge_bitmap = makeView(missing_bridge_words[0..], capacity);
    const base_mask = makeMask(base_words[0..], capacity);
    const drift_mask = makeMask(drift_words[0..], capacity);
    const rejoin_mask = makeMask(rejoin_words[0..], capacity);
    const missing_bridge_mask = makeMask(missing_bridge_words[0..], capacity);

    try expectBitmapCpuMirror(base_words[0..], capacity, 7, 0);
    try expectBitmapCpuMirror(drift_words[0..], capacity, 5, 0);
    try expectBitmapCpuMirror(rejoin_words[0..], capacity, 7, 0);

    try testing.expect(drift_bitmap.isSubsetOf(base_bitmap));
    try testing.expect(!base_bitmap.isSubsetOf(drift_bitmap));
    try testing.expect(missing_bridge_bitmap.isSubsetOf(base_bitmap));
    try testing.expect(!missing_bridge_bitmap.intersects(drift_bitmap));
    try testing.expect(rejoin_bitmap.isSubsetOf(base_bitmap));
    try testing.expect(base_bitmap.isSubsetOf(rejoin_bitmap));

    try testing.expect(drift_mask.isSubsetOf(base_mask));
    try testing.expect(!base_mask.isSubsetOf(drift_mask));
    try testing.expect(missing_bridge_mask.isSubsetOf(base_mask));
    try testing.expect(!missing_bridge_mask.intersects(drift_mask));
    try testing.expect(rejoin_mask.isSubsetOf(base_mask));
    try testing.expect(base_mask.isSubsetOf(rejoin_mask));

    try testing.expectEqual(@as(?usize, 13), base_bitmap.nextSetBit(9));
    try testing.expectEqual(@as(?usize, 21), drift_bitmap.nextSetBit(9));
    try testing.expectEqual(@as(?usize, word_bits + 3), missing_bridge_bitmap.nextSetBit(14));
    try testing.expectEqual(@as(?usize, word_bits + 2), base_bitmap.nextClearBit(word_bits + 2));

    try testing.expectEqual(@as(?usize, 13), base_mask.nextCpu(9));
    try testing.expectEqual(@as(?usize, 21), drift_mask.nextCpu(9));
    try testing.expectEqual(@as(?usize, word_bits + 3), missing_bridge_mask.nextCpu(14));
    try testing.expectEqual(@as(?usize, word_bits + 2), base_mask.nextMissingCpu(word_bits + 2));
}
