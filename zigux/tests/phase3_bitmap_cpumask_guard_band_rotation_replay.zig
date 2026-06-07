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

test "phase3 bitmap cpumask guard bands rotate around stable anchors" {
    const capacity = word_bits * 3 + 19;
    const base_words = [_]Word{
        bit(0) | bit(6) | bit(12) | bit(18) | bit(24) | bit(30) | bit(36) | bit(42) | bit(48) | bit(54) | bit(60),
        bit(3) | bit(9) | bit(15) | bit(21) | bit(27) | bit(33) | bit(39) | bit(45) | bit(51) | bit(57) | bit(63),
        bit(1) | bit(8) | bit(16) | bit(24) | bit(32) | bit(40) | bit(48) | bit(56),
        bit(0) | bit(5) | bit(18) | bit(63),
    };
    const rotated_words = [_]Word{
        bit(0) | bit(2) | bit(8) | bit(14) | bit(20) | bit(26) | bit(32) | bit(38) | bit(44) | bit(50) | bit(56) | bit(62),
        bit(0) | bit(6) | bit(12) | bit(18) | bit(24) | bit(30) | bit(36) | bit(42) | bit(48) | bit(54) | bit(60) | bit(63),
        bit(4) | bit(12) | bit(20) | bit(28) | bit(32) | bit(36) | bit(44) | bit(52) | bit(60),
        bit(1) | bit(6) | bit(18) | bit(50),
    };
    const anchor_words = [_]Word{
        bit(0),
        bit(63),
        bit(32),
        bit(18) | bit(50),
    };
    const envelope_words = [_]Word{
        base_words[0] | rotated_words[0],
        base_words[1] | rotated_words[1],
        base_words[2] | rotated_words[2],
        base_words[3] | rotated_words[3],
    };

    try expectMirrors(base_words[0..], capacity, 33, 0, 1);
    try expectMirrors(rotated_words[0..], capacity, 36, 0, 1);
    try expectMirrors(anchor_words[0..], capacity, 4, 0, 1);
    try expectMirrors(envelope_words[0..], capacity, 65, 0, 1);

    try expectCursorMirror(base_words[0..], capacity, 1, 6, 1);
    try expectCursorMirror(rotated_words[0..], capacity, word_bits + 61, word_bits + 63, word_bits + 61);
    try expectCursorMirror(envelope_words[0..], capacity, word_bits * 2 + 33, word_bits * 2 + 36, word_bits * 2 + 33);
    try expectCursorMirror(envelope_words[0..], capacity, capacity, null, null);

    const base_bitmap = BitmapView.init(base_words[0..], capacity);
    const rotated_bitmap = BitmapView.init(rotated_words[0..], capacity);
    const anchor_bitmap = BitmapView.init(anchor_words[0..], capacity);
    const envelope_bitmap = BitmapView.init(envelope_words[0..], capacity);
    const base_cpumask = CpuMaskView.init(base_words[0..], capacity);
    const rotated_cpumask = CpuMaskView.init(rotated_words[0..], capacity);
    const anchor_cpumask = CpuMaskView.init(anchor_words[0..], capacity);
    const envelope_cpumask = CpuMaskView.init(envelope_words[0..], capacity);

    try std.testing.expect(base_bitmap.isSubsetOf(envelope_bitmap));
    try std.testing.expect(base_cpumask.isSubsetOf(envelope_cpumask));
    try std.testing.expect(rotated_bitmap.isSubsetOf(envelope_bitmap));
    try std.testing.expect(rotated_cpumask.isSubsetOf(envelope_cpumask));
    try std.testing.expect(anchor_bitmap.isSubsetOf(base_bitmap));
    try std.testing.expect(anchor_cpumask.isSubsetOf(base_cpumask));
    try std.testing.expect(anchor_bitmap.isSubsetOf(rotated_bitmap));
    try std.testing.expect(anchor_cpumask.isSubsetOf(rotated_cpumask));
    try std.testing.expect(base_bitmap.intersects(rotated_bitmap));
    try std.testing.expect(base_cpumask.intersects(rotated_cpumask));
    try std.testing.expect(!envelope_bitmap.isSubsetOf(base_bitmap));
    try std.testing.expect(!envelope_cpumask.isSubsetOf(base_cpumask));
    try std.testing.expect(base_cpumask.hasCpu(word_bits * 3 + 18));
    try std.testing.expect(!base_cpumask.hasCpu(word_bits * 3 + 17));
}

