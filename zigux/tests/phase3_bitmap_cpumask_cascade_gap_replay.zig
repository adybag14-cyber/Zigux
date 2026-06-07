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

test "lane27 cascade gap keeps bitmap and cpumask mirrors aligned" {
    const capacity = (word_bits * 2) + 13;
    const primary_words = [_]Word{
        bit(0) | bit(1) | bit(3) | bit(6) | bit(10) | bit(15) | bit(21) | bit(28),
        bit(word_bits) | bit(word_bits + 2) | bit(word_bits + 5) | bit(word_bits + 9) | bit(word_bits + 14) | bit(word_bits + 20) | bit(word_bits + 27) | bit((word_bits * 2) - 1),
        bit((word_bits * 2) + 1) | bit((word_bits * 2) + 4) | bit((word_bits * 2) + 8) | bit((word_bits * 2) + 12) | (~@as(Word, 0) << 13),
    };
    const left_cascade_words = [_]Word{
        bit(0) | bit(3) | bit(10) | bit(21),
        bit(word_bits + 2) | bit(word_bits + 9) | bit(word_bits + 20),
        bit((word_bits * 2) + 4) | bit((word_bits * 2) + 12) | (~@as(Word, 0) << 13),
    };
    const right_cascade_words = [_]Word{
        bit(1) | bit(6) | bit(15) | bit(28),
        bit(word_bits) | bit(word_bits + 5) | bit(word_bits + 14) | bit(word_bits + 27) | bit((word_bits * 2) - 1),
        bit((word_bits * 2) + 1) | bit((word_bits * 2) + 8) | (~@as(Word, 0) << 13),
    };
    const disjoint_gap_words = [_]Word{
        bit(2) | bit(4) | bit(8) | bit(13) | bit(19) | bit(26),
        bit(word_bits + 1) | bit(word_bits + 4) | bit(word_bits + 8) | bit(word_bits + 13) | bit(word_bits + 19) | bit(word_bits + 26),
        bit((word_bits * 2) + 0) | bit((word_bits * 2) + 3) | bit((word_bits * 2) + 7) | bit((word_bits * 2) + 11) | (~@as(Word, 0) << 13),
    };

    const primary_bitmap = makeView(primary_words[0..], capacity);
    const left_bitmap = makeView(left_cascade_words[0..], capacity);
    const right_bitmap = makeView(right_cascade_words[0..], capacity);
    const disjoint_bitmap = makeView(disjoint_gap_words[0..], capacity);
    const primary_mask = makeMask(primary_words[0..], capacity);
    const left_mask = makeMask(left_cascade_words[0..], capacity);
    const right_mask = makeMask(right_cascade_words[0..], capacity);
    const disjoint_mask = makeMask(disjoint_gap_words[0..], capacity);

    try expectBitmapCpuMirror(primary_words[0..], capacity, 20, 2);
    try expectBitmapCpuMirror(left_cascade_words[0..], capacity, 9, 1);
    try expectBitmapCpuMirror(right_cascade_words[0..], capacity, 11, 0);
    try expectBitmapCpuMirror(disjoint_gap_words[0..], capacity, 16, 0);

    try testing.expect(left_bitmap.isSubsetOf(primary_bitmap));
    try testing.expect(right_bitmap.isSubsetOf(primary_bitmap));
    try testing.expect(!primary_bitmap.isSubsetOf(left_bitmap));
    try testing.expect(!left_bitmap.intersects(right_bitmap));
    try testing.expect(!primary_bitmap.intersects(disjoint_bitmap));

    try testing.expect(left_mask.isSubsetOf(primary_mask));
    try testing.expect(right_mask.isSubsetOf(primary_mask));
    try testing.expect(!primary_mask.isSubsetOf(left_mask));
    try testing.expect(!left_mask.intersects(right_mask));
    try testing.expect(!primary_mask.intersects(disjoint_mask));

    try testing.expectEqual(@as(?usize, 0), primary_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 3), primary_bitmap.nextSetBit(2));
    try testing.expectEqual(@as(?usize, word_bits + 2), primary_bitmap.nextSetBit(word_bits + 1));
    try testing.expectEqual(@as(?usize, (word_bits * 2) + 8), primary_bitmap.nextSetBit((word_bits * 2) + 5));
    try testing.expectEqual(@as(?usize, null), primary_bitmap.nextSetBit(capacity));

    try testing.expectEqual(@as(?usize, 0), primary_mask.firstCpu());
    try testing.expectEqual(@as(?usize, 3), primary_mask.nextCpu(2));
    try testing.expectEqual(@as(?usize, word_bits + 2), primary_mask.nextCpu(word_bits + 1));
    try testing.expectEqual(@as(?usize, (word_bits * 2) + 8), primary_mask.nextCpu((word_bits * 2) + 5));
    try testing.expectEqual(@as(?usize, null), primary_mask.nextCpu(capacity));
}

