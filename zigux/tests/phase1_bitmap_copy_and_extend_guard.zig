const std = @import("std");
const bitmap = @import("bitmap");

test "phase1 bitmap copyAndExtend zero-count clears declared destination words" {
    const Word = bitmap.Word;
    const whole_word_size = bitmap.bits_per_long * 2;
    const empty_src = [_]Word{};

    var direct = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    bitmap.copyAndExtend(&direct, &empty_src, 0, whole_word_size);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, 0 }, &direct);

    var alias = [_]Word{ 0x55aa, 0xaa55 };
    bitmap.bitmap_copy_and_extend(&alias, &empty_src, 0, whole_word_size);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, 0 }, &alias);
}

test "phase1 bitmap copyAndExtend zero-count clears partial tail destinations too" {
    const Word = bitmap.Word;
    const tail_size = bitmap.bits_per_long + 5;
    const empty_src = [_]Word{};
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };

    bitmap.copyAndExtend(&dst, &empty_src, 0, tail_size);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, 0 }, &dst);
}
