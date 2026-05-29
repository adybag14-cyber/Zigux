const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;

test "bitmap empty and full ignore storage past declared tails" {
    const nbits = bitmap.bits_per_long + 9;
    const tail_noise = ~bitmap.lastWordMask(nbits);

    var empty_words = [_]Word{ 0, tail_noise };
    try std.testing.expect(bitmap.empty(&empty_words, nbits));
    try std.testing.expect(bitmap.bitmap_empty(&empty_words, nbits));
    try std.testing.expectEqual(@as(usize, 0), bitmap.weight(&empty_words, nbits));

    var full_words = [_]Word{ ~@as(Word, 0), bitmap.lastWordMask(nbits) | tail_noise };
    try std.testing.expect(bitmap.full(&full_words, nbits));
    try std.testing.expect(bitmap.bitmap_full(&full_words, nbits));
    try std.testing.expectEqual(nbits, bitmap.bitmap_weight(&full_words, nbits));

    full_words[1] &= ~(@as(Word, 1) << 8);
    try std.testing.expect(!bitmap.full(&full_words, nbits));
    try std.testing.expectEqual(nbits - 1, bitmap.weight(&full_words, nbits));
}

test "find_bit zero windows and past-end starts do not observe backing words" {
    const words = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    const nbits = bitmap.bits_per_long + 3;

    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(&words, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&words, 0));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&words, nbits, nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextZeroBit(&words, nbits, nbits + 7));
    try std.testing.expectEqual(nbits, find_bit.find_next_bit(&words, nbits, nbits + 1));
    try std.testing.expectEqual(nbits, find_bit.find_next_zero_bit(&words, nbits, nbits + 1));
}

test "string boolean and c-string helpers stop before dirty suffix bytes" {
    var dest = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x' };
    try std.testing.expectEqual(@as(usize, 2), string.strlcpy(&dest, "on\x00ignored"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'n', 0, 'x', 'x', 'x' }, &dest);
    try std.testing.expect(try string.strtobool(dest[0..2]));

    var trimmed = [_]u8{ ' ', '\t', 'n', 'o', '\n', 0, 'z' };
    const stripped = string.strim(&trimmed);
    try std.testing.expectEqualStrings("no", stripped);
    try std.testing.expect(!try string.strtobool(stripped));
    try std.testing.expectEqual(@as(u8, 'z'), trimmed[6]);

    try std.testing.expectError(error.Invalid, string.strtobool("maybe"));
    try std.testing.expect(string.streq("same\x00dirty", "same"));
}

test "rbtree postorder walks all linked nodes before cleared node detaches" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const @This() = @fieldParentPtr("node", lhs);
            const rhs_entry: *const @This() = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    };

    var entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 12 },
        .{ .key = 2 },
        .{ .key = 6 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, Entry.less);
    }

    var seen: usize = 0;
    var current = rbtree.firstPostorder(&root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        seen += 1;
    }
    try std.testing.expectEqual(entries.len, seen);
    try std.testing.expect(rbtree.firstPostorder(&rbtree.Root.init()) == null);

    rbtree.clearNode(&entries[0].node);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expect(rbtree.rb_next_postorder(null) == null);
}
