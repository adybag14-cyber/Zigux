const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 bitmap copy-and-extend keeps tail clear and aliases aligned" {
    const src_bits = bitmap.bits_per_long + 5;
    const dst_bits = bitmap.bits_per_long * 2 + 3;
    const src = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) |
            (@as(bitmap.Word, 1) << 5) |
            (@as(bitmap.Word, 1) << (bitmap.bits_per_long - 1)),
        (@as(bitmap.Word, 1) << 0) |
            (@as(bitmap.Word, 1) << 2) |
            (@as(bitmap.Word, 1) << 4) |
            (@as(bitmap.Word, 1) << 9),
    };

    var direct = [_]bitmap.Word{ std.math.maxInt(bitmap.Word), std.math.maxInt(bitmap.Word), std.math.maxInt(bitmap.Word) };
    var alias = [_]bitmap.Word{ std.math.maxInt(bitmap.Word), std.math.maxInt(bitmap.Word), std.math.maxInt(bitmap.Word) };

    bitmap.copyAndExtend(&direct, &src, src_bits, dst_bits);
    bitmap.bitmap_copy_and_extend(&alias, &src, src_bits, dst_bits);

    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expect(bitmap.bitmap_subset(direct[0..bitmap.bitsToWords(src_bits)], &src, src_bits));
    try std.testing.expect(bitmap.bitmap_empty(
        direct[bitmap.bitsToWords(src_bits)..bitmap.bitsToWords(dst_bits)],
        dst_bits - bitmap.bits_per_long * bitmap.bitsToWords(src_bits),
    ));

    try std.testing.expectEqual(@as(bitmap.Word, src[0]), direct[0]);
    try std.testing.expectEqual(src[1] & bitmap.lastWordMask(src_bits), direct[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct[2]);
}

test "lane06 find_bit next-and and next-zero aliases cross word boundaries" {
    const nbits = find_bit.bits_per_long * 2 + 7;
    const lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << (find_bit.bits_per_long - 2)) |
            (@as(find_bit.Word, 1) << (find_bit.bits_per_long - 1)),
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4),
        (@as(find_bit.Word, 1) << 0),
    };
    const rhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << (find_bit.bits_per_long - 1)),
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 3) |
            (@as(find_bit.Word, 1) << 4),
        0,
    };
    const filled = [_]find_bit.Word{
        std.math.maxInt(find_bit.Word),
        std.math.maxInt(find_bit.Word),
        @as(find_bit.Word, 0b0011_1111),
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long - 1),
        find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long - 3),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.find_next_and_bit(&lhs, &rhs, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long * 2 + 6),
        find_bit.findNextZeroBit(&filled, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long * 2 + 6),
        find_bit.find_next_zero_bit(&filled, nbits, find_bit.bits_per_long + 3),
    );
}

test "lane06 string skip trim basename and prefix helpers stay aligned" {
    try std.testing.expectEqualStrings("lane06 value", string.skipSpaces(" \t\nlane06 value"));
    try std.testing.expectEqualStrings("phase1", string.skip_spaces("  phase1"));

    var trim_buf = [_]u8{ ' ', '\t', 'k', 'e', 'e', 'p', ' ', '\n', 0, 0 };
    const trimmed = string.trimSpaces(&trim_buf);
    try std.testing.expectEqualStrings("keep", trimmed);
    try std.testing.expectEqualStrings("keep", string.strstrip(&trim_buf));

    var remove_buf = [_]u8{ 'a', ' ', 'b', ' ', 'c', 0, 0 };
    const compact = string.remove_spaces(&remove_buf);
    try std.testing.expectEqualStrings("abc", compact);

    try std.testing.expectEqual(@as(usize, 5), string.strHasPrefix("lane06-replay", "lane0"));
    try std.testing.expectEqual(@as(usize, 5), string.str_has_prefix("lane06-replay", "lane0"));
    try std.testing.expect(string.strstarts("lane06-replay", "lane0"));
}

test "lane06 rbtree duplicate match walking and reverse aliases stay ordered" {
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

    const cmp_key = struct {
        fn compare(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
            const key: *const i32 = @ptrCast(@alignCast(key_ptr));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (key.* < entry.key) return -1;
            if (key.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 4, .serial = 0 },
        .{ .key = 2, .serial = 1 },
        .{ .key = 4, .serial = 2 },
        .{ .key = 4, .serial = 3 },
        .{ .key = 7, .serial = 4 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const match_key: i32 = 4;
    var iter = rbtree.matchIterator(&match_key, &root, cmp_key);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), iter.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), iter.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), iter.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iter.next());

    const tail = rbtree.rb_last(&root).?;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[4].node), tail);
    const before_tail = rbtree.rb_prev(tail).?;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[3].node), before_tail);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.nextMatch(&match_key, &entries[2].node, cmp_key));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextMatch(&match_key, before_tail, cmp_key));
}
