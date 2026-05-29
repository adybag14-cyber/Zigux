const std = @import("std");
const bitmap = @import("bitmap");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap logical comparisons ignore bits beyond the declared tail" {
    const nbits = bits_per_long + 5;
    const visible_tail = @as(Word, 1) << 2;
    const hidden_tail = @as(Word, 1) << 11;

    const clean = [_]Word{ 0b1010, visible_tail };
    const noisy = [_]Word{ 0b1010, visible_tail | hidden_tail };
    const different_visible = [_]Word{ 0b1010, @as(Word, 1) << 4 };

    try std.testing.expect(bitmap.equal(&clean, &noisy, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&clean, &noisy, nbits));
    try std.testing.expect(!bitmap.equal(&clean, &different_visible, nbits));
    try std.testing.expect(!bitmap.bitmap_equal(&clean, &different_visible, nbits));
}

test "bitmap subset and intersects clamp source noise to the visible tail" {
    const nbits = bits_per_long + 5;
    const hidden_tail = @as(Word, 1) << 12;

    const only_hidden_tail = [_]Word{ 0, hidden_tail };
    const empty = [_]Word{ 0, 0 };
    const visible_owner = [_]Word{ 0, (@as(Word, 1) << 3) | hidden_tail };
    const visible_candidate = [_]Word{ 0, @as(Word, 1) << 3 };

    try std.testing.expect(bitmap.subset(&only_hidden_tail, &empty, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&only_hidden_tail, &empty, nbits));
    try std.testing.expect(!bitmap.intersects(&only_hidden_tail, &empty, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&only_hidden_tail, &empty, nbits));

    try std.testing.expect(bitmap.subset(&visible_candidate, &visible_owner, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&visible_candidate, &visible_owner, nbits));
    try std.testing.expect(bitmap.intersects(&visible_candidate, &visible_owner, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&visible_candidate, &visible_owner, nbits));
}

test "bitmap weighted and destinations mask partial tail words" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{ 0b1110, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 10) };
    const rhs = [_]Word{ 0b1010, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 10) };
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    const direct_any = bitmap.andBits(&direct, &lhs, &rhs, nbits);
    const alias_any = bitmap.bitmap_and(&alias, &lhs, &rhs, nbits);
    try std.testing.expect(direct_any);
    try std.testing.expectEqual(direct_any, alias_any);
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expectEqual(@as(Word, 0b1010), direct[0]);
    try std.testing.expectEqual(@as(Word, 1) << 1, direct[1]);
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&direct, nbits));
}
