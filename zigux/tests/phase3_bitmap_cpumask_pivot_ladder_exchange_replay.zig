const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const word_bits = bitmap_view.word_bits;

fn bitMask(bit_index: usize) usize {
    return @as(usize, 1) << @intCast(bit_index % word_bits);
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

test "bitmap and cpumask mirror pivot ladder exchange relations" {
    const capacity = word_bits * 2 + 11;

    const pivot_words = [_]usize{
        bitMask(2) | bitMask(9),
        bitMask(word_bits + 3) | bitMask(word_bits + 10),
        bitMask(word_bits * 2 + 4) | (std.math.maxInt(usize) & ~(@as(usize, 0x7ff))),
    };
    const ladder_words = [_]usize{
        bitMask(2) | bitMask(14),
        bitMask(word_bits + 3) | bitMask(word_bits + 17),
        bitMask(word_bits * 2 + 4) | bitMask(word_bits * 2 + 9) | (std.math.maxInt(usize) & ~(@as(usize, 0x7ff))),
    };
    const exchange_words = [_]usize{
        bitMask(2) | bitMask(9) | bitMask(14),
        bitMask(word_bits + 3) | bitMask(word_bits + 10) | bitMask(word_bits + 17),
        bitMask(word_bits * 2 + 4) | bitMask(word_bits * 2 + 9) | (std.math.maxInt(usize) & ~(@as(usize, 0x7ff))),
    };
    const outside_words = [_]usize{
        bitMask(0) | bitMask(1),
        bitMask(word_bits + 1),
        bitMask(word_bits * 2 + 7) | (std.math.maxInt(usize) & ~(@as(usize, 0x7ff))),
    };

    const pivot_bitmap = BitmapView.init(pivot_words[0..], capacity);
    const ladder_bitmap = BitmapView.init(ladder_words[0..], capacity);
    const exchange_bitmap = BitmapView.init(exchange_words[0..], capacity);
    const outside_bitmap = BitmapView.init(outside_words[0..], capacity);

    const pivot_cpus = CpuMaskView.init(pivot_words[0..], capacity);
    const ladder_cpus = CpuMaskView.init(ladder_words[0..], capacity);
    const exchange_cpus = CpuMaskView.init(exchange_words[0..], capacity);
    const outside_cpus = CpuMaskView.init(outside_words[0..], capacity);

    try expectBitmapCpuMirror(pivot_bitmap, pivot_cpus);
    try expectBitmapCpuMirror(ladder_bitmap, ladder_cpus);
    try expectBitmapCpuMirror(exchange_bitmap, exchange_cpus);

    try std.testing.expect(pivot_bitmap.isSubsetOf(exchange_bitmap));
    try std.testing.expect(ladder_bitmap.isSubsetOf(exchange_bitmap));
    try std.testing.expect(pivot_cpus.isSubsetOf(exchange_cpus));
    try std.testing.expect(ladder_cpus.isSubsetOf(exchange_cpus));
    try std.testing.expect(!exchange_bitmap.isSubsetOf(pivot_bitmap));
    try std.testing.expect(!exchange_cpus.isSubsetOf(pivot_cpus));

    try std.testing.expect(pivot_bitmap.intersects(ladder_bitmap));
    try std.testing.expect(pivot_cpus.intersects(ladder_cpus));
    try std.testing.expect(!pivot_bitmap.intersects(outside_bitmap));
    try std.testing.expect(!ladder_bitmap.intersects(outside_bitmap));
    try std.testing.expect(!pivot_cpus.intersects(outside_cpus));
    try std.testing.expect(!ladder_cpus.intersects(outside_cpus));

    try std.testing.expectEqual(@as(usize, 5), pivot_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 6), ladder_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 8), exchange_bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 4), outside_bitmap.countSetBits());
}

test "pivot ladder exchange keeps cursors and tail noise bounded" {
    const capacity = word_bits * 2 + 11;
    const exchange_words = [_]usize{
        bitMask(2) | bitMask(9) | bitMask(14),
        bitMask(word_bits + 3) | bitMask(word_bits + 10) | bitMask(word_bits + 17),
        bitMask(word_bits * 2 + 4) | bitMask(word_bits * 2 + 9) | (std.math.maxInt(usize) & ~(@as(usize, 0x7ff))),
    };

    const bitmap = BitmapView.init(exchange_words[0..], capacity);
    const cpus = CpuMaskView.init(exchange_words[0..], capacity);

    try std.testing.expectEqual(@as(?usize, 2), bitmap.nextSetBit(0));
    try std.testing.expectEqual(@as(?usize, 9), cpus.nextCpu(3));
    try std.testing.expectEqual(@as(?usize, word_bits + 3), bitmap.nextSetBit(15));
    try std.testing.expectEqual(@as(?usize, word_bits + 17), cpus.nextCpu(word_bits + 11));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 4), bitmap.nextSetBit(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 9), cpus.nextCpu(word_bits * 2 + 5));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), cpus.nextCpu(capacity));

    try std.testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try std.testing.expectEqual(@as(?usize, 3), cpus.nextMissingCpu(3));
    try std.testing.expectEqual(@as(?usize, word_bits + 4), bitmap.nextClearBit(word_bits + 4));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 5), cpus.nextMissingCpu(word_bits * 2 + 5));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextClearBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), cpus.nextMissingCpu(capacity));

    try std.testing.expectEqual(@as(usize, 8), bitmap.countSetBits());
    try std.testing.expectEqual(@as(usize, 8), cpus.countPresentCpus());
}
