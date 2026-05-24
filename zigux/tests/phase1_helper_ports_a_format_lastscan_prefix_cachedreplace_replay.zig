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

fn cachedLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const CachedEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const CachedEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn returnedIdentity(node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const CachedEntry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

fn firstCachedIdentity(root: *const rbtree.RootCached) ?struct { i32, usize } {
    return returnedIdentity(rbtree.firstCached(root));
}

test "lane06 replay keeps bitmap formatting aliases aligned across partial tails" {
    const nbits = bitmap.bits_per_long + 6;
    const expected_words = bitmap.bitsToWords(nbits);

    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };

    bitmap.fill(&direct, nbits);
    bitmap.bitmap_fill(&alias, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(@as(usize, expected_words * @sizeOf(bitmap.Word)), bitmap.bitmap_size(nbits));

    bitmap.clearRange(&direct, 1, 3);
    bitmap.clearRange(&direct, bitmap.bits_per_long + 2, 2);
    bitmap.bitmap_zero(&alias, nbits);
    alias[0] = direct[0];
    alias[1] = direct[1];

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&direct, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, &alias_buffer);

    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 1), bitmap.weight(&direct, nbits));
}

test "lane06 replay keeps find_bit last-scan and shared-tail aliases clamped" {
    const nbits = find_bit.bits_per_long + 5;
    const tail_bit = find_bit.bits_per_long + 3;
    const set_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 3) |
            (@as(find_bit.Word, 1) << 8),
    };
    const shared_lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 7),
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 8),
    };
    const shared_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, tail_bit), find_bit.findLastBit(&set_map, nbits));
    try std.testing.expectEqual(@as(usize, tail_bit), find_bit.find_last_bit(&set_map, nbits));
    try std.testing.expectEqual(@as(usize, tail_bit), find_bit._find_last_bit(&set_map, nbits));
    try std.testing.expectEqual(@as(usize, tail_bit), find_bit.findFirstAndBit(&shared_lhs, &shared_rhs, nbits));
    try std.testing.expectEqual(@as(usize, tail_bit), find_bit.find_next_and_bit(&shared_lhs, &shared_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_and_bit(&shared_lhs, &shared_rhs, nbits, tail_bit + 1));
}

test "lane06 replay keeps string prefix and suffix helpers C-string aware" {
    const c_prefix = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'x' };
    const c_suffix = [_]u8{ 'm', 'o', 'd', 'u', 'l', 'e', 0, 'y' };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&c_prefix, "ker"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix(&c_prefix, "ker"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(&c_prefix, "kid"));
    try std.testing.expect(string.strstarts(&c_prefix, "kernel"));
    try std.testing.expect(!string.strstarts(&c_prefix, "kernels"));

    try std.testing.expect(string.strEndsWith(&c_suffix, "ule"));
    try std.testing.expect(string.str_ends_with(&c_suffix, "ule"));
    try std.testing.expect(string.strEndsWith(&c_suffix, "module"));
    try std.testing.expect(!string.strEndsWith(&c_suffix, "rule"));
}

test "lane06 replay keeps cached rbtree replace and erase aliases aligned" {
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    var primary_root_entry = CachedEntry{ .key = 10, .serial = 0 };
    var primary_left = CachedEntry{ .key = 5, .serial = 1 };
    var primary_right = CachedEntry{ .key = 15, .serial = 2 };
    var primary_replacement = CachedEntry{ .key = 5, .serial = 3 };

    var alias_root_entry = CachedEntry{ .key = 10, .serial = 0 };
    var alias_left = CachedEntry{ .key = 5, .serial = 1 };
    var alias_right = CachedEntry{ .key = 15, .serial = 2 };
    var alias_replacement = CachedEntry{ .key = 5, .serial = 3 };

    _ = rbtree.addCached(&primary_root_entry.node, &primary_root, cachedLess);
    _ = rbtree.addCached(&primary_left.node, &primary_root, cachedLess);
    _ = rbtree.addCached(&primary_right.node, &primary_root, cachedLess);

    _ = rbtree.rb_add_cached(&alias_root_entry.node, &alias_root, cachedLess);
    _ = rbtree.rb_add_cached(&alias_left.node, &alias_root, cachedLess);
    _ = rbtree.rb_add_cached(&alias_right.node, &alias_root, cachedLess);

    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 1 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));

    rbtree.replaceNodeCached(&primary_left.node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_left.node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 3 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));

    try std.testing.expectEqual(
        returnedIdentity(rbtree.eraseCached(&primary_replacement.node, &primary_root)),
        returnedIdentity(rbtree.rb_erase_cached(&alias_replacement.node, &alias_root)),
    );
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 10, 0 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
}
