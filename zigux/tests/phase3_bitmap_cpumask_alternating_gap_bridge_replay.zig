const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const word_bits = bitmap_view.word_bits;

fn bit(bit_index: usize) usize {
    return @as(usize, 1) << @intCast(bit_index % word_bits);
}

fn expectCursorPair(
    bitmap: bitmap_view.BitmapView,
    cpumask: cpumask_view.CpuMaskView,
    start: usize,
    expected_present: ?usize,
    expected_missing: ?usize,
) !void {
    try testing.expectEqual(expected_present, bitmap.nextSetBit(start));
    try testing.expectEqual(expected_present, cpumask.nextCpu(start));
    try testing.expectEqual(expected_missing, bitmap.nextClearBit(start));
    try testing.expectEqual(expected_missing, cpumask.nextMissingCpu(start));
}

test "phase3 bitmap/cpumask alternating gap bridge replay keeps cursors aligned" {
    const capacity = (word_bits * 2) + 7;
    const shared_words = [_]usize{
        bit(0) | bit(2) | bit(5),
        bit(word_bits + 1) | bit(word_bits + 4),
        bit(word_bits * 2) |
            bit((word_bits * 2) + 2) |
            bit((word_bits * 2) + 6) |
            (~@as(usize, 0) << 7),
    };
    const gap_words = [_]usize{
        bit(1) | bit(3) | bit(4),
        bit(word_bits) | bit(word_bits + 2) | bit(word_bits + 5),
        bit((word_bits * 2) + 1) |
            bit((word_bits * 2) + 3) |
            bit((word_bits * 2) + 5),
    };
    const superset_words = [_]usize{
        shared_words[0] | bit(1),
        shared_words[1] | bit(word_bits + 2),
        shared_words[2],
    };

    const bitmap = bitmap_view.BitmapView.init(shared_words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(shared_words[0..], capacity);
    const gaps = bitmap_view.BitmapView.init(gap_words[0..], capacity);
    const gap_mask = cpumask_view.CpuMaskView.init(gap_words[0..], capacity);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], capacity);
    const superset_cpumask = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);

    try testing.expectEqual(@as(usize, 8), bitmap.countSetBits());
    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, 1), bitmap.firstClearBit());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    try expectCursorPair(bitmap, cpumask, 0, 0, 1);
    try expectCursorPair(bitmap, cpumask, 3, 5, 3);
    try expectCursorPair(bitmap, cpumask, word_bits, word_bits + 1, word_bits);
    try expectCursorPair(bitmap, cpumask, word_bits + 2, word_bits + 4, word_bits + 2);
    try expectCursorPair(bitmap, cpumask, word_bits * 2 + 1, word_bits * 2 + 2, word_bits * 2 + 1);
    try expectCursorPair(bitmap, cpumask, word_bits * 2 + 6, word_bits * 2 + 6, null);
    try expectCursorPair(bitmap, cpumask, capacity, null, null);

    try testing.expect(bitmap.isSubsetOf(superset_bitmap));
    try testing.expect(cpumask.isSubsetOf(superset_cpumask));
    try testing.expect(!superset_bitmap.isSubsetOf(bitmap));
    try testing.expect(!superset_cpumask.isSubsetOf(cpumask));
    try testing.expect(!bitmap.intersects(gaps));
    try testing.expect(!cpumask.intersects(gap_mask));
    try testing.expect(bitmap.intersects(superset_bitmap));
    try testing.expect(cpumask.intersects(superset_cpumask));
}
