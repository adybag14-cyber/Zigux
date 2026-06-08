const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @as(std.math.Log2Int(Word), @intCast(bit_index % word_bits));
}

const capacity = (2 * word_bits) + 9;

const lower_words = [_]Word{
    bit(2) | bit(5),
    bit(word_bits + 3),
    bit((2 * word_bits) + 1),
};

const upper_words = [_]Word{
    bit(4),
    bit(word_bits + 6),
    bit((2 * word_bits) + 2) | bit((2 * word_bits) + 7),
};

const bridge_words = [_]Word{
    bit(2) | bit(4) | bit(5),
    bit(word_bits + 1) | bit(word_bits + 3) | bit(word_bits + 4) | bit(word_bits + 6),
    bit((2 * word_bits) + 1) | bit((2 * word_bits) + 2) | bit((2 * word_bits) + 7) | bit((2 * word_bits) + 15),
};

const handoff_words = [_]Word{
    bit(5),
    bit(word_bits + 3) | bit(word_bits + 4),
    bit((2 * word_bits) + 2) | bit((2 * word_bits) + 14),
};

const outside_words = [_]Word{
    bit(0),
    bit(word_bits + 8),
    bit((2 * word_bits) + 8),
};

test "bitmap lattice handoff keeps bridge relations inside declared capacity" {
    const lower = BitmapView.init(lower_words[0..], capacity);
    const upper = BitmapView.init(upper_words[0..], capacity);
    const bridge = BitmapView.init(bridge_words[0..], capacity);
    const handoff = BitmapView.init(handoff_words[0..], capacity);
    const outside = BitmapView.init(outside_words[0..], capacity);

    try std.testing.expect(lower.isSubsetOf(bridge));
    try std.testing.expect(upper.isSubsetOf(bridge));
    try std.testing.expect(handoff.isSubsetOf(bridge));
    try std.testing.expect(!bridge.isSubsetOf(handoff));
    try std.testing.expect(!outside.intersects(bridge));

    try std.testing.expectEqual(@as(usize, 10), bridge.countSetBits());
    try std.testing.expectEqual(@as(usize, 4), handoff.countSetBits());
    try std.testing.expectEqual(@as(?usize, null), bridge.nextSetBit((2 * word_bits) + 8));
    try std.testing.expectEqual(@as(?usize, null), handoff.nextSetBit((2 * word_bits) + 3));
}

test "bitmap lattice handoff mirrors cpumask presence and gap cursors" {
    const bridge_bitmap = BitmapView.init(bridge_words[0..], capacity);
    const handoff_bitmap = BitmapView.init(handoff_words[0..], capacity);
    const bridge_cpus = CpuMaskView.init(bridge_words[0..], capacity);
    const handoff_cpus = CpuMaskView.init(handoff_words[0..], capacity);
    const outside_cpus = CpuMaskView.init(outside_words[0..], capacity);

    try std.testing.expect(handoff_cpus.isSubsetOf(bridge_cpus));
    try std.testing.expect(!outside_cpus.intersects(bridge_cpus));

    try std.testing.expectEqual(bridge_bitmap.countSetBits(), bridge_cpus.countPresentCpus());
    try std.testing.expectEqual(bridge_bitmap.firstSetBit(), bridge_cpus.firstCpu());
    try std.testing.expectEqual(bridge_bitmap.firstClearBit(), bridge_cpus.firstMissingCpu());

    try std.testing.expectEqual(@as(?usize, 2), bridge_cpus.nextCpu(0));
    try std.testing.expectEqual(@as(?usize, 4), bridge_cpus.nextCpu(3));
    try std.testing.expectEqual(@as(?usize, word_bits + 1), bridge_cpus.nextCpu(6));
    try std.testing.expectEqual(@as(?usize, (2 * word_bits) + 7), bridge_cpus.nextCpu((2 * word_bits) + 3));
    try std.testing.expectEqual(@as(?usize, null), bridge_cpus.nextCpu(capacity));

    try std.testing.expectEqual(handoff_bitmap.nextSetBit(word_bits), handoff_cpus.nextCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits + 5), handoff_cpus.nextMissingCpu(word_bits + 4));
    try std.testing.expectEqual(@as(?usize, capacity - 1), handoff_cpus.nextMissingCpu(capacity - 1));
    try std.testing.expectEqual(@as(?usize, null), handoff_cpus.nextMissingCpu(capacity));
}
