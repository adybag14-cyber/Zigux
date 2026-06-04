const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap copy-and-extend feeds andnot scans across a tail window" {
    const nbits = bits_per_long + 9;
    const original = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << @intCast(bits_per_long - 1)),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 8) | (@as(Word, 1) << 12),
    };
    const mask = [_]Word{
        @as(Word, 1) << @intCast(bits_per_long - 1),
        (@as(Word, 1) << 8) | (@as(Word, 1) << 14),
    };
    var copied = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    var andnot = [_]Word{ 0, 0, 0 };

    bitmap.bitmap_copy_and_extend(&copied, &original, nbits, bits_per_long * 3);
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitsToWords(bits_per_long * 3));
    try std.testing.expectEqual(@as(usize, 1), find_bit.find_first_bit(&copied, bits_per_long * 3));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.find_next_bit(&copied, bits_per_long * 3, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 8), find_bit.find_last_bit(&copied, bits_per_long * 3));

    try std.testing.expect(bitmap.bitmap_andnot(&andnot, &copied, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.find_first_bit(&andnot, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.find_next_andnot_bit(&copied, &mask, nbits, bits_per_long));
    try std.testing.expectEqual(nbits, find_bit.find_next_andnot_bit(&copied, &mask, nbits, bits_per_long + 3));
    try std.testing.expectEqual(@as(Word, 0), andnot[1] & ~bitmap.lastWordMask(nbits));
}

test "string sysfs matching and bounded character search agree on cleaned tokens" {
    var raw = [_]u8{ ' ', '\t', 'o', 'n', 'l', 'i', 'n', 'e', '\n', 0, 'x', 'x' };
    const trimmed = string.strim(&raw);
    const choices = [_][]const u8{ "offline", "online", "maintenance" };

    try std.testing.expectEqualSlices(u8, "online", trimmed);
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&choices, "online\n"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(&choices, "online\n"));
    try std.testing.expectEqual(@as(?usize, 7), string.strnchr(&raw, raw.len, 'e'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&raw, 6, 'e'));
    try std.testing.expect(string.str_ends_with(trimmed, "line"));
}

test "rbtree cached erase aliases preserve leftmost promotion and singleton reset" {
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

    var left = Entry{ .key = 5 };
    var root_entry = Entry{ .key = 10 };
    var right = Entry{ .key = 15 };
    var cached = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.rb_add_cached(&root_entry.node, &cached, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left.node), rbtree.rb_add_cached(&left.node, &cached, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&right.node, &cached, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left.node), rbtree.rb_first_cached(&cached));

    const promoted = rbtree.rb_erase_cached(&left.node, &cached) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.rb_first_cached(&cached));

    rbtree.rb_erase_init_cached(&root_entry.node, &cached);
    try std.testing.expect(rbtree.emptyNode(&root_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &right.node), rbtree.rb_first_cached(&cached));

    rbtree.rb_erase_init_cached(&right.node, &cached);
    try std.testing.expect(rbtree.emptyNode(&right.node));
    try std.testing.expect(rbtree.emptyRoot(&cached.root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_first_cached(&cached));
}
