const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bitmapSubsetOf(lhs: bitmap_view.BitmapView, rhs: bitmap_view.BitmapView) bool {
    std.debug.assert(lhs.bit_len == rhs.bit_len);
    for (0..lhs.bit_len) |bit| {
        if (lhs.isSet(bit) and !rhs.isSet(bit)) return false;
    }
    return true;
}

fn bitmapIntersects(lhs: bitmap_view.BitmapView, rhs: bitmap_view.BitmapView) bool {
    std.debug.assert(lhs.bit_len == rhs.bit_len);
    for (0..lhs.bit_len) |bit| {
        if (lhs.isSet(bit) and rhs.isSet(bit)) return true;
    }
    return false;
}

fn expectLockstep(words: []const usize, capacity: usize) !void {
    const bitmap = bitmap_view.BitmapView.init(words, capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words, capacity);

    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());
    for (0..capacity) |bit| {
        try testing.expectEqual(bitmap.isSet(bit), cpumask.hasCpu(bit));
    }
}

fn expectRelationLockstep(
    lhs_words: []const usize,
    rhs_words: []const usize,
    capacity: usize,
) !void {
    const lhs_bitmap = bitmap_view.BitmapView.init(lhs_words, capacity);
    const rhs_bitmap = bitmap_view.BitmapView.init(rhs_words, capacity);
    const lhs_cpumask = cpumask_view.CpuMaskView.init(lhs_words, capacity);
    const rhs_cpumask = cpumask_view.CpuMaskView.init(rhs_words, capacity);

    try testing.expectEqual(bitmapSubsetOf(lhs_bitmap, rhs_bitmap), lhs_cpumask.isSubsetOf(rhs_cpumask));
    try testing.expectEqual(bitmapSubsetOf(rhs_bitmap, lhs_bitmap), rhs_cpumask.isSubsetOf(lhs_cpumask));
    try testing.expectEqual(bitmapIntersects(lhs_bitmap, rhs_bitmap), lhs_cpumask.intersects(rhs_cpumask));
    try testing.expectEqual(bitmapIntersects(rhs_bitmap, lhs_bitmap), rhs_cpumask.intersects(lhs_cpumask));
}

test "lane27 lockstep replay keeps zero-capacity views empty even with noisy backing words" {
    const lhs_words = [_]usize{ std.math.maxInt(usize), std.math.maxInt(usize) };
    const rhs_words = [_]usize{ 0, std.math.maxInt(usize) };

    try expectLockstep(lhs_words[0..], 0);
    try expectLockstep(rhs_words[0..], 0);
    try expectRelationLockstep(lhs_words[0..], rhs_words[0..], 0);
}

test "lane27 lockstep replay ignores a fully out-of-range trailing word on exact word boundaries" {
    const lhs_words = [_]usize{
        (@as(usize, 1) << 1) | (@as(usize, 1) << 5) | (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        std.math.maxInt(usize),
    };
    const rhs_words = [_]usize{
        (@as(usize, 1) << 1) | (@as(usize, 1) << 5),
        (@as(usize, 1) << 7),
    };

    try expectLockstep(lhs_words[0..], bitmap_view.word_bits);
    try expectLockstep(rhs_words[0..], bitmap_view.word_bits);
    try expectRelationLockstep(lhs_words[0..], rhs_words[0..], bitmap_view.word_bits);
}

test "lane27 lockstep replay keeps partial-tail subset and overlap checks aligned" {
    const capacity = bitmap_view.word_bits + 2;
    const lhs_words = [_]usize{
        (@as(usize, 1) << 0) | (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        (@as(usize, 1) << 1) | (@as(usize, 1) << 6),
    };
    const rhs_words = [_]usize{
        (@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << (bitmap_view.word_bits - 1)),
        (@as(usize, 1) << 1) | (@as(usize, 1) << 9),
    };

    try expectLockstep(lhs_words[0..], capacity);
    try expectLockstep(rhs_words[0..], capacity);
    try expectRelationLockstep(lhs_words[0..], rhs_words[0..], capacity);
}
