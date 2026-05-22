const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn setBit(words: []usize, bit: usize) void {
    const word_index = bit / bitmap_view.word_bits;
    const bit_index = bit % bitmap_view.word_bits;
    words[word_index] |= @as(usize, 1) << @intCast(bit_index);
}

fn fillPattern(words: []usize, capacity: usize, pattern: []const usize) void {
    @memset(words, 0);
    for (pattern) |bit| {
        std.debug.assert(bit < capacity);
        setBit(words, bit);
    }
}

fn addNoise(words: []usize, capacity: usize) void {
    const active_word_len = if (capacity == 0) 0 else (capacity + (bitmap_view.word_bits - 1)) / bitmap_view.word_bits;
    if (active_word_len == 0) return;

    const remainder = capacity % bitmap_view.word_bits;
    if (remainder != 0) {
        const valid_mask = (@as(usize, 1) << @intCast(remainder)) - 1;
        words[active_word_len - 1] |= ~valid_mask;
    }
    if (words.len > active_word_len) {
        words[active_word_len] = std.math.maxInt(usize);
    }
}

test "spoke ring keeps bitmap and cpumask summaries aligned under noisy tail storage" {
    const capacity = (6 * bitmap_view.word_bits) + 11;
    const ring_bits = [_]usize{
        0,
        bitmap_view.word_bits - 1,
        bitmap_view.word_bits + 1,
        bitmap_view.word_bits + 7,
        2 * bitmap_view.word_bits,
        (2 * bitmap_view.word_bits) + 5,
        (3 * bitmap_view.word_bits) - 2,
        (3 * bitmap_view.word_bits) + 3,
        4 * bitmap_view.word_bits,
        (4 * bitmap_view.word_bits) + 6,
        (5 * bitmap_view.word_bits) - 1,
        (5 * bitmap_view.word_bits) + 2,
        capacity - 2,
    };

    var words = [_]usize{ 0, 0, 0, 0, 0, 0, 0, 0 };
    fillPattern(words[0..], capacity, ring_bits[0..]);
    addNoise(words[0..], capacity);

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(ring_bits.len, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet((4 * bitmap_view.word_bits) + 6));
    try testing.expect(cpumask.hasCpu(capacity - 2));
    try testing.expect(!cpumask.hasCpu(1));
    try testing.expect(!cpumask.hasCpu((2 * bitmap_view.word_bits) + 4));
}

test "peer spoke ring masks intersect on shared spokes without collapsing into a subset" {
    const capacity = (6 * bitmap_view.word_bits) + 11;
    const base_bits = [_]usize{
        0,
        bitmap_view.word_bits - 1,
        bitmap_view.word_bits + 1,
        bitmap_view.word_bits + 7,
        2 * bitmap_view.word_bits,
        (2 * bitmap_view.word_bits) + 5,
        (3 * bitmap_view.word_bits) - 2,
        (3 * bitmap_view.word_bits) + 3,
        4 * bitmap_view.word_bits,
        (4 * bitmap_view.word_bits) + 6,
        (5 * bitmap_view.word_bits) - 1,
        (5 * bitmap_view.word_bits) + 2,
        capacity - 2,
    };
    const peer_bits = [_]usize{
        0,
        bitmap_view.word_bits - 3,
        bitmap_view.word_bits + 1,
        bitmap_view.word_bits + 9,
        (2 * bitmap_view.word_bits) + 5,
        (3 * bitmap_view.word_bits) - 2,
        (3 * bitmap_view.word_bits) + 4,
        (4 * bitmap_view.word_bits) + 6,
        (5 * bitmap_view.word_bits) - 4,
        (5 * bitmap_view.word_bits) + 2,
        capacity - 4,
    };

    var base_words = [_]usize{ 0, 0, 0, 0, 0, 0, 0, 0 };
    var peer_words = [_]usize{ 0, 0, 0, 0, 0, 0, 0, 0 };
    fillPattern(base_words[0..], capacity, base_bits[0..]);
    fillPattern(peer_words[0..], capacity, peer_bits[0..]);
    addNoise(base_words[0..], capacity);
    addNoise(peer_words[0..], capacity);

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const peer = cpumask_view.CpuMaskView.init(peer_words[0..], capacity);

    try testing.expect(base.intersects(peer));
    try testing.expect(peer.intersects(base));
    try testing.expect(!base.isSubsetOf(peer));
    try testing.expect(!peer.isSubsetOf(base));
    try testing.expect(base.hasCpu(bitmap_view.word_bits + 7));
    try testing.expect(!peer.hasCpu(bitmap_view.word_bits + 7));
    try testing.expect(!base.hasCpu(capacity - 4));
    try testing.expect(peer.hasCpu(capacity - 4));
}

test "inner spoke ring stays a bounded subset of the broader shape" {
    const capacity = (6 * bitmap_view.word_bits) + 11;
    const base_bits = [_]usize{
        0,
        bitmap_view.word_bits - 1,
        bitmap_view.word_bits + 1,
        bitmap_view.word_bits + 7,
        2 * bitmap_view.word_bits,
        (2 * bitmap_view.word_bits) + 5,
        (3 * bitmap_view.word_bits) - 2,
        (3 * bitmap_view.word_bits) + 3,
        4 * bitmap_view.word_bits,
        (4 * bitmap_view.word_bits) + 6,
        (5 * bitmap_view.word_bits) - 1,
        (5 * bitmap_view.word_bits) + 2,
        capacity - 2,
    };
    const inner_bits = [_]usize{
        bitmap_view.word_bits + 1,
        (2 * bitmap_view.word_bits) + 5,
        (3 * bitmap_view.word_bits) - 2,
        (4 * bitmap_view.word_bits) + 6,
        (5 * bitmap_view.word_bits) + 2,
    };

    var base_words = [_]usize{ 0, 0, 0, 0, 0, 0, 0, 0 };
    var inner_words = [_]usize{ 0, 0, 0, 0, 0, 0, 0, 0 };
    fillPattern(base_words[0..], capacity, base_bits[0..]);
    fillPattern(inner_words[0..], capacity, inner_bits[0..]);
    addNoise(base_words[0..], capacity);
    addNoise(inner_words[0..], capacity);

    const inner_bitmap = bitmap_view.BitmapView.init(inner_words[0..], capacity);
    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const inner = cpumask_view.CpuMaskView.init(inner_words[0..], capacity);

    try testing.expectEqual(inner_bits.len, inner_bitmap.countSetBits());
    try testing.expectEqual(inner_bitmap.countSetBits(), inner.countPresentCpus());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 1), inner_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), inner_bitmap.firstClearBit());
    try testing.expect(inner.isSubsetOf(base));
    try testing.expect(base.intersects(inner));
    try testing.expect(inner.intersects(base));
    try testing.expect(!base.isSubsetOf(inner));
    try testing.expect(inner.hasCpu((5 * bitmap_view.word_bits) + 2));
    try testing.expect(!inner.hasCpu(0));
}
