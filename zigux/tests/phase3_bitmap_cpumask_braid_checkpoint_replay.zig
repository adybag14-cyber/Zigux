const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const bit_len = word_bits * 3 + 13;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn view(words: []const Word) bitmap_view.BitmapView {
    return bitmap_view.BitmapView.init(words, bit_len);
}

fn cpuView(words: []const Word) cpumask_view.CpuMaskView {
    return cpumask_view.CpuMaskView.init(words, bit_len);
}

fn expectBitmapCpuAligned(words: []const Word, expected_count: usize, first_present: ?usize, first_missing: ?usize) !void {
    const bitmap = view(words);
    const cpus = cpuView(words);

    try std.testing.expectEqual(expected_count, bitmap.countSetBits());
    try std.testing.expectEqual(expected_count, cpus.countPresentCpus());
    try std.testing.expectEqual(first_present, bitmap.firstSetBit());
    try std.testing.expectEqual(first_present, cpus.firstCpu());
    try std.testing.expectEqual(first_missing, bitmap.firstClearBit());
    try std.testing.expectEqual(first_missing, cpus.firstMissingCpu());
}

test "bitmap cpumask braid checkpoints stay aligned across rollback and promotion" {
    var checkpoint_a = [_]Word{
        bit(0) | bit(5) | bit(9) | bit(17),
        bit(word_bits + 2) | bit(word_bits + 19) | bit(word_bits + 34),
        bit(word_bits * 2 + 3) | bit(word_bits * 2 + 29),
        bit(word_bits * 3 + 1) | bit(word_bits * 3 + 7) | (@as(Word, 0x1fff) << 13),
    };
    var checkpoint_b = [_]Word{
        checkpoint_a[0] | bit(23) | bit(41),
        checkpoint_a[1] | bit(word_bits + 5) | bit(word_bits + 48),
        checkpoint_a[2] | bit(word_bits * 2 + 8) | bit(word_bits * 2 + 51),
        checkpoint_a[3] | bit(word_bits * 3 + 4) | bit(word_bits * 3 + 12) | (@as(Word, 0x7fff) << 17),
    };
    const bridge = [_]Word{
        bit(5) | bit(23) | bit(41),
        bit(word_bits + 5) | bit(word_bits + 19),
        bit(word_bits * 2 + 8) | bit(word_bits * 2 + 29),
        bit(word_bits * 3 + 4) | bit(word_bits * 3 + 12) | (@as(Word, 0xffff) << 16),
    };
    const outside = [_]Word{
        bit(1) | bit(6) | bit(18),
        bit(word_bits + 1) | bit(word_bits + 17),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 31),
        bit(word_bits * 3 + 0) | bit(word_bits * 3 + 8) | (@as(Word, 0xffff) << 18),
    };

    try expectBitmapCpuAligned(checkpoint_a[0..], 11, 0, 1);
    try expectBitmapCpuAligned(checkpoint_b[0..], 19, 0, 1);

    const bitmap_a = view(checkpoint_a[0..]);
    const bitmap_b = view(checkpoint_b[0..]);
    const bitmap_bridge = view(bridge[0..]);
    const bitmap_outside = view(outside[0..]);
    const cpus_a = cpuView(checkpoint_a[0..]);
    const cpus_b = cpuView(checkpoint_b[0..]);
    const cpus_bridge = cpuView(bridge[0..]);
    const cpus_outside = cpuView(outside[0..]);

    try std.testing.expect(bitmap_a.isSubsetOf(bitmap_b));
    try std.testing.expect(cpus_a.isSubsetOf(cpus_b));
    try std.testing.expect(bitmap_bridge.isSubsetOf(bitmap_b));
    try std.testing.expect(cpus_bridge.isSubsetOf(cpus_b));
    try std.testing.expect(!bitmap_bridge.isSubsetOf(bitmap_a));
    try std.testing.expect(!cpus_bridge.isSubsetOf(cpus_a));
    try std.testing.expect(!bitmap_outside.intersects(bitmap_b));
    try std.testing.expect(!cpus_outside.intersects(cpus_b));

    try std.testing.expectEqual(@as(?usize, 23), bitmap_b.nextSetBit(18));
    try std.testing.expectEqual(@as(?usize, 23), cpus_b.nextCpu(18));
    try std.testing.expectEqual(@as(?usize, word_bits + 5), bitmap_b.nextSetBit(word_bits + 3));
    try std.testing.expectEqual(@as(?usize, word_bits + 5), cpus_b.nextCpu(word_bits + 3));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 12), bitmap_b.nextSetBit(word_bits * 3 + 8));
    try std.testing.expectEqual(@as(?usize, word_bits * 3 + 12), cpus_b.nextCpu(word_bits * 3 + 8));
    try std.testing.expectEqual(@as(?usize, 1), bitmap_b.nextClearBit(0));
    try std.testing.expectEqual(@as(?usize, 1), cpus_b.nextMissingCpu(0));
    try std.testing.expectEqual(@as(?usize, null), bitmap_b.nextClearBit(word_bits * 3 + 13));
    try std.testing.expectEqual(@as(?usize, null), cpus_b.nextMissingCpu(word_bits * 3 + 13));

    checkpoint_b = checkpoint_a;
    try expectBitmapCpuAligned(checkpoint_b[0..], 11, 0, 1);
    try std.testing.expect(view(checkpoint_b[0..]).isSubsetOf(bitmap_a));
    try std.testing.expect(cpuView(checkpoint_b[0..]).isSubsetOf(cpus_a));
}

test "bitmap cpumask braid replay masks declared tail noise" {
    const clean_tail = [_]Word{
        bit(2) | bit(13) | bit(37),
        bit(word_bits + 11) | bit(word_bits + 27),
        bit(word_bits * 2 + 5) | bit(word_bits * 2 + 44),
        bit(word_bits * 3 + 3) | bit(word_bits * 3 + 9),
    };
    const noisy_tail = [_]Word{
        clean_tail[0],
        clean_tail[1],
        clean_tail[2],
        clean_tail[3] | ~((@as(Word, 1) << 13) - 1),
    };

    try expectBitmapCpuAligned(clean_tail[0..], 9, 2, 0);
    try expectBitmapCpuAligned(noisy_tail[0..], 9, 2, 0);

    const clean_bitmap = view(clean_tail[0..]);
    const noisy_bitmap = view(noisy_tail[0..]);
    const clean_cpus = cpuView(clean_tail[0..]);
    const noisy_cpus = cpuView(noisy_tail[0..]);

    try std.testing.expect(clean_bitmap.isSubsetOf(noisy_bitmap));
    try std.testing.expect(noisy_bitmap.isSubsetOf(clean_bitmap));
    try std.testing.expect(clean_cpus.isSubsetOf(noisy_cpus));
    try std.testing.expect(noisy_cpus.isSubsetOf(clean_cpus));
    try std.testing.expect(clean_bitmap.intersects(noisy_bitmap));
    try std.testing.expect(clean_cpus.intersects(noisy_cpus));
    try std.testing.expectEqual(@as(?usize, null), noisy_bitmap.nextSetBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), noisy_cpus.nextCpu(bit_len));
}
