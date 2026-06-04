const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap aliases roundtrip through find-bit scans and range rendering" {
    const nbits = bits_per_long + 9;
    var map = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&map, bits_per_long - 1, 3);
    bitmap.bitmap_set(&map, bits_per_long + 7, 1);
    bitmap.bitmap_clear(&map, bits_per_long, 1);

    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&map, nbits));
    try std.testing.expectEqual(bits_per_long - 1, find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(bits_per_long + 1, find_bit.findNextBit(&map, nbits, bits_per_long));
    try std.testing.expectEqual(bits_per_long + 7, find_bit.findLastBit(&map, nbits));

    var rendered: [64]u8 = undefined;
    const len = bitmap.bitmap_scnprintf(&map, nbits, &rendered);

    var expected: [64]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d},{d},{d}",
        .{ bits_per_long - 1, bits_per_long + 1, bits_per_long + 7 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..len]);
}

test "string in-place aliases feed stable prefix checks after mutation" {
    var source = [_]u8{ '\t', ' ', 'k', 'e', 'r', ' ', 'n', 'e', 'l', ' ', 0, 'x' };

    const trimmed = string.trimSpaces(source[0..]);
    try std.testing.expectEqualStrings("ker nel", trimmed);

    const compacted = string.removeSpaces(trimmed);
    try std.testing.expectEqualStrings("kernel", compacted);
    try std.testing.expectEqual(@as(usize, 6), string.strreplace(compacted, 'e', 'E'));
    try std.testing.expectEqualStrings("kErnEl", compacted);
    try std.testing.expectEqual(@as(usize, 2), string.strHasPrefix(compacted, "kE"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(compacted, "ke"));
}

test "rbtree cached aliases keep duplicate match iteration stable after leftmost changes" {
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

    const cmpKey = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 3, .serial = 3 },
        .{ .key = 10, .serial = 4 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.firstCached(&root));
    rbtree.eraseInitCached(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    const duplicate_key = @as(i32, 10);
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, cmpKey);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
