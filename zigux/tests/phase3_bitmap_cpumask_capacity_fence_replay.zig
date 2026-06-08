const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn expectBitmapCpuMirror(bitmap: BitmapView, cpus: CpuMaskView, expected_count: usize) !void {
    try std.testing.expectEqual(expected_count, bitmap.countSetBits());
    try std.testing.expectEqual(expected_count, cpus.countPresentCpus());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpus.firstCpu());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpus.firstMissingCpu());

    var cursor: usize = 0;
    while (cursor < bitmap.bit_len) : (cursor += 1) {
        try std.testing.expectEqual(bitmap.nextSetBit(cursor), cpus.nextCpu(cursor));
        try std.testing.expectEqual(bitmap.nextClearBit(cursor), cpus.nextMissingCpu(cursor));
    }
}

test "capacity fence clips bitmap and cpumask tail noise" {
    const capacity = word_bits + 9;
    const low_anchor = 2;
    const bridge = word_bits - 1;
    const fence_edge = word_bits + 8;
    const tail_noise = word_bits + 10;

    const fenced_words = [_]Word{
        bit(low_anchor) | bit(bridge),
        bit(fence_edge) | bit(tail_noise) | bit(tail_noise + 7),
    };
    const cpus = CpuMaskView.init(fenced_words[0..], capacity);
    const bitmap = BitmapView.init(fenced_words[0..], capacity);

    try expectBitmapCpuMirror(bitmap, cpus, 3);
    try std.testing.expect(cpus.hasCpu(low_anchor));
    try std.testing.expect(cpus.hasCpu(bridge));
    try std.testing.expect(cpus.hasCpu(fence_edge));
    try std.testing.expectEqual(@as(?usize, null), cpus.nextCpu(fence_edge + 1));
    try std.testing.expectEqual(@as(?usize, null), bitmap.nextSetBit(fence_edge + 1));
    try std.testing.expectEqual(@as(?usize, 0), cpus.firstMissingCpu());
    try std.testing.expectEqual(@as(?usize, word_bits), cpus.nextMissingCpu(word_bits));
}

test "capacity fence preserves relation checks across cpumask mirrors" {
    const capacity = word_bits + 13;
    const shared_low = 1;
    const shared_bridge = word_bits + 2;
    const candidate_only = word_bits + 12;
    const outside_capacity = word_bits + 20;

    const base_words = [_]Word{
        bit(shared_low),
        bit(shared_bridge) | bit(outside_capacity),
    };
    const candidate_words = [_]Word{
        bit(shared_low) | bit(5),
        bit(shared_bridge) | bit(candidate_only) | bit(outside_capacity),
    };
    const disjoint_words = [_]Word{
        bit(6),
        bit(word_bits + 5) | bit(outside_capacity),
    };

    const base_bitmap = BitmapView.init(base_words[0..], capacity);
    const candidate_bitmap = BitmapView.init(candidate_words[0..], capacity);
    const disjoint_bitmap = BitmapView.init(disjoint_words[0..], capacity);
    const base_cpus = CpuMaskView.init(base_words[0..], capacity);
    const candidate_cpus = CpuMaskView.init(candidate_words[0..], capacity);
    const disjoint_cpus = CpuMaskView.init(disjoint_words[0..], capacity);

    try std.testing.expect(base_bitmap.isSubsetOf(candidate_bitmap));
    try std.testing.expect(base_cpus.isSubsetOf(candidate_cpus));
    try std.testing.expect(!candidate_bitmap.isSubsetOf(base_bitmap));
    try std.testing.expect(!candidate_cpus.isSubsetOf(base_cpus));
    try std.testing.expect(candidate_bitmap.intersects(base_bitmap));
    try std.testing.expect(candidate_cpus.intersects(base_cpus));
    try std.testing.expect(!base_bitmap.intersects(disjoint_bitmap));
    try std.testing.expect(!base_cpus.intersects(disjoint_cpus));

    try expectBitmapCpuMirror(candidate_bitmap, candidate_cpus, 4);
    try std.testing.expectEqual(@as(?usize, shared_bridge), candidate_cpus.nextCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, candidate_only), candidate_cpus.nextCpu(shared_bridge + 1));
    try std.testing.expectEqual(@as(?usize, null), candidate_cpus.nextCpu(candidate_only + 1));
}
