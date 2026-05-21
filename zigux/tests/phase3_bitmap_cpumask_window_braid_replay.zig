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

test "window braid keeps bitmap and cpumask summaries aligned under bounded tail noise" {
    const capacity = (3 * bitmap_view.word_bits) + 7;
    const primary_bits = [_]usize{
        1,
        2,
        bitmap_view.word_bits - 1,
        bitmap_view.word_bits,
        bitmap_view.word_bits + 2,
        (2 * bitmap_view.word_bits) - 3,
        (2 * bitmap_view.word_bits) - 2,
        (3 * bitmap_view.word_bits) + 1,
        (3 * bitmap_view.word_bits) + 5,
        capacity - 1,
    };

    var words = [_]usize{ 0, 0, 0, 0, 0 };
    fillPattern(words[0..], capacity, primary_bits[0..]);
    addNoise(words[0..], capacity);

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(primary_bits.len, bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    try testing.expect(bitmap.isSet(bitmap_view.word_bits));
    try testing.expect(bitmap.isSet(capacity - 1));
    try testing.expect(cpumask.hasCpu((2 * bitmap_view.word_bits) - 2));
    try testing.expect(!cpumask.hasCpu(0));
    try testing.expect(!cpumask.hasCpu(bitmap_view.word_bits + 1));
    try testing.expect(!cpumask.hasCpu(capacity - 3));
}

test "braided peers intersect inside the valid window without collapsing into subsets" {
    const capacity = (3 * bitmap_view.word_bits) + 7;
    const primary_bits = [_]usize{
        1,
        2,
        bitmap_view.word_bits - 1,
        bitmap_view.word_bits,
        bitmap_view.word_bits + 2,
        (2 * bitmap_view.word_bits) - 3,
        (2 * bitmap_view.word_bits) - 2,
        (3 * bitmap_view.word_bits) + 1,
        (3 * bitmap_view.word_bits) + 5,
        capacity - 1,
    };
    const peer_bits = [_]usize{
        2,
        3,
        bitmap_view.word_bits - 2,
        bitmap_view.word_bits,
        bitmap_view.word_bits + 1,
        (2 * bitmap_view.word_bits) - 2,
        (2 * bitmap_view.word_bits) + 1,
        3 * bitmap_view.word_bits,
        (3 * bitmap_view.word_bits) + 5,
    };

    var primary_words = [_]usize{ 0, 0, 0, 0, 0 };
    var peer_words = [_]usize{ 0, 0, 0, 0, 0 };
    fillPattern(primary_words[0..], capacity, primary_bits[0..]);
    fillPattern(peer_words[0..], capacity, peer_bits[0..]);
    addNoise(primary_words[0..], capacity);
    addNoise(peer_words[0..], capacity);

    const full_words = [_]usize{
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
        std.math.maxInt(usize),
    };

    const primary = cpumask_view.CpuMaskView.init(primary_words[0..], capacity);
    const peer = cpumask_view.CpuMaskView.init(peer_words[0..], capacity);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], capacity);

    try testing.expect(primary.intersects(peer));
    try testing.expect(peer.intersects(primary));
    try testing.expect(!primary.isSubsetOf(peer));
    try testing.expect(!peer.isSubsetOf(primary));
    try testing.expect(primary.isSubsetOf(full));
    try testing.expect(peer.isSubsetOf(full));
    try testing.expectEqual(capacity, full.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), full.firstCpu());
    try testing.expectEqual(@as(?usize, null), full.firstMissingCpu());
}

test "narrowed braid stays a bounded subset of the broader primary shape" {
    const capacity = (3 * bitmap_view.word_bits) + 7;
    const primary_bits = [_]usize{
        1,
        2,
        bitmap_view.word_bits - 1,
        bitmap_view.word_bits,
        bitmap_view.word_bits + 2,
        (2 * bitmap_view.word_bits) - 3,
        (2 * bitmap_view.word_bits) - 2,
        (3 * bitmap_view.word_bits) + 1,
        (3 * bitmap_view.word_bits) + 5,
        capacity - 1,
    };
    const narrowed_bits = [_]usize{
        2,
        bitmap_view.word_bits,
        (2 * bitmap_view.word_bits) - 2,
        (3 * bitmap_view.word_bits) + 5,
    };

    var primary_words = [_]usize{ 0, 0, 0, 0, 0 };
    var narrowed_words = [_]usize{ 0, 0, 0, 0, 0 };
    fillPattern(primary_words[0..], capacity, primary_bits[0..]);
    fillPattern(narrowed_words[0..], capacity, narrowed_bits[0..]);
    addNoise(primary_words[0..], capacity);
    addNoise(narrowed_words[0..], capacity);

    const narrowed_bitmap = bitmap_view.BitmapView.init(narrowed_words[0..], capacity);
    const primary = cpumask_view.CpuMaskView.init(primary_words[0..], capacity);
    const narrowed = cpumask_view.CpuMaskView.init(narrowed_words[0..], capacity);

    try testing.expectEqual(narrowed_bits.len, narrowed_bitmap.countSetBits());
    try testing.expectEqual(narrowed_bitmap.countSetBits(), narrowed.countPresentCpus());
    try testing.expectEqual(@as(?usize, 2), narrowed_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), narrowed_bitmap.firstClearBit());
    try testing.expect(narrowed.isSubsetOf(primary));
    try testing.expect(primary.intersects(narrowed));
    try testing.expect(narrowed.intersects(primary));
    try testing.expect(!primary.isSubsetOf(narrowed));
    try testing.expect(narrowed.hasCpu(capacity - 2));
    try testing.expect(!narrowed.hasCpu(capacity - 1));
}
