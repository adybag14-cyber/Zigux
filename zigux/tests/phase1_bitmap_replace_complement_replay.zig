const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

fn bit(index: usize) Word {
    return @as(Word, 1) << @intCast(index);
}

fn tailMask(nbits: usize) Word {
    const tail = nbits & (bits_per_long - 1);
    if (tail == 0) {
        return ~@as(Word, 0);
    }
    return bit(tail) - 1;
}

test "bitmap replace clamps partial tail and preserves full words" {
    const nbits = bits_per_long + 9;
    const old = [_]Word{
        bit(1) | bit(5) | bit(63),
        bit(1) | bit(4) | bit(12),
    };
    const new = [_]Word{
        bit(2) | bit(5) | bit(62),
        bit(0) | bit(8) | bit(14),
    };
    const mask = [_]Word{
        bit(1) | bit(2) | bit(62),
        bit(0) | bit(4) | bit(8) | bit(14),
    };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };

    bitmap.bitmap_replace(&dst, &old, &new, &mask, nbits);

    try std.testing.expectEqual((old[0] & ~mask[0]) | (new[0] & mask[0]), dst[0]);
    try std.testing.expectEqual(((old[1] & ~mask[1]) | (new[1] & mask[1])) & tailMask(nbits), dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[1] & ~tailMask(nbits));
}

test "bitmap complement aliases clear invalid tail bits" {
    const nbits = bits_per_long + 6;
    const src = [_]Word{
        bit(0) | bit(7) | bit(63),
        bit(1) | bit(4) | bit(11),
    };
    var primary_dst = [_]Word{ 0, ~@as(Word, 0) };
    var alias_dst = [_]Word{ ~@as(Word, 0), 0 };

    bitmap.complement(&primary_dst, &src, nbits);
    bitmap.bitmap_complement(&alias_dst, &src, nbits);

    try std.testing.expectEqualSlices(Word, &primary_dst, &alias_dst);
    try std.testing.expectEqual(~src[0], primary_dst[0]);
    try std.testing.expectEqual((~src[1]) & tailMask(nbits), primary_dst[1]);
    try std.testing.expectEqual(@as(Word, 0), primary_dst[1] & ~tailMask(nbits));
}

test "bitmap replace and complement leave zero bit windows untouched" {
    const old = [_]Word{bit(3)};
    const new = [_]Word{bit(5)};
    const mask = [_]Word{~@as(Word, 0)};
    const src = [_]Word{0};
    var replace_dst = [_]Word{bit(11)};
    var complement_dst = [_]Word{bit(13)};

    bitmap.bitmap_replace(&replace_dst, &old, &new, &mask, 0);
    bitmap.bitmap_complement(&complement_dst, &src, 0);

    try std.testing.expectEqual(bit(11), replace_dst[0]);
    try std.testing.expectEqual(bit(13), complement_dst[0]);
}
