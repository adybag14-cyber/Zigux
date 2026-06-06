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

    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), cpus.nextCpu(bit_len));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextClearBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), cpus.nextMissingCpu(bit_len));
}

test "bitmap and cpumask sparse clusters compact into lower-word anchors" {
    const bit_len = word_bits * 4 + 9;
    const active_tail_mask = (@as(Word, 1) << 9) - 1;
    const tail_noise = ~active_tail_mask;

    var cluster_words = [_]Word{
        bit(2) | bit(3) | bit(11),
        bit(word_bits + 5) | bit(word_bits + 6) | bit(word_bits * 2 - 1),
        bit(word_bits * 2 + 9) | bit(word_bits * 2 + 10) | bit(word_bits * 2 + 41),
        bit(word_bits * 3) | bit(word_bits * 3 + 37) | bit(word_bits * 4 - 2),
        bit(word_bits * 4 + 1) | bit(word_bits * 4 + 8) | tail_noise,
    };
    const compact_words = [_]Word{
        bit(0) | bit(1) | bit(2) | bit(3) | bit(4) | bit(5),
        bit(word_bits) | bit(word_bits + 1) | bit(word_bits + 2) | bit(word_bits + 3),
        bit(word_bits * 2) | bit(word_bits * 2 + 1) | bit(word_bits * 2 + 2),
        bit(word_bits * 3),
        tail_noise,
    };
    const envelope_words = [_]Word{
        cluster_words[0] | compact_words[0],
        cluster_words[1] | compact_words[1],
        cluster_words[2] | compact_words[2],
        cluster_words[3] | compact_words[3],
        cluster_words[4] | compact_words[4],
    };
    const gap_probe_words = [_]Word{
        bit(14) | bit(21),
        bit(word_bits + 15),
        bit(word_bits * 2 + 18),
        bit(word_bits * 3 + 12),
        bit(word_bits * 4 + 4) | tail_noise,
    };

    try expectMirror(cluster_words[0..], bit_len, 14, 2, 0, &.{
        2,
        3,
        11,
        word_bits + 5,
        word_bits + 6,
        word_bits * 2 - 1,
        word_bits * 2 + 9,
        word_bits * 2 + 10,
        word_bits * 2 + 41,
        word_bits * 3,
        word_bits * 3 + 37,
        word_bits * 4 - 2,
        word_bits * 4 + 1,
        word_bits * 4 + 8,
    }, &.{
        0,
        4,
        word_bits + 7,
        word_bits * 2 + 11,
        word_bits * 3 + 1,
        word_bits * 4,
        word_bits * 4 + 2,
    });

    const cluster_bitmap = bitmap_view.BitmapView.init(cluster_words[0..], bit_len);
    const compact_bitmap = bitmap_view.BitmapView.init(compact_words[0..], bit_len);
    const envelope_bitmap = bitmap_view.BitmapView.init(envelope_words[0..], bit_len);
    const gap_bitmap = bitmap_view.BitmapView.init(gap_probe_words[0..], bit_len);
    const cluster_cpus = cpumask_view.CpuMaskView.init(cluster_words[0..], bit_len);
    const compact_cpus = cpumask_view.CpuMaskView.init(compact_words[0..], bit_len);
    const envelope_cpus = cpumask_view.CpuMaskView.init(envelope_words[0..], bit_len);
    const gap_cpus = cpumask_view.CpuMaskView.init(gap_probe_words[0..], bit_len);

    try std.testing.expect(cluster_bitmap.isSubsetOf(envelope_bitmap));
    try std.testing.expect(cluster_cpus.isSubsetOf(envelope_cpus));
    try std.testing.expect(compact_bitmap.isSubsetOf(envelope_bitmap));
    try std.testing.expect(compact_cpus.isSubsetOf(envelope_cpus));
    try std.testing.expect(!envelope_bitmap.isSubsetOf(cluster_bitmap));
    try std.testing.expect(!envelope_cpus.isSubsetOf(cluster_cpus));
    try std.testing.expect(cluster_bitmap.intersects(compact_bitmap));
    try std.testing.expect(cluster_cpus.intersects(compact_cpus));
    try std.testing.expect(!cluster_bitmap.intersects(gap_bitmap));
    try std.testing.expect(!cluster_cpus.intersects(gap_cpus));
    try std.testing.expect(!compact_bitmap.intersects(gap_bitmap));
    try std.testing.expect(!compact_cpus.intersects(gap_cpus));

    cluster_words = compact_words;

    const compacted_bitmap = bitmap_view.BitmapView.init(cluster_words[0..], bit_len);
    const compacted_cpus = cpumask_view.CpuMaskView.init(cluster_words[0..], bit_len);

    try std.testing.expect(compacted_bitmap.isSubsetOf(envelope_bitmap));
    try std.testing.expect(compacted_cpus.isSubsetOf(envelope_cpus));
    try std.testing.expect(!gap_bitmap.intersects(compacted_bitmap));
    try std.testing.expect(!gap_cpus.intersects(compacted_cpus));
    try expectMirror(cluster_words[0..], bit_len, 14, 0, 6, &.{
        0,
        1,
        2,
        3,
        4,
        5,
        word_bits,
        word_bits + 1,
        word_bits + 2,
        word_bits + 3,
        word_bits * 2,
        word_bits * 2 + 1,
        word_bits * 2 + 2,
        word_bits * 3,
    }, &.{
        6,
        word_bits + 4,
        word_bits * 2 + 3,
        word_bits * 3 + 1,
        word_bits * 4,
        word_bits * 4 + 8,
    });
}