test "lane27 cascade gap rejects stale fill before tail closure" {
    const capacity = word_bits + 11;
    const base_words = [_]Word{
        bit(4) | bit(7) | bit(11) | bit(16) | bit(22) | bit(29),
        bit(word_bits + 1) | bit(word_bits + 5) | bit(word_bits + 10) | (~@as(Word, 0) << 11),
    };
    const stale_fill_words = [_]Word{
        bit(4) | bit(7) | bit(11) | bit(16) | bit(18) | bit(22) | bit(29),
        bit(word_bits + 1) | bit(word_bits + 5) | bit(word_bits + 9) | bit(word_bits + 10) | (~@as(Word, 0) << 11),
    };
    const tail_closure_words = [_]Word{
        bit(4) | bit(7) | bit(11) | bit(16) | bit(22) | bit(29),
        bit(word_bits + 1) | bit(word_bits + 5) | bit(word_bits + 9) | bit(word_bits + 10) | (~@as(Word, 0) << 11),
    };
    const stale_only_words = [_]Word{
        bit(18),
        bit(word_bits + 9) | (~@as(Word, 0) << 11),
    };

    const base_bitmap = makeView(base_words[0..], capacity);
    const stale_fill_bitmap = makeView(stale_fill_words[0..], capacity);
    const tail_closure_bitmap = makeView(tail_closure_words[0..], capacity);
    const stale_only_bitmap = makeView(stale_only_words[0..], capacity);
    const base_mask = makeMask(base_words[0..], capacity);
    const stale_fill_mask = makeMask(stale_fill_words[0..], capacity);
    const tail_closure_mask = makeMask(tail_closure_words[0..], capacity);
    const stale_only_mask = makeMask(stale_only_words[0..], capacity);

    try expectBitmapCpuMirror(base_words[0..], capacity, 9, 0);
    try expectBitmapCpuMirror(stale_fill_words[0..], capacity, 11, 0);
    try expectBitmapCpuMirror(tail_closure_words[0..], capacity, 10, 0);

    try testing.expect(base_bitmap.isSubsetOf(stale_fill_bitmap));
    try testing.expect(!stale_fill_bitmap.isSubsetOf(base_bitmap));
    try testing.expect(tail_closure_bitmap.isSubsetOf(stale_fill_bitmap));
    try testing.expect(!stale_only_bitmap.intersects(base_bitmap));
    try testing.expect(stale_only_bitmap.intersects(stale_fill_bitmap));
    try testing.expect(stale_only_bitmap.intersects(tail_closure_bitmap));

    try testing.expect(base_mask.isSubsetOf(stale_fill_mask));
    try testing.expect(!stale_fill_mask.isSubsetOf(base_mask));
    try testing.expect(tail_closure_mask.isSubsetOf(stale_fill_mask));
    try testing.expect(!stale_only_mask.intersects(base_mask));
    try testing.expect(stale_only_mask.intersects(stale_fill_mask));
    try testing.expect(stale_only_mask.intersects(tail_closure_mask));

    try testing.expectEqual(@as(?usize, 22), base_bitmap.nextSetBit(17));
    try testing.expectEqual(@as(?usize, 18), stale_fill_bitmap.nextSetBit(17));
    try testing.expectEqual(@as(?usize, word_bits + 9), tail_closure_bitmap.nextSetBit(word_bits + 6));
    try testing.expectEqual(@as(?usize, word_bits + 6), base_bitmap.nextClearBit(word_bits + 6));

    try testing.expectEqual(@as(?usize, 22), base_mask.nextCpu(17));
    try testing.expectEqual(@as(?usize, 18), stale_fill_mask.nextCpu(17));
    try testing.expectEqual(@as(?usize, word_bits + 9), tail_closure_mask.nextCpu(word_bits + 6));
    try testing.expectEqual(@as(?usize, word_bits + 6), base_mask.nextMissingCpu(word_bits + 6));
}
