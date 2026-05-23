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

fn cachedCmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const CachedEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const CachedEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn returnedIdentity(node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const CachedEntry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

fn firstCachedIdentity(root: *const rbtree.RootCached) ?struct { i32, usize } {
    return returnedIdentity(rbtree.firstCached(root));
}

test "lane06 replay keeps bitmap weighted helpers tail-clamped and alias-aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{
        0b1011,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 7),
    };
    const rhs = [_]bitmap.Word{
        0b0101,
        (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };

    var primary_or = [_]bitmap.Word{ 0, 0 };
    var alias_or = [_]bitmap.Word{ 0, 0 };
    const primary_or_weight = bitmap.weightedOr(&primary_or, &lhs, &rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);

    try std.testing.expectEqual(primary_or_weight, alias_or_weight);
    try std.testing.expectEqual(bitmap.weight(&primary_or, nbits), primary_or_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &primary_or, &alias_or);
    try std.testing.expectEqual(@as(bitmap.Word, 0b1111), primary_or[0]);
    try std.testing.expectEqual(
        @as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 7) | (@as(bitmap.Word, 1) << 9)),
        primary_or[1],
    );

    var primary_xor = [_]bitmap.Word{ 0, 0 };
    var alias_xor = [_]bitmap.Word{ 0, 0 };
    const primary_xor_weight = bitmap.weightedXor(&primary_xor, &lhs, &rhs, nbits);
    const alias_xor_weight = bitmap.__bitmap_weighted_xor(&alias_xor, &lhs, &rhs, nbits);

    try std.testing.expectEqual(primary_xor_weight, alias_xor_weight);
    try std.testing.expectEqual(bitmap.weight(&primary_xor, nbits), primary_xor_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &primary_xor, &alias_xor);
    try std.testing.expectEqual(@as(bitmap.Word, 0b1110), primary_xor[0]);
    try std.testing.expectEqual(
        @as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 7) | (@as(bitmap.Word, 1) << 9)),
        primary_xor[1],
    );
}

test "lane06 replay keeps find_bit first-and scans clamped across tail and single-word windows" {
    const tail_nbits = find_bit.bits_per_long + 5;
    const tail_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 8),
    };
    const tail_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 9),
    };
    const tail_andnot_rhs = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << 8,
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.findFirstAndBit(&tail_lhs, &tail_rhs, tail_nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.find_first_and_bit(&tail_lhs, &tail_rhs, tail_nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit._find_first_and_bit(&tail_lhs, &tail_lhs, find_bit.bits_per_long + 2));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.findFirstAndNotBit(&tail_lhs, &tail_andnot_rhs, tail_nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.find_first_andnot_bit(&tail_lhs, &tail_andnot_rhs, tail_nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit._find_first_andnot_bit(&tail_lhs, &tail_andnot_rhs, find_bit.bits_per_long + 2));

    const single_nbits = 6;
    const single_lhs = [_]find_bit.Word{(@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 8)};
    const single_rhs = [_]find_bit.Word{(@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 8)};
    const single_andnot_rhs = [_]find_bit.Word{@as(find_bit.Word, 1) << 4};

    try std.testing.expectEqual(@as(usize, 4), find_bit.findFirstAndBit(&single_lhs, &single_rhs, single_nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.findFirstAndBit(&tail_lhs, &tail_rhs, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstAndNotBit(&single_lhs, &single_andnot_rhs, single_nbits));
}

test "lane06 replay keeps string pad and match helpers C-string aware" {
    var padded = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x' };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, &[_]u8{ 'o', 'k', 0, '!' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &padded);

    var alias_padded = [_]u8{ 'y', 'y', 'y', 'y', 'y' };
    try std.testing.expectEqual(@as(isize, 1), string.strscpy_pad(&alias_padded, &[_]u8{ 'z', 0, 'w' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 0, 0, 0, 0 }, &alias_padded);

    try std.testing.expect(string.streq(&[_]u8{ 'n', 'o', 'd', 'e', 0, 'x' }, "node"));
    try std.testing.expect(!string.streq(&[_]u8{ 'n', 'o', 'd', 'e', 0, 'x' }, "mode"));

    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto\n"));

    const match_haystack = [_][]const u8{
        &[_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'x' },
        "beta",
        "gamma",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(match_haystack[0..], "alpha"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(match_haystack[0..], "beta"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(match_haystack[0..], "alphabet"));
}

test "lane06 replay keeps cached rbtree duplicate insertion identity stable" {
    var root = rbtree.RootCached.init();
    var first = CachedEntry{ .key = 10, .serial = 0 };
    var left = CachedEntry{ .key = 5, .serial = 1 };
    var right = CachedEntry{ .key = 15, .serial = 2 };
    var duplicate = CachedEntry{ .key = 10, .serial = 99 };
    var new_right = CachedEntry{ .key = 12, .serial = 3 };

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&first.node, &root, cachedCmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&left.node, &root, cachedCmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&right.node, &root, cachedCmp));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 1 }), firstCachedIdentity(&root));

    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 10, 0 }), returnedIdentity(rbtree.findAddCached(&duplicate.node, &root, cachedCmp)));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 1 }), firstCachedIdentity(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), duplicate.node.parent);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), duplicate.node.left);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), duplicate.node.right);

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&new_right.node, &root, cachedCmp));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 1 }), returnedIdentity(rbtree.rb_first_cached(&root)));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
