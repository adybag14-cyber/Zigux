const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap and andnot mask dirty tail bits and report expected counts" {
    const nbits = bits_per_long + 5;
    const tail_mask = bitmap.lastWordMask(nbits);

    const lhs = [_]Word{
        0b10110101,
        ~tail_mask | 0b10101,
    };
    const rhs = [_]Word{
        0b01110001,
        ~tail_mask | 0b11001,
    };

    var and_bits = [_]Word{ 0, 0 };
    var andnot_bits = [_]Word{ 0, 0 };

    try std.testing.expect(bitmap.bitmap_and(and_bits[0..], lhs[0..], rhs[0..], nbits));
    try std.testing.expect(bitmap.bitmap_andnot(andnot_bits[0..], lhs[0..], rhs[0..], nbits));

    try std.testing.expectEqual(@as(Word, 0b00110001), and_bits[0]);
    try std.testing.expectEqual(@as(Word, 0b10001), and_bits[1]);
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(and_bits[0..], nbits));
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight_and(lhs[0..], rhs[0..], nbits));

    try std.testing.expectEqual(@as(Word, 0b10000100), andnot_bits[0]);
    try std.testing.expectEqual(@as(Word, 0b00100), andnot_bits[1]);
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(andnot_bits[0..], nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight_andnot(lhs[0..], rhs[0..], nbits));
}

test "bitmap and andnot ignore overlap that only exists beyond nbits" {
    const nbits = bits_per_long + 3;
    const tail_mask = bitmap.lastWordMask(nbits);

    const lhs = [_]Word{
        0,
        ~tail_mask,
    };
    const rhs = [_]Word{
        0,
        ~tail_mask,
    };

    var and_bits = [_]Word{ 1234, 5678 };
    var andnot_bits = [_]Word{ 4321, 8765 };

    try std.testing.expect(!bitmap.bitmap_and(and_bits[0..], lhs[0..], rhs[0..], nbits));
    try std.testing.expect(!bitmap.bitmap_andnot(andnot_bits[0..], lhs[0..], rhs[0..], nbits));

    try std.testing.expectEqual(@as(Word, 0), and_bits[0]);
    try std.testing.expectEqual(@as(Word, 0), and_bits[1]);
    try std.testing.expectEqual(@as(Word, 0), andnot_bits[0]);
    try std.testing.expectEqual(@as(Word, 0), andnot_bits[1]);
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weight_and(lhs[0..], rhs[0..], nbits));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weight_andnot(lhs[0..], rhs[0..], nbits));
}

test "bitmap empty and full ignore dirty tail bits outside the tracked width" {
    const nbits = bits_per_long + 6;
    const tail_mask = bitmap.lastWordMask(nbits);

    const empty_bits = [_]Word{
        0,
        ~tail_mask,
    };
    const full_bits = [_]Word{
        ~@as(Word, 0),
        ~tail_mask | tail_mask,
    };
    const partial_bits = [_]Word{
        ~@as(Word, 0),
        ~tail_mask | 0b011111,
    };

    try std.testing.expect(bitmap.bitmap_empty(empty_bits[0..], nbits));
    try std.testing.expect(!bitmap.bitmap_full(empty_bits[0..], nbits));

    try std.testing.expect(bitmap.bitmap_full(full_bits[0..], nbits));
    try std.testing.expect(!bitmap.bitmap_empty(full_bits[0..], nbits));

    try std.testing.expect(!bitmap.bitmap_full(partial_bits[0..], nbits));
    try std.testing.expect(!bitmap.bitmap_empty(partial_bits[0..], nbits));
}
