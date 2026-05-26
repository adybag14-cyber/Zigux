const std = @import("std");
const bitmap = @import("bitmap");

test "phase 1 bitmap transform review replay keeps weighted aliases and masked replace tails aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{
        0b101101,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    const rhs = [_]bitmap.Word{
        0b011011,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 11),
    };

    var primary_dst = [_]bitmap.Word{ 0, 0 };
    var alias_dst = [_]bitmap.Word{ 0, 0 };

    const primary_or_weight = bitmap.weightedOr(&primary_dst, &lhs, &rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_dst, &lhs, &rhs, nbits);
    try std.testing.expectEqual(primary_or_weight, alias_or_weight);
    try std.testing.expectEqual(primary_or_weight, bitmap.weight(&primary_dst, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &primary_dst, &alias_dst);
    try std.testing.expectEqualSlices(
        bitmap.Word,
        &[_]bitmap.Word{
            0b111111,
            (@as(bitmap.Word, 1) << 1) |
                (@as(bitmap.Word, 1) << 2) |
                (@as(bitmap.Word, 1) << 4) |
                (@as(bitmap.Word, 1) << 9) |
                (@as(bitmap.Word, 1) << 11),
        },
        &primary_dst,
    );

    const primary_xor_weight = bitmap.weightedXor(&primary_dst, &lhs, &rhs, nbits);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&alias_dst, &lhs, &rhs, nbits);
    try std.testing.expectEqual(primary_xor_weight, alias_xor_weight);
    try std.testing.expectEqual(primary_xor_weight, bitmap.weight(&primary_dst, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &primary_dst, &alias_dst);
    try std.testing.expectEqualSlices(
        bitmap.Word,
        &[_]bitmap.Word{
            0b110110,
            (@as(bitmap.Word, 1) << 1) |
                (@as(bitmap.Word, 1) << 2) |
                (@as(bitmap.Word, 1) << 9) |
                (@as(bitmap.Word, 1) << 11),
        },
        &primary_dst,
    );

    const replace_old = [_]bitmap.Word{
        0b11110000,
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8),
    };
    const replace_new = [_]bitmap.Word{
        0b01011100,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 10),
    };
    const replace_mask = [_]bitmap.Word{
        0b00111100,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 10),
    };

    bitmap.replace(&primary_dst, &replace_old, &replace_new, &replace_mask, nbits);
    bitmap.bitmap_replace(&alias_dst, &replace_old, &replace_new, &replace_mask, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &primary_dst, &alias_dst);
    try std.testing.expectEqualSlices(
        bitmap.Word,
        &[_]bitmap.Word{ 0b11011100, 0b01011 },
        &primary_dst,
    );
}

test "phase 1 bitmap transform review replay keeps copy-tail and extension boundaries explicit" {
    const count = bitmap.bits_per_long + 5;
    const size = bitmap.bits_per_long * 2 + 3;
    const src = [_]bitmap.Word{
        0b100101,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };

    var primary_cleared = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    var alias_cleared = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    bitmap.copyClearTail(&primary_cleared, &src, count);
    bitmap.bitmap_copy_clear_tail(&alias_cleared, &src, count);
    try std.testing.expectEqualSlices(bitmap.Word, &primary_cleared, &alias_cleared);
    try std.testing.expectEqualSlices(
        bitmap.Word,
        &[_]bitmap.Word{ src[0], 0b10100 },
        &primary_cleared,
    );

    var primary_extended = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
    };
    var alias_extended = primary_extended;
    bitmap.copyAndExtend(&primary_extended, &src, count, size);
    bitmap.bitmap_copy_and_extend(&alias_extended, &src, count, size);
    try std.testing.expectEqualSlices(bitmap.Word, &primary_extended, &alias_extended);
    try std.testing.expectEqualSlices(
        bitmap.Word,
        &[_]bitmap.Word{ src[0], 0b10100, 0 },
        &primary_extended,
    );

    var zero_extended = [_]bitmap.Word{ 0x55aa, 0xaa55 };
    bitmap.bitmap_copy_and_extend(zero_extended[0..0], &[_]bitmap.Word{}, 0, 0);
    try std.testing.expectEqualSlices(bitmap.Word, &[_]bitmap.Word{ 0x55aa, 0xaa55 }, &zero_extended);
}
