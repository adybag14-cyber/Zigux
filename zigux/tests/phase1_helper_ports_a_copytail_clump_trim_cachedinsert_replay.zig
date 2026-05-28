const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap copy-clear tail and extend keep masked parity" {
    const nbits = bitmap.bits_per_long + 5;
    const size = nbits + bitmap.bits_per_long;
    const src = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };

    var copied = [_]bitmap.Word{ 0, 0 };
    bitmap.copyClearTail(&copied, &src, nbits);
    try std.testing.expect(bitmap.full(&copied, nbits));

    var expected = [_]bitmap.Word{ 0, 0 };
    bitmap.fill(&expected, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &expected, &copied);

    var inverse = [_]bitmap.Word{ 0, 0 };
    bitmap.complement(&inverse, &copied, nbits);
    try std.testing.expect(bitmap.empty(&inverse, nbits));

    var overlap = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    try std.testing.expect(!bitmap.andBits(&overlap, &copied, &inverse, nbits));
    try std.testing.expect(bitmap.empty(&overlap, nbits));

    var extended = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
    };
    bitmap.copyAndExtend(&extended, &copied, nbits, size);
    try std.testing.expectEqual(@as(usize, nbits), bitmap.weight(&extended, size));
    try std.testing.expect(bitmap.full(extended[0..2], nbits));
    try std.testing.expect(bitmap.empty(extended[2..3], bitmap.bits_per_long));
}

test "phase1 helper ports A clump scans and andnot offsets stay byte-aligned" {
    const nbits = find_bit.bits_per_long + 16;
    const map = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 2,
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 9),
    };
    const rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 2,
        @as(find_bit.Word, 1) << 0,
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_0100), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&clump, &map, nbits, 8));
    try std.testing.expectEqual(@as(u8, 0b0000_0001), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.findNextClump8(&clump, &map, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(u8, 0b0000_0010), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 9), find_bit.findFirstAndNotBit(&map, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 9), find_bit.findNextAndNotBit(&map, &rhs, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&map, &rhs, nbits, find_bit.bits_per_long + 10));
}

test "phase1 helper ports A string trimming replacement and suffix checks stay C-string aware" {
    try std.testing.expectEqualStrings("alpha", string.skipSpaces(" \t alpha"));

    var trim_buf = [_]u8{ ' ', 'a', ' ', 'b', ' ', ' ', 0, 'x' };
    const trimmed = string.strim(&trim_buf);
    try std.testing.expectEqualStrings("a b", trimmed);

    var replace_buf = [_]u8{ 'a', '-', 'b', '-', 0, 'x' };
    try std.testing.expectEqual(@as(usize, 4), string.strreplace(&replace_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 'b', '_', 0 }, replace_buf[0..5]);

    try std.testing.expectEqual(@as(?usize, 2), string.memchrInv("  x", ' '));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv("    ", ' '));
    try std.testing.expect(string.strEndsWith(&[_]u8{ 'o', 'k', 0, 'x' }, "ok"));
    try std.testing.expect(!string.strEndsWith("okay", "kayz"));
}

test "phase1 helper ports A cached insert and replacement keep leftmost stable" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const cmp_node = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const cmp_key = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var leftmost = Entry{ .key = 5, .serial = 0 };
    var root_entry = Entry{ .key = 10, .serial = 1 };
    var rightmost = Entry{ .key = 15, .serial = 2 };
    var duplicate = Entry{ .key = 10, .serial = 3 };
    var replacement = Entry{ .key = 15, .serial = 4 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&root_entry.node, &root, cmp_node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&leftmost.node, &root, cmp_node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&rightmost.node, &root, cmp_node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    const existing = rbtree.findAddCached(&duplicate.node, &root, cmp_node) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), existing);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&rightmost.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    const wanted = @as(i32, 15);
    const found = rbtree.find(&wanted, &root.root, cmp_key) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &replacement.node), found);
}
