const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");

test "phase1 bitmap-find-bit edges import the live helper modules" {
    try std.testing.expect(@hasDecl(bitmap, "bitmap_copy_clear_tail"));
    try std.testing.expect(@hasDecl(bitmap, "bitmap_weighted_or"));
    try std.testing.expect(@hasDecl(bitmap, "bitmap_scnprintf"));
    try std.testing.expect(@hasDecl(find_bit, "findFirstAndNotBit"));
    try std.testing.expect(@hasDecl(find_bit, "find_next_andnot_bit"));
}

test "phase1 bitmap-find-bit edges keep tail masks and range rendering aligned" {
    const word_bits = find_bit.bits_per_long;
    const nbits = word_bits + 5;
    var map = [_]find_bit.Word{ 0, 0 };
    bitmap.setRange(&map, word_bits - 2, 4);
    bitmap.setRange(&map, nbits - 1, 4);

    try std.testing.expectEqual(word_bits - 2, find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(word_bits + 2, find_bit.findNextZeroBit(&map, nbits, word_bits - 2));
    try std.testing.expectEqual(word_bits, find_bit.findNextBit(&map, nbits, word_bits));
    try std.testing.expectEqual(word_bits + 1, find_bit.findNextBit(&map, nbits, word_bits + 1));
    try std.testing.expectEqual(nbits - 1, find_bit.findLastBit(&map, nbits));

    var direct_buffer = [_]u8{0} ** 32;
    var alias_buffer = [_]u8{0} ** 32;
    const direct_len = bitmap.scnprintf(&map, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&map, nbits, &alias_buffer);

    var expected_buffer: [32]u8 = undefined;
    const expected = try std.fmt.bufPrint(
        &expected_buffer,
        "{d}-{d},{d}",
        .{ word_bits - 2, word_bits + 1, nbits - 1 },
    );

    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(expected, direct_buffer[0..direct_len]);
    try std.testing.expectEqualStrings(expected, alias_buffer[0..alias_len]);
}

test "phase1 bitmap-find-bit edges keep copy and andnot aliases tail-safe" {
    const word_bits = find_bit.bits_per_long;
    const nbits = word_bits + 3;

    var src = [_]find_bit.Word{ 0, 0 };
    bitmap.setRange(&src, word_bits - 1, 5);

    var copied_direct = [_]find_bit.Word{ 0xaaaa, 0xbbbb };
    var copied_alias = [_]find_bit.Word{ 0xaaaa, 0xbbbb };
    bitmap.copyClearTail(&copied_direct, &src, nbits);
    bitmap.bitmap_copy_clear_tail(&copied_alias, &src, nbits);

    try std.testing.expectEqualSlices(find_bit.Word, &copied_direct, &copied_alias);
    try std.testing.expectEqual(word_bits - 1, find_bit.findFirstBit(&copied_direct, nbits));
    try std.testing.expectEqual(nbits - 1, find_bit.findLastBit(&copied_direct, nbits));

    var lhs = [_]find_bit.Word{ 0, 0 };
    bitmap.setRange(&lhs, word_bits - 1, 3);
    var rhs = [_]find_bit.Word{ 0, 0 };
    bitmap.setRange(&rhs, word_bits, 4);

    var union_direct = [_]find_bit.Word{ 0, 0 };
    var union_alias = [_]find_bit.Word{ 0, 0 };
    const direct_weight = bitmap.weightedOr(&union_direct, &lhs, &rhs, nbits);
    const alias_weight = bitmap.bitmap_weighted_or(&union_alias, &lhs, &rhs, nbits);

    try std.testing.expectEqual(@as(usize, 4), direct_weight);
    try std.testing.expectEqual(direct_weight, alias_weight);
    try std.testing.expectEqualSlices(find_bit.Word, &union_direct, &union_alias);

    var mask = [_]find_bit.Word{ 0, 0 };
    bitmap.setRange(&mask, word_bits - 1, 2);

    try std.testing.expectEqual(word_bits + 1, find_bit.findFirstAndNotBit(&union_alias, &mask, nbits));
    try std.testing.expectEqual(word_bits + 1, find_bit.find_first_andnot_bit(&union_alias, &mask, nbits));
    try std.testing.expectEqual(word_bits + 1, find_bit.findNextAndNotBit(&union_alias, &mask, nbits, word_bits + 1));
    try std.testing.expectEqual(word_bits + 1, find_bit.find_next_andnot_bit(&union_alias, &mask, nbits, word_bits + 1));
    try std.testing.expectEqual(word_bits + 2, find_bit.findNextAndNotBit(&union_alias, &mask, nbits, word_bits + 2));
    try std.testing.expectEqual(nbits, find_bit._find_next_andnot_bit(&union_alias, &mask, nbits, nbits));
}
