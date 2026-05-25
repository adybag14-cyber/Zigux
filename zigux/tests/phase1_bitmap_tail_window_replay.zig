const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");

test "phase1 bitmap tail window replay keeps weighted helpers aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 8) };
    const rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };

    var direct_or = [_]find_bit.Word{ 0, 0 };
    var alias_or = [_]find_bit.Word{ 0, 0 };
    const direct_or_weight = bitmap.weightedOr(&direct_or, &lhs, &rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 3), direct_or_weight);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try std.testing.expectEqualSlices(find_bit.Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&direct_or, nbits));

    var direct_xor = [_]find_bit.Word{ 0, 0 };
    var alias_xor = [_]find_bit.Word{ 0, 0 };
    const direct_xor_weight = bitmap.weightedXor(&direct_xor, &lhs, &rhs, nbits);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&alias_xor, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_xor_weight);
    try std.testing.expectEqual(direct_xor_weight, alias_xor_weight);
    try std.testing.expectEqualSlices(find_bit.Word, &direct_xor, &alias_xor);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_xor, nbits));

    var direct_and = [_]find_bit.Word{ 0, 0 };
    var alias_and = [_]find_bit.Word{ 0, 0 };
    try std.testing.expect(bitmap.andBits(&direct_and, &lhs, &rhs, nbits));
    try std.testing.expectEqual(bitmap.andBits(&direct_and, &lhs, &rhs, nbits), bitmap.bitmap_and(&alias_and, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(find_bit.Word, &direct_and, &alias_and);

    var direct_andnot = [_]find_bit.Word{ 0, 0 };
    var alias_andnot = [_]find_bit.Word{ 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&direct_andnot, &lhs, &rhs, nbits));
    try std.testing.expectEqual(bitmap.andNotBits(&direct_andnot, &lhs, &rhs, nbits), bitmap.bitmap_andnot(&alias_andnot, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(find_bit.Word, &direct_andnot, &alias_andnot);
}

test "phase1 bitmap tail window replay keeps range formatting edges aligned" {
    const nbits = find_bit.bits_per_long + 8;
    var map = [_]find_bit.Word{ 0, 0 };
    bitmap.setRange(&map, find_bit.bits_per_long - 2, 5);
    bitmap.bitmap_set(&map, find_bit.bits_per_long + 6, 1);

    var full_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const full_len = bitmap.scnprintf(&map, nbits, &full_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&map, nbits, &alias_buffer);
    try std.testing.expectEqual(full_len, alias_len);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{ find_bit.bits_per_long - 2, find_bit.bits_per_long + 2, find_bit.bits_per_long + 6 },
    );
    try std.testing.expectEqualStrings(expected_text, full_buffer[0..full_len]);
    try std.testing.expectEqualStrings(full_buffer[0..full_len], alias_buffer[0..alias_len]);

    var terminator_only = [_]u8{0xaa};
    const terminator_only_len = bitmap.scnprintf(&map, nbits, terminator_only[0..1]);
    try std.testing.expectEqual(@as(usize, 0), terminator_only_len);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);

    var zero_length_backing = [_]u8{0xbb};
    const zero_length_len = bitmap.bitmap_scnprintf(&map, nbits, zero_length_backing[0..0]);
    try std.testing.expectEqual(@as(usize, 0), zero_length_len);
    try std.testing.expectEqual(@as(u8, 0xbb), zero_length_backing[0]);
}

test "phase1 bitmap tail window replay keeps copy and complement tail clamping aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const src = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 7) | (@as(find_bit.Word, 1) << 10),
    };

    var direct_tail = [_]find_bit.Word{ 0, 0 };
    var alias_tail = [_]find_bit.Word{ 0, 0 };
    bitmap.copyClearTail(&direct_tail, &src, nbits);
    bitmap.bitmap_copy_clear_tail(&alias_tail, &src, nbits);
    try std.testing.expectEqualSlices(find_bit.Word, &direct_tail, &alias_tail);
    try std.testing.expectEqual(@as(find_bit.Word, @as(find_bit.Word, 1) << 1), direct_tail[1]);

    var direct_complement = [_]find_bit.Word{ 0, 0 };
    var alias_complement = [_]find_bit.Word{ 0, 0 };
    bitmap.complement(&direct_complement, &src, nbits);
    bitmap.bitmap_complement(&alias_complement, &src, nbits);
    try std.testing.expectEqualSlices(find_bit.Word, &direct_complement, &alias_complement);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct_complement[1]);

    var outside_only = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 10 };
    try std.testing.expect(bitmap.bitmap_empty(&outside_only, nbits));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_weight(&outside_only, nbits));
}
