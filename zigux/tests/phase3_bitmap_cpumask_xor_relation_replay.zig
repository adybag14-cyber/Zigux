const std = @import("std");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");

const Word = bitmap_view.Word;
const word_bits = bitmap_view.word_bits;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index % word_bits);
}

fn makeView(words: []const Word, bit_len: usize) struct {
    bitmap: bitmap_view.BitmapView,
    cpumask: cpumask_view.CpuMaskView,
} {
    return .{
        .bitmap = bitmap_view.BitmapView.init(words, bit_len),
        .cpumask = cpumask_view.CpuMaskView.init(words, bit_len),
    };
}

fn expectMirrors(words: []const Word, bit_len: usize, expected_count: usize, expected_first: ?usize, expected_first_missing: ?usize) !void {
    const pair = makeView(words, bit_len);

    try std.testing.expectEqual(expected_count, pair.bitmap.countSetBits());
    try std.testing.expectEqual(expected_count, pair.cpumask.countPresentCpus());
    try std.testing.expectEqual(expected_first, pair.bitmap.firstSetBit());
    try std.testing.expectEqual(expected_first, pair.cpumask.firstCpu());
    try std.testing.expectEqual(expected_first_missing, pair.bitmap.firstClearBit());
    try std.testing.expectEqual(expected_first_missing, pair.cpumask.firstMissingCpu());

    var start: usize = 0;
    while (start <= bit_len) : (start += 7) {
        try std.testing.expectEqual(pair.bitmap.nextSetBit(start), pair.cpumask.nextCpu(start));
        try std.testing.expectEqual(pair.bitmap.nextClearBit(start), pair.cpumask.nextMissingCpu(start));
    }
}

test "phase3 bitmap cpumask xor relation mirrors shared and exclusive bits" {
    const bit_len = word_bits * 2 + 11;
    const left_words = [_]Word{
        bit(1) | bit(5) | bit(word_bits - 2),
        bit(word_bits + 3) | bit(word_bits + 9),
        bit(word_bits * 2 + 2) | bit(word_bits * 2 + 7) | (@as(Word, 1) << 59),
    };
    const right_words = [_]Word{
        bit(5) | bit(8) | bit(word_bits - 2),
        bit(word_bits + 4) | bit(word_bits + 9) | bit(word_bits + 12),
        bit(word_bits * 2 + 7) | bit(word_bits * 2 + 10) | (@as(Word, 1) << 59),
    };
    const shared_words = [_]Word{
        left_words[0] & right_words[0],
        left_words[1] & right_words[1],
        left_words[2] & right_words[2],
    };
    const xor_words = [_]Word{
        left_words[0] ^ right_words[0],
        left_words[1] ^ right_words[1],
        left_words[2] ^ right_words[2],
    };
    const union_words = [_]Word{
        left_words[0] | right_words[0],
        left_words[1] | right_words[1],
        left_words[2] | right_words[2],
    };

    try expectMirrors(left_words[0..], bit_len, 7, 1, 0);
    try expectMirrors(right_words[0..], bit_len, 8, 5, 0);
    try expectMirrors(shared_words[0..], bit_len, 4, 5, 0);
    try expectMirrors(xor_words[0..], bit_len, 7, 1, 0);
    try expectMirrors(union_words[0..], bit_len, 11, 1, 0);

    const left = makeView(left_words[0..], bit_len);
    const right = makeView(right_words[0..], bit_len);
    const shared = makeView(shared_words[0..], bit_len);
    const xor = makeView(xor_words[0..], bit_len);
    const union_pair = makeView(union_words[0..], bit_len);

    try std.testing.expect(shared.bitmap.isSubsetOf(left.bitmap));
    try std.testing.expect(shared.cpumask.isSubsetOf(left.cpumask));
    try std.testing.expect(shared.bitmap.isSubsetOf(right.bitmap));
    try std.testing.expect(shared.cpumask.isSubsetOf(right.cpumask));
    try std.testing.expect(xor.bitmap.isSubsetOf(union_pair.bitmap));
    try std.testing.expect(xor.cpumask.isSubsetOf(union_pair.cpumask));
    try std.testing.expect(!union_pair.bitmap.isSubsetOf(xor.bitmap));
    try std.testing.expect(!union_pair.cpumask.isSubsetOf(xor.cpumask));
    try std.testing.expect(!shared.bitmap.intersects(xor.bitmap));
    try std.testing.expect(!shared.cpumask.intersects(xor.cpumask));
    try std.testing.expect(left.bitmap.intersects(right.bitmap));
    try std.testing.expect(left.cpumask.intersects(right.cpumask));

    try std.testing.expectEqual(@as(?usize, 1), xor.bitmap.nextSetBit(0));
    try std.testing.expectEqual(@as(?usize, 1), xor.cpumask.nextCpu(0));
    try std.testing.expectEqual(@as(?usize, 8), xor.bitmap.nextSetBit(6));
    try std.testing.expectEqual(@as(?usize, 8), xor.cpumask.nextCpu(6));
    try std.testing.expectEqual(@as(?usize, word_bits + 3), xor.bitmap.nextSetBit(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits + 3), xor.cpumask.nextCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 10), xor.bitmap.nextSetBit(word_bits * 2 + 8));
    try std.testing.expectEqual(@as(?usize, word_bits * 2 + 10), xor.cpumask.nextCpu(word_bits * 2 + 8));
    try std.testing.expectEqual(@as(?usize, null), xor.bitmap.nextSetBit(bit_len));
    try std.testing.expectEqual(@as(?usize, null), xor.cpumask.nextCpu(bit_len));
}

