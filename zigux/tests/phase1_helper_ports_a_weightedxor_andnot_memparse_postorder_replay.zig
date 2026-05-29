const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;

test "bitmap weighted xor and find_bit andnot clamp declared tail bits" {
    const nbits = bitmap.bits_per_long + 9;
    const valid_tail_bit = bitmap.bits_per_long + 7;
    const noisy_tail_bit = bitmap.bits_per_long + 12;

    var lhs = [_]Word{ 0, 0 };
    var rhs = [_]Word{ 0, 0 };
    var dst = [_]Word{ 0, 0 };

    lhs[0] = (@as(Word, 1) << 2) | (@as(Word, 1) << 4);
    rhs[0] = (@as(Word, 1) << 4) | (@as(Word, 1) << 5);
    lhs[1] = (@as(Word, 1) << (valid_tail_bit - bitmap.bits_per_long)) |
        (@as(Word, 1) << (noisy_tail_bit - bitmap.bits_per_long));
    rhs[1] = @as(Word, 1) << (valid_tail_bit - bitmap.bits_per_long);

    try std.testing.expectEqual(@as(usize, 2), bitmap.weightedXor(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&dst, nbits));
    try std.testing.expectEqual(noisy_tail_bit, find_bit.findLastBit(&dst, noisy_tail_bit + 1));
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, valid_tail_bit + 1));

    lhs[1] |= @as(Word, 1) << 6;
    try std.testing.expectEqual(valid_tail_bit - 1, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, valid_tail_bit));
}

test "string memparse keeps signed suffix rests and saturation boundaries" {
    const negative = string.memparse("-3Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -3072))), negative.value);
    try std.testing.expectEqualStrings("tail", negative.rest);

    const positive = string.memparse("+7Mmore");
    try std.testing.expectEqual(@as(u64, 7 << 20), positive.value);
    try std.testing.expectEqualStrings("more", positive.rest);

    const saturated = string.memparse("+9223372036854775808Kafter");
    try std.testing.expectEqual(@as(u64, std.math.maxInt(i64)), saturated.value);
    try std.testing.expectEqualStrings("after", saturated.rest);
}

test "rbtree cached mutations still permit complete postorder walks" {
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

    var entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 12 },
        .{ .key = 2 },
        .{ .key = 6 },
        .{ .key = 10 },
        .{ .key = 14 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(&entries[3].node, rbtree.firstCached(&root).?);
    rbtree.eraseInitCached(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try std.testing.expectEqual(&entries[1].node, rbtree.firstCached(&root).?);

    var seen = [_]bool{false} ** entries.len;
    var count: usize = 0;
    var current = rbtree.firstPostorder(&root.root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        for (&entries, 0..) |*entry, idx| {
            if (node == &entry.node) {
                try std.testing.expect(!seen[idx]);
                seen[idx] = true;
                count += 1;
                break;
            }
        }
    }

    try std.testing.expectEqual(@as(usize, entries.len - 1), count);
    try std.testing.expect(!seen[3]);
}
