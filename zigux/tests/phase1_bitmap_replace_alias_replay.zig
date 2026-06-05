const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "phase1 bitmap replace preserves old new and mask ownership" {
    const nbits = bits_per_long + 5;
    const old = [_]Word{
        0b1010_0101,
        (@as(Word, 1) << 0) | (@as(Word, 1) << 2) | (@as(Word, 1) << 9),
    };
    const new = [_]Word{
        0b0101_1100,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 11),
    };
    const mask = [_]Word{
        0b1111_0000,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 2) | (@as(Word, 1) << 8),
    };
    var replaced = [_]Word{ 0, 0 };

    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);

    try std.testing.expectEqual(@as(Word, 0b0101_0101), replaced[0]);
    try std.testing.expectEqual(@as(Word, (@as(Word, 1) << 0) | (@as(Word, 1) << 1)), replaced[1]);
    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&replaced, nbits));
}

test "phase1 bitmap replace clamps partial tails before reporting predicates" {
    const nbits = bits_per_long + 3;
    const tail_noise = (@as(Word, 1) << 5) | (@as(Word, 1) << 9);
    const old = [_]Word{ 0, tail_noise };
    const new = [_]Word{ 0, (@as(Word, 1) << 1) | tail_noise };
    const mask = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 9) };
    var replaced = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };

    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);

    try std.testing.expectEqual(@as(Word, 0), replaced[0]);
    try std.testing.expectEqual(@as(Word, 1) << 1, replaced[1]);
    try std.testing.expectEqual(@as(usize, 1), bitmap.weight(&replaced, nbits));
    try std.testing.expect(bitmap.subset(&replaced, &new, nbits));
    try std.testing.expect(bitmap.intersects(&replaced, &new, nbits));
}

test "phase1 bitmap replace keeps zero bit caller views untouched through aliases" {
    const old = [_]Word{0x1111};
    const new = [_]Word{0x2222};
    const mask = [_]Word{0xffff};
    var first = [_]Word{0xaaaa};
    var second = [_]Word{0xbbbb};

    bitmap.bitmap_replace(first[0..0], old[0..0], new[0..0], mask[0..0], 0);
    bitmap.bitmap_replace(second[0..0], old[0..0], new[0..0], mask[0..0], 0);

    try std.testing.expectEqual(@as(Word, 0xaaaa), first[0]);
    try std.testing.expectEqual(@as(Word, 0xbbbb), second[0]);
    try std.testing.expectEqual(@as(usize, 0), bitmap.weight(first[0..0], 0));
}
