const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const BitmapView = bitmap_view.BitmapView;
const CpuMaskView = cpumask_view.CpuMaskView;
const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn localBit(offset: usize) Word {
    return @as(Word, 1) << @as(std.math.Log2Int(Word), @intCast(offset));
}

fn absoluteBit(word_index: usize, local_offset: usize) usize {
    return word_index * word_bits + local_offset;
}

fn expectBitmapCpuMirrors(bitmap: BitmapView, cpus: CpuMaskView) !void {
    try std.testing.expectEqual(bitmap.countSetBits(), cpus.countPresentCpus());
    try std.testing.expectEqual(bitmap.firstSetBit(), cpus.firstCpu());
    try std.testing.expectEqual(bitmap.firstClearBit(), cpus.firstMissingCpu());

    const probes = [_]usize{
        0,
        2,
        5,
        word_bits - 1,
        word_bits,
        word_bits + 8,
        word_bits * 2,
        bitmap.bit_len - 1,
        bitmap.bit_len,
    };

    for (probes) |probe| {
        try std.testing.expectEqual(bitmap.nextSetBit(probe), cpus.nextCpu(probe));
        try std.testing.expectEqual(bitmap.nextClearBit(probe), cpus.nextMissingCpu(probe));
    }
}

test "ripple quorum relay keeps bitmap and cpumask bridge mirrors aligned" {
    const capacity = word_bits * 2 + 19;
    const relay_words = [_]Word{
        localBit(2) | localBit(5) | localBit(13) | localBit(21) | localBit(34) | localBit(55),
        localBit(1) | localBit(8) | localBit(17) | localBit(29) | localBit(46) | localBit(63),
        localBit(0) | localBit(7) | localBit(18) | localBit(22) | localBit(40),
    };
    const bridge_words = [_]Word{
        localBit(5) | localBit(21) | localBit(55),
        localBit(8) | localBit(46),
        localBit(7),
    };
    const outside_words = [_]Word{
        localBit(0) | localBit(8) | localBit(35),
        localBit(0) | localBit(9) | localBit(30),
        localBit(2) | localBit(15),
    };
    const relay = BitmapView.init(relay_words[0..], capacity);
    const relay_cpus = CpuMaskView.init(relay_words[0..], capacity);
    const bridge = BitmapView.init(bridge_words[0..], capacity);
    const bridge_cpus = CpuMaskView.init(bridge_words[0..], capacity);
    const outside = BitmapView.init(outside_words[0..], capacity);
    const outside_cpus = CpuMaskView.init(outside_words[0..], capacity);

    try expectBitmapCpuMirrors(relay, relay_cpus);
    try expectBitmapCpuMirrors(bridge, bridge_cpus);
    try expectBitmapCpuMirrors(outside, outside_cpus);

    try std.testing.expectEqual(@as(usize, 15), relay.countSetBits());
    try std.testing.expectEqual(@as(usize, 15), relay_cpus.countPresentCpus());
    try std.testing.expectEqual(@as(usize, 6), bridge.countSetBits());
    try std.testing.expectEqual(@as(usize, 8), outside.countSetBits());
    try std.testing.expectEqual(@as(?usize, 2), relay.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 0), relay.firstClearBit());
    try std.testing.expectEqual(@as(?usize, absoluteBit(1, 1)), relay.nextSetBit(word_bits));
    try std.testing.expectEqual(@as(?usize, absoluteBit(2, 7)), relay_cpus.nextCpu(word_bits * 2 + 3));

    try std.testing.expect(bridge.isSubsetOf(relay));
    try std.testing.expect(bridge_cpus.isSubsetOf(relay_cpus));
    try std.testing.expect(!relay.isSubsetOf(bridge));
    try std.testing.expect(!relay_cpus.isSubsetOf(bridge_cpus));
    try std.testing.expect(relay.intersects(bridge));
    try std.testing.expect(relay_cpus.intersects(bridge_cpus));
    try std.testing.expect(!relay.intersects(outside));
    try std.testing.expect(!relay_cpus.intersects(outside_cpus));

    try std.testing.expect(relay_cpus.hasCpu(absoluteBit(0, 55)));
    try std.testing.expect(relay_cpus.hasCpu(absoluteBit(1, 63)));
    try std.testing.expect(relay_cpus.hasCpu(absoluteBit(2, 18)));
    try std.testing.expectEqual(@as(?usize, null), relay.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), relay_cpus.nextCpu(capacity));
}

test "ripple quorum rollback masks dropped lanes and declared tail noise" {
    const capacity = word_bits * 2 + 11;
    const promoted_words = [_]Word{
        localBit(1) | localBit(7) | localBit(18) | localBit(33) | localBit(47),
        localBit(4) | localBit(11) | localBit(24) | localBit(39) | localBit(52),
        localBit(1) | localBit(5) | localBit(10) | localBit(16) | localBit(31),
    };
    const rollback_words = [_]Word{
        localBit(1) | localBit(18) | localBit(47),
        localBit(11) | localBit(39),
        localBit(5) | localBit(10) | localBit(16) | localBit(31),
    };
    const stable_words = [_]Word{
        localBit(1) | localBit(47),
        localBit(39),
        localBit(10) | localBit(31),
    };
    const promoted = BitmapView.init(promoted_words[0..], capacity);
    const promoted_cpus = CpuMaskView.init(promoted_words[0..], capacity);
    const rollback = BitmapView.init(rollback_words[0..], capacity);
    const rollback_cpus = CpuMaskView.init(rollback_words[0..], capacity);
    const stable = BitmapView.init(stable_words[0..], capacity);
    const stable_cpus = CpuMaskView.init(stable_words[0..], capacity);

    try expectBitmapCpuMirrors(promoted, promoted_cpus);
    try expectBitmapCpuMirrors(rollback, rollback_cpus);
    try expectBitmapCpuMirrors(stable, stable_cpus);

    try std.testing.expectEqual(@as(usize, 13), promoted.countSetBits());
    try std.testing.expectEqual(@as(usize, 7), rollback.countSetBits());
    try std.testing.expectEqual(@as(usize, 4), stable.countSetBits());
    try std.testing.expect(stable.isSubsetOf(rollback));
    try std.testing.expect(stable_cpus.isSubsetOf(rollback_cpus));
    try std.testing.expect(rollback.isSubsetOf(promoted));
    try std.testing.expect(rollback_cpus.isSubsetOf(promoted_cpus));
    try std.testing.expect(!promoted.isSubsetOf(rollback));
    try std.testing.expect(!promoted_cpus.isSubsetOf(rollback_cpus));

    try std.testing.expectEqual(@as(?usize, 1), promoted.firstSetBit());
    try std.testing.expectEqual(@as(?usize, 0), promoted.firstClearBit());
    try std.testing.expectEqual(@as(?usize, absoluteBit(1, 11)), rollback.nextSetBit(word_bits + 5));
    try std.testing.expectEqual(@as(?usize, absoluteBit(2, 5)), rollback_cpus.nextCpu(word_bits * 2));
    try std.testing.expectEqual(@as(?usize, absoluteBit(2, 0)), promoted.nextClearBit(word_bits * 2));

    try std.testing.expect(promoted_cpus.hasCpu(absoluteBit(2, 10)));
    try std.testing.expectEqual(@as(?usize, null), promoted.nextSetBit(capacity));
    try std.testing.expectEqual(@as(?usize, null), promoted_cpus.nextCpu(capacity));
}
