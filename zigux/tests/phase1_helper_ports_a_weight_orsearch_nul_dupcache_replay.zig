const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps weighted bitmap aliases clamped to the declared tail window" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 6;
    const lhs = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
    };
    const rhs = [_]Word{
        0,
        (@as(Word, 1) << 4) | (@as(Word, 1) << 5) | (@as(Word, 1) << 10),
    };

    var direct_or = [_]Word{ 0, 0 };
    var alias_or = [_]Word{ 0, 0 };
    const direct_or_weight = bitmap.weightedOr(&direct_or, &lhs, &rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);

    try std.testing.expectEqual(@as(usize, 3), direct_or_weight);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try std.testing.expectEqualSlices(Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&direct_or, nbits));

    var direct_xor = [_]Word{ 0, 0 };
    var alias_xor = [_]Word{ 0, 0 };
    const direct_xor_weight = bitmap.weightedXor(&direct_xor, &lhs, &rhs, nbits);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&alias_xor, &lhs, &rhs, nbits);

    try std.testing.expectEqual(@as(usize, 2), direct_xor_weight);
    try std.testing.expectEqual(direct_xor_weight, alias_xor_weight);
    try std.testing.expectEqualSlices(Word, &direct_xor, &alias_xor);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_xor, nbits));
}

test "lane06 replay keeps shared-set scans inside the caller-selected tail window" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 6;
    const lhs = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
    };
    const rhs = [_]Word{
        0,
        (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | (@as(Word, 1) << 11),
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findFirstAndBit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.find_next_and_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 6),
    );
}

test "lane06 replay keeps boolean parsing and dirty-byte lookups aligned" {
    try std.testing.expect(try string.strtobool("On"));
    try std.testing.expect(!(try string.strtobool("off")));

    var padded = [_]u8{0} ** 32;
    padded[19] = 1;
    try std.testing.expectEqual(@as(?usize, 19), string.memchrInv(padded[0..], 0));
    try std.testing.expectEqual(@as(?usize, 19), string.memchr_inv(padded[0..], 0));
}

test "lane06 replay keeps cached duplicate inserts and replacement order stable" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var duplicate = Entry{ .key = 10, .serial = 3 };
    var replacement = Entry{ .key = 15, .serial = 4 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    const existing = rbtree.findAddCached(&duplicate.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), existing);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&entries[2].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.last(&root.root));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15 }, order[0..count]);
}
