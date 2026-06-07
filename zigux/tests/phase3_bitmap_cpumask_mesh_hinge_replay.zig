const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const word_bits = bitmap_view.word_bits;
const Word = usize;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index % word_bits);
}

fn tailNoise(active_tail_bits: usize) Word {
    return ~@as(Word, 0) << @intCast(active_tail_bits);
}

fn bitmap(words: []const Word, capacity: usize) bitmap_view.BitmapView {
    return bitmap_view.BitmapView.init(words, capacity);
}

fn cpumask(words: []const Word, capacity: usize) cpumask_view.CpuMaskView {
    return cpumask_view.CpuMaskView.init(words, capacity);
}

fn expectMirror(words: []const Word, capacity: usize, count: usize, first_set: ?usize, first_clear: ?usize) !void {
    const b = bitmap(words, capacity);
    const c = cpumask(words, capacity);

    try testing.expectEqual(count, b.countSetBits());
    try testing.expectEqual(count, c.countPresentCpus());
    try testing.expectEqual(first_set, b.firstSetBit());
    try testing.expectEqual(first_set, c.firstCpu());
    try testing.expectEqual(first_clear, b.firstClearBit());
    try testing.expectEqual(first_clear, c.firstMissingCpu());
}

test "lane27 mesh hinge keeps relation and cursor mirrors aligned" {
    const capacity = (word_bits * 2) + 17;
    const mesh_words = [_]Word{
        bit(0) | bit(4) | bit(9) | bit(13) | bit(18) | bit(24) | bit(31),
        bit(word_bits + 2) | bit(word_bits + 7) | bit(word_bits + 12) | bit(word_bits + 19) | bit(word_bits + 28),
        bit((word_bits * 2) + 1) | bit((word_bits * 2) + 5) | bit((word_bits * 2) + 9) | bit((word_bits * 2) + 16) | tailNoise(17),
    };
    const left_hinge_words = [_]Word{
        bit(0) | bit(9) | bit(18) | bit(31),
        bit(word_bits + 7) | bit(word_bits + 19),
        bit((word_bits * 2) + 5) | bit((word_bits * 2) + 16) | tailNoise(17),
    };
    const right_hinge_words = [_]Word{
        bit(4) | bit(13) | bit(24),
        bit(word_bits + 2) | bit(word_bits + 12) | bit(word_bits + 28),
        bit((word_bits * 2) + 1) | bit((word_bits * 2) + 9) | tailNoise(17),
    };
    const hinge_bridge_words = [_]Word{
        bit(0) | bit(4) | bit(9) | bit(13),
        bit(word_bits + 7) | bit(word_bits + 12),
        bit((word_bits * 2) + 5) | tailNoise(17),
    };
    const outside_gap_words = [_]Word{
        bit(2) | bit(6) | bit(15) | bit(21) | bit(29),
        bit(word_bits + 4) | bit(word_bits + 10) | bit(word_bits + 17) | bit(word_bits + 25),
        bit((word_bits * 2) + 3) | bit((word_bits * 2) + 11) | tailNoise(17),
    };

    const mesh_bitmap = bitmap(mesh_words[0..], capacity);
    const left_bitmap = bitmap(left_hinge_words[0..], capacity);
    const right_bitmap = bitmap(right_hinge_words[0..], capacity);
    const bridge_bitmap = bitmap(hinge_bridge_words[0..], capacity);
    const outside_bitmap = bitmap(outside_gap_words[0..], capacity);
    const mesh_mask = cpumask(mesh_words[0..], capacity);
    const left_mask = cpumask(left_hinge_words[0..], capacity);
    const right_mask = cpumask(right_hinge_words[0..], capacity);
    const bridge_mask = cpumask(hinge_bridge_words[0..], capacity);
    const outside_mask = cpumask(outside_gap_words[0..], capacity);

    try expectMirror(mesh_words[0..], capacity, 16, 0, 1);
    try expectMirror(left_hinge_words[0..], capacity, 8, 0, 1);
    try expectMirror(right_hinge_words[0..], capacity, 8, 4, 0);
    try expectMirror(hinge_bridge_words[0..], capacity, 7, 0, 1);
    try expectMirror(outside_gap_words[0..], capacity, 11, 2, 0);

    try testing.expect(left_bitmap.isSubsetOf(mesh_bitmap));
    try testing.expect(right_bitmap.isSubsetOf(mesh_bitmap));
    try testing.expect(bridge_bitmap.isSubsetOf(mesh_bitmap));
    try testing.expect(!mesh_bitmap.isSubsetOf(bridge_bitmap));
    try testing.expect(!left_bitmap.intersects(right_bitmap));
    try testing.expect(bridge_bitmap.intersects(left_bitmap));
    try testing.expect(bridge_bitmap.intersects(right_bitmap));
    try testing.expect(!mesh_bitmap.intersects(outside_bitmap));

    try testing.expect(left_mask.isSubsetOf(mesh_mask));
    try testing.expect(right_mask.isSubsetOf(mesh_mask));
    try testing.expect(bridge_mask.isSubsetOf(mesh_mask));
    try testing.expect(!mesh_mask.isSubsetOf(bridge_mask));
    try testing.expect(!left_mask.intersects(right_mask));
    try testing.expect(bridge_mask.intersects(left_mask));
    try testing.expect(bridge_mask.intersects(right_mask));
    try testing.expect(!mesh_mask.intersects(outside_mask));

    try testing.expectEqual(@as(?usize, 13), mesh_bitmap.nextSetBit(10));
    try testing.expectEqual(@as(?usize, word_bits + 12), mesh_bitmap.nextSetBit(word_bits + 8));
    try testing.expectEqual(@as(?usize, (word_bits * 2) + 16), mesh_bitmap.nextSetBit((word_bits * 2) + 10));
    try testing.expectEqual(@as(?usize, null), mesh_bitmap.nextSetBit(capacity));
    try testing.expectEqual(@as(?usize, 13), mesh_mask.nextCpu(10));
    try testing.expectEqual(@as(?usize, word_bits + 12), mesh_mask.nextCpu(word_bits + 8));
    try testing.expectEqual(@as(?usize, (word_bits * 2) + 16), mesh_mask.nextCpu((word_bits * 2) + 10));
    try testing.expectEqual(@as(?usize, null), mesh_mask.nextCpu(capacity));
}

