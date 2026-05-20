const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn tailMask(bit_len: usize) usize {
    const remainder = bit_len % bitmap_view.word_bits;
    if (remainder == 0) return std.math.maxInt(usize);
    return (@as(usize, 1) << @intCast(remainder)) - 1;
}

fn inactiveTailNoise(bit_len: usize) usize {
    return ~tailMask(bit_len);
}

fn alternatingMask(start_bit: usize, bit_len: usize) usize {
    var word: usize = 0;
    var bit = start_bit;
    while (bit < bit_len) : (bit += 2) {
        word |= @as(usize, 1) << @intCast(bit);
    }
    return word;
}

test "alternating tail pattern stays aligned for bitmap and cpumask views" {
    const capacity = bitmap_view.word_bits + 7;
    const words = [_]usize{
        alternatingMask(0, bitmap_view.word_bits),
        alternatingMask(0, capacity - bitmap_view.word_bits) | inactiveTailNoise(capacity),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);
    const expected_count = (capacity + 1) / 2;
    const tail_bit = capacity - 1;

    try testing.expectEqual(expected_count, bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstClearBit());
    try testing.expect(bitmap.isSet(0));
    try testing.expect(!bitmap.isSet(1));
    try testing.expect(bitmap.isSet(tail_bit));

    try testing.expectEqual(expected_count, cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), cpumask.firstMissingCpu());
    try testing.expect(cpumask.hasCpu(0));
    try testing.expect(!cpumask.hasCpu(1));
    try testing.expect(cpumask.hasCpu(tail_bit));
}

test "alternating complements stay disjoint inside the bounded tail window" {
    const capacity = bitmap_view.word_bits + 7;
    const even_words = [_]usize{
        alternatingMask(0, bitmap_view.word_bits),
        alternatingMask(0, capacity - bitmap_view.word_bits) | inactiveTailNoise(capacity),
    };
    const odd_words = [_]usize{
        alternatingMask(1, bitmap_view.word_bits),
        alternatingMask(1, capacity - bitmap_view.word_bits) | inactiveTailNoise(capacity),
    };
    const full_words = [_]usize{
        std.math.maxInt(usize),
        tailMask(capacity),
    };

    const even = cpumask_view.CpuMaskView.init(even_words[0..], capacity);
    const odd = cpumask_view.CpuMaskView.init(odd_words[0..], capacity);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], capacity);

    try testing.expect(even.isSubsetOf(full));
    try testing.expect(odd.isSubsetOf(full));
    try testing.expect(!even.isSubsetOf(odd));
    try testing.expect(!odd.isSubsetOf(even));
    try testing.expect(!even.intersects(odd));
    try testing.expect(!odd.intersects(even));
    try testing.expectEqual(capacity, even.countPresentCpus() + odd.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), odd.firstCpu());
    try testing.expectEqual(@as(?usize, 0), odd.firstMissingCpu());
}
