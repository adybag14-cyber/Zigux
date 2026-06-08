const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const cpu_capacity = word_bits + 11;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn view(words: []const Word) bitmap_view.BitmapView {
    return bitmap_view.BitmapView.init(words, cpu_capacity);
}

fn cpus(words: []const Word) cpumask_view.CpuMaskView {
    return cpumask_view.CpuMaskView.init(words, cpu_capacity);
}

test "bitmap and cpumask nested rings keep subset and intersection parity" {
    const core_words = [_]Word{
        bit(1) | bit(5) | bit(9),
        bit(word_bits + 2) | bit(word_bits + 7) | bit(word_bits + 13),
    };
    const inner_ring_words = [_]Word{
        core_words[0] | bit(13) | bit(21),
        core_words[1] | bit(word_bits + 5) | bit(word_bits + 12),
    };
    const outer_ring_words = [_]Word{
        inner_ring_words[0] | bit(2) | bit(34),
        inner_ring_words[1] | bit(word_bits + 0) | bit(word_bits + 10),
    };
    const isolated_words = [_]Word{
        bit(3) | bit(8) | bit(14),
        bit(word_bits + 1) | bit(word_bits + 4),
    };

    const core_bitmap = view(core_words[0..]);
    const inner_bitmap = view(inner_ring_words[0..]);
    const outer_bitmap = view(outer_ring_words[0..]);
    const isolated_bitmap = view(isolated_words[0..]);
    const core_mask = cpus(core_words[0..]);
    const inner_mask = cpus(inner_ring_words[0..]);
    const outer_mask = cpus(outer_ring_words[0..]);
    const isolated_mask = cpus(isolated_words[0..]);

    try std.testing.expect(core_bitmap.isSubsetOf(inner_bitmap));
    try std.testing.expect(inner_bitmap.isSubsetOf(outer_bitmap));
    try std.testing.expect(!outer_bitmap.isSubsetOf(inner_bitmap));
    try std.testing.expect(!core_bitmap.intersects(isolated_bitmap));
    try std.testing.expect(inner_bitmap.intersects(outer_bitmap));

    try std.testing.expect(core_mask.isSubsetOf(inner_mask));
    try std.testing.expect(inner_mask.isSubsetOf(outer_mask));
    try std.testing.expect(!outer_mask.isSubsetOf(inner_mask));
    try std.testing.expect(!core_mask.intersects(isolated_mask));
    try std.testing.expect(inner_mask.intersects(outer_mask));
}

test "bitmap and cpumask nested rings agree on cursors and declared tail clipping" {
    const nested_words = [_]Word{
        bit(0) | bit(6) | bit(11) | bit(23) | bit(31),
        bit(word_bits + 1) |
            bit(word_bits + 4) |
            bit(word_bits + 8) |
            bit(word_bits + 12) |
            bit(word_bits + 29),
    };
    const expected_present = [_]usize{
        0,
        6,
        11,
        23,
        31,
        word_bits + 1,
        word_bits + 4,
        word_bits + 8,
    };
    const expected_missing = [_]usize{ 1, 7, word_bits + 2, word_bits + 9 };

    const bitmap = view(nested_words[0..]);
    const mask = cpus(nested_words[0..]);

    try std.testing.expectEqual(@as(usize, expected_present.len), bitmap.countSetBits());
    try std.testing.expectEqual(bitmap.countSetBits(), mask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, expected_present[0]), bitmap.firstSetBit());
    try std.testing.expectEqual(bitmap.firstSetBit(), mask.firstCpu());

    for (expected_present) |cpu| {
        try std.testing.expect(bitmap.isSet(cpu));
        try std.testing.expect(mask.hasCpu(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), bitmap.nextSetBit(cpu));
        try std.testing.expectEqual(bitmap.nextSetBit(cpu), mask.nextCpu(cpu));
    }

    for (expected_missing) |cpu| {
        try std.testing.expect(!bitmap.isSet(cpu));
        try std.testing.expect(!mask.hasCpu(cpu));
        try std.testing.expectEqual(@as(?usize, cpu), bitmap.nextClearBit(cpu));
        try std.testing.expectEqual(bitmap.nextClearBit(cpu), mask.nextMissingCpu(cpu));
    }

    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(cpu_capacity));
    try std.testing.expectEqual(@as(?usize, null), mask.nextCpu(cpu_capacity));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextClearBit(cpu_capacity));
    try std.testing.expectEqual(@as(?usize, null), mask.nextMissingCpu(cpu_capacity));
}
