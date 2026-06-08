const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const word_bits = bitmap_view.word_bits;

fn bitMask(bit_index: usize) usize {
    return @as(usize, 1) << @intCast(bit_index % word_bits);
}

fn tailNoise(active_bits: usize) usize {
    const remainder = active_bits % word_bits;
    if (remainder == 0) return 0;
    return std.math.maxInt(usize) & ~((@as(usize, 1) << @intCast(remainder)) - 1);
}

fn expectBitmapCpuMirror(bitmap: BitmapView, cpus: CpuMaskView) !void {
    try std.testing.expectEqual(bitmap.countSetBits(), cpus.countPresentCpus());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpus.firstCpu());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpus.firstMissingCpu());

    var bit: usize = 0;
    while (bit < bitmap.bit_len) : (bit += 1) {
        try std.testing.expectEqual(bitmap.isSet(bit), cpus.hasCpu(bit));
    }
}

test "bitmap and cpumask mirror braid window exchange relations" {
    const capacity = word_bits * 2 + 13;
    const noise = tailNoise(capacity);

    const left_words = [_]usize{
        bitMask(3) | bitMask(11) | bitMask(23),
        bitMask(word_bits + 4) | bitMask(word_bits + 21),
        bitMask(word_bits * 2 + 2) | noise,
    };
    const right_words = [_]usize{
        bitMask(11) | bitMask(18) | bitMask(31),
        bitMask(word_bits + 4) | bitMask(word_bits + 29),
        bitMask(word_bits * 2 + 2) | bitMask(word_bits * 2 + 10) | noise,
    };
    const braid_words = [_]usize{
        bitMask(3) | bitMask(11) | bitMask(18) | bitMask(23) | bitMask(31),
        bitMask(word_bits + 4) | bitMask(word_bits + 21) | bitMask(word_bits + 29),
        bitMask(word_bits * 2 + 2) | bitMask(word_bits * 2 + 10) | noise,
    };
    const window_words = [_]usize{
        bitMask(6) | bitMask(7),
        bitMask(word_bits + 7) | bitMask(word_bits + 8),
        bitMask(word_bits * 2 + 5) | noise,
    };

    const left_bitmap = BitmapView.init(left_words[0..], capacity);
    const right_bitmap = BitmapView.init(right_words[0..], capacity);
    const braid_bitmap = BitmapView.init(braid_words[0..], capacity);
    const window_bitmap = BitmapView.init(window_words[0..], capacity);

    const left_cpus = CpuMaskView.init(left_words[0..], capacity);
    const right_cpus = CpuMaskView.init(right_words[0..], capacity);
    const braid_cpus = CpuMaskView.init(braid_words[0..], capacity);
    const window_cpus = CpuMaskView.init(window_words[0..], capacity);

    try expectBitmapCpuMirror(left_bitmap, left_cpus);
    try expectBitmapCpuMirror(right_bitmap, right_cpus);
    try expectBitmapCpuMirror(braid_bitmap, braid_cpus);
    try expectBitmapCpuMirror(window_bitmap, window_cpus);

    try std.testing.expect(left_bitmap.isSubsetOf(braid_bitmap));
    try std.testing.expect(right_bitmap.isSubsetOf(braid_bitmap));
    try std.testing.expect(left_cpus.isSubsetOf(braid_cpus));
    try std.testing.expect(right_cpus.isSubsetOf(braid_cpus));
    try std.testing.expect(!braid_bitmap.isSubsetOf(left_bitmap));
    try std.testing.expect(!braid_cpus.isSubsetOf(left_cpus));

    try std.testing.expect(left_bitmap.intersects(right_bitmap));
    try std.testing.expect(left_cpus.intersects(right_cpus));
    try std.testing.expect(!left_bitmap.intersects(window_bitmap));
    try std.testing.expect(!right_bitmap.intersects(window_bitmap));
    try std.testing.expect(!left_cpus.intersects(window_cpus));
    try std.testing.expect(!right_cpus.intersects(window_cpus));

    try std.testing.expectEqual(@as(usize, 6), left_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 7), right_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 10), braid_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 5), window_bitmap.countSetBits());
}

test "braid window exchange keeps cursors and declared tail bounded" {
    const capacity = word_bits * 2 + 13;
    const noise = tailNoise(capacity);
    const braid_words = [_]usize{
        bitMask(3) | bitMask(11) | bitMask(18) | bitMask(23) | bitMask(31),
        bitMask(word_bits + 4) | bitMask(word_bits + 21) | bitMask(word_bits + 29),
        bitMask(word_bits * 2 + 2) | bitMask(word_bits * 2 + 10) | noise,
    };

    const bitmap = BitmapView.init(braid_words[0..], capacity);
    const cpus = CpuMaskView.init(braid_words[0..], capacity);

    try std.testing.expectEqual(@as(?usize, 3), bitmap.nextSetBit(0));
    try std.testing.expectEqual(@as(?usize, 11), cpus.nextCpu(4));
    try std.testing.expectEqual(@as(?usize, 31), bitmap.nextSetBit(24));
    try std.testing.expectEqual(@as(?usize, word_bits + 4), cpus.nextCpu(32));
    try std.testing.expectEqual(@as(?usize, word_bits + 29), bitmap.nextSetBit(word_bits + 22));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 2), cpus.nextCpu(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 10), bitmap.nextSetBit(word_bits * 2 + 3));
    try std.testing.expectEqual(@as(?usize, null), cpus.nextCpu(capacity));

    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 4), cpus.nextMissingCpu(4));
    try std.testing.expectEqual(@as(?usize, word_bits + 5), bitmap.nextClearBit(word_bits + 5));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 3), cpus.nextMissingCpu(word_bits * 2 + 3));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextClearBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), cpus.nextMissingCpu(capacity));

    try std.testing.expectEqual(@as(usize, 10), bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 10), cpus.countPresentCpus());
}
