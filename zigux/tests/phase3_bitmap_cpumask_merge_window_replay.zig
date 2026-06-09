const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn tailNoise(valid_bits: usize) Word {
    if (valid_bits == 0) return std.math.maxInt(Word);
    if (valid_bits >= word_bits) return 0;
    return ~((@as(Word, 1) << @intCast(valid_bits)) - 1);
}

fn makeView(words: []const Word, bit_len: usize) bitmap_view.BitmapView {
    return bitmap_view.BitmapView.init(words, bit_len);
}

fn makeCpuMask(words: []const Word, cpu_capacity: usize) cpumask_view.CpuMaskView {
    return cpumask_view.CpuMaskView.init(words, cpu_capacity);
}

test "merge window mirrors staged bitmap and cpumask lanes" {
    const capacity = word_bits * 3 + 10;
    const intake_words = [_]Word{
        bit(1) | bit(17) | bit(33) | bit(49),
        bit(word_bits + 5) | bit(word_bits + 21) |
            bit(word_bits + 37) | bit(word_bits + 53),
        bit(word_bits * 2 + 9) | bit(word_bits * 2 + 25) |
            bit(word_bits * 2 + 41) | bit(word_bits * 2 + 57),
        bit(word_bits * 3 + 2) | bit(word_bits * 3 + 8) | tailNoise(10),
    };
    const staged_words = [_]Word{
        bit(4) | bit(20) | bit(36) | bit(52),
        bit(word_bits + 8) | bit(word_bits + 24) |
            bit(word_bits + 40) | bit(word_bits + 56),
        bit(word_bits * 2 + 12) | bit(word_bits * 2 + 28) |
            bit(word_bits * 2 + 44) | bit(word_bits * 2 + 60),
        bit(word_bits * 3 + 4) | tailNoise(10),
    };
    const drain_words = [_]Word{
        bit(7) | bit(23) | bit(39) | bit(55),
        bit(word_bits + 11) | bit(word_bits + 27) |
            bit(word_bits + 43) | bit(word_bits + 59),
        bit(word_bits * 2 + 15) | bit(word_bits * 2 + 31) |
            bit(word_bits * 2 + 47) | bit(word_bits * 2 + 63),
        bit(word_bits * 3 + 6) | tailNoise(10),
    };
    const merged_words = [_]Word{
        intake_words[0] | staged_words[0] | drain_words[0],
        intake_words[1] | staged_words[1] | drain_words[1],
        intake_words[2] | staged_words[2] | drain_words[2],
        intake_words[3] | staged_words[3] | drain_words[3],
    };
    const guard_words = [_]Word{
        bit(0) | bit(14) | bit(30) | bit(46) | bit(62),
        bit(word_bits + 2) | bit(word_bits + 18) |
            bit(word_bits + 34) | bit(word_bits + 50),
        bit(word_bits * 2 + 4) | bit(word_bits * 2 + 22) |
            bit(word_bits * 2 + 38) | bit(word_bits * 2 + 54),
        bit(word_bits * 3 + 0) | bit(word_bits * 3 + 5) |
            bit(word_bits * 3 + 9),
    };

    const intake = makeView(intake_words[0..], capacity);
    const staged = makeView(staged_words[0..], capacity);
    const drain = makeView(drain_words[0..], capacity);
    const merged = makeView(merged_words[0..], capacity);
    const guard = makeView(guard_words[0..], capacity);
    const intake_mask = makeCpuMask(intake_words[0..], capacity);
    const staged_mask = makeCpuMask(staged_words[0..], capacity);
    const drain_mask = makeCpuMask(drain_words[0..], capacity);
    const merged_mask = makeCpuMask(merged_words[0..], capacity);
    const guard_mask = makeCpuMask(guard_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 14), intake.countSetBits());
    try std.testing.expectEqual(intake.countSetBits(), intake_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 13), staged.countSetBits());
    try std.testing.expectEqual(staged.countSetBits(), staged_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 13), drain.countSetBits());
    try std.testing.expectEqual(drain.countSetBits(), drain_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 40), merged.countSetBits());
    try std.testing.expectEqual(merged.countSetBits(), merged_mask.countPresentCpus());

    try std.testing.expect(intake.isSubsetOf(merged));
    try std.testing.expect(staged.isSubsetOf(merged));
    try std.testing.expect(drain.isSubsetOf(merged));
    try std.testing.expect(intake_mask.isSubsetOf(merged_mask));
    try std.testing.expect(staged_mask.isSubsetOf(merged_mask));
    try std.testing.expect(drain_mask.isSubsetOf(merged_mask));
    try std.testing.expect(!merged.isSubsetOf(intake));
    try std.testing.expect(!merged_mask.isSubsetOf(intake_mask));
    try std.testing.expect(!intake.intersects(staged));
    try std.testing.expect(!intake_mask.intersects(staged_mask));
    try std.testing.expect(!staged.intersects(drain));
    try std.testing.expect(!staged_mask.intersects(drain_mask));
    try std.testing.expect(!merged.intersects(guard));
    try std.testing.expect(!merged_mask.intersects(guard_mask));

    try std.testing.expect(merged.isSet(word_bits * 3 + 8));
    try std.testing.expect(merged_mask.hasCpu(word_bits * 3 + 8));
    try std.testing.expectEqual(@as(?usize, 1), merged.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 1), merged_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 4), merged.nextSetBit(2));
    try std.testing.expectEqual(@as(?usize, 4), merged_mask.nextCpu(2));
    try std.testing.expectEqual(@as(?usize, word_bits + 59), merged.nextSetBit(word_bits + 57));
    try std.testing.expectEqual(@as(?usize, word_bits + 59), merged_mask.nextCpu(word_bits + 57));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 63), merged.nextSetBit(word_bits * 2 + 61));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 63), merged_mask.nextCpu(word_bits * 2 + 61));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 8), merged.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 8), merged_mask.lastCpu());

    try std.testing.expectEqual(@as(?usize, 0), merged.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), merged_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 3), merged.nextClearBit(word_bits * 3 + 3));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 3), merged_mask.nextMissingCpu(word_bits * 3 + 3));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 9), merged.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 9), merged_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), merged.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), merged_mask.nextCpu(capacity));
}

