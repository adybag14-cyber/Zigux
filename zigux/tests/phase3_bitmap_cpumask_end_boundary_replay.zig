const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn finalActiveBit() usize {
    return bitmap_view.word_bits + 8;
}

fn finalBitOnlyWords() [2]usize {
    return .{
        0,
        (@as(usize, 1) << 8) | (~@as(usize, 0) << 9),
    };
}

test "bitmap end-boundary replay stops set scans at declared capacity" {
    const capacity = finalActiveBit() + 1;
    const words = finalBitOnlyWords();
    const view = bitmap_view.BitmapView.init(words[0..], capacity);

    try testing.expect(view.isSet(finalActiveBit()));
    try testing.expectEqual(@as(usize, 1), view.countSetBits());
    try testing.expectEqual(@as(?usize, finalActiveBit()), view.firstSetBit());
    try testing.expectEqual(@as(?usize, finalActiveBit()), view.nextSetBit(finalActiveBit()));
    try testing.expectEqual(@as(?usize, null), view.nextSetBit(capacity));
}

test "bitmap end-boundary replay does not report padding as clear space" {
    const capacity = finalActiveBit() + 1;
    const words = finalBitOnlyWords();
    const view = bitmap_view.BitmapView.init(words[0..], capacity);

    try testing.expectEqual(@as(?usize, 0), view.firstClearBit());
    try testing.expectEqual(@as(?usize, null), view.nextClearBit(finalActiveBit()));
    try testing.expectEqual(@as(?usize, null), view.nextClearBit(capacity));
}

test "bitmap end-boundary replay masks padding in subset and overlap checks" {
    const capacity = finalActiveBit() + 1;
    const base_words = finalBitOnlyWords();
    const superset_words = [_]usize{
        0,
        (@as(usize, 1) << 8) | std.math.maxInt(usize),
    };
    const padding_only_words = [_]usize{
        0,
        ~@as(usize, 0) << 9,
    };

    const base = bitmap_view.BitmapView.init(base_words[0..], capacity);
    const superset = bitmap_view.BitmapView.init(superset_words[0..], capacity);
    const padding_only = bitmap_view.BitmapView.init(padding_only_words[0..], capacity);

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(padding_only));
    try testing.expect(!base.intersects(padding_only));
}

test "cpumask end-boundary replay mirrors final-cpu scan behavior" {
    const capacity = finalActiveBit() + 1;
    const words = finalBitOnlyWords();
    const mask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expect(mask.hasCpu(finalActiveBit()));
    try testing.expectEqual(@as(usize, 1), mask.countPresentCpus());
    try testing.expectEqual(@as(?usize, finalActiveBit()), mask.firstCpu());
    try testing.expectEqual(@as(?usize, finalActiveBit()), mask.nextCpu(finalActiveBit()));
    try testing.expectEqual(@as(?usize, null), mask.nextCpu(capacity));
}

test "cpumask end-boundary replay keeps padding-only cpus invisible" {
    const capacity = finalActiveBit() + 1;
    const words = finalBitOnlyWords();
    const mask = cpumask_view.CpuMaskView.init(words[0..], capacity);

    try testing.expectEqual(@as(?usize, 0), mask.firstMissingCpu());
    try testing.expectEqual(@as(?usize, null), mask.nextMissingCpu(finalActiveBit()));
    try testing.expectEqual(@as(?usize, null), mask.nextMissingCpu(capacity));
}

test "cpumask end-boundary replay mirrors bounded subset and overlap" {
    const capacity = finalActiveBit() + 1;
    const base_words = finalBitOnlyWords();
    const superset_words = [_]usize{
        0,
        (@as(usize, 1) << 8) | std.math.maxInt(usize),
    };
    const padding_only_words = [_]usize{
        0,
        ~@as(usize, 0) << 9,
    };

    const base = cpumask_view.CpuMaskView.init(base_words[0..], capacity);
    const superset = cpumask_view.CpuMaskView.init(superset_words[0..], capacity);
    const padding_only = cpumask_view.CpuMaskView.init(padding_only_words[0..], capacity);

    try testing.expect(base.isSubsetOf(superset));
    try testing.expect(!superset.isSubsetOf(padding_only));
    try testing.expect(!base.intersects(padding_only));
}
