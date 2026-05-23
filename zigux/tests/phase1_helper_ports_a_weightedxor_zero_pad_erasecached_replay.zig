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
    if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
    return lhs_entry.serial < rhs_entry.serial;
}

test "lane06 replay keeps bitmap weighted xor aliases aligned across partial tails" {
    const nbits = bitmap.bits_per_long + 5;
    const src1 = [_]bitmap.Word{
        0b10110110,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    const src2 = [_]bitmap.Word{
        0b01101100,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 11),
    };

    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };
    var lowlevel = [_]bitmap.Word{ 0, 0 };

    const direct_weight = bitmap.weightedXor(&direct, &src1, &src2, nbits);
    const alias_weight = bitmap.bitmap_weighted_xor(&alias, &src1, &src2, nbits);
    const lowlevel_weight = bitmap.__bitmap_weighted_xor(&lowlevel, &src1, &src2, nbits);

    try std.testing.expectEqual(direct_weight, alias_weight);
    try std.testing.expectEqual(direct_weight, lowlevel_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &lowlevel);
    try std.testing.expectEqual(@as(bitmap.Word, src1[1] ^ src2[1]), direct[1]);
    try std.testing.expectEqual(@as(usize, 7), direct_weight);
    try std.testing.expectEqual(direct_weight, bitmap.weight(&direct, nbits));
}

test "lane06 replay keeps find_bit zero-scan aliases aligned across tail windows" {
    const nbits = find_bit.bits_per_long + 3;
    const map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 8)),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findFirstZeroBit(&map, nbits));
    try std.testing.expectEqual(
        find_bit.findFirstZeroBit(&map, nbits),
        find_bit.find_first_zero_bit(&map, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findNextZeroBit(&map, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        find_bit.findNextZeroBit(&map, nbits, find_bit.bits_per_long),
        find_bit._find_next_zero_bit(&map, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextZeroBit(&map, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.find_next_zero_bit(&map, nbits, nbits),
    );
}

test "lane06 replay keeps string padded copy and bounded search helpers C-string aware" {
    const src = [_]u8{ 'h', 'i', 0, 'x' };

    var direct = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    var alias = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };

    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&direct, &src));
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(&alias, &src));
    try std.testing.expectEqualSlices(u8, &direct, &alias);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, &direct);

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&direct, direct.len, 'i'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&direct, direct.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&direct, direct.len, 'x'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr("padded", 3, 'd'));
}

test "lane06 replay keeps cached erase aliases aligned around leftmost updates" {
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    var primary_mid = CachedEntry{ .key = 10, .serial = 0 };
    var primary_left = CachedEntry{ .key = 5, .serial = 1 };
    var primary_right = CachedEntry{ .key = 15, .serial = 2 };

    var alias_mid = CachedEntry{ .key = 10, .serial = 0 };
    var alias_left = CachedEntry{ .key = 5, .serial = 1 };
    var alias_right = CachedEntry{ .key = 15, .serial = 2 };

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_mid.node), rbtree.addCached(&primary_mid.node, &primary_root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_mid.node), rbtree.rb_add_cached(&alias_mid.node, &alias_root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_left.node), rbtree.addCached(&primary_left.node, &primary_root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_left.node), rbtree.rb_add_cached(&alias_left.node, &alias_root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&primary_right.node, &primary_root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&alias_right.node, &alias_root, cachedLess));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 1 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));

    const primary_next = rbtree.eraseCached(&primary_left.node, &primary_root);
    const alias_next = rbtree.rb_erase_cached(&alias_left.node, &alias_root);
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 10, 0 }), returnedIdentity(primary_next));
    try std.testing.expectEqual(returnedIdentity(primary_next), returnedIdentity(alias_next));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 10, 0 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.eraseCached(&primary_right.node, &primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_erase_cached(&alias_right.node, &alias_root));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 10, 0 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
}