test "merge window rollback keeps committed and skipped lanes separate" {
    const capacity = word_bits * 2 + 11;
    const committed_words = [_]Word{
        bit(3) | bit(19) | bit(35) | bit(51),
        bit(word_bits + 6) | bit(word_bits + 30) |
            bit(word_bits + 54),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 10) | tailNoise(11),
    };
    const skipped_words = [_]Word{
        bit(10) | bit(26) | bit(42) | bit(58),
        bit(word_bits + 14) | bit(word_bits + 38) |
            bit(word_bits + 62),
        bit(word_bits * 2 + 4) | bit(word_bits * 2 + 8) | tailNoise(11),
    };
    const window_words = [_]Word{
        committed_words[0] | skipped_words[0],
        committed_words[1] | skipped_words[1],
        committed_words[2] | skipped_words[2],
    };

    const committed = makeView(committed_words[0..], capacity);
    const skipped = makeView(skipped_words[0..], capacity);
    const window = makeView(window_words[0..], capacity);
    const committed_mask = makeCpuMask(committed_words[0..], capacity);
    const skipped_mask = makeCpuMask(skipped_words[0..], capacity);
    const window_mask = makeCpuMask(window_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 9), committed.countSetBits());
    try std.testing.expectEqual(committed.countSetBits(), committed_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 9), skipped.countSetBits());
    try std.testing.expectEqual(skipped.countSetBits(), skipped_mask.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 18), window.countSetBits());
    try std.testing.expectEqual(window.countSetBits(), window_mask.countPresentCpus());

    try std.testing.expect(committed.isSubsetOf(window));
    try std.testing.expect(skipped.isSubsetOf(window));
    try std.testing.expect(committed_mask.isSubsetOf(window_mask));
    try std.testing.expect(skipped_mask.isSubsetOf(window_mask));
    try std.testing.expect(!window.isSubsetOf(committed));
    try std.testing.expect(!window_mask.isSubsetOf(committed_mask));
    try std.testing.expect(!committed.intersects(skipped));
    try std.testing.expect(!committed_mask.intersects(skipped_mask));

    try std.testing.expectEqual(@as(?usize, 3), committed.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 3), committed_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 19), committed.nextSetBit(4));
    try std.testing.expectEqual(@as(?usize, 19), committed_mask.nextCpu(4));
    try std.testing.expectEqual(@as(?usize, word_bits + 30), committed.nextSetBit(word_bits + 7));
    try std.testing.expectEqual(@as(?usize, word_bits + 30), committed_mask.nextCpu(word_bits + 7));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 10), committed.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 10), committed_mask.lastCpu());

    try std.testing.expectEqual(@as(?usize, 10), skipped.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 10), skipped_mask.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), skipped.lastSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 8), skipped_mask.lastCpu());

    try std.testing.expectEqual(@as(?usize, 0), committed.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 0), committed_mask.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 2), committed.nextClearBit(word_bits * 2 + 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 2), committed_mask.nextMissingCpu(word_bits * 2 + 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 9), committed.lastClearBit());
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 9), committed_mask.lastMissingCpu());
    try std.testing.expectEqual(@as(?usize, null), window.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), window_mask.nextCpu(capacity));
}
