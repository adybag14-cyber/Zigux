const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const CachedEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn returnedIdentity(node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const CachedEntry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

fn firstCachedIdentity(root: *const rbtree.RootCached) ?struct { i32, usize } {
    return returnedIdentity(rbtree.firstCached(root));
}

fn cachedLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const CachedEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const CachedEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

test "lane06 replay keeps bitmap range and state helpers alias-aligned across tail windows" {
    const nbits = bitmap.bits_per_long + 5;
    const span_start = bitmap.bits_per_long - 2;
    const span_len = 6;

    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };

    bitmap.setRange(&direct, span_start, span_len);
    bitmap.bitmap_set(&alias, span_start, span_len);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expect(bitmap.intersects(&direct, &alias, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&alias, &direct, nbits));
    try std.testing.expect(bitmap.equal(&direct, &alias, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&alias, &direct, nbits));

    bitmap.clearRange(&direct, bitmap.bits_per_long + 1, 2);
    bitmap.bitmap_clear(&alias, bitmap.bits_per_long + 1, 2);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expect(!bitmap.full(&direct, nbits));
    try std.testing.expect(!bitmap.bitmap_full(&alias, nbits));
    try std.testing.expect(!bitmap.empty(&direct, nbits));
    try std.testing.expect(!bitmap.bitmap_empty(&alias, nbits));

    const superset = [_]bitmap.Word{
        direct[0],
        direct[1] | (@as(bitmap.Word, 1) << 4),
    };
    try std.testing.expect(bitmap.subset(&direct, &superset, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&alias, &superset, nbits));
    try std.testing.expectEqual(@as(usize, span_len - 2), bitmap.weight(&direct, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weight(&alias, nbits));
}

test "lane06 replay keeps find_bit next-scan windows clamped across single-word tail and word-boundary starts" {
    const tail_nbits = find_bit.bits_per_long + 5;
    const tail_set = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 8),
    };
    const tail_zero = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(tail_nbits) & ~((@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 4)),
    };
    const tail_and_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 8),
    };
    const tail_and_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };
    const tail_andnot_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 8),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextBit(&tail_set, tail_nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_next_bit(&tail_set, tail_nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, tail_nbits), find_bit._find_next_bit(&tail_set, tail_nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.findNextZeroBit(&tail_zero, tail_nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_next_zero_bit(&tail_zero, tail_nbits, find_bit.bits_per_long + 3));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_next_and_bit(&tail_and_lhs, &tail_and_rhs, tail_nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit._find_next_andnot_bit(&tail_and_lhs, &tail_andnot_rhs, tail_nbits, find_bit.bits_per_long + 2));

    const single_nbits = 6;
    const single_set = [_]find_bit.Word{(@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 5) | (@as(find_bit.Word, 1) << 8)};
    const single_zero = [_]find_bit.Word{find_bit.lastWordMask(single_nbits) & ~(@as(find_bit.Word, 1) << 2)};

    try std.testing.expectEqual(@as(usize, 1), find_bit.findNextBit(&single_set, single_nbits, 0));
    try std.testing.expectEqual(@as(usize, 5), find_bit.find_next_bit(&single_set, single_nbits, 2));
    try std.testing.expectEqual(@as(usize, single_nbits), find_bit._find_next_bit(&single_set, single_nbits, single_nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findNextZeroBit(&single_zero, single_nbits, 0));
    try std.testing.expectEqual(@as(usize, single_nbits), find_bit.find_next_zero_bit(&single_zero, single_nbits, 3));
}

test "lane06 replay keeps string trim and sysfs helpers C-string aware" {
    try std.testing.expectEqualStrings("lead", string.skipSpaces(" \tlead"));
    try std.testing.expectEqualStrings("keep", string.skip_spaces("  keep"));
    try std.testing.expect(string.streq(&[_]u8{ 'o', 'k', 0, 'x' }, "ok"));
    try std.testing.expect(!string.strEq(&[_]u8{ 'o', 'k', 0, 'x' }, "okay"));

    var trimmed = [_]u8{ ' ', 'o', 'k', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("ok", string.trimSpaces(trimmed[0..]));
    try std.testing.expectEqualStrings("ok", string.strim(trimmed[0..]));
    try std.testing.expectEqualStrings("ok", string.strstrip(trimmed[0..]));

    var compacted = [_]u8{ 'a', ' ', 'b', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("ab", string.removeSpaces(compacted[0..]));
    try std.testing.expectEqualStrings("ab", string.remove_spaces(compacted[0..]));

    var replaced = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string.replaceChar(replaced[0..], '-', '+'));
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(replaced[0..], '+', '-'));

    try std.testing.expect(string.sysfsStreq("mode\n", "mode"));
    try std.testing.expect(string.sysfs_streq("mode\n", "mode"));
}

test "lane06 replay keeps cached rbtree erase-init reseeding aligned with alias helpers" {
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    var primary_first = CachedEntry{ .key = 10, .serial = 0 };
    var primary_left = CachedEntry{ .key = 5, .serial = 1 };
    var primary_right = CachedEntry{ .key = 15, .serial = 2 };
    var primary_reseed = CachedEntry{ .key = 7, .serial = 3 };

    var alias_first = CachedEntry{ .key = 10, .serial = 0 };
    var alias_left = CachedEntry{ .key = 5, .serial = 1 };
    var alias_right = CachedEntry{ .key = 15, .serial = 2 };
    var alias_reseed = CachedEntry{ .key = 7, .serial = 3 };

    _ = rbtree.addCached(&primary_first.node, &primary_root, cachedLess);
    _ = rbtree.addCached(&primary_left.node, &primary_root, cachedLess);
    _ = rbtree.addCached(&primary_right.node, &primary_root, cachedLess);

    _ = rbtree.rb_add_cached(&alias_first.node, &alias_root, cachedLess);
    _ = rbtree.rb_add_cached(&alias_left.node, &alias_root, cachedLess);
    _ = rbtree.rb_add_cached(&alias_right.node, &alias_root, cachedLess);

    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 1 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));

    rbtree.eraseInitCached(&primary_left.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_left.node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_left.node));
    try std.testing.expect(rbtree.emptyNode(&alias_left.node));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 10, 0 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_reseed.node), rbtree.addCached(&primary_reseed.node, &primary_root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_reseed.node), rbtree.rb_add_cached(&alias_reseed.node, &alias_root, cachedLess));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 7, 3 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
}
