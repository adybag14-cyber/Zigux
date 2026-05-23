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

fn cachedCmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const CachedEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const CachedEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

test "lane06 replay keeps bitmap state aliases aligned across partial tails" {
    const nbits = bitmap.bits_per_long + 5;
    const noisy_tail = (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 11);

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
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weight(&alias, nbits));

    const masked_full = [_]bitmap.Word{ ~@as(bitmap.Word, 0), bitmap.lastWordMask(nbits) | noisy_tail };
    const masked_empty = [_]bitmap.Word{ 0, noisy_tail };
    try std.testing.expect(bitmap.full(&masked_full, nbits));
    try std.testing.expect(bitmap.bitmap_full(&masked_full, nbits));
    try std.testing.expect(bitmap.empty(&masked_empty, nbits));
    try std.testing.expect(bitmap.bitmap_empty(&masked_empty, nbits));
}

test "lane06 replay keeps find_bit clump and last-bit aliases aligned across tail windows" {
    const clump_nbits = find_bit.bits_per_long + 8;
    const bitmap_words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &bitmap_words, clump_nbits));
    try std.testing.expectEqual(@as(u8, 0b0100_1000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_first_clump8(&clump, &bitmap_words, clump_nbits));
    try std.testing.expectEqual(@as(u8, 0b0100_1000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, clump_nbits), find_bit.findNextClump8(&clump, &bitmap_words, clump_nbits, find_bit.bits_per_long + 8));
    try std.testing.expectEqual(@as(u8, 0), clump);

    const nbits = find_bit.bits_per_long + 5;
    var last_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 10),
    };
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findLastBit(&last_map, nbits));
    try std.testing.expectEqual(find_bit.findLastBit(&last_map, nbits), find_bit.find_last_bit(&last_map, nbits));

    last_map[1] &= ~(@as(find_bit.Word, 1) << 3);
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(&last_map, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_last_bit(&last_map, nbits));
}

test "lane06 replay keeps string prefix and match helpers C-string aware" {
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&[_]u8{ 'k', 'e', 'r', 0, 'x' }, "ker"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix("kernel", "ker"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix("kernel", "xyz"));
    try std.testing.expect(string.strstarts("kernel", "ker"));
    try std.testing.expect(!string.strstarts("kernel", "ern"));

    try std.testing.expect(string.strEndsWith(&[_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'x' }, "nel"));
    try std.testing.expect(string.str_ends_with("kernel", "nel"));
    try std.testing.expect(!string.strEndsWith("kernel", "xyz"));

    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(sysfs_haystack[0..], "missing"));

    const cstr_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(cstr_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(cstr_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(cstr_haystack[0..], "gamma"));
}

test "lane06 replay keeps cached rbtree duplicate insertion aliases aligned" {
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    var primary_first = CachedEntry{ .key = 10, .serial = 0 };
    var primary_left = CachedEntry{ .key = 5, .serial = 1 };
    var primary_right = CachedEntry{ .key = 15, .serial = 2 };
    var primary_duplicate = CachedEntry{ .key = 10, .serial = 3 };

    var alias_first = CachedEntry{ .key = 10, .serial = 0 };
    var alias_left = CachedEntry{ .key = 5, .serial = 1 };
    var alias_right = CachedEntry{ .key = 15, .serial = 2 };
    var alias_duplicate = CachedEntry{ .key = 10, .serial = 3 };

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_first.node, &primary_root, cachedCmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_first.node, &alias_root, cachedCmp));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 10, 0 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_left.node, &primary_root, cachedCmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_left.node, &alias_root, cachedCmp));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 1 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_right.node, &primary_root, cachedCmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_right.node, &alias_root, cachedCmp));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));

    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_root, cachedCmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cachedCmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 10, 0 }), returnedIdentity(primary_existing));
    try std.testing.expectEqual(returnedIdentity(primary_existing), returnedIdentity(alias_existing));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 1 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
}