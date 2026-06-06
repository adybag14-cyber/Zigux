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

fn expectViewMirrors(
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

test "phase3 bitmap cpumask braided bands keep direct mirrors aligned" {
    const capacity = word_bits * 3 + 17;
    const braided_words = [_]Word{
        localBit(2) | localBit(13) | localBit(31),
        localBit(5) | localBit(21) | localBit(40) | localBit(word_bits - 1),
        localBit(8) | localBit(34) | localBit(54),
        localBit(0) | localBit(7) | localBit(16) | localBit(25),
    };

    try expectViewMirrors(braided_words[0..], capacity, 13, 2, 0);

    const bitmap = BitmapView.init(braided_words[0..], capacity);
    const cpumask = CpuMaskView.init(braided_words[0..], capacity);

    try std.testing.expect(cpumask.hasCpu(2));
    try std.testing.expect(cpumask.hasCpu(word_bits + word_bits - 1));
    try std.testing.expect(cpumask.hasCpu(word_bits * 3 + 16));
    try std.testing.expect(!cpumask.hasCpu(word_bits * 3 + 15));

    try std.testing.expectEqual(@as(?usize, word_bits + 5), bitmap.nextSetBit(32));
    try std.testing.expectEqual(@as(?usize, word_bits + 5), cpumask.nextCpu(32));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), bitmap.nextSetBit(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), cpumask.nextCpu(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 7), bitmap.nextSetBit(word_bits * 3 + 1));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 7), cpumask.nextCpu(word_bits * 3 + 1));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), cpumask.nextCpu(capacity));
}

test "phase3 bitmap cpumask braided bands collapse and re-expand cleanly" {
    const capacity = word_bits * 3 + 17;
    const collapsed_words = [_]Word{
        localBit(13),
        localBit(21),
        localBit(34),
        localBit(7),
    };
    const braided_words = [_]Word{
        localBit(2) | localBit(13) | localBit(31),
        localBit(5) | localBit(21) | localBit(40) | localBit(word_bits - 1),
        localBit(8) | localBit(34) | localBit(54),
        localBit(0) | localBit(7) | localBit(16) | localBit(31),
    };
    const expanded_words = [_]Word{
        braided_words[0] | localBit(48),
        braided_words[1] | localBit(0) | localBit(33),
        braided_words[2] | localBit(12) | localBit(61),
        braided_words[3] | localBit(3) | localBit(11),
    };
    const separate_words = [_]Word{
        localBit(4) | localBit(9) | localBit(22),
        localBit(6) | localBit(18) | localBit(50),
        localBit(2) | localBit(15) | localBit(47),
        localBit(1) | localBit(5) | localBit(14),
    };

    try expectViewMirrors(collapsed_words[0..], capacity, 4, 13, 0);
    try expectViewMirrors(braided_words[0..], capacity, 13, 2, 0);
    try expectViewMirrors(expanded_words[0..], capacity, 20, 2, 0);

    const collapsed_bitmap = BitmapView.init(collapsed_words[0..], capacity);
    const braided_bitmap = BitmapView.init(braided_words[0..], capacity);
    const expanded_bitmap = BitmapView.init(expanded_words[0..], capacity);
    const separate_bitmap = BitmapView.init(separate_words[0..], capacity);
    const collapsed_cpumask = CpuMaskView.init(collapsed_words[0..], capacity);
    const braided_cpumask = CpuMaskView.init(braided_words[0..], capacity);
    const expanded_cpumask = CpuMaskView.init(expanded_words[0..], capacity);
    const separate_cpumask = CpuMaskView.init(separate_words[0..], capacity);

    try std.testing.expect(collapsed_bitmap.isSubsetOf(braided_bitmap));
    try std.testing.expect(collapsed_cpumask.isSubsetOf(braided_cpumask));
    try std.testing.expect(braided_bitmap.isSubsetOf(expanded_bitmap));
    try std.testing.expect(braided_cpumask.isSubsetOf(expanded_cpumask));
    try std.testing.expect(expanded_bitmap.intersects(collapsed_bitmap));
    try std.testing.expect(expanded_cpumask.intersects(collapsed_cpumask));
    try std.testing.expect(!collapsed_bitmap.intersects(separate_bitmap));
    try std.testing.expect(!collapsed_cpumask.intersects(separate_cpumask));

    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 16), expanded_bitmap.nextSetBit(word_bits * 3 + 12));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 16), expanded_cpumask.nextCpu(word_bits * 3 + 12));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 12), expanded_bitmap.nextClearBit(word_bits * 3 + 12));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 12), expanded_cpumask.nextMissingCpu(word_bits * 3 + 12));
}
