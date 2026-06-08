const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;
const bit_len = word_bits + 19;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn makeView(words: []const Word) bitmap_view.BitmapView {
    return bitmap_view.BitmapView.init(words, bit_len);
}

fn makeCpuMask(words: []const Word) cpumask_view.CpuMaskView {
    return cpumask_view.CpuMaskView.init(words, bit_len);
}

fn expectSharedSurface(words: []const Word, expected_count: usize, first: usize, gap: usize) !void {
    const bitmap = makeView(words);
    const cpumask = makeCpuMask(words);

    try std.testing.expectEqual(expected_count, bitmap.countSetBits());
    try std.testing.expectEqual(expected_count, cpumask.countPresentCpus());
    try std.testing.expectEqual(@as(?usize, first), bitmap.firstSetBit());
    try std.testing.expectEqual(@as(?usize, first), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, gap), bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, gap), cpumask.firstMissingCpu());
}

test "phase3 bitmap cpumask window exchange keeps handoff windows aligned" {
    const left_window = [_]Word{
        bit(2) | bit(5) | bit(8) | bit(13) | bit(word_bits - 2),
        bit(word_bits + 1) | bit(word_bits + 4) | bit(word_bits + 9),
    };
    const right_window = [_]Word{
        bit(5) | bit(8) | bit(21) | bit(word_bits - 1),
        bit(word_bits + 4) | bit(word_bits + 9) | bit(word_bits + 15),
    };
    const exchange_bridge = [_]Word{
        left_window[0] | right_window[0],
        left_window[1] | right_window[1] | bit(bit_len + 6),
    };
    const released_left = [_]Word{
        right_window[0] | bit(13),
        right_window[1] | bit(bit_len + 2),
    };
    const outside_window = [_]Word{
        bit(0) | bit(17),
        bit(word_bits + 12) | bit(bit_len + 7),
    };

    const left_bits = makeView(left_window[0..]);
    const right_bits = makeView(right_window[0..]);
    const bridge_bits = makeView(exchange_bridge[0..]);
    const released_bits = makeView(released_left[0..]);
    const outside_bits = makeView(outside_window[0..]);

    const left_cpus = makeCpuMask(left_window[0..]);
    const right_cpus = makeCpuMask(right_window[0..]);
    const bridge_cpus = makeCpuMask(exchange_bridge[0..]);
    const released_cpus = makeCpuMask(released_left[0..]);
    const outside_cpus = makeCpuMask(outside_window[0..]);

    try expectSharedSurface(left_window[0..], 8, 2, 0);
    try expectSharedSurface(right_window[0..], 7, 5, 0);
    try expectSharedSurface(exchange_bridge[0..], 11, 2, 0);
    try expectSharedSurface(released_left[0..], 8, 5, 0);

    try std.testing.expect(left_bits.isSubsetOf(bridge_bits));
    try std.testing.expect(right_bits.isSubsetOf(bridge_bits));
    try std.testing.expect(left_cpus.isSubsetOf(bridge_cpus));
    try std.testing.expect(right_cpus.isSubsetOf(bridge_cpus));
    try std.testing.expect(!bridge_bits.isSubsetOf(left_bits));
    try std.testing.expect(!bridge_cpus.isSubsetOf(right_cpus));

    try std.testing.expect(released_bits.isSubsetOf(bridge_bits));
    try std.testing.expect(released_cpus.isSubsetOf(bridge_cpus));
    try std.testing.expect(!left_bits.isSubsetOf(released_bits));
    try std.testing.expect(!left_cpus.isSubsetOf(released_cpus));

    try std.testing.expect(!outside_bits.intersects(bridge_bits));
    try std.testing.expect(!outside_cpus.intersects(bridge_cpus));
    try std.testing.expect(!outside_bits.intersects(released_bits));
    try std.testing.expect(!outside_cpus.intersects(released_cpus));

    try std.testing.expect(left_cpus.hasCpu(2));
    try std.testing.expect(!left_cpus.hasCpu(21));
    try std.testing.expect(bridge_cpus.hasCpu(21));
    try std.testing.expect(bridge_cpus.hasCpu(word_bits + 15));
    try std.testing.expect(!released_cpus.hasCpu(2));
    try std.testing.expect(released_cpus.hasCpu(13));
    try std.testing.expect(!released_cpus.hasCpu(word_bits + 1));

    try std.testing.expectEqual(@as(?usize, 5), left_bits.nextSetBit(3));
    try std.testing.expectEqual(@as(?usize, 5), left_cpus.nextCpu(3));
    try std.testing.expectEqual(@as(?usize, 21), bridge_bits.nextSetBit(14));
    try std.testing.expectEqual(@as(?usize, 21), bridge_cpus.nextCpu(14));
    try std.testing.expectEqual(@as(?usize, word_bits + 15), released_bits.nextSetBit(word_bits + 10));
    try std.testing.expectEqual(@as(?usize, word_bits + 15), released_cpus.nextCpu(word_bits + 10));

    try std.testing.expectEqual(@as(?usize, 6), right_bits.nextClearBit(5));
    try std.testing.expectEqual(@as(?usize, 6), right_cpus.nextMissingCpu(5));
    try std.testing.expectEqual(@as(?usize, word_bits + 16), bridge_bits.nextClearBit(word_bits + 15));
    try std.testing.expectEqual(@as(?usize, word_bits + 16), bridge_cpus.nextMissingCpu(word_bits + 15));
}

test "phase3 bitmap cpumask window exchange masks declared tail noise" {
    const saturated = [_]Word{
        bit(1) | bit(7) | bit(word_bits - 3),
        bit(word_bits + 2) | bit(word_bits + 18) | bit(bit_len + 1) | bit(bit_len + 4),
    };
    const active_only = [_]Word{
        saturated[0],
        bit(word_bits + 2) | bit(word_bits + 18),
    };

    const saturated_bits = makeView(saturated[0..]);
    const active_bits = makeView(active_only[0..]);
    const saturated_cpus = makeCpuMask(saturated[0..]);
    const active_cpus = makeCpuMask(active_only[0..]);

    try expectSharedSurface(saturated[0..], 5, 1, 0);
    try std.testing.expect(saturated_bits.isSubsetOf(active_bits));
    try std.testing.expect(active_bits.isSubsetOf(saturated_bits));
    try std.testing.expect(saturated_cpus.isSubsetOf(active_cpus));
    try std.testing.expect(active_cpus.isSubsetOf(saturated_cpus));

    try std.testing.expect(saturated_bits.intersects(active_bits));
    try std.testing.expect(saturated_cpus.intersects(active_cpus));
    try std.testing.expectEqual(@as(?usize, word_bits + 18), saturated_bits.nextSetBit(word_bits + 10));
    try std.testing.expectEqual(@as(?usize, word_bits + 18), saturated_cpus.nextCpu(word_bits + 10));
    try std.testing.expectEqual(@as(?usize, null), saturated_bits.nextSetBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), saturated_cpus.nextCpu(bit_len));
    try std.testing.expectEqual(@as(?usize, null), saturated_bits.nextClearBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), saturated_cpus.nextMissingCpu(bit_len));
}
