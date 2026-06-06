const std = @import("std");
const testing = std.testing;

const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

fn bit(global_bit: usize) usize {
    return @as(usize, 1) << @intCast(global_bit % bitmap_view.word_bits);
}

fn setBit(words: []usize, global_bit: usize) void {
    words[global_bit / bitmap_view.word_bits] |= bit(global_bit);
}

fn addWindow(words: []usize, first_bit: usize, len: usize, stride: usize) void {
    var offset: usize = 0;
    while (offset < len) : (offset += stride) {
        setBit(words, first_bit + offset);
    }
}

fn expectBitmapCpuMaskMirror(words: []const usize, capacity: usize, starts: []const usize) !void {
    const bitmap = bitmap_view.BitmapView.init(words, capacity);
    const cpumask = cpumask_view.CpuMaskView.init(words, capacity);

    try testing.expectEqual(bitmap.countSetBits(), cpumask.countPresentCpus());
    try testing.expectEqual(bitmap.firstSetBit(), cpumask.firstCpu());
    try testing.expectEqual(bitmap.firstClearBit(), cpumask.firstMissingCpu());

    for (starts) |start| {
        try testing.expectEqual(bitmap.nextSetBit(start), cpumask.nextCpu(start));
        try testing.expectEqual(bitmap.nextClearBit(start), cpumask.nextMissingCpu(start));
    }
}

fn expectRelationMirror(left_words: []const usize, right_words: []const usize, capacity: usize) !void {
    const left_bitmap = bitmap_view.BitmapView.init(left_words, capacity);
    const right_bitmap = bitmap_view.BitmapView.init(right_words, capacity);
    const left_cpumask = cpumask_view.CpuMaskView.init(left_words, capacity);
    const right_cpumask = cpumask_view.CpuMaskView.init(right_words, capacity);

    try testing.expectEqual(left_bitmap.intersects(right_bitmap), left_cpumask.intersects(right_cpumask));
    try testing.expectEqual(left_bitmap.isSubsetOf(right_bitmap), left_cpumask.isSubsetOf(right_cpumask));
    try testing.expectEqual(right_bitmap.isSubsetOf(left_bitmap), right_cpumask.isSubsetOf(left_cpumask));
}

test "bitmap and cpumask keep disjoint windows aligned through union masks" {
    const capacity = bitmap_view.word_bits * 3 + 19;
    const starts = [_]usize{
        0,
        2,
        bitmap_view.word_bits - 1,
        bitmap_view.word_bits,
        bitmap_view.word_bits + 14,
        bitmap_view.word_bits * 2 + 1,
        capacity - 1,
        capacity,
    };

    var low_window = [_]usize{ 0, 0, 0, 0 };
    var high_window = [_]usize{ 0, 0, 0, 0 };
    var union_window = [_]usize{ 0, 0, 0, 0 };

    addWindow(low_window[0..], 2, bitmap_view.word_bits + 7, 9);
    addWindow(high_window[0..], bitmap_view.word_bits + 17, bitmap_view.word_bits + 21, 11);
    setBit(high_window[0..], bitmap_view.word_bits * 3 + 5);
    high_window[3] |= ~@as(usize, 0) << 19;

    for (0..union_window.len) |index| {
        union_window[index] = low_window[index] | high_window[index];
    }

    try expectBitmapCpuMaskMirror(low_window[0..], capacity, starts[0..]);
    try expectBitmapCpuMaskMirror(high_window[0..], capacity, starts[0..]);
    try expectBitmapCpuMaskMirror(union_window[0..], capacity, starts[0..]);
    try expectRelationMirror(low_window[0..], high_window[0..], capacity);
    try expectRelationMirror(low_window[0..], union_window[0..], capacity);
    try expectRelationMirror(high_window[0..], union_window[0..], capacity);

    const low_bitmap = bitmap_view.BitmapView.init(low_window[0..], capacity);
    const high_cpumask = cpumask_view.CpuMaskView.init(high_window[0..], capacity);
    const union_cpumask = cpumask_view.CpuMaskView.init(union_window[0..], capacity);

    try testing.expect(!low_bitmap.intersects(high_cpumask.bitmap));
    try testing.expect(low_bitmap.isSubsetOf(union_cpumask.bitmap));
    try testing.expect(high_cpumask.isSubsetOf(union_cpumask));
    try testing.expectEqual(low_bitmap.countSetBits() + high_cpumask.countPresentCpus(), union_cpumask.countPresentCpus());
    try testing.expectEqual(@as(?usize, 2), low_bitmap.firstSetBit());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 17), high_cpumask.firstCpu());
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits * 3 + 5), union_cpumask.nextCpu(bitmap_view.word_bits * 3));
    try testing.expectEqual(@as(?usize, null), union_cpumask.nextCpu(capacity));
}

test "bitmap and cpumask detect window overlap after shared backing expansion" {
    const capacity = bitmap_view.word_bits * 2 + 23;
    const starts = [_]usize{
        0,
        1,
        bitmap_view.word_bits - 4,
        bitmap_view.word_bits + 3,
        bitmap_view.word_bits + 32,
        bitmap_view.word_bits * 2 + 9,
        capacity - 1,
        capacity,
    };

    var primary_words = [_]usize{ 0, 0, 0 };
    var probe_words = [_]usize{ 0, 0, 0 };

    addWindow(primary_words[0..], bitmap_view.word_bits - 4, 40, 5);
    addWindow(primary_words[0..], bitmap_view.word_bits * 2 + 3, 17, 4);
    addWindow(probe_words[0..], 1, 31, 6);
    addWindow(probe_words[0..], bitmap_view.word_bits * 2 + 6, 14, 7);
    probe_words[2] |= ~@as(usize, 0) << 23;

    try expectBitmapCpuMaskMirror(primary_words[0..], capacity, starts[0..]);
    try expectBitmapCpuMaskMirror(probe_words[0..], capacity, starts[0..]);
    try expectRelationMirror(primary_words[0..], probe_words[0..], capacity);

    var primary_bitmap = bitmap_view.BitmapView.init(primary_words[0..], capacity);
    var probe_cpumask = cpumask_view.CpuMaskView.init(probe_words[0..], capacity);
    try testing.expect(!primary_bitmap.intersects(probe_cpumask.bitmap));
    try testing.expect(!probe_cpumask.isSubsetOf(cpumask_view.CpuMaskView.init(primary_words[0..], capacity)));

    setBit(probe_words[0..], bitmap_view.word_bits + 16);
    setBit(probe_words[0..], bitmap_view.word_bits * 2 + 11);
    setBit(probe_words[0..], capacity + 5);

    primary_bitmap = bitmap_view.BitmapView.init(primary_words[0..], capacity);
    probe_cpumask = cpumask_view.CpuMaskView.init(probe_words[0..], capacity);
    try expectBitmapCpuMaskMirror(probe_words[0..], capacity, starts[0..]);
    try expectRelationMirror(primary_words[0..], probe_words[0..], capacity);

    try testing.expect(primary_bitmap.intersects(probe_cpumask.bitmap));
    try testing.expect(probe_cpumask.intersects(cpumask_view.CpuMaskView.init(primary_words[0..], capacity)));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits + 16), probe_cpumask.nextCpu(bitmap_view.word_bits + 12));
    try testing.expectEqual(@as(?usize, bitmap_view.word_bits * 2 + 11), primary_bitmap.nextSetBit(bitmap_view.word_bits * 2 + 9));
    try testing.expectEqual(@as(?usize, null), probe_cpumask.nextCpu(capacity));
}
