const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn keyOf(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

test "weighted bitmap windows feed find-bit scans and string matching" {
    const nbits = bitmap.bits_per_long + 6;
    const tail_base = bitmap.bits_per_long;
    const out_of_range_lhs = @as(Word, 1) << 9;
    const out_of_range_rhs = @as(Word, 1) << 11;
    const lhs = [_]Word{
        @as(Word, 1) << 2,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | out_of_range_lhs,
    };
    const rhs = [_]Word{
        @as(Word, 1) << 5,
        (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | out_of_range_rhs,
    };

    var union_map = [_]Word{ 0, 0 };
    const union_weight = bitmap.weightedOr(&union_map, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 5), union_weight);
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&union_map, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextBit(&union_map, nbits, 3));
    try std.testing.expectEqual(@as(usize, tail_base + 1), find_bit.findNextBit(&union_map, nbits, tail_base));
    try std.testing.expectEqual(@as(usize, tail_base + 4), find_bit.findLastBit(&union_map, nbits));

    var xor_map = [_]Word{ 0, 0 };
    const xor_weight = bitmap.weightedXor(&xor_map, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 4), xor_weight);
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&xor_map, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextBit(&xor_map, nbits, 3));
    try std.testing.expectEqual(@as(usize, tail_base + 1), find_bit.findNextBit(&xor_map, nbits, tail_base));
    try std.testing.expectEqual(@as(usize, tail_base + 4), find_bit.findLastBit(&xor_map, nbits));

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&union_map, nbits, &rendered);
    var expected: [64]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "2,5,{d},{d}-{d}",
        .{ tail_base + 1, tail_base + 3, tail_base + 4 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);

    var copied: [64]u8 = @splat(0xaa);
    try std.testing.expectEqual(rendered_len, string.strlcpy(copied[0..], rendered[0..rendered_len]));
    try std.testing.expectEqual(@as(u8, 0), copied[rendered_len]);
    try std.testing.expectEqualStrings(expected_text, copied[0..rendered_len]);

    const haystack = [_][]const u8{ "missing", copied[0 .. rendered_len + 1], "tail\n" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(haystack[0..], expected_text));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfs_match_string(haystack[0..], "tail"));
}

test "rbtree postorder covers bitmap-derived keys before cached reseed" {
    const nbits = bitmap.bits_per_long + 6;
    const tail_base = bitmap.bits_per_long;
    var map = [_]Word{ 0, 0 };
    bitmap.setRange(&map, 1, 2);
    bitmap.setRange(&map, 9, 1);
    bitmap.setRange(&map, tail_base + 2, 2);

    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&map, nbits) },
        .{ .key = find_bit.findNextBit(&map, nbits, 2) },
        .{ .key = find_bit.findNextBit(&map, nbits, 3) },
        .{ .key = find_bit.findNextBit(&map, nbits, tail_base) },
        .{ .key = find_bit.findLastBit(&map, nbits) },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(usize, 1), keyOf(rbtree.first(&root.root).?));
    try std.testing.expectEqual(@as(usize, tail_base + 3), keyOf(rbtree.last(&root.root).?));

    var seen = [_]bool{false} ** entries.len;
    var visited: usize = 0;
    var last_seen: ?*rbtree.Node = null;
    var cursor = rbtree.firstPostorder(&root.root);
    while (cursor) |node| : (cursor = rbtree.nextPostorder(node)) {
        const key = keyOf(node);
        for (&entries, 0..) |*entry, idx| {
            if (entry.key == key) {
                try std.testing.expect(!seen[idx]);
                seen[idx] = true;
                visited += 1;
                break;
            }
        } else {
            return error.TestUnexpectedResult;
        }
        last_seen = node;
    }

    try std.testing.expectEqual(entries.len, visited);
    try std.testing.expectEqual(root.root.node, last_seen);
    try std.testing.expect(rbtree.rb_next_postorder(null) == null);

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    entries[0].key = 0;
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.addCached(&entries[0].node, &root, less));
    try std.testing.expectEqual(@as(usize, 0), keyOf(rbtree.rb_first_cached(&root).?));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
