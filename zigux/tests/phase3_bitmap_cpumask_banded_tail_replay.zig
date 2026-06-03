const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(relative_index: usize) usize {
    return @as(usize, 1) << @intCast(relative_index);
}

fn paddingAfter(relative_index: usize) usize {
    return ~@as(usize, 0) << @intCast(relative_index);
}

const wb = bitmap_view.word_bits;
const banded_tail_capacity = (4 * wb) + 17;

const banded_tail_words = [_]usize{
    bit(1) | bit(2) | bit(9) | bit(wb - 4),
    bit(0) | bit(11) | bit(12) | bit(wb - 1),
    bit(3) | bit(4) | bit(35),
    bit(6) | bit(7) | bit(wb - 2),
    bit(0) | bit(8) | bit(16) | paddingAfter(17),
};

test "bitmap banded-tail replay walks sparse bands and final tail bits" {
    const view = bitmap_view.BitmapView.init(banded_tail_words[0..], banded_tail_capacity);

    try testing.expectEqual(@as(usize, 17), view.countSetBits());
    try testing.expectEqual(@as(?usize, 1), view.firstSetBit());
    try testing.expectEqual(@as(?usize, 0), view.firstClearBit());
    try testing.expectEqual(@as(?usize, 2), view.nextSetBit(2));
    try testing.expectEqual(@as(?usize, 9), view.nextSetBit(3));
    try testing.expectEqual(@as(?usize, wb - 4), view.nextSetBit(10));
    try testing.expectEqual(@as(?usize, wb), view.nextSetBit(wb));
    try testing.expectEqual(@as(?usize, (2 * wb) + 3), view.nextSetBit((2 * wb) + 1));
    try testing.expectEqual(@as(?usize, (3 * wb) + 6), view.nextSetBit(3 * wb));
    try testing.expectEqual(@as(?usize, (4 * wb) + 16), view.nextSetBit((4 * wb) + 9));
    try testing.expectEqual(@as(?usize, null), view.nextSetBit(banded_tail_capacity));

    try testing.expectEqual(@as(?usize, wb + 1), view.nextClearBit(wb));
    try testing.expectEqual(@as(?usize, (4 * wb) + 1), view.nextClearBit(4 * wb));
    try testing.expectEqual(@as(?usize, null), view.nextClearBit(banded_tail_capacity));
}

test "cpumask banded-tail replay mirrors bitmap traversal and membership" {
    const bitmap = bitmap_view.BitmapView.init(banded_tail_words[0..], banded_tail_capacity);
    const mask = cpumask_view.CpuMaskView.init(banded_tail_words[0..], banded_tail_capacity);

    try testing.expect(mask.hasCpu(1));
    try testing.expect(mask.hasCpu(wb + 12));
    try testing.expect(mask.hasCpu((3 * wb) + 7));
    try testing.expect(mask.hasCpu((4 * wb) + 16));
    try testing.expect(!mask.hasCpu((4 * wb) + 15));
    try testing.expectEqual(bitmap.countSetBits(), mask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), mask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), mask.firstMissingCpu());
    try testing.expectEqual(bitmap.nextSetBit(2 * wb), mask.nextCpu(2 * wb));
    try testing.expectEqual(bitmap.nextClearBit((4 * wb) + 1), mask.nextMissingCpu((4 * wb) + 1));
}

test "banded-tail replay bounds subset and overlap to declared capacity" {
    const subset_words = [_]usize{
        bit(2) | bit(wb - 4),
        bit(11),
        bit(4),
        bit(7),
        bit(8) | paddingAfter(17),
    };
    const superset_words = [_]usize{
        banded_tail_words[0] | bit(20),
        banded_tail_words[1] | bit(20),
        banded_tail_words[2],
        banded_tail_words[3] | bit(12),
        (banded_tail_words[4] & ~paddingAfter(17)) | bit(4),
    };
    const padding_only_words = [_]usize{
        0,
        0,
        0,
        0,
        paddingAfter(17),
    };

    const subset_bitmap = bitmap_view.BitmapView.init(subset_words[0..], banded_tail_capacity);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], banded_tail_capacity);
    const padding_bitmap = bitmap_view.BitmapView.init(padding_only_words[0..], banded_tail_capacity);
    const subset_mask = cpumask_view.CpuMaskView.init(subset_words[0..], banded_tail_capacity);
    const superset_mask = cpumask_view.CpuMaskView.init(superset_words[0..], banded_tail_capacity);
    const padding_mask = cpumask_view.CpuMaskView.init(padding_only_words[0..], banded_tail_capacity);

    try testing.expect(subset_bitmap.isSubsetOf(superset_bitmap));
    try testing.expect(subset_mask.isSubsetOf(superset_mask));
    try testing.expect(!superset_bitmap.isSubsetOf(subset_bitmap));
    try testing.expect(!superset_mask.isSubsetOf(subset_mask));
    try testing.expect(!subset_bitmap.intersects(padding_bitmap));
    try testing.expect(!subset_mask.intersects(padding_mask));
    try testing.expectEqual(@as(usize, 0), padding_bitmap.countSetBits());
    try testing.expectEqual(@as(usize, 0), padding_mask.countPresentCpus());
}
