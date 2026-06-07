const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(offset: usize) Word {
    return @as(Word, 1) << @intCast(offset);
}

fn expectMirrors(
    words: []const Word,
    capacity: usize,
    expected_count: usize,
    expected_first_present: ?usize,
    expected_first_missing: ?usize,
) !void {
    const bitmap = BitmapView.init(words, capacity);
    const cpumask = CpuMaskView.init(words, capacity);

    try std.testing.expectEqual(expected_count, bitmap.countSetBits());
    try std.testing.expectEqual(expected_count, cpumask.countPresentCpus());
    try std.testing.expectEqual(expected_first_present, bitmap.firstSetBit());
    try std.testing.expectEqual(expected_first_present, cpumask.firstCpu());
    try std.testing.expectEqual(expected_first_missing, bitmap.firstClearBit());
    try std.testing.expectEqual(expected_first_missing, cpumask.firstMissingCpu());
}

fn expectCursorMirror(words: []const Word, capacity: usize, start: usize, present: ?usize, missing: ?usize) !void {
    const bitmap = BitmapView.init(words, capacity);
    const cpumask = CpuMaskView.init(words, capacity);

    try std.testing.expectEqual(present, bitmap.nextSetBit(start));
    try std.testing.expectEqual(present, cpumask.nextCpu(start));
    try std.testing.expectEqual(missing, bitmap.nextClearBit(start));
    try std.testing.expectEqual(missing, cpumask.nextMissingCpu(start));
}

test "phase3 bitmap cpumask zigzag frontier mirrors low mid high migrations" {
    const capacity = word_bits * 4 + 11;
    const start_words = [_]Word{
        bit(0) | bit(7) | bit(15) | bit(31) | bit(47) | bit(63),
        bit(2) | bit(18) | bit(34) | bit(50),
        bit(5) | bit(21) | bit(37) | bit(53),
        bit(1) | bit(9) | bit(17) | bit(33) | bit(49),
        bit(10) | bit(40),
    };
    const migrated_words = [_]Word{
        bit(0) | bit(8) | bit(16) | bit(32) | bit(48),
        bit(1) | bit(17) | bit(33) | bit(49) | bit(63),
        bit(4) | bit(20) | bit(36) | bit(52),
        bit(0) | bit(8) | bit(16) | bit(32) | bit(48),
        bit(2) | bit(10) | bit(39),
    };
    const shared_anchor_words = [_]Word{
        bit(0) | bit(47),
        bit(33),
        bit(52),
        bit(1) | bit(48),
        bit(10) | bit(38),
    };
    const envelope_words = [_]Word{
        start_words[0] | migrated_words[0],
        start_words[1] | migrated_words[1],
        start_words[2] | migrated_words[2],
        start_words[3] | migrated_words[3],
        start_words[4] | migrated_words[4],
    };

    try expectMirrors(start_words[0..], capacity, 20, 0, 1);
    try expectMirrors(migrated_words[0..], capacity, 21, 0, 1);
    try expectMirrors(shared_anchor_words[0..], capacity, 7, 0, 1);
    try expectMirrors(envelope_words[0..], capacity, 39, 0, 1);

    try expectCursorMirror(start_words[0..], capacity, 1, 7, 1);
    try expectCursorMirror(start_words[0..], capacity, word_bits + 3, word_bits + 18, word_bits + 3);
    try expectCursorMirror(migrated_words[0..], capacity, word_bits * 3 + 2, word_bits * 3 + 8, word_bits * 3 + 2);
    try expectCursorMirror(migrated_words[0..], capacity, word_bits * 4 + 3, word_bits * 4 + 10, word_bits * 4 + 3);
    try expectCursorMirror(envelope_words[0..], capacity, capacity, null, null);

    const start_bitmap = BitmapView.init(start_words[0..], capacity);
    const migrated_bitmap = BitmapView.init(migrated_words[0..], capacity);
    const shared_anchor_bitmap = BitmapView.init(shared_anchor_words[0..], capacity);
    const envelope_bitmap = BitmapView.init(envelope_words[0..], capacity);
    const start_cpumask = CpuMaskView.init(start_words[0..], capacity);
    const migrated_cpumask = CpuMaskView.init(migrated_words[0..], capacity);
    const shared_anchor_cpumask = CpuMaskView.init(shared_anchor_words[0..], capacity);
    const envelope_cpumask = CpuMaskView.init(envelope_words[0..], capacity);

    try std.testing.expect(start_bitmap.isSubsetOf(envelope_bitmap));
    try std.testing.expect(start_cpumask.isSubsetOf(envelope_cpumask));
    try std.testing.expect(migrated_bitmap.isSubsetOf(envelope_bitmap));
    try std.testing.expect(migrated_cpumask.isSubsetOf(envelope_cpumask));
    try std.testing.expect(shared_anchor_bitmap.isSubsetOf(envelope_bitmap));
    try std.testing.expect(shared_anchor_cpumask.isSubsetOf(envelope_cpumask));
    try std.testing.expect(start_bitmap.intersects(shared_anchor_bitmap));
    try std.testing.expect(start_cpumask.intersects(shared_anchor_cpumask));
    try std.testing.expect(migrated_bitmap.intersects(shared_anchor_bitmap));
    try std.testing.expect(migrated_cpumask.intersects(shared_anchor_cpumask));
    try std.testing.expect(!envelope_bitmap.isSubsetOf(start_bitmap));
    try std.testing.expect(!envelope_cpumask.isSubsetOf(start_cpumask));
    try std.testing.expect(start_cpumask.hasCpu(word_bits * 4 + 10));
    try std.testing.expect(!start_cpumask.hasCpu(word_bits * 4 + 9));
}