test "phase3 bitmap cpumask xor recomputes after relation mutation" {
    const bit_len = word_bits + 13;
    var left_words = [_]Word{
        bit(0) | bit(2) | bit(7) | bit(word_bits - 1),
        bit(word_bits + 2) | bit(word_bits + 8),
    };
    var right_words = [_]Word{
        bit(2) | bit(4) | bit(word_bits - 1),
        bit(word_bits + 3) | bit(word_bits + 8) | (@as(Word, 1) << 61),
    };

    var xor_words = [_]Word{
        left_words[0] ^ right_words[0],
        left_words[1] ^ right_words[1],
    };
    var shared_words = [_]Word{
        left_words[0] & right_words[0],
        left_words[1] & right_words[1],
    };

    try expectMirrors(xor_words[0..], bit_len, 5, 0, 1);
    try expectMirrors(shared_words[0..], bit_len, 3, 2, 0);

    left_words[0] |= bit(4);
    right_words[1] |= bit(word_bits + 2);
    left_words[1] &= ~bit(word_bits + 8);

    xor_words = .{
        left_words[0] ^ right_words[0],
        left_words[1] ^ right_words[1],
    };
    shared_words = .{
        left_words[0] & right_words[0],
        left_words[1] & right_words[1],
    };

    try expectMirrors(xor_words[0..], bit_len, 4, 0, 1);
    try expectMirrors(shared_words[0..], bit_len, 4, 2, 0);

    const xor = makeView(xor_words[0..], bit_len);
    const shared = makeView(shared_words[0..], bit_len);
    const left = makeView(left_words[0..], bit_len);
    const right = makeView(right_words[0..], bit_len);

    try std.testing.expect(!xor.bitmap.intersects(shared.bitmap));
    try std.testing.expect(!xor.cpumask.intersects(shared.cpumask));
    try std.testing.expect(shared.bitmap.isSubsetOf(left.bitmap));
    try std.testing.expect(shared.cpumask.isSubsetOf(left.cpumask));
    try std.testing.expect(shared.bitmap.isSubsetOf(right.bitmap));
    try std.testing.expect(shared.cpumask.isSubsetOf(right.cpumask));
    try std.testing.expectEqual(@as(?usize, word_bits + 3), xor.bitmap.nextSetBit(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits + 3), xor.cpumask.nextCpu(word_bits));
    try std.testing.expectEqual(@as(?usize, word_bits + 8), xor.bitmap.nextSetBit(word_bits + 4));
    try std.testing.expectEqual(@as(?usize, word_bits + 8), xor.cpumask.nextCpu(word_bits + 4));
}
