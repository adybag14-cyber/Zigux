const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports a copy helpers preserve masked tails and zero extension" {
    const count = bitmap.bits_per_long + 5;
    const size = bitmap.bits_per_long * 3;
    const src = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        (~@as(bitmap.Word, 0)) ^ (@as(bitmap.Word, 1) << 9),
        0x55aa_55aa_55aa_55aa,
    };

    var cleared = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.bitmap_copy_clear_tail(&cleared, &src, count);
    try std.testing.expectEqual(@as(bitmap.Word, ~@as(bitmap.Word, 0)), cleared[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), cleared[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), cleared[2]);

    var extended = [_]bitmap.Word{
        0xffff_ffff_ffff_ffff,
        0xffff_ffff_ffff_ffff,
        0xffff_ffff_ffff_ffff,
    };
    bitmap.bitmap_copy_and_extend(&extended, &src, count, size);
    try std.testing.expectEqual(@as(bitmap.Word, ~@as(bitmap.Word, 0)), extended[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), extended[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), extended[2]);
}

test "phase1 helper ports a zero and last-bit scans clamp to the declared range" {
    const nbits = find_bit.bits_per_long * 2 + 5;
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        ~@as(find_bit.Word, 0),
        bitmap.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 4)),
    };
    const last_map = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 7,
        @as(find_bit.Word, 1) << 3,
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long * 2), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long * 2));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long * 2 + 4), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long * 2 + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long * 2 + 5));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long * 2 + 2), find_bit.findLastBit(&last_map, nbits));
}

test "phase1 helper ports a string helpers honor prefixes, suffixes, and bounded searches" {
    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix("zigux=42,end", "zigux="));
    try std.testing.expect(string.strEndsWith("alpha:beta/gamma", "gamma"));
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr("zigux", 5, 'u'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("zigux", 3, 'u'));

    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&cstr, cstr.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, 'c'));

    const dirty = [_]u8{ 0, 0, 0, 1, 0, 0 };
    try std.testing.expectEqual(@as(?usize, 3), string.memchrInv(&dirty, 0));
}

test "phase1 helper ports a cached reset replay keeps leftmost tracking through replacement and erase-init" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var first_entry = Entry{ .key = 10 };
    var leftmost_entry = Entry{ .key = 5 };
    var right_entry = Entry{ .key = 15 };
    var replacement = Entry{ .key = 5 };
    var root = rbtree.RootCached.init();

    _ = rbtree.addCached(&first_entry.node, &root, less);
    _ = rbtree.addCached(&leftmost_entry.node, &root, less);
    _ = rbtree.addCached(&right_entry.node, &root, less);

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&leftmost_entry.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&first_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&first_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &right_entry.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&right_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&right_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));
}
