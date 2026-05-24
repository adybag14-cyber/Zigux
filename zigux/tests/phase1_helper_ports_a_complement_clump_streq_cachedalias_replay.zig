const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 bitmap complement aliases clamp partial tails and preserve zero-sized views" {
    const nbits = bitmap.bits_per_long + 5;
    const src = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };

    bitmap.complement(&direct, &src, nbits);
    bitmap.bitmap_complement(&alias, &src, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(~@as(bitmap.Word, 0b1010), direct[0]);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct[1]);

    var zero_src = [_]bitmap.Word{~@as(bitmap.Word, 0)};
    var zero_dst = [_]bitmap.Word{0x1357};
    bitmap.bitmap_complement(zero_dst[0..0], zero_src[0..0], 0);
    try std.testing.expectEqual(@as(bitmap.Word, 0x1357), zero_dst[0]);
}

test "lane06 find_bit clump aliases align to bytes and leave caller state untouched past the end" {
    const nbits = find_bit.bits_per_long + 8;
    const bitmap_words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6),
    };

    var direct_clump: u8 = 0;
    var alias_clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findFirstClump8(&direct_clump, &bitmap_words, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.find_first_clump8(&alias_clump, &bitmap_words, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0b0100_1000), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);

    var preserved_direct: u8 = 0x5a;
    var preserved_alias: u8 = 0x5a;
    try std.testing.expectEqual(
        @as(usize, 8),
        find_bit.findNextClump8(&preserved_direct, &[_]find_bit.Word{@as(find_bit.Word, 1) << 3}, 8, 12),
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        find_bit.find_next_clump8(&preserved_alias, &[_]find_bit.Word{@as(find_bit.Word, 1) << 3}, 8, 12),
    );
    try std.testing.expectEqual(@as(u8, 0x5a), preserved_direct);
    try std.testing.expectEqual(preserved_direct, preserved_alias);
}

test "lane06 string streq and memchr_inv keep C-string and dirty-byte semantics aligned" {
    try std.testing.expect(string.streq(&[_]u8{ 'a', 0, 'x' }, &[_]u8{ 'a', 0, 'y' }));
    try std.testing.expect(!string.streq("abc", "abd"));

    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(replace_buf[0..], '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '+', 'b', 0, '-' }, replace_buf[0..]);

    var zero_backing = [_]u8{0} ** 40;
    zero_backing[13] = 4;
    try std.testing.expectEqual(@as(?usize, 13), string.memchr_inv(zero_backing[0..32], 0));

    var value_backing = [_]u8{7} ** 40;
    value_backing[11] = 5;
    try std.testing.expectEqual(@as(?usize, 11), string.memchr_inv(value_backing[0..32], 7));
}

test "lane06 rbtree cached aliases keep leftmost and replacement state in sync" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
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

    const firstIdentity = struct {
        fn read(root: *const rbtree.RootCached) ?struct { i32, usize } {
            const node = rbtree.firstCached(root) orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", node);
            return .{ entry.key, entry.serial };
        }
    }.read;

    var primary_first = Entry{ .key = 10, .serial = 0 };
    var alias_first = Entry{ .key = 10, .serial = 0 };
    var primary_second = Entry{ .key = 5, .serial = 1 };
    var alias_second = Entry{ .key = 5, .serial = 1 };
    var primary_third = Entry{ .key = 15, .serial = 2 };
    var alias_third = Entry{ .key = 15, .serial = 2 };
    var primary_duplicate = Entry{ .key = 10, .serial = 3 };
    var alias_duplicate = Entry{ .key = 10, .serial = 3 };
    var primary_replacement = Entry{ .key = 10, .serial = 4 };
    var alias_replacement = Entry{ .key = 10, .serial = 4 };

    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_first.node), rbtree.addCached(&primary_first.node, &primary_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_first.node), rbtree.rb_add_cached(&alias_first.node, &alias_root, less));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_second.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_second.node, &alias_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_third.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_third.node, &alias_root, cmp));

    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_root, cmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cmp) orelse return error.TestUnexpectedResult;
    const primary_existing_entry: *const Entry = @fieldParentPtr("node", primary_existing);
    const alias_existing_entry: *const Entry = @fieldParentPtr("node", alias_existing);
    try std.testing.expectEqual(primary_existing_entry.key, alias_existing_entry.key);
    try std.testing.expectEqual(primary_existing_entry.serial, alias_existing_entry.serial);

    const primary_promoted = rbtree.eraseCached(&primary_second.node, &primary_root);
    const alias_promoted = rbtree.rb_erase_cached(&alias_second.node, &alias_root);
    try std.testing.expectEqual(primary_promoted != null, alias_promoted != null);
    try std.testing.expectEqual(firstIdentity(&primary_root), firstIdentity(&alias_root));

    rbtree.replaceNodeCached(&primary_first.node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_first.node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(firstIdentity(&primary_root), firstIdentity(&alias_root));

    rbtree.eraseInitCached(&primary_replacement.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_replacement.node, &alias_root);
    try std.testing.expectEqual(firstIdentity(&primary_root), firstIdentity(&alias_root));
}
