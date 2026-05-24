const std = @import("std");
const find_bit = @import("find_bit");

fn word(bit: usize) find_bit.Word {
    return @as(find_bit.Word, 1) << @intCast(bit);
}

test "phase1 find_last_bit tail replay clamps tail words before falling back" {
    const word_bits = find_bit.bits_per_long;
    const nbits = word_bits + 5;

    var bitmap = [_]find_bit.Word{
        word(7),
        word(1) | word(4) | word(9),
    };

    try std.testing.expectEqual(@as(usize, word_bits + 4), find_bit.findLastBit(&bitmap, nbits));
    try std.testing.expectEqual(find_bit.findLastBit(&bitmap, nbits), find_bit.find_last_bit(&bitmap, nbits));
    try std.testing.expectEqual(find_bit.findLastBit(&bitmap, nbits), find_bit._find_last_bit(&bitmap, nbits));

    bitmap[1] &= ~word(4);
    try std.testing.expectEqual(@as(usize, word_bits + 1), find_bit.findLastBit(&bitmap, nbits));

    bitmap[1] &= ~word(1);
    try std.testing.expectEqual(@as(usize, 7), find_bit.findLastBit(&bitmap, nbits));
}

test "phase1 find_last_bit tail replay keeps single-word tails and exact boundaries honest" {
    const single_word_nbits = 11;
    var single_word = [_]find_bit.Word{
        word(4) | word(13),
    };

    try std.testing.expectEqual(@as(usize, 4), find_bit.findLastBit(&single_word, single_word_nbits));

    single_word[0] &= ~word(4);
    try std.testing.expectEqual(@as(usize, single_word_nbits), find_bit.findLastBit(&single_word, single_word_nbits));

    const boundary = find_bit.bits_per_long - 1;
    const exact_boundary = [_]find_bit.Word{
        word(boundary),
        word(5),
    };
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findLastBit(&exact_boundary, find_bit.bits_per_long));

    const empty = [_]find_bit.Word{};
    try std.testing.expectEqual(@as(usize, 0), find_bit.findLastBit(&empty, 0));
}
