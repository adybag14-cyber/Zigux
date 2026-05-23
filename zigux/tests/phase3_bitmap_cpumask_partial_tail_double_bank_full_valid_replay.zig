const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn invalidTailNoise(bit_len: usize) usize {
    const remainder = bit_len % bitmap_view.word_bits;
    std.debug.assert(remainder != 0);

    const valid_mask = (@as(usize, 1) << @intCast(remainder)) - 1;
    return ~valid_mask;
}

test "lane27 double-bank full-valid bitmap replay keeps the trailing full window explicit" {
    const capacity = (bitmap_view.word_bits * 2) + 5;
    const words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        (@as(usize, 1) << 5) - 1 | invalidTailNoise(capacity),
    };
    const view = bitmap_view.BitmapView.init(words[0..], capacity);

    try testing.expectEqual(capacity, view.countSetBits());
    try testing.expectEqual(@as(?usize, 0), view.firstSetBit());
    try testing.expectEqual(@as(?usize, null), view.firstClearBit());
    try testing.expect(view.isSet((bitmap_view.word_bits * 2) - 1));
    try testing.expect(view.isSet(bitmap_view.word_bits * 2));
    try testing.expect(view.isSet(capacity - 1));
}

test "lane27 double-bank full-valid cpumask replay ignores tail-only noise in subset checks" {
    const capacity = (bitmap_view.word_bits * 2) + 5;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        (@as(usize, 1) << 5) - 1 | invalidTailNoise(capacity),
    };
    const peer_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        (@as(usize, 1) << 5) - 1 | invalidTailNoise(capacity),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const peer = cpumask_view.CpuMaskView.init(peer_words[0..], capacity);

    try testing.expectEqual(capacity, base.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), base.firstCpu());
    try testing.expectEqual(@as(?usize, null), base.firstMissingCpu());
    try testing.expect(base.isSubsetOf(peer));
    try testing.expect(peer.isSubsetOf(base));
    try testing.expect(base.intersects(peer));
}

test "lane27 double-bank full-valid cpumask replay treats pure tail noise as disjoint" {
    const capacity = (bitmap_view.word_bits * 2) + 5;
    const base_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        (@as(usize, 1) << 5) - 1 | invalidTailNoise(capacity),
    };
    const tail_noise_only_words = [_]usize{
        0,
        0,
        invalidTailNoise(capacity),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const tail_noise_only = cpumask_view.CpuMaskView.init(tail_noise_only_words[0..], capacity);

    try testing.expectEqual(@as(?usize, null), tail_noise_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), tail_noise_only.firstMissingCpu());
    try testing.expectEqual(@as(usize, 0), tail_noise_only.countPresentCpus());
    try testing.expect(tail_noise_only.isSubsetOf(base));
    try testing.expect(!base.isSubsetOf(tail_noise_only));
    try testing.expect(!base.intersects(tail_noise_only));
}
