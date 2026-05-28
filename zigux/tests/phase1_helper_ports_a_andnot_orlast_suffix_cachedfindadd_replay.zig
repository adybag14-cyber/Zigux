const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "phase1 helper ports A bitmap andnot and or keep partial tails exact" {
    const nbits = find_bit.bits_per_long + 9;
    const lhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 1) |
            (@as(bitmap.Word, 1) << 3) |
            (@as(bitmap.Word, 1) << 8) |
            (@as(bitmap.Word, 1) << 12),
    };
    const rhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 3) |
            (@as(bitmap.Word, 1) << 12),
    };

    var diff = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.bitmap_andnot(&diff, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&diff, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findFirstBit(&diff, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.findLastBit(&diff, nbits));
    try std.testing.expectEqual(
        @as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 8)),
        diff[1],
    );

    var combined = [_]bitmap.Word{ 0, 0 };
    try std.testing.expectEqual(@as(usize, 3), bitmap.weightedOr(&combined, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.findLastBit(&combined, nbits));
}

test "phase1 helper ports A tail next-bit and last-bit scans clamp to the declared tail" {
    const nbits = find_bit.bits_per_long + 7;
    const lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 9) };
    const rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 5) | (@as(find_bit.Word, 1) << 10) };
    const merged = [_]find_bit.Word{ 0, lhs[1] | rhs[1] };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.findNextBit(&merged, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.find_next_bit(&merged, nbits, find_bit.bits_per_long + 3));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&merged, nbits, find_bit.bits_per_long + 6));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.findLastBit(&rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.find_last_bit(&rhs, nbits));
}

test "phase1 helper ports A suffix and dirty-byte scans respect C-string boundaries" {
    const suffix_cstr = [_]u8{ 'm', 'o', 'd', 'e', 0, '.', 'c' };
    try std.testing.expect(string.strEndsWith(&suffix_cstr, "mode"));
    try std.testing.expect(string.str_ends_with(&suffix_cstr, "ode"));
    try std.testing.expect(!string.strEndsWith(&suffix_cstr, "de.c"));

    var dirty = [_]u8{'a'} ** 24;
    dirty[9] = 'z';
    try std.testing.expectEqual(@as(?usize, 9), string.memchrInv(&dirty, 'a'));
    try std.testing.expectEqual(@as(?usize, 9), string.memchr_inv(&dirty, 'a'));

    const counted = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&counted, counted.len, 'x'));
}

test "phase1 helper ports A cached duplicate insertion keeps leftmost truthful" {
    const Entry = struct {
        const Self = @This();

        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),

        fn cmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Self = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Self = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    };

    var root_entry = Entry{ .key = 8, .serial = 0 };
    var leftmost_entry = Entry{ .key = 4, .serial = 1 };
    var greater_entry = Entry{ .key = 12, .serial = 2 };
    var duplicate_entry = Entry{ .key = 8, .serial = 3 };
    var new_leftmost = Entry{ .key = 2, .serial = 4 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&root_entry.node, &root, Entry.cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&leftmost_entry.node, &root, Entry.cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&greater_entry.node, &root, Entry.cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.rb_first_cached(&root));

    const duplicate = rbtree.rb_find_add_cached(&duplicate_entry.node, &root, Entry.cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), duplicate);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.rb_first_cached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&new_leftmost.node, &root, Entry.cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &new_leftmost.node), rbtree.rb_first_cached(&root));
}
