const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const word_bits = bitmap_view.word_bits;
const Word = bitmap_view.Word;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn expectSamePresence(bitmap: BitmapView, cpumask: CpuMaskView, cpu: usize) !void {
    try std.testing.expectEqual(bitmap.isSet(cpu), cpumask.hasCpu(cpu));
}

test "bitmap cpumask zigzag handoff keeps subset and intersection mirrors" {
    const capacity = word_bits * 2 + 5;
    const zigzag_words = [_]Word{
        bit(1) | bit(4) | bit(9) | bit(15) | bit(22) | bit(31),
        bit(word_bits + 2) | bit(word_bits + 8) | bit(word_bits + 17) | bit(word_bits + 25) | bit(word_bits + 33),
        bit(word_bits * 2 + 1) | bit(word_bits * 2 + 4) | bit(word_bits * 2 + 8),
    };
    const lower_words = [_]Word{
        bit(1) | bit(9) | bit(22),
        bit(word_bits + 8) | bit(word_bits + 25),
        bit(word_bits * 2 + 1),
    };
    const upper_words = [_]Word{
        bit(4) | bit(15) | bit(31),
        bit(word_bits + 2) | bit(word_bits + 17) | bit(word_bits + 33),
        bit(word_bits * 2 + 4),
    };
    const outside_words = [_]Word{
        bit(0) | bit(3) | bit(8),
        bit(word_bits + 1) | bit(word_bits + 7),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 3),
    };

    const zigzag_bitmap = BitmapView.init(zigzag_words[0..], capacity);
    const lower_bitmap = BitmapView.init(lower_words[0..], capacity);
    const upper_bitmap = BitmapView.init(upper_words[0..], capacity);
    const outside_bitmap = BitmapView.init(outside_words[0..], capacity);

    const zigzag_cpu = CpuMaskView.init(zigzag_words[0..], capacity);
    const lower_cpu = CpuMaskView.init(lower_words[0..], capacity);
    const upper_cpu = CpuMaskView.init(upper_words[0..], capacity);
    const outside_cpu = CpuMaskView.init(outside_words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 13), zigzag_bitmap.countSetBits());
    try std.testing.expectEqual(zigzag_bitmap.countSetBits(), zigzag_cpu.countPresentCpus());

    try std.testing.expect(lower_bitmap.isSubsetOf(zigzag_bitmap));
    try std.testing.expect(upper_bitmap.isSubsetOf(zigzag_bitmap));
    try std.testing.expect(!zigzag_bitmap.isSubsetOf(lower_bitmap));
    try std.testing.expect(lower_cpu.isSubsetOf(zigzag_cpu));
    try std.testing.expect(upper_cpu.isSubsetOf(zigzag_cpu));
    try std.testing.expect(!zigzag_cpu.isSubsetOf(lower_cpu));

    try std.testing.expect(!lower_bitmap.intersects(upper_bitmap));
    try std.testing.expect(!lower_cpu.intersects(upper_cpu));
    try std.testing.expect(!zigzag_bitmap.intersects(outside_bitmap));
    try std.testing.expect(!zigzag_cpu.intersects(outside_cpu));

    try expectSamePresence(zigzag_bitmap, zigzag_cpu, 1);
    try expectSamePresence(zigzag_bitmap, zigzag_cpu, word_bits + 17);
    try expectSamePresence(zigzag_bitmap, zigzag_cpu, word_bits * 2 + 4);
    try expectSamePresence(zigzag_bitmap, zigzag_cpu, word_bits * 2 + 3);
}

test "bitmap cpumask zigzag handoff mirrors cursors and clips tail noise" {
    const capacity = word_bits * 2 + 5;
    const words = [_]Word{
        bit(2) | bit(11) | bit(23) | bit(47),
        bit(word_bits + 5) | bit(word_bits + 19) | bit(word_bits + 41),
        bit(word_bits * 2 + 0) | bit(word_bits * 2 + 4) | bit(word_bits * 2 + 9),
    };

    const bitmap = BitmapView.init(words[0..], capacity);
    const cpumask = CpuMaskView.init(words[0..], capacity);

    try std.testing.expectEqual(@as(usize, 9), bitmap.countSetBits());
    try std.testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());

    try std.testing.expectEqual(@as(?usize, 2), bitmap.firstSetBit());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    try std.testing.expectEqual(@as(?usize, 23), bitmap.nextSetBit(12));
    try std.testing.expectEqual(bitmap.nextSetBit(12), cpumask.nextCpu(12));
    try std.testing.expectEqual(@as(?usize, word_bits + 19), bitmap.nextSetBit(word_bits + 6));
    try std.testing.expectEqual(bitmap.nextSetBit(word_bits + 6), cpumask.nextCpu(word_bits + 6));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 4), bitmap.nextSetBit(word_bits * 2 + 1));
    try std.testing.expectEqual(bitmap.nextSetBit(word_bits * 2 + 1), cpumask.nextCpu(word_bits * 2 + 1));

    try std.testing.expectEqual(@as(?usize, 12), bitmap.nextClearBit(12));
    try std.testing.expectEqual(bitmap.nextClearBit(12), cpumask.nextMissingCpu(12));
    try std.testing.expectEqual(@as(?usize, word_bits + 6), bitmap.nextClearBit(word_bits + 6));
    try std.testing.expectEqual(bitmap.nextClearBit(word_bits + 6), cpumask.nextMissingCpu(word_bits + 6));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(capacity));
    try std.testing.expectEqual(bitmap.nextSetBit(capacity), cpumask.nextCpu(capacity));

    try std.testing.expect(bitmap.isSet(word_bits * 2 + 4));
    try std.testing.expect(cpumask.hasCpu(word_bits * 2 + 4));
}
