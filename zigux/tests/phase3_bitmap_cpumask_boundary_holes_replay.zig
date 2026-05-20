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

test "boundary holes stay aligned for bitmap and cpumask views" {
    const boundary_gap = bitmap_view.word_bits - 1;
    const capacity = bitmap_view.word_bits + 5;
    const tail_gap = capacity - 1;
    const words = [_]usize{
        std.math.maxInt(usize) & ~(@as(usize, 1) << @intCast(boundary_gap)),
        (tailMask(capacity) & ~(@as(usize, 1) << @intCast(tail_gap - bitmap_view.word_bits))) |
            inactiveTailNoise(capacity),
    };

    const bitmap = bitmap_view.BitmapView.init(words[0..], capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(capacity - 2, bitmap.countSetBits());
    try testing.expectEqual(@as(?usize, 0), bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, boundary_gap), bitmap.firstClearBit());
    try testing.expect(!bitmap.isSet(boundary_gap));
    try testing.expect(!bitmap.isSet(tail_gap));
    try testing.expect(bitmap.isSet(boundary_gap - 1));
    try testing.expect(bitmap.isSet(tail_gap - 1));

    try testing.expectEqual(capacity - 2, cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 0), cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, boundary_gap), cpumask.firstMissingCpu());
    try testing.expect(!cpumask.hasCpu(boundary_gap));
    try testing.expect(!cpumask.hasCpu(tail_gap));
    try testing.expect(cpumask.hasCpu(boundary_gap - 1));
    try testing.expect(cpumask.hasCpu(tail_gap - 1));
}

test "boundary holes keep subset and overlap checks honest" {
    const boundary_gap = bitmap_view.word_bits - 1;
    const capacity = bitmap_view.word_bits + 5;
    const tail_gap = capacity - 1;
    const base_words = [_]usize{
        std.math.maxInt(usize) & ~(@as(usize, 1) << @intCast(boundary_gap)),
        tailMask(capacity) & ~(@as(usize, 1) << @intCast(tail_gap - bitmap_view.word_bits)),
    };
    const full_words = [_]usize{
        std.math.maxInt(usize),
        tailMask(capacity),
    };
    const holes_only_words = [_]usize{
        (@as(usize, 1) << @intCast(boundary_gap)),
        (@as(usize, 1) << @intCast(tail_gap - bitmap_view.word_bits)) | inactiveTailNoise(capacity),
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const full = cpumask_view.CpuMaskView.init(full_words[0..], capacity);
    const holes_only = cpumask_view.CpuMaskView.init(holes_only_words[0..], capacity);

    try testing.expect(base.isSubsetOf(full));
    try testing.expect(!full.isSubsetOf(base));
    try testing.expect(!base.intersects(holes_only));
    try testing.expect(!holes_only.intersects(base));
    try testing.expect(full.intersects(holes_only));
    try testing.expectEqual(@as(?usize, boundary_gap), holes_only.firstCpu());
    try testing.expectEqual(@as(?usize, 0), holes_only.firstMissingCpu());
    try testing.expectEqual(@as(usize, 2), holes_only.countPresentCpus());
}
