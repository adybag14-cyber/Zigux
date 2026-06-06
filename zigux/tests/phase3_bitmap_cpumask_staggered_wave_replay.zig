const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn localBit(offset: usize) Word {
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

test "phase3 bitmap cpumask staggered wave keeps cursor mirrors aligned" {
    const capacity = word_bits * 3 + 11;
    const words = [_]Word{
        localBit(3) | localBit(11) | localBit(27) | localBit(48),
        localBit(0) | localBit(19) | localBit(41) | localBit(word_bits - 1),
        localBit(7) | localBit(22) | localBit(36) | localBit(55),
        localBit(2) | localBit(10) | localBit(20) | localBit(33),
    };

    try expectMirrors(words[0..], capacity, 14, 3, 0);

    const bitmap = BitmapView.init(words[0..], capacity);
    const cpumask = CpuMaskView.init(words[0..], capacity);

    try std.testing.expect(cpumask.hasCpu(word_bits));
    try std.testing.expect(cpumask.hasCpu(word_bits * 3 + 10));
    try std.testing.expect(!cpumask.hasCpu(word_bits * 3 + 9));
    try std.testing.expectEqual(@as(?usize, word_bits + 19), bitmap.nextSetBit(word_bits + 1));
    try std.testing.expectEqual(@as(?usize, word_bits + 19), cpumask.nextCpu(word_bits + 1));
    try std.testing.expectEqual(@as(?usize, word_bits * 2), bitmap.nextClearBit(word_bits + word_bits - 1));
    try std.testing.expectEqual(@as(?usize, word_bits * 2), cpumask.nextMissingCpu(word_bits + word_bits - 1));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextCpu(capacity));
}

test "phase3 bitmap cpumask staggered wave promotion and prune stay bounded" {
    const capacity = word_bits * 3 + 11;
    const anchor_words = [_]Word{
        localBit(3) | localBit(27),
        localBit(19) | localBit(word_bits - 1),
        localBit(7) | localBit(55),
        localBit(10) | localBit(18),
    };
    const promoted_words = [_]Word{
        anchor_words[0] | localBit(11) | localBit(48),
        anchor_words[1] | localBit(0) | localBit(41),
        anchor_words[2] | localBit(22) | localBit(36),
        anchor_words[3] | localBit(2) | localBit(20),
    };
    const pruned_words = [_]Word{
        localBit(27),
        localBit(19),
        localBit(55),
        localBit(10) | localBit(30),
    };
    const separate_words = [_]Word{
        localBit(5) | localBit(9),
        localBit(7) | localBit(23),
        localBit(1) | localBit(44),
        localBit(0) | localBit(8) | localBit(40),
    };

    try expectMirrors(anchor_words[0..], capacity, 7, 3, 0);
    try expectMirrors(promoted_words[0..], capacity, 14, 3, 0);
    try expectMirrors(pruned_words[0..], capacity, 4, 27, 0);

    const anchor_bitmap = BitmapView.init(anchor_words[0..], capacity);
    const promoted_bitmap = BitmapView.init(promoted_words[0..], capacity);
    const pruned_bitmap = BitmapView.init(pruned_words[0..], capacity);
    const separate_bitmap = BitmapView.init(separate_words[0..], capacity);
    const anchor_cpumask = CpuMaskView.init(anchor_words[0..], capacity);
    const promoted_cpumask = CpuMaskView.init(promoted_words[0..], capacity);
    const pruned_cpumask = CpuMaskView.init(pruned_words[0..], capacity);
    const separate_cpumask = CpuMaskView.init(separate_words[0..], capacity);

    try std.testing.expect(anchor_bitmap.isSubsetOf(promoted_bitmap));
    try std.testing.expect(anchor_cpumask.isSubsetOf(promoted_cpumask));
    try std.testing.expect(pruned_bitmap.isSubsetOf(promoted_bitmap));
    try std.testing.expect(pruned_cpumask.isSubsetOf(promoted_cpumask));
    try std.testing.expect(promoted_bitmap.intersects(pruned_bitmap));
    try std.testing.expect(promoted_cpumask.intersects(pruned_cpumask));
    try std.testing.expect(!anchor_bitmap.intersects(separate_bitmap));
    try std.testing.expect(!anchor_cpumask.intersects(separate_cpumask));

    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 10), promoted_bitmap.nextSetBit(word_bits * 3 + 3));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 10), promoted_cpumask.nextCpu(word_bits * 3 + 3));
    try std.testing.expectEqual(@as(?usize, null), promoted_bitmap.nextSetBit(word_bits * 3 + 11));
    try std.testing.expectEqual(@as(?usize, null), promoted_cpumask.nextCpu(word_bits * 3 + 11));
}