test "lane27 mesh hinge tracks closure without counting declared-tail noise" {
    const capacity = word_bits + 15;
    const open_words = [_]Word{
        bit(3) | bit(8) | bit(14) | bit(23) | bit(30),
        bit(word_bits + 2) | bit(word_bits + 9) | tailNoise(15),
    };
    const closed_words = [_]Word{
        bit(3) | bit(8) | bit(14) | bit(20) | bit(23) | bit(30),
        bit(word_bits + 2) | bit(word_bits + 6) | bit(word_bits + 9) | bit(word_bits + 14) | tailNoise(15),
    };
    const hinge_only_words = [_]Word{
        bit(20),
        bit(word_bits + 6) | bit(word_bits + 14) | tailNoise(15),
    };
    const tail_noise_only_words = [_]Word{
        0,
        tailNoise(15),
    };

    const open_bitmap = bitmap(open_words[0..], capacity);
    const closed_bitmap = bitmap(closed_words[0..], capacity);
    const hinge_bitmap = bitmap(hinge_only_words[0..], capacity);
    const noise_bitmap = bitmap(tail_noise_only_words[0..], capacity);
    const open_mask = cpumask(open_words[0..], capacity);
    const closed_mask = cpumask(closed_words[0..], capacity);
    const hinge_mask = cpumask(hinge_only_words[0..], capacity);
    const noise_mask = cpumask(tail_noise_only_words[0..], capacity);

    try expectMirror(open_words[0..], capacity, 7, 3, 0);
    try expectMirror(closed_words[0..], capacity, 10, 3, 0);
    try expectMirror(hinge_only_words[0..], capacity, 3, 20, 0);
    try expectMirror(tail_noise_only_words[0..], capacity, 0, null, 0);

    try testing.expect(open_bitmap.isSubsetOf(closed_bitmap));
    try testing.expect(!closed_bitmap.isSubsetOf(open_bitmap));
    try testing.expect(!hinge_bitmap.intersects(open_bitmap));
    try testing.expect(hinge_bitmap.intersects(closed_bitmap));
    try testing.expect(!noise_bitmap.intersects(closed_bitmap));

    try testing.expect(open_mask.isSubsetOf(closed_mask));
    try testing.expect(!closed_mask.isSubsetOf(open_mask));
    try testing.expect(!hinge_mask.intersects(open_mask));
    try testing.expect(hinge_mask.intersects(closed_mask));
    try testing.expect(!noise_mask.intersects(closed_mask));

    try testing.expectEqual(@as(?usize, 23), open_bitmap.nextSetBit(15));
    try testing.expectEqual(@as(?usize, 20), closed_bitmap.nextSetBit(15));
    try testing.expectEqual(@as(?usize, word_bits + 10), closed_bitmap.nextClearBit(word_bits + 10));
    try testing.expectEqual(@as(?usize, 23), open_mask.nextCpu(15));
    try testing.expectEqual(@as(?usize, 20), closed_mask.nextCpu(15));
    try testing.expectEqual(@as(?usize, word_bits + 10), closed_mask.nextMissingCpu(word_bits + 10));
}
