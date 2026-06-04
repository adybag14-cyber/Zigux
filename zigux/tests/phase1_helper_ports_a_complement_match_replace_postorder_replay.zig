const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "helper ports A complement masks tail before andnot scans" {
    const nbits = bits_per_long + 9;
    var source = [_]Word{ 0, 0 };
    source[0] |= (@as(Word, 1) << 1) | (@as(Word, 1) << 5);
    source[1] |= (@as(Word, 1) << 0) | (@as(Word, 1) << 8) | (@as(Word, 1) << 12);

    var complement = [_]Word{ 0, ~@as(Word, 0) };
    bitmap.complement(&complement, &source, nbits);

    try std.testing.expectEqual(~source[0], complement[0]);
    try std.testing.expectEqual((bitmap.lastWordMask(nbits) & ~source[1]), complement[1]);
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextBit(&complement, nbits, bits_per_long));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&complement, nbits, bits_per_long + 9));

    var masked = [_]Word{ 0, 0 };
    const had_bits = bitmap.andNotBits(&masked, &source, &complement, nbits);
    try std.testing.expect(had_bits);
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&masked, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 8), find_bit.findLastBit(&masked, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&masked, nbits));
}

test "helper ports A andnot result feeds first and next scans" {
    const nbits = bits_per_long + 7;
    const lhs = [_]Word{
        (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 6) | (@as(Word, 1) << 10),
    };
    const rhs = [_]Word{
        @as(Word, 1) << 4,
        (@as(Word, 1) << 6) | (@as(Word, 1) << 10),
    };

    var dst = [_]Word{ 0, 0 };
    try std.testing.expect(bitmap.bitmap_andnot(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 9), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 10));
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bits_per_long + 2));
    try std.testing.expect(bitmap.equal(&dst, &[_]Word{ @as(Word, 1) << 9, @as(Word, 1) << 1 }, nbits));
}

test "helper ports A string match helpers keep C-string and sysfs boundaries" {
    const haystack = [_][]const u8{
        &[_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'x' },
        "beta\n",
        "gamma",
    };

    try std.testing.expectEqual(@as(?usize, 0), string.matchString(&haystack, "alpha"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&haystack, "beta"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&haystack, "beta"));
    try std.testing.expect(string.strstarts(&[_]u8{ 'a', 'l', 'p', 0, 'x' }, "al"));
}

test "helper ports A cached replacement remains reachable by postorder walk" {
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
        .{ .key = 20 },
        .{ .key = 10 },
        .{ .key = 30 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var replacement = Entry{ .key = 5 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(&entries[3].node, rbtree.firstCached(&root));
    rbtree.replaceNodeCached(&entries[3].node, &replacement.node, &root);
    try std.testing.expectEqual(&replacement.node, rbtree.firstCached(&root));

    var count: usize = 0;
    var key_sum: i32 = 0;
    var saw_replacement = false;
    var saw_victim = false;
    var current = rbtree.firstPostorder(&root.root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        count += 1;
        key_sum += entry.key;
        if (node == &replacement.node) {
            saw_replacement = true;
        }
        if (node == &entries[3].node) {
            saw_victim = true;
        }
    }

    try std.testing.expectEqual(@as(usize, 5), count);
    try std.testing.expectEqual(@as(i32, 80), key_sum);
    try std.testing.expect(saw_replacement);
    try std.testing.expect(!saw_victim);
}
