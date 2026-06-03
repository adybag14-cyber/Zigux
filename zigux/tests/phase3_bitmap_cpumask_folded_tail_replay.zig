const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(relative_index: usize) usize {
    return @as(usize, 1) << @intCast(relative_index);
}

const wb = bitmap_view.word_bits;
const folded_tail_capacity = (3 * wb) + 11;

const folded_tail_words = [_]usize{
    bit(0) | bit(7) | bit(wb - 1),
    bit(2) | bit(5),
    bit(wb - 3),
    bit(0) | bit(3) | bit(10) | (~@as(usize, 0) << 11),
};

test "bitmap folded-tail replay keeps traversal bounded across reused tail storage" {
    const view = bitmap_view.BitmapView.init(folded_tail_words[0..], folded_tail_capacity);

    try testing.expectEqual(@as(usize, 9), view.countSetBits());
    try testing.expectEqual(@as(?usize, 0), view.firstSetBit());
    try testing.expectEqual(@as(?usize, 1), view.firstClearBit());
    try testing.expectEqual(@as(?usize, 7), view.nextSetBit(1));
    try testing.expectEqual(@as(?usize, wb - 1), view.nextSetBit(8));
    try testing.expectEqual(@as(?usize, wb + 2), view.nextSetBit(wb));
    try testing.expectEqual(@as(?usize, (2 * wb) + (wb - 3)), view.nextSetBit((2 * wb) + 1));
    try testing.expectEqual(@as(?usize, 3 * wb), view.nextSetBit(3 * wb));
    try testing.expectEqual(@as(?usize, (3 * wb) + 10), view.nextSetBit((3 * wb) + 4));
    try testing.expectEqual(@as(?usize, null), view.nextSetBit(folded_tail_capacity));

    try testing.expectEqual(@as(?usize, wb), view.nextClearBit(wb));
    try testing.expectEqual(@as(?usize, (3 * wb) + 1), view.nextClearBit(3 * wb));
    try testing.expectEqual(@as(?usize, null), view.nextClearBit(folded_tail_capacity));
}

test "cpumask folded-tail replay mirrors bitmap membership and walks" {
    const bitmap = bitmap_view.BitmapView.init(folded_tail_words[0..], folded_tail_capacity);
    const mask = cpumask_view.CpuMaskView.init(folded_tail_words[0..], folded_tail_capacity);

    try testing.expect(mask.hasCpu(0));
    try testing.expect(mask.hasCpu(wb + 2));
    try testing.expect(mask.hasCpu((3 * wb) + 10));
    try testing.expect(!mask.hasCpu((3 * wb) + 9));
    try testing.expectEqual(bitmap.countSetBits(), mask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), mask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), mask.firstMissingCpu());
    try testing.expectEqual(bitmap.nextSetBit(wb + 3), mask.nextCpu(wb + 3));
    try testing.expectEqual(bitmap.nextClearBit((3 * wb) + 4), mask.nextMissingCpu((3 * wb) + 4));
}

test "folded-tail replay ignores padding-only overlap and subset noise" {
    const subset_words = [_]usize{
        bit(7),
        bit(2),
        0,
        bit(3) | (~@as(usize, 0) << 11),
    };
    const superset_words = [_]usize{
        folded_tail_words[0] | bit(9),
        folded_tail_words[1] | bit(1),
        folded_tail_words[2],
        (folded_tail_words[3] & ~(~@as(usize, 0) << 11)) | bit(8),
    };
    const padding_only_words = [_]usize{
        0,
        0,
        0,
        ~@as(usize, 0) << 11,
    };

    const subset_bitmap = bitmap_view.BitmapView.init(subset_words[0..], folded_tail_capacity);
    const superset_bitmap = bitmap_view.BitmapView.init(superset_words[0..], folded_tail_capacity);
    const padding_bitmap = bitmap_view.BitmapView.init(padding_only_words[0..], folded_tail_capacity);
    const subset_mask = cpumask_view.CpuMaskView.init(subset_words[0..], folded_tail_capacity);
    const superset_mask = cpumask_view.CpuMaskView.init(superset_words[0..], folded_tail_capacity);
    const padding_mask = cpumask_view.CpuMaskView.init(padding_only_words[0..], folded_tail_capacity);

    try testing.expect(subset_bitmap.isSubsetOf(superset_bitmap));
    try testing.expect(subset_mask.isSubsetOf(superset_mask));
    try testing.expect(!subset_bitmap.intersects(padding_bitmap));
    try testing.expect(!subset_mask.intersects(padding_mask));
    try testing.expectEqual(@as(usize, 0), padding_bitmap.countSetBits());
    try testing.expectEqual(@as(usize, 0), padding_mask.countPresentCpus());
}
