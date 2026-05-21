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

test "rung weave keeps bitmap and cpumask summaries aligned under noisy tail storage" {
    const capacity = (3 * bitmap_view.word_bits) + 19;
    const weave_bits = [_]usize{
        1,
        4,
        bitmap_view.word_bits - 3,
        bitmap_view.word_bits + 2,
        bitmap_view.word_bits + 5,
        (2 * bitmap_view.word_bits) - 1,
        2 * bitmap_view.word_bits,
        (2 * bitmap_view.word_bits) + 4,
        (2 * bitmap_view.word_bits) + 9,
        capacity - 4,
        capacity - 1,
    };

    var words = [_]usize{ 0, 0, 0, 0, 0 };
    fillPattern(words[0..], capacity, weave_bits[0..]);
    addNoise(words[0..], capacity);

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(weave_bits.len, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet((2 * bitmap_view.word_bits) + 9));
    try testing.expect(cpumask.hasCpu(capacity - 1));
    try testing.expect(!cpumask.hasCpu(0));
    try testing.expect(!cpumask.hasCpu(capacity - 2));
}

test "peer rung weave overlaps on shared rungs without collapsing into a subset" {
    const capacity = (3 * bitmap_view.word_bits) + 19;
    const base_bits = [_]usize{
        1,
        4,
        bitmap_view.word_bits - 3,
        bitmap_view.word_bits + 2,
        bitmap_view.word_bits + 5,
        (2 * bitmap_view.word_bits) - 1,
        2 * bitmap_view.word_bits,
        (2 * bitmap_view.word_bits) + 4,
        (2 * bitmap_view.word_bits) + 9,
        capacity - 4,
        capacity - 1,
    };
    const peer_bits = [_]usize{
        1,
        3,
        bitmap_view.word_bits - 3,
        bitmap_view.word_bits + 1,
        bitmap_view.word_bits + 5,
        (2 * bitmap_view.word_bits) - 1,
        (2 * bitmap_view.word_bits) + 3,
        (2 * bitmap_view.word_bits) + 4,
        (2 * bitmap_view.word_bits) + 10,
        capacity - 4,
        capacity - 2,
    };

    var base_words = [_]usize{ 0, 0, 0, 0, 0 };
    var peer_words = [_]usize{ 0, 0, 0, 0, 0 };
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
    try testing.expect(base.hasCpu(bitmap_view.word_bits + 2));
    try testing.expect(!peer.hasCpu(bitmap_view.word_bits + 2));
    try testing.expect(!base.hasCpu(capacity - 2));
    try testing.expect(peer.hasCpu(capacity - 2));
}

test "narrow rung weave stays a bounded subset of the broader weave" {
    const capacity = (3 * bitmap_view.word_bits) + 19;
    const base_bits = [_]usize{
        1,
        4,
        bitmap_view.word_bits - 3,
        bitmap_view.word_bits + 2,
        bitmap_view.word_bits + 5,
        (2 * bitmap_view.word_bits) - 1,
        2 * bitmap_view.word_bits,
        (2 * bitmap_view.word_bits) + 4,
        (2 * bitmap_view.word_bits) + 9,
        capacity - 4,
        capacity - 1,
    };
    const narrow_bits = [_]usize{
        bitmap_view.word_bits - 3,
        bitmap_view.word_bits + 5,
        (2 * bitmap_view.word_bits) + 4,
        capacity - 4,
    };

    var base_words = [_]usize{ 0, 0, 0, 0, 0 };
    var narrow_words = [_]usize{ 0, 0, 0, 0, 0 };
    fillPattern(base_words[0..], capacity, base_bits[0..]);
    fillPattern(narrow_words[0..], capacity, narrow_bits[0..]);
    addNoise(base_words[0..], capacity);
    addNoise(narrow_words[0..], capacity);

    const narrow_bitmap = bitmap_view.BitmapView.init(narrow_words[0..], capacity);
    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const narrow = cpumask_view.CpuMaskView.init(narrow_words[0..], capacity);

    try testing.expectEqual(narrow_bits.len, narrow_bitmap.countSetBits());
    try testing.expectEqual(narrow_bitmap.countSetBits(), narrow.countPresentCpus());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits - 3), narrow_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), narrow_bitmap.firstClearBit());
    try testing.expect(narrow.isSubsetOf(base));
    try testing.expect(base.intersects(narrow));
    try testing.expect(narrow.intersects(base));
    try testing.expect(!base.isSubsetOf(narrow));
    try testing.expect(narrow.hasCpu(capacity - 4));
    try testing.expect(!narrow.hasCpu(1));
}
