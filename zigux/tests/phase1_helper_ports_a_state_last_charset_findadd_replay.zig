const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string_helpers = @import("string_helpers");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap state helpers aligned across a partial tail" {
    const nbits = bitmap.bits_per_long + 5;
    var direct = [_]bitmap.Word{ 0xaa55, 0xaa55 };
    var alias = [_]bitmap.Word{ 0xaa55, 0xaa55 };

    bitmap.zero(&direct, nbits);
    bitmap.bitmap_zero(&alias, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expect(bitmap.empty(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_empty(&alias, nbits));

    bitmap.fill(&direct, nbits);
    bitmap.bitmap_fill(&alias, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expect(bitmap.full(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_full(&alias, nbits));
    try std.testing.expectEqual(@as(usize, nbits), bitmap.weight(&direct, nbits));
    try std.testing.expectEqual(@as(usize, nbits), bitmap.bitmap_weight(&alias, nbits));

    bitmap.clearRange(&direct, bitmap.bits_per_long + 1, 2);
    bitmap.bitmap_clear(&alias, bitmap.bits_per_long + 1, 2);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expect(!bitmap.full(&direct, nbits));
    try std.testing.expect(!bitmap.bitmap_full(&alias, nbits));
    try std.testing.expectEqual(@as(usize, nbits - 2), bitmap.weight(&direct, nbits));
    try std.testing.expectEqual(@as(usize, nbits - 2), bitmap.bitmap_weight(&alias, nbits));

    bitmap.setRange(&direct, bitmap.bits_per_long + 2, 1);
    bitmap.bitmap_set(&alias, bitmap.bits_per_long + 2, 1);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(@as(usize, nbits - 1), bitmap.weight(&direct, nbits));
    try std.testing.expectEqual(@as(usize, nbits - 1), bitmap.bitmap_weight(&alias, nbits));
}

test "lane06 replay keeps find-last helpers clamped to the declared tail window" {
    const nbits = find_bit.bits_per_long + 5;
    var map = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 5,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_last_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit._find_last_bit(&map, nbits));

    map[1] &= ~(@as(find_bit.Word, 1) << 4);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findLastBit(&map, nbits));

    map[1] &= ~(@as(find_bit.Word, 1) << 1);
    try std.testing.expectEqual(@as(usize, 5), find_bit.findLastBit(&map, nbits));

    map[0] = 0;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_last_bit(&map, nbits));
}

test "lane06 replay keeps string copy cleanup and bounded search helpers stable" {
    var padded = [_]u8{ 1, 1, 1, 1, 1 };
    try std.testing.expectEqual(@as(isize, 2), string_helpers.strscpyPad(padded[0..], "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0 }, padded[0..]);

    var spaces = [_]u8{ 'l', ' ', 'a', ' ', 'n', 'e', 0, 'x' };
    try std.testing.expectEqualStrings("lane", string_helpers.removeSpaces(spaces[0..]));

    var replace = [_]u8{ 'l', '-', 'n', '-', 0, '-' };
    try std.testing.expectEqual(@as(usize, 4), string_helpers.replaceChar(replace[0..], '-', 'a'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'l', 'a', 'n', 'a', 0, '-' }, replace[0..]);

    try std.testing.expectEqual(@as(?usize, 3), string_helpers.strnchr("lane", 4, 'e'));
    try std.testing.expectEqual(@as(?usize, null), string_helpers.strnchr(&[_]u8{ 'l', 'a', 0, 'e' }, 4, 'e'));
}

test "lane06 replay keeps cached duplicate find-add behavior and exact lookups stable" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const key_cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var first = Entry{ .key = 10, .serial = 0 };
    var leftmost = Entry{ .key = 5, .serial = 1 };
    var greater = Entry{ .key = 15, .serial = 2 };
    var duplicate = Entry{ .key = 10, .serial = 3 };
    var miss = Entry{ .key = 12, .serial = 4 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &first.node), rbtree.rb_add_cached(&first.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&leftmost.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&greater.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.rb_first_cached(&root));

    const existing = rbtree.rb_find_add_cached(&duplicate.node, &root, cmp) orelse return error.TestUnexpectedResult;
    const existing_entry: *const Entry = @fieldParentPtr("node", existing);
    try std.testing.expectEqual(@as(i32, 10), existing_entry.key);
    try std.testing.expectEqual(@as(usize, 0), existing_entry.serial);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.rb_first_cached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&miss.node, &root, cmp));
    const miss_key = @as(i32, 12);
    const found_miss = rbtree.find(&miss_key, &root.root, key_cmp) orelse return error.TestUnexpectedResult;
    const found_miss_entry: *const Entry = @fieldParentPtr("node", found_miss);
    try std.testing.expectEqual(@as(usize, 4), found_miss_entry.serial);

    const duplicate_key = @as(i32, 10);
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, key_cmp);
    const first_match = iter.next() orelse return error.TestUnexpectedResult;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_match_entry.serial);
    try std.testing.expect(iter.next() == null);
}
