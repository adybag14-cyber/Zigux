const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const bit_len = word_bits + 23;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn makeView(words: []const Word) bitmap_view.BitmapView {
    return bitmap_view.BitmapView.init(words, bit_len);
}

fn makeCpuMask(words: []const Word) cpumask_view.CpuMaskView {
    return cpumask_view.CpuMaskView.init(words, bit_len);
}

fn expectMirroredSurface(words: []const Word, expected_count: usize, first: usize, first_gap: usize) !void {
    const bitmap = makeView(words);
    const cpumask = makeCpuMask(words);

    try std.testing.expectEqual(expected_count, bitmap.countSetBits());
    try std.testing.expectEqual(expected_count, cpumask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, first), bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, first), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, first_gap), bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, first_gap), cpumask.firstMissingCpu());
}

test "phase3 bitmap cpumask hinge weave preserves bridge and rollback mirrors" {
    const lower_hinge = [_]Word{
        bit(1) | bit(6) | bit(14) | bit(27) | bit(word_bits - 4),
        bit(word_bits + 3) | bit(word_bits + 11) | bit(word_bits + 20),
    };
    const upper_hinge = [_]Word{
        bit(6) | bit(15) | bit(28) | bit(word_bits - 2),
        bit(word_bits + 3) | bit(word_bits + 12) | bit(word_bits + 21),
    };
    const woven_bridge = [_]Word{
        lower_hinge[0] | upper_hinge[0] | bit(40),
        lower_hinge[1] | upper_hinge[1] | bit(bit_len + 5),
    };
    const rollback_lower = [_]Word{
        lower_hinge[0] | bit(15),
        bit(word_bits + 3) | bit(word_bits + 20) | bit(bit_len + 7),
    };
    const release_upper = [_]Word{
        bit(28) | bit(word_bits - 2),
        bit(word_bits + 12) | bit(word_bits + 21) | bit(bit_len + 9),
    };
    const isolated = [_]Word{
        bit(0) | bit(18) | bit(33),
        bit(word_bits + 7) | bit(bit_len + 8),
    };

    const lower_bits = makeView(lower_hinge[0..]);
    const upper_bits = makeView(upper_hinge[0..]);
    const bridge_bits = makeView(woven_bridge[0..]);
    const rollback_bits = makeView(rollback_lower[0..]);
    const release_bits = makeView(release_upper[0..]);
    const isolated_bits = makeView(isolated[0..]);

    const lower_cpus = makeCpuMask(lower_hinge[0..]);
    const upper_cpus = makeCpuMask(upper_hinge[0..]);
    const bridge_cpus = makeCpuMask(woven_bridge[0..]);
    const rollback_cpus = makeCpuMask(rollback_lower[0..]);
    const release_cpus = makeCpuMask(release_upper[0..]);
    const isolated_cpus = makeCpuMask(isolated[0..]);

    try expectMirroredSurface(lower_hinge[0..], 8, 1, 0);
    try expectMirroredSurface(upper_hinge[0..], 7, 6, 0);
    try expectMirroredSurface(woven_bridge[0..], 14, 1, 0);
    try expectMirroredSurface(rollback_lower[0..], 8, 1, 0);
    try expectMirroredSurface(release_upper[0..], 4, 28, 0);

    try std.testing.expect(lower_bits.isSubsetOf(bridge_bits));
    try std.testing.expect(upper_bits.isSubsetOf(bridge_bits));
    try std.testing.expect(lower_cpus.isSubsetOf(bridge_cpus));
    try std.testing.expect(upper_cpus.isSubsetOf(bridge_cpus));
    try std.testing.expect(!bridge_bits.isSubsetOf(lower_bits));
    try std.testing.expect(!bridge_cpus.isSubsetOf(upper_cpus));

    try std.testing.expect(rollback_bits.isSubsetOf(bridge_bits));
    try std.testing.expect(rollback_cpus.isSubsetOf(bridge_cpus));
    try std.testing.expect(release_bits.isSubsetOf(bridge_bits));
    try std.testing.expect(release_cpus.isSubsetOf(bridge_cpus));
    try std.testing.expect(!release_bits.intersects(lower_bits));
    try std.testing.expect(!release_cpus.intersects(lower_cpus));

    try std.testing.expect(!isolated_bits.intersects(bridge_bits));
    try std.testing.expect(!isolated_cpus.intersects(bridge_cpus));
    try std.testing.expect(!isolated_bits.intersects(rollback_bits));
    try std.testing.expect(!isolated_cpus.intersects(rollback_cpus));

    try std.testing.expect(lower_cpus.hasCpu(1));
    try std.testing.expect(!lower_cpus.hasCpu(15));
    try std.testing.expect(bridge_cpus.hasCpu(15));
    try std.testing.expect(bridge_cpus.hasCpu(word_bits + 21));
    try std.testing.expect(rollback_cpus.hasCpu(15));
    try std.testing.expect(!rollback_cpus.hasCpu(word_bits + 11));
    try std.testing.expect(!release_cpus.hasCpu(6));

    try std.testing.expectEqual(@as(?usize, 27), lower_bits.nextSetBit(16));
    try std.testing.expectEqual(@as(?usize, 27), lower_cpus.nextCpu(16));
    try std.testing.expectEqual(@as(?usize, 40), bridge_bits.nextSetBit(29));
    try std.testing.expectEqual(@as(?usize, 40), bridge_cpus.nextCpu(29));
    try std.testing.expectEqual(@as(?usize, word_bits + 20), rollback_bits.nextSetBit(word_bits + 4));
    try std.testing.expectEqual(@as(?usize, word_bits + 20), rollback_cpus.nextCpu(word_bits + 4));
    try std.testing.expectEqual(@as(?usize, word_bits + 21), release_bits.nextSetBit(word_bits + 13));
    try std.testing.expectEqual(@as(?usize, word_bits + 21), release_cpus.nextCpu(word_bits + 13));

    try std.testing.expectEqual(@as(?usize, 7), upper_bits.nextClearBit(6));
    try std.testing.expectEqual(@as(?usize, 7), upper_cpus.nextMissingCpu(6));
    try std.testing.expectEqual(@as(?usize, word_bits + 22), bridge_bits.nextClearBit(word_bits + 21));
    try std.testing.expectEqual(@as(?usize, word_bits + 22), bridge_cpus.nextMissingCpu(word_bits + 21));
}

