const std = @import("std");
const bitmap = @import("bitmap");

fn expectWordSlice(actual: []const bitmap.Word, expected: []const bitmap.Word) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (actual, expected) |value, expected_value| {
        try std.testing.expectEqual(expected_value, value);
    }
}

test "phase 1 bitmap copy clear tail masks the copied tail bits" {
    const nbits = bitmap.bits_per_long + 5;
    const expected = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        bitmap.lastWordMask(nbits),
    };

    const src = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
    };

    var copied = [_]bitmap.Word{ 0, 0 };
    bitmap.copyClearTail(&copied, &src, nbits);
    try expectWordSlice(&copied, &expected);

    var alias_copied = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_copy_clear_tail(&alias_copied, &src, nbits);
    try expectWordSlice(&alias_copied, &expected);

    try expectWordSlice(&src, &[_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
    });
}

test "phase 1 bitmap copy and extend zero fills beyond the copied tail" {
    const count = bitmap.bits_per_long + 3;
    const size = count + bitmap.bits_per_long + 7;
    const expected = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        bitmap.lastWordMask(count),
        0,
    };

    const src = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
    };

    var extended = [_]bitmap.Word{
        0x1111,
        0x2222,
        0x3333,
    };
    bitmap.copyAndExtend(&extended, &src, count, size);
    try expectWordSlice(&extended, &expected);

    var alias_extended = [_]bitmap.Word{
        0xAAAA,
        0xBBBB,
        0xCCCC,
    };
    bitmap.bitmap_copy_and_extend(&alias_extended, &src, count, size);
    try expectWordSlice(&alias_extended, &expected);
}

test "phase 1 bitmap replace and complement clamp the final tail word" {
    const nbits = bitmap.bits_per_long + 6;

    const old = [_]bitmap.Word{
        0b00110110,
        ~@as(bitmap.Word, 0),
    };
    const new = [_]bitmap.Word{
        0b11001001,
        0,
    };
    const mask = [_]bitmap.Word{
        0b11110000,
        ~@as(bitmap.Word, 0),
    };

    const expected_replace = [_]bitmap.Word{
        (old[0] & ~mask[0]) | (new[0] & mask[0]),
        0,
    };

    var replaced = [_]bitmap.Word{ 0, 0 };
    bitmap.replace(&replaced, &old, &new, &mask, nbits);
    try expectWordSlice(&replaced, &expected_replace);

    var alias_replaced = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_replace(&alias_replaced, &old, &new, &mask, nbits);
    try expectWordSlice(&alias_replaced, &expected_replace);

    const expected_complement = [_]bitmap.Word{
        ~expected_replace[0],
        bitmap.lastWordMask(nbits),
    };

    var complemented = [_]bitmap.Word{ 0, 0 };
    bitmap.complement(&complemented, &replaced, nbits);
    try expectWordSlice(&complemented, &expected_complement);

    var alias_complemented = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_complement(&alias_complemented, &alias_replaced, nbits);
    try expectWordSlice(&alias_complemented, &expected_complement);
}