test "phase3 bitmap cpumask guard bands collapse and expand under tail mask" {
    const capacity = word_bits * 3 + 19;
    const collapsed_words = [_]Word{
        bit(0) | bit(60),
        bit(63),
        bit(32),
        bit(18) | bit(50),
    };
    const envelope_words = [_]Word{
        bit(0) | bit(2) | bit(6) | bit(8) | bit(12) | bit(14) | bit(18) | bit(20) | bit(24) | bit(26) | bit(30) | bit(32) | bit(36) | bit(38) | bit(42) | bit(44) | bit(48) | bit(50) | bit(54) | bit(56) | bit(60) | bit(62),
        bit(0) | bit(3) | bit(6) | bit(9) | bit(12) | bit(15) | bit(18) | bit(21) | bit(24) | bit(27) | bit(30) | bit(33) | bit(36) | bit(39) | bit(42) | bit(45) | bit(48) | bit(51) | bit(54) | bit(57) | bit(60) | bit(63),
        bit(1) | bit(4) | bit(8) | bit(12) | bit(16) | bit(20) | bit(24) | bit(28) | bit(32) | bit(36) | bit(40) | bit(44) | bit(48) | bit(52) | bit(56) | bit(60),
        bit(0) | bit(1) | bit(5) | bit(6) | bit(18) | bit(63),
    };
    const expanded_words = [_]Word{
        envelope_words[0] | bit(1) | bit(3) | bit(5),
        envelope_words[1] | bit(1) | bit(2) | bit(4),
        envelope_words[2] | bit(0) | bit(2) | bit(3),
        envelope_words[3] | bit(2) | bit(3) | bit(4) | bit(8) | bit(61),
    };

    try expectMirrors(collapsed_words[0..], capacity, 5, 0, 1);
    try expectMirrors(envelope_words[0..], capacity, 65, 0, 1);
    try expectMirrors(expanded_words[0..], capacity, 78, 0, 4);

    try expectCursorMirror(collapsed_words[0..], capacity, 1, 60, 1);
    try expectCursorMirror(envelope_words[0..], capacity, word_bits + 1, word_bits + 3, word_bits + 1);
    try expectCursorMirror(expanded_words[0..], capacity, word_bits * 3 + 8, word_bits * 3 + 8, word_bits * 3 + 9);
    try expectCursorMirror(expanded_words[0..], capacity, word_bits * 3 + 19, null, null);

    const collapsed_bitmap = BitmapView.init(collapsed_words[0..], capacity);
    const envelope_bitmap = BitmapView.init(envelope_words[0..], capacity);
    const expanded_bitmap = BitmapView.init(expanded_words[0..], capacity);
    const collapsed_cpumask = CpuMaskView.init(collapsed_words[0..], capacity);
    const envelope_cpumask = CpuMaskView.init(envelope_words[0..], capacity);
    const expanded_cpumask = CpuMaskView.init(expanded_words[0..], capacity);

    try std.testing.expect(collapsed_bitmap.isSubsetOf(envelope_bitmap));
    try std.testing.expect(collapsed_cpumask.isSubsetOf(envelope_cpumask));
    try std.testing.expect(envelope_bitmap.isSubsetOf(expanded_bitmap));
    try std.testing.expect(envelope_cpumask.isSubsetOf(expanded_cpumask));
    try std.testing.expect(!expanded_bitmap.isSubsetOf(envelope_bitmap));
    try std.testing.expect(!expanded_cpumask.isSubsetOf(envelope_cpumask));
    try std.testing.expect(collapsed_bitmap.intersects(expanded_bitmap));
    try std.testing.expect(collapsed_cpumask.intersects(expanded_cpumask));
    try std.testing.expect(expanded_cpumask.hasCpu(word_bits * 3 + 8));
    try std.testing.expect(!expanded_cpumask.hasCpu(word_bits * 3 + 9));
}
