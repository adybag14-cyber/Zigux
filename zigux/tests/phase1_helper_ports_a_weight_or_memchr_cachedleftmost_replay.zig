const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

fn cachedFirstKey(root: *const rbtree.RootCached) ?i32 {
    const node = rbtree.firstCached(root) orelse return null;
    const entry: *const CachedEntry = @fieldParentPtr("node", node);
    return entry.key;
}

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

fn cachedCmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const CachedEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const CachedEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

test "lane06 replay clamps bitmap weighted helpers to the declared tail window" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8) };
    const rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9) };
    var or_dst = [_]bitmap.Word{ 0, 0 };
    var xor_dst = [_]bitmap.Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 3), bitmap.weightedOr(&or_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weighted_or(&or_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weightedXor(&xor_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weighted_xor(&xor_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&or_dst, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&xor_dst, nbits));

    try std.testing.expectEqual(
        @as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 9)),
        or_dst[1],
    );
    try std.testing.expectEqual(
        @as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 9)),
        xor_dst[1],
    );
}

test "lane06 replay keeps findNextAndBit inclusive across whole-word and tail windows" {
    const boundary = find_bit.bits_per_long;
    const whole_nbits = boundary * 2;
    const whole_lhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary - 1),
        @as(find_bit.Word, 1) << 5,
    };
    const whole_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 5),
    };

    try std.testing.expectEqual(@as(usize, boundary + 5), find_bit.findNextAndBit(&whole_lhs, &whole_rhs, whole_nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 5), find_bit.findNextAndBit(&whole_lhs, &whole_rhs, whole_nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary + 5), find_bit.find_next_and_bit(&whole_lhs, &whole_rhs, whole_nbits, boundary));

    const tail_nbits = boundary + 6;
    const tail_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const tail_rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) };

    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.findNextAndBit(&tail_lhs, &tail_rhs, tail_nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextAndBit(&tail_lhs, &tail_rhs, tail_nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, tail_nbits), find_bit.findNextAndBit(&tail_lhs, &tail_rhs, tail_nbits, boundary + 5));
}

test "lane06 replay keeps string dirty-byte scans and padded copies aligned" {
    for (0..@sizeOf(usize)) |offset| {
        var backing = [_]u8{0} ** 40;
        backing[offset + 11] = 2;
        const slice = backing[offset .. offset + 32];
        try std.testing.expectEqual(@as(?usize, 11), string.memchrInv(slice, 0));
        try std.testing.expectEqual(@as(?usize, 11), string.memchr_inv(slice, 0));
    }

    var padded = [_]u8{ 9, 9, 9, 9, 9 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(padded[0..], &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0 }, padded[0..]);

    var alias_padded = [_]u8{ 7, 7, 7, 7 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(alias_padded[0..], "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0 }, alias_padded[0..]);
}

test "lane06 replay keeps cached rbtree leftmost state stable across duplicates and replacement" {
    var root = rbtree.RootCached.init();
    var first_entry = CachedEntry{ .key = 10, .serial = 0 };
    var leftmost_entry = CachedEntry{ .key = 5, .serial = 1 };
    var right_entry = CachedEntry{ .key = 20, .serial = 2 };
    var duplicate_entry = CachedEntry{ .key = 10, .serial = 3 };
    var replacement_entry = CachedEntry{ .key = 20, .serial = 4 };

    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.addCached(&first_entry.node, &root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.addCached(&leftmost_entry.node, &root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&right_entry.node, &root, cachedLess));
    try std.testing.expectEqual(@as(?i32, 5), cachedFirstKey(&root));

    const duplicate = rbtree.findAddCached(&duplicate_entry.node, &root, cachedCmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &first_entry.node), duplicate);
    try std.testing.expectEqual(@as(?i32, 5), cachedFirstKey(&root));

    rbtree.replaceNodeCached(&right_entry.node, &replacement_entry.node, &root);
    try std.testing.expectEqual(@as(?i32, 5), cachedFirstKey(&root));

    const promoted = rbtree.eraseCached(&leftmost_entry.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &first_entry.node), promoted);
    try std.testing.expectEqual(@as(?i32, 10), cachedFirstKey(&root));

    var alias_root = rbtree.RootCached.init();
    var alias_first = CachedEntry{ .key = 8, .serial = 0 };
    var alias_leftmost = CachedEntry{ .key = 3, .serial = 1 };

    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_first.node), rbtree.rb_add_cached(&alias_first.node, &alias_root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_leftmost.node), rbtree.rb_add_cached(&alias_leftmost.node, &alias_root, cachedLess));

    const alias_promoted = rbtree.rb_erase_cached(&alias_leftmost.node, &alias_root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &alias_first.node), alias_promoted);
    try std.testing.expectEqual(@as(?i32, 8), cachedFirstKey(&alias_root));
}
