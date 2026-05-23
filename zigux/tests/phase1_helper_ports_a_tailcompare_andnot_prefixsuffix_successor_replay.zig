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

fn cachedFirstIdentity(root: *const rbtree.RootCached) ?struct { i32, usize } {
    const node = rbtree.firstCached(root) orelse return null;
    const entry: *const CachedEntry = @fieldParentPtr("node", node);
    return .{ entry.key, entry.serial };
}

fn returnedIdentity(node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const CachedEntry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

test "lane06 replay keeps bitmap tail comparisons and aliases aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const in_range_tail = @as(bitmap.Word, 1) << 3;
    const lhs = [_]bitmap.Word{ 0b1010, in_range_tail | (@as(bitmap.Word, 1) << 9) };
    const rhs = [_]bitmap.Word{ 0b1010, in_range_tail | (@as(bitmap.Word, 1) << 11) };
    const outside_only = [_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 12 };

    try std.testing.expect(bitmap.equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.subset(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&lhs, &rhs, nbits));

    try std.testing.expect(bitmap.equal(&outside_only, &[_]bitmap.Word{ 0, 0 }, nbits));
    try std.testing.expect(!bitmap.intersects(&outside_only, &outside_only, nbits));
    try std.testing.expect(bitmap.subset(&outside_only, &[_]bitmap.Word{ 0, 0 }, nbits));
}

test "lane06 replay keeps find_bit zero and andnot boundary scans inclusive" {
    const boundary = find_bit.bits_per_long;
    const whole_nbits = boundary * 2;
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        ~((@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 5)),
    };
    const andnot_lhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary - 1),
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 5),
    };
    const andnot_rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary - 1),
        @as(find_bit.Word, 1) << 5,
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextZeroBit(&zero_map, whole_nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 5), find_bit.findNextZeroBit(&zero_map, whole_nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_next_zero_bit(&zero_map, whole_nbits, boundary));

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, whole_nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_next_andnot_bit(&andnot_lhs, &andnot_rhs, whole_nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit._find_next_andnot_bit(&andnot_lhs, &andnot_rhs, whole_nbits, boundary));
    try std.testing.expectEqual(@as(usize, whole_nbits), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, whole_nbits, boundary + 1));

    const tail_nbits = boundary + 6;
    const tail_zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(tail_nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    const tail_andnot_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };
    const tail_andnot_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.findNextZeroBit(&tail_zero_map, tail_nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextZeroBit(&tail_zero_map, tail_nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, tail_nbits), find_bit.findNextZeroBit(&tail_zero_map, tail_nbits, boundary + 5));

    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, tail_nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, tail_nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, tail_nbits), find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, tail_nbits, boundary + 5));
}

test "lane06 replay keeps string prefix suffix and bounded searches aligned" {
    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix(&[_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0, 'x' }, "prefix"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix("prefix", "pre"));
    try std.testing.expect(string.strstarts(&[_]u8{ 'p', 'r', 'e', 0, 'x' }, "pre"));
    try std.testing.expect(!string.strstarts("prefix", "fix"));

    try std.testing.expect(string.strEndsWith(&[_]u8{ 'n', 'o', 'd', 'e', 0, '/' }, "de"));
    try std.testing.expect(string.str_ends_with("kernel", "nel"));
    try std.testing.expect(!string.strEndsWith("kernel", "ern"));

    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));

    const match_haystack = [_][]const u8{
        &[_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'x' },
        "beta",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(match_haystack[0..], "alpha"));

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&[_]u8{ 'a', 'b', 0, 'c' }, 4, 'b'));
}

test "lane06 replay keeps cached rbtree successor promotion aligned when erasing the leftmost node" {
    var root = rbtree.RootCached.init();
    var leftmost = CachedEntry{ .key = 5, .serial = 0 };
    var successor = CachedEntry{ .key = 7, .serial = 1 };
    var root_entry = CachedEntry{ .key = 10, .serial = 2 };
    var right_entry = CachedEntry{ .key = 15, .serial = 3 };

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.addCached(&leftmost.node, &root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&root_entry.node, &root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&successor.node, &root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&right_entry.node, &root, cachedLess));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 0 }), cachedFirstIdentity(&root));

    const promoted = rbtree.eraseCached(&leftmost.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &successor.node), promoted);
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 7, 1 }), cachedFirstIdentity(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var alias_root = rbtree.RootCached.init();
    var alias_leftmost = CachedEntry{ .key = 4, .serial = 0 };
    var alias_successor = CachedEntry{ .key = 6, .serial = 1 };
    var alias_root_entry = CachedEntry{ .key = 9, .serial = 2 };

    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_leftmost.node), rbtree.rb_add_cached(&alias_leftmost.node, &alias_root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&alias_root_entry.node, &alias_root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&alias_successor.node, &alias_root, cachedLess));

    try std.testing.expectEqual(
        @as(?struct { i32, usize }, .{ 6, 1 }),
        returnedIdentity(rbtree.rb_erase_cached(&alias_leftmost.node, &alias_root)),
    );
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 6, 1 }), cachedFirstIdentity(&alias_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
}