test "phase3 bitmap cpumask zigzag frontier prunes and refills bounded tail" {
    const capacity = word_bits * 4 + 11;
    const frontier_words = [_]Word{
        bit(0) | bit(8) | bit(16) | bit(32) | bit(48),
        bit(1) | bit(17) | bit(33) | bit(49) | bit(63),
        bit(4) | bit(20) | bit(36) | bit(52),
        bit(0) | bit(8) | bit(16) | bit(32) | bit(48),
        bit(2) | bit(10) | bit(39),
    };
    const refill_words = [_]Word{
        frontier_words[0] | bit(1) | bit(9) | bit(24),
        frontier_words[1] | bit(0) | bit(18) | bit(40),
        frontier_words[2] | bit(3) | bit(21) | bit(44),
        frontier_words[3] | bit(7) | bit(17) | bit(40),
        frontier_words[4] | bit(0) | bit(5) | bit(48),
    };
    const pruned_words = [_]Word{
        bit(32) | bit(48),
        bit(33) | bit(49) | bit(63),
        bit(36) | bit(52),
        bit(32) | bit(48),
        bit(10) | bit(52),
    };

    try expectMirrors(frontier_words[0..], capacity, 21, 0, 1);
    try expectMirrors(refill_words[0..], capacity, 35, 0, 2);
    try expectMirrors(pruned_words[0..], capacity, 10, 32, 0);

    try expectCursorMirror(refill_words[0..], capacity, 2, 8, 2);
    try expectCursorMirror(refill_words[0..], capacity, word_bits + 40, word_bits + 40, word_bits + 41);
    try expectCursorMirror(pruned_words[0..], capacity, word_bits * 2 + 1, word_bits * 2 + 36, word_bits * 2 + 1);
    try expectCursorMirror(pruned_words[0..], capacity, word_bits * 4 + 10, word_bits * 4 + 10, null);

    const frontier_bitmap = BitmapView.init(frontier_words[0..], capacity);
    const refill_bitmap = BitmapView.init(refill_words[0..], capacity);
    const pruned_bitmap = BitmapView.init(pruned_words[0..], capacity);
    const frontier_cpumask = CpuMaskView.init(frontier_words[0..], capacity);
    const refill_cpumask = CpuMaskView.init(refill_words[0..], capacity);
    const pruned_cpumask = CpuMaskView.init(pruned_words[0..], capacity);

    try std.testing.expect(frontier_bitmap.isSubsetOf(refill_bitmap));
    try std.testing.expect(frontier_cpumask.isSubsetOf(refill_cpumask));
    try std.testing.expect(pruned_bitmap.isSubsetOf(frontier_bitmap));
    try std.testing.expect(pruned_cpumask.isSubsetOf(frontier_cpumask));
    try std.testing.expect(!refill_bitmap.isSubsetOf(frontier_bitmap));
    try std.testing.expect(!refill_cpumask.isSubsetOf(frontier_cpumask));
    try std.testing.expect(pruned_bitmap.intersects(refill_bitmap));
    try std.testing.expect(pruned_cpumask.intersects(refill_cpumask));
    try std.testing.expect(refill_cpumask.hasCpu(word_bits * 4 + 5));
    try std.testing.expect(!pruned_cpumask.hasCpu(word_bits * 4 + 5));
}