test "phase3 bitmap cpumask hinge weave clips declared tail noise" {
    const noisy_tail = [_]Word{
        bit(3) | bit(9) | bit(word_bits - 5),
        bit(word_bits + 2) | bit(word_bits + 22) | bit(bit_len + 2) | bit(bit_len + 10),
    };
    const active_tail = [_]Word{
        noisy_tail[0],
        bit(word_bits + 2) | bit(word_bits + 22),
    };
    const non_overlapping = [_]Word{
        bit(0) | bit(19),
        bit(word_bits + 8) | bit(bit_len + 6),
    };

    const noisy_bits = makeView(noisy_tail[0..]);
    const active_bits = makeView(active_tail[0..]);
    const non_overlapping_bits = makeView(non_overlapping[0..]);
    const noisy_cpus = makeCpuMask(noisy_tail[0..]);
    const active_cpus = makeCpuMask(active_tail[0..]);
    const non_overlapping_cpus = makeCpuMask(non_overlapping[0..]);

    try expectMirroredSurface(noisy_tail[0..], 5, 3, 0);
    try std.testing.expect(noisy_bits.isSubsetOf(active_bits));
    try std.testing.expect(active_bits.isSubsetOf(noisy_bits));
    try std.testing.expect(noisy_cpus.isSubsetOf(active_cpus));
    try std.testing.expect(active_cpus.isSubsetOf(noisy_cpus));

    try std.testing.expect(noisy_bits.intersects(active_bits));
    try std.testing.expect(noisy_cpus.intersects(active_cpus));
    try std.testing.expect(!noisy_bits.intersects(non_overlapping_bits));
    try std.testing.expect(!noisy_cpus.intersects(non_overlapping_cpus));

    try std.testing.expectEqual(@as(?usize, word_bits + 22), noisy_bits.nextSetBit(word_bits + 10));
    try std.testing.expectEqual(@as(?usize, word_bits + 22), noisy_cpus.nextCpu(word_bits + 10));
    try std.testing.expectEqual(@as(?usize, null), noisy_bits.nextSetBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), noisy_cpus.nextCpu(bit_len));
    try std.testing.expectEqual(@as(?usize, null), noisy_bits.nextClearBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), noisy_cpus.nextMissingCpu(bit_len));
}
