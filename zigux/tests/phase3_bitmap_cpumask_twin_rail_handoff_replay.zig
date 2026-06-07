const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const bit_len = word_bits * 4 + 9;

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

test "bitmap cpumask twin rails stay aligned across bridge handoff and rollback" {
    const left_rail = [_]Word{
        bit(2) | bit(6) | bit(14) | bit(28),
        bit(word_bits + 1) | bit(word_bits + 9) | bit(word_bits + 22) | bit(word_bits + 40),
        bit(word_bits * 2 + 3) | bit(word_bits * 2 + 18) | bit(word_bits * 2 + 33) | bit(word_bits * 2 + 49),
        bit(word_bits * 3 + 5) | bit(word_bits * 3 + 17) | bit(word_bits * 3 + 31) | bit(word_bits * 3 + 45),
        bit(word_bits * 4 + 1) | bit(word_bits * 4 + 7) | (@as(Word, 0x1fff) << 12),
    };
    const right_rail = [_]Word{
        bit(3) | bit(7) | bit(15) | bit(29),
        bit(word_bits + 2) | bit(word_bits + 10) | bit(word_bits + 23) | bit(word_bits + 41),
        bit(word_bits * 2 + 4) | bit(word_bits * 2 + 19) | bit(word_bits * 2 + 34) | bit(word_bits * 2 + 50),
        bit(word_bits * 3 + 6) | bit(word_bits * 3 + 18) | bit(word_bits * 3 + 32) | bit(word_bits * 3 + 46),
        bit(word_bits * 4 + 2) | bit(word_bits * 4 + 8) | (@as(Word, 0x7fff) << 11),
    };
    const handoff = [_]Word{
        bit(2) | bit(3) | bit(14) | bit(15) | bit(28) | bit(29),
        bit(word_bits + 1) | bit(word_bits + 2) | bit(word_bits + 9) | bit(word_bits + 22) | bit(word_bits + 23) | bit(word_bits + 40),
        bit(word_bits * 2 + 3) | bit(word_bits * 2 + 4) | bit(word_bits * 2 + 18) | bit(word_bits * 2 + 33) | bit(word_bits * 2 + 34) | bit(word_bits * 2 + 49),
        bit(word_bits * 3 + 5) | bit(word_bits * 3 + 17) | bit(word_bits * 3 + 18) | bit(word_bits * 3 + 32) | bit(word_bits * 3 + 45),
        bit(word_bits * 4 + 1) | bit(word_bits * 4 + 7) | bit(word_bits * 4 + 8) | (@as(Word, 0xffff) << 10),
    };
    const envelope = [_]Word{
        left_rail[0] | right_rail[0],
        left_rail[1] | right_rail[1],
        left_rail[2] | right_rail[2],
        left_rail[3] | right_rail[3],
        left_rail[4] | right_rail[4],
    };
    const outside = [_]Word{
        bit(0) | bit(1) | bit(4),
        bit(word_bits + 0) | bit(word_bits + 3) | bit(word_bits + 11),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 5) | bit(word_bits * 2 + 20),
        bit(word_bits * 3 + 0) | bit(word_bits * 3 + 7) | bit(word_bits * 3 + 19),
        bit(word_bits * 4 + 0) | bit(word_bits * 4 + 3) | (@as(Word, 0xffff) << 16),
    };

    try expectBitmapCpuAligned(left_rail[0..], 18, 2, 0);
    try expectBitmapCpuAligned(right_rail[0..], 18, 3, 0);
    try expectBitmapCpuAligned(handoff[0..], 26, 2, 0);
    try expectBitmapCpuAligned(envelope[0..], 36, 2, 0);

    const bitmap_left = view(left_rail[0..]);
    const bitmap_right = view(right_rail[0..]);
    const bitmap_handoff = view(handoff[0..]);
    const bitmap_envelope = view(envelope[0..]);
    const bitmap_outside = view(outside[0..]);
    const cpus_left = cpuView(left_rail[0..]);
    const cpus_right = cpuView(right_rail[0..]);
    const cpus_handoff = cpuView(handoff[0..]);
    const cpus_envelope = cpuView(envelope[0..]);
    const cpus_outside = cpuView(outside[0..]);

    try std.testing.expect(!bitmap_left.intersects(bitmap_right));
    try std.testing.expect(!cpus_left.intersects(cpus_right));
    try std.testing.expect(bitmap_left.isSubsetOf(bitmap_envelope));
    try std.testing.expect(cpus_left.isSubsetOf(cpus_envelope));
    try std.testing.expect(bitmap_right.isSubsetOf(bitmap_envelope));
    try std.testing.expect(cpus_right.isSubsetOf(cpus_envelope));
    try std.testing.expect(bitmap_handoff.isSubsetOf(bitmap_envelope));
    try std.testing.expect(cpus_handoff.isSubsetOf(cpus_envelope));
    try std.testing.expect(bitmap_handoff.intersects(bitmap_left));
    try std.testing.expect(cpus_handoff.intersects(cpus_left));
    try std.testing.expect(bitmap_handoff.intersects(bitmap_right));
    try std.testing.expect(cpus_handoff.intersects(cpus_right));
    try std.testing.expect(!bitmap_handoff.isSubsetOf(bitmap_left));
    try std.testing.expect(!cpus_handoff.isSubsetOf(cpus_left));
    try std.testing.expect(!bitmap_handoff.isSubsetOf(bitmap_right));
    try std.testing.expect(!cpus_handoff.isSubsetOf(cpus_right));
    try std.testing.expect(!bitmap_outside.intersects(bitmap_envelope));
    try std.testing.expect(!cpus_outside.intersects(cpus_envelope));

    try std.testing.expectEqual(@as(?usize, 14), bitmap_handoff.nextSetBit(6));
    try std.testing.expectEqual(@as(?usize, 14), cpus_handoff.nextCpu(6));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), bitmap_handoff.nextSetBit(word_bits + 2));
    try std.testing.expectEqual(@as(?usize, word_bits + 2), cpus_handoff.nextCpu(word_bits + 2));
    try std.testing.expectEqual(@as(?usize, word_bits + 3), bitmap_handoff.nextClearBit(word_bits + 1));
    try std.testing.expectEqual(@as(?usize, word_bits + 3), cpus_handoff.nextMissingCpu(word_bits + 1));
    try std.testing.expectEqual(@as(?usize, word_bits * 4 + 7), bitmap_handoff.nextSetBit(word_bits * 4 + 7));
    try std.testing.expectEqual(@as(?usize, word_bits * 4 + 7), cpus_handoff.nextCpu(word_bits * 4 + 7));
    try std.testing.expectEqual(@as(?usize, word_bits * 4 + 8), bitmap_handoff.nextSetBit(word_bits * 4 + 8));
    try std.testing.expectEqual(@as(?usize, word_bits * 4 + 8), cpus_handoff.nextCpu(word_bits * 4 + 8));
    try std.testing.expectEqual(@as(?usize, null), bitmap_handoff.nextSetBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), cpus_handoff.nextCpu(bit_len));

    var rollback = handoff;
    rollback = left_rail;
    try expectBitmapCpuAligned(rollback[0..], 18, 2, 0);
    try std.testing.expect(view(rollback[0..]).isSubsetOf(bitmap_left));
    try std.testing.expect(cpuView(rollback[0..]).isSubsetOf(cpus_left));
}

test "bitmap cpumask twin rail replay masks declared tail noise" {
    const clean_tail = [_]Word{
        bit(5) | bit(21) | bit(42),
        bit(word_bits + 8) | bit(word_bits + 30) | bit(word_bits + 55),
        bit(word_bits * 2 + 13) | bit(word_bits * 2 + 37),
        bit(word_bits * 3 + 2) | bit(word_bits * 3 + 44),
        bit(word_bits * 4 + 4),
    };
    const noisy_tail = [_]Word{
        clean_tail[0],
        clean_tail[1],
        clean_tail[2],
        clean_tail[3],
        clean_tail[4] | ~((@as(Word, 1) << 9) - 1),
    };

    try expectBitmapCpuAligned(clean_tail[0..], 11, 5, 0);
    try expectBitmapCpuAligned(noisy_tail[0..], 11, 5, 0);

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
