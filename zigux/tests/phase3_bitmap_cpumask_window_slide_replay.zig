const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn expectViewsMirror(words: []const Word, bit_len: usize, expected_count: usize, expected_set: []const usize, expected_clear: []const usize) !void {
    const bitmap = bitmap_view.BitmapView.init(words, bit_len);
    const cpus = cpumask_view.CpuMaskView.init(words, bit_len);

    try std.testing.expectEqual(expected_count, bitmap.countSetBits());
    try std.testing.expectEqual(expected_count, cpus.countPresentCpus());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpus.firstCpu());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpus.firstMissingCpu());

    for (expected_set) |cpu| {
        try std.testing.expect(bitmap.isSet(cpu));
        try std.testing.expect(cpus.hasCpu(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), bitmap.nextSetBit(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), cpus.nextCpu(cpu));
    }

    for (expected_clear) |cpu| {
        try std.testing.expect(!bitmap.isSet(cpu));
        try std.testing.expect(!cpus.hasCpu(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), bitmap.nextClearBit(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), cpus.nextMissingCpu(cpu));
    }
}

test "bitmap and cpumask views mirror a sliding active window across word banks" {
    const bit_len = word_bits * 3 + 11;
    const active_tail_mask = (@as(Word, 1) << 11) - 1;
    const tail_noise = ~active_tail_mask;

    var left_words = [_]Word{
        bit(word_bits - 3) | bit(word_bits - 1),
        bit(word_bits) | bit(word_bits + 17) | bit(word_bits * 2 - 1),
        bit(word_bits * 2) | bit(word_bits * 2 + 9),
        bit(word_bits * 3) | bit(word_bits * 3 + 5) | tail_noise,
    };
    const right_words = [_]Word{
        bit(1) | bit(word_bits - 1),
        bit(word_bits) | bit(word_bits + 18),
        bit(word_bits * 2) | bit(word_bits * 2 + 9) | bit(word_bits * 3 - 2),
        bit(word_bits * 3 + 5) | tail_noise,
    };

    try expectViewsMirror(left_words[0..], bit_len, 9, &.{
        word_bits - 3,
        word_bits - 1,
        word_bits,
        word_bits + 17,
        word_bits * 2 - 1,
        word_bits * 2,
        word_bits * 2 + 9,
        word_bits * 3,
        word_bits * 3 + 5,
    }, &.{
        0,
        word_bits + 1,
        word_bits * 2 + 1,
        word_bits * 3 + 1,
    });

    try expectViewsMirror(right_words[0..], bit_len, 8, &.{
        1,
        word_bits - 1,
        word_bits,
        word_bits + 18,
        word_bits * 2,
        word_bits * 2 + 9,
        word_bits * 3 - 2,
        word_bits * 3 + 5,
    }, &.{
        0,
        word_bits - 3,
        word_bits + 17,
        word_bits * 3,
    });

    const left_bitmap = bitmap_view.BitmapView.init(left_words[0..], bit_len);
    const right_bitmap = bitmap_view.BitmapView.init(right_words[0..], bit_len);
    const left_cpus = cpumask_view.CpuMaskView.init(left_words[0..], bit_len);
    const right_cpus = cpumask_view.CpuMaskView.init(right_words[0..], bit_len);

    try std.testing.expect(!left_bitmap.isSubsetOf(right_bitmap));
    try std.testing.expect(!left_cpus.isSubsetOf(right_cpus));
    try std.testing.expect(left_bitmap.intersects(right_bitmap));
    try std.testing.expect(left_cpus.intersects(right_cpus));

    left_words[0] &= ~bit(word_bits - 3);
    left_words[1] &= ~bit(word_bits + 17);
    left_words[1] &= ~bit(word_bits * 2 - 1);
    left_words[3] &= ~bit(word_bits * 3);
    left_words[3] |= bit(word_bits * 3 + 5);

    const narrowed_bitmap = bitmap_view.BitmapView.init(left_words[0..], bit_len);
    const narrowed_cpus = cpumask_view.CpuMaskView.init(left_words[0..], bit_len);

    try std.testing.expect(narrowed_bitmap.isSubsetOf(right_bitmap));
    try std.testing.expect(narrowed_cpus.isSubsetOf(right_cpus));
    try std.testing.expectEqual(@as(?usize, word_bits - 1), narrowed_bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, word_bits - 1), narrowed_cpus.firstCpu());
    try std.testing.expectEqual(@as(?usize, word_bits - 3), narrowed_bitmap.nextClearBit(word_bits - 3));
    try std.testing.expectEqual(@as(?usize, word_bits - 3), narrowed_cpus.nextMissingCpu(word_bits - 3));
}
