const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

test "bitmap copy clear tail preserves declared bits and clears storage tail" {
    const nbits = bitmap.bits_per_long + 9;
    const tail_mask = bitmap.lastWordMask(nbits);
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    var direct = [_]Word{ 0, 0, 0 };
    var alias = [_]Word{ 0, 0, 0 };

    bitmap.copyClearTail(&direct, &src, nbits);
    bitmap.bitmap_copy_clear_tail(&alias, &src, nbits);

    try std.testing.expectEqual(~@as(Word, 0), direct[0]);
    try std.testing.expectEqual(tail_mask, direct[1]);
    try std.testing.expectEqual(@as(Word, 0), direct[1] & ~tail_mask);
    try std.testing.expectEqual(@as(Word, 0), direct[2]);
    try std.testing.expectEqualSlices(Word, &direct, &alias);
}

test "find bit first-and scans ignore disjoint and out-of-window storage" {
    const nbits = find_bit.bits_per_long + 6;
    const lhs = [_]Word{
        @as(Word, 1) << 2,
        (@as(Word, 1) << 3) | (@as(Word, 1) << 12),
    };
    const rhs = [_]Word{
        @as(Word, 1) << 5,
        (@as(Word, 1) << 3) | (@as(Word, 1) << 14),
    };

    try std.testing.expectEqual(bitmap.bits_per_long + 3, find_bit.findFirstAndBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(bitmap.bits_per_long + 3, find_bit.find_first_and_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(bitmap.bits_per_long + 3, find_bit._find_first_and_bit(&lhs, &rhs, nbits));

    const short_window = bitmap.bits_per_long + 2;
    try std.testing.expectEqual(short_window, find_bit.findFirstAndBit(&lhs, &rhs, short_window));
}

test "string bool parser accepts Linux spellings and rejects empty input" {
    try std.testing.expect(try string.strtobool("y"));
    try std.testing.expect(try string.strtobool("YES"));
    try std.testing.expect(!try string.strtobool("0"));
    try std.testing.expect(!try string.strtobool("off"));

    try std.testing.expectError(error.Invalid, string.strtobool(null));
    try std.testing.expectError(error.Invalid, string.strtobool(""));
    try std.testing.expectError(error.Invalid, string.strtobool("maybe"));
}

test "rbtree singleton first last aliases stop at root boundaries" {
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

    var entry = Entry{ .key = 42 };
    var root = rbtree.Root.init();

    rbtree.add(&entry.node, &root, less);

    try std.testing.expectEqual(&entry.node, rbtree.first(&root).?);
    try std.testing.expectEqual(&entry.node, rbtree.rb_first(&root).?);
    try std.testing.expectEqual(&entry.node, rbtree.last(&root).?);
    try std.testing.expectEqual(&entry.node, rbtree.rb_last(&root).?);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.next(&entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_next(&entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_prev(&entry.node));
}
