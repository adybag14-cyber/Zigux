const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay bitmap fill clear and formatting stay clamped to the declared tail" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;
    var map = [_]Word{ 0, 0 };

    bitmap.bitmap_fill(&map, nbits);
    try std.testing.expect(bitmap.bitmap_full(&map, nbits));
    try std.testing.expectEqual(@as(usize, nbits), bitmap.bitmap_weight(&map, nbits));

    bitmap.bitmap_clear(&map, 2, 2);
    bitmap.bitmap_clear(&map, bitmap.bits_per_long + 1, 2);
    try std.testing.expect(!bitmap.bitmap_full(&map, nbits));
    try std.testing.expectEqual(@as(usize, nbits - 4), bitmap.bitmap_weight(&map, nbits));

    var buffer: [64]u8 = undefined;
    const len = bitmap.bitmap_scnprintf(&map, nbits, &buffer);

    var expected: [64]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "0-1,4-{d},{d}-{d}",
        .{ bitmap.bits_per_long, bitmap.bits_per_long + 3, bitmap.bits_per_long + 4 },
    );
    try std.testing.expectEqualStrings(expected_text, buffer[0..len]);

    bitmap.bitmap_zero(&map, nbits);
    try std.testing.expect(bitmap.bitmap_empty(&map, nbits));
}

test "lane06 replay find-bit andnot zero and clump helpers keep partial tails explicit" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 8) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 8) };
    const zero_map = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(Word, 1) << 0) | (@as(Word, 1) << 4)),
    };
    const clump_map = [_]Word{ 0, (@as(Word, 1) << 0) | (@as(Word, 1) << 4) | (@as(Word, 1) << 7) };
    var clump: u8 = 0xaa;

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 4));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstZeroBit(&zero_map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 1));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &clump_map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_0001), clump);
}

test "lane06 replay string pad suffix and sentinel helpers stop at the first C-string edge" {
    const text = [_]u8{ 'a', 'b', 'c', 0, 'x', 'y' };
    const modes = [_][]const u8{ "off\n", "auto", "auto\n", "on" };
    var padded = [_]u8{ 1, 1, 1, 1, 1 };
    var repeated = [_]u8{'q'} ** 24;
    repeated[17] = 'z';

    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(padded[0..], &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0 }, padded[0..]);
    try std.testing.expect(string.strEndsWith(text[0..], "bc"));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(text[0..], text.len, 'x'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(text[0..], text.len, 'c'));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(modes[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 17), string.memchr_inv(repeated[0..], 'q'));
}

test "lane06 replay cached rbtree replacement and erase-init keep the leftmost pointer aligned" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var leftmost = Entry{ .key = 5 };
    var root_entry = Entry{ .key = 10 };
    var right_entry = Entry{ .key = 15 };
    var replacement = Entry{ .key = 15 };
    var cached_root = rbtree.RootCached.init();

    _ = rbtree.rb_add_cached(&root_entry.node, &cached_root, less);
    _ = rbtree.rb_add_cached(&leftmost.node, &cached_root, less);
    _ = rbtree.rb_add_cached(&right_entry.node, &cached_root, less);

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.rb_first_cached(&cached_root));

    rbtree.rb_replace_node_cached(&right_entry.node, &replacement.node, &cached_root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.rb_first_cached(&cached_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_last(&cached_root.root));

    rbtree.rb_erase_init_cached(&leftmost.node, &cached_root);
    try std.testing.expect(rbtree.emptyNode(&leftmost.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.rb_first_cached(&cached_root));

    rbtree.rb_erase_init_cached(&root_entry.node, &cached_root);
    try std.testing.expect(rbtree.emptyNode(&root_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_first_cached(&cached_root));
    try std.testing.expectEqual(rbtree.rb_first(&cached_root.root), rbtree.rb_first_cached(&cached_root));
}
