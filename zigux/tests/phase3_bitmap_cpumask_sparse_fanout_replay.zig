const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn expectMirror(
    words: []const Word,
    bit_len: usize,
    expected_count: usize,
    first_present: ?usize,
    first_missing: ?usize,
    present_cpus: []const usize,
    missing_cpus: []const usize,
) !void {
    const bitmap = bitmap_view.BitmapView.init(words, bit_len);
    const cpus = cpumask_view.CpuMaskView.init(words, bit_len);

    try std.testing.expectEqual(expected_count, bitmap.countSetBits());
    try std.testing.expectEqual(expected_count, cpus.countPresentCpus());
    try std.testing.expectEqual(first_present, bitmap.firstSetBit());
    try std.testing.expectEqual(first_present, cpus.firstCpu());
    try std.testing.expectEqual(first_missing, bitmap.firstClearBit());
    try std.testing.expectEqual(first_missing, cpus.firstMissingCpu());

    for (present_cpus) |cpu| {
        try std.testing.expect(bitmap.isSet(cpu));
        try std.testing.expect(cpus.hasCpu(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), bitmap.nextSetBit(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), cpus.nextCpu(cpu));
    }

    for (missing_cpus) |cpu| {
        try std.testing.expect(!bitmap.isSet(cpu));
        try std.testing.expect(!cpus.hasCpu(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), bitmap.nextClearBit(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), cpus.nextMissingCpu(cpu));
    }
}

test "bitmap and cpumask sparse fanout mirrors prune back into a subset" {
    const bit_len = word_bits * 4 + 13;
    const active_tail_mask = (@as(Word, 1) << 13) - 1;
    const tail_noise = ~active_tail_mask;

    var fanout_words = [_]Word{
        bit(0) | bit(7) | bit(word_bits - 2),
        bit(word_bits + 4) | bit(word_bits + 23),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 31),
        bit(word_bits * 3) | bit(word_bits * 3 + 17) | bit(word_bits * 4 - 1),
        bit(word_bits * 4 + 2) | bit(word_bits * 4 + 12) | tail_noise,
    };
    const anchor_words = [_]Word{
        bit(0) | bit(word_bits - 2),
        bit(word_bits + 4),
        bit(word_bits * 2 + 31),
        bit(word_bits * 3 + 17) | bit(word_bits * 4 - 1),
        bit(word_bits * 4 + 12) | tail_noise,
    };
    const disjoint_words = [_]Word{
        bit(3) | bit(word_bits - 1),
        bit(word_bits + 8),
        bit(word_bits * 2 + 9),
        bit(word_bits * 3 + 11),
        bit(word_bits * 4 + 1) | tail_noise,
    };

    try expectMirror(fanout_words[0..], bit_len, 12, 0, 1, &.{
        0,
        7,
        word_bits - 2,
        word_bits + 4,
        word_bits + 23,
        word_bits * 2 + 1,
        word_bits * 2 + 31,
        word_bits * 3,
        word_bits * 3 + 17,
        word_bits * 4 - 1,
        word_bits * 4 + 12,
    }, &.{
        1,
        word_bits + 5,
        word_bits * 2 + 2,
        word_bits * 3 + 1,
        word_bits * 4 + 3,
    });

    const fanout_bitmap = bitmap_view.BitmapView.init(fanout_words[0..], bit_len);
    const anchor_bitmap = bitmap_view.BitmapView.init(anchor_words[0..], bit_len);
    const disjoint_bitmap = bitmap_view.BitmapView.init(disjoint_words[0..], bit_len);
    const fanout_cpus = cpumask_view.CpuMaskView.init(fanout_words[0..], bit_len);
    const anchor_cpus = cpumask_view.CpuMaskView.init(anchor_words[0..], bit_len);
    const disjoint_cpus = cpumask_view.CpuMaskView.init(disjoint_words[0..], bit_len);

    try std.testing.expect(anchor_bitmap.isSubsetOf(fanout_bitmap));
    try std.testing.expect(anchor_cpus.isSubsetOf(fanout_cpus));
    try std.testing.expect(!fanout_bitmap.isSubsetOf(anchor_bitmap));
    try std.testing.expect(!fanout_cpus.isSubsetOf(anchor_cpus));
    try std.testing.expect(fanout_bitmap.intersects(anchor_bitmap));
    try std.testing.expect(fanout_cpus.intersects(anchor_cpus));
    try std.testing.expect(!fanout_bitmap.intersects(disjoint_bitmap));
    try std.testing.expect(!fanout_cpus.intersects(disjoint_cpus));

    fanout_words[0] &= ~bit(7);
    fanout_words[1] &= ~bit(word_bits + 23);
    fanout_words[2] &= ~bit(word_bits * 2 + 1);
    fanout_words[3] &= ~bit(word_bits * 3);
    fanout_words[4] &= ~bit(word_bits * 4 + 2);

    const pruned_bitmap = bitmap_view.BitmapView.init(fanout_words[0..], bit_len);
    const pruned_cpus = cpumask_view.CpuMaskView.init(fanout_words[0..], bit_len);

    try std.testing.expect(pruned_bitmap.isSubsetOf(anchor_bitmap));
    try std.testing.expect(pruned_cpus.isSubsetOf(anchor_cpus));
    try std.testing.expect(anchor_bitmap.isSubsetOf(pruned_bitmap));
    try std.testing.expect(anchor_cpus.isSubsetOf(pruned_cpus));
    try expectMirror(fanout_words[0..], bit_len, 7, 0, 1, &.{
        0,
        word_bits - 2,
        word_bits + 4,
        word_bits * 2 + 31,
        word_bits * 3 + 17,
        word_bits * 4 - 1,
        word_bits * 4 + 12,
    }, &.{
        1,
        7,
        word_bits + 23,
        word_bits * 3,
        word_bits * 4 + 2,
    });
    try std.testing.expectEqual(@as(?usize, 7), pruned_bitmap.nextClearBit(7));
    try std.testing.expectEqual(@as(?usize, 7), pruned_cpus.nextMissingCpu(7));
}
