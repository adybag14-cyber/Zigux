const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

fn bit(bit_idx: usize) Word {
    return @as(Word, 1) << @intCast(bit_idx);
}

test "bitmap relation helpers ignore noise beyond declared tail" {
    const nbits = bits_per_long + 6;
    const valid_tail = bit(1) | bit(4);
    const lhs_noise = bit(8) | bit(13);
    const rhs_noise = bit(9) | bit(15);
    const lhs = [_]Word{ 0b10110, valid_tail | lhs_noise };
    const rhs = [_]Word{ 0b10110, valid_tail | rhs_noise };
    const changed = [_]Word{ 0b10010, valid_tail | lhs_noise };

    try std.testing.expect(bitmap.equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expect(!bitmap.equal(&lhs, &changed, nbits));

    try std.testing.expect(bitmap.intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&rhs, &lhs, nbits));
    try std.testing.expect(bitmap.subset(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&rhs, &lhs, nbits));
}

test "bitmap boolean operators clamp results to the active tail" {
    const nbits = bits_per_long + 6;
    const lhs = [_]Word{ 0b11100, bit(1) | bit(3) | bit(9) };
    const rhs = [_]Word{ 0b10100, bit(3) | bit(5) | bit(11) };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    var alias_dst = [_]Word{ 0, 0 };

    try std.testing.expect(bitmap.andBits(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0b10100, bit(3) }, &dst);
    try std.testing.expectEqual(bitmap.andBits(&alias_dst, &lhs, &rhs, nbits), bitmap.bitmap_and(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &dst, &alias_dst);

    try std.testing.expect(bitmap.andNotBits(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0b01000, bit(1) }, &dst);
    try std.testing.expectEqual(bitmap.andNotBits(&alias_dst, &lhs, &rhs, nbits), bitmap.bitmap_andnot(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(Word, &dst, &alias_dst);

    const outside_only = [_]Word{ 0, bit(12) };
    try std.testing.expect(!bitmap.andBits(&dst, &outside_only, &outside_only, nbits));
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, 0 }, &dst);
}

test "bitmap empty full weight and complement keep tail state explicit" {
    const nbits = bits_per_long + 6;
    const tail_noise = bit(8) | bit(12);
    const empty_map = [_]Word{ 0, tail_noise };
    const full_map = [_]Word{ ~@as(Word, 0), bitmap.lastWordMask(nbits) | tail_noise };
    const sparse_map = [_]Word{ bit(3), bit(2) | tail_noise };
    var complement = [_]Word{ 0, 0 };

    try std.testing.expect(bitmap.empty(&empty_map, nbits));
    try std.testing.expect(bitmap.bitmap_empty(&empty_map, nbits));
    try std.testing.expectEqual(@as(usize, 0), bitmap.weight(&empty_map, nbits));

    try std.testing.expect(bitmap.full(&full_map, nbits));
    try std.testing.expect(bitmap.bitmap_full(&full_map, nbits));
    try std.testing.expectEqual(nbits, bitmap.bitmap_weight(&full_map, nbits));

    try std.testing.expect(!bitmap.empty(&sparse_map, nbits));
    try std.testing.expect(!bitmap.full(&sparse_map, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&sparse_map, nbits));

    bitmap.complement(&complement, &sparse_map, nbits);
    try std.testing.expectEqual(~bit(3), complement[0]);
    try std.testing.expectEqual((~sparse_map[1]) & bitmap.lastWordMask(nbits), complement[1]);
    try std.testing.expect(bitmap.full(&[_]Word{ complement[0] | bit(3), complement[1] | bit(2) }, nbits));
}
