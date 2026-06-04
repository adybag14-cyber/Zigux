const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "bitmap allocation reseed feeds find-bit tail scans" {
    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 9;

    var allocated: ?[]bitmap.Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &allocated);

    const map = allocated.?;
    try std.testing.expect(bitmap.bitmap_empty(map, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_first_bit(map, nbits));

    bitmap.bitmap_set(map, bitmap.bits_per_long - 1, 3);
    bitmap.bitmap_set(map, bitmap.bits_per_long + 8, 1);

    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long - 1), find_bit.find_first_bit(map, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), find_bit.find_next_bit(map, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 8), find_bit.find_last_bit(map, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long - 8), find_bit.find_next_clump8(&clump, map, nbits, bitmap.bits_per_long - 1));
    try std.testing.expect((clump & 0b1000_0000) != 0);

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(map, nbits, &rendered);
    var expected: [64]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{ bitmap.bits_per_long - 1, bitmap.bits_per_long + 1, bitmap.bits_per_long + 8 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);

    bitmap.bitmap_free(allocator, &allocated);
    try std.testing.expect(allocated == null);
}

test "string bounded cleanup preserves token and tail authority" {
    var token = [_]u8{ ' ', 'k', 'e', 'r', 'n', 'e', 'l', ' ', 0, 'x' };
    const trimmed = string.strim(token[0..]);
    try std.testing.expectEqualStrings("kernel", trimmed);
    try std.testing.expect(string.strstarts(trimmed, "ker"));
    try std.testing.expect(string.strEndsWith(trimmed, "nel"));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(trimmed, trimmed.len, 'z'));

    var mutable = [_]u8{ 'a', ' ', 'b', ' ', 'c', 0, 'd' };
    const compacted = string.remove_spaces(mutable[0..]);
    try std.testing.expectEqualStrings("abc", compacted);
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(compacted, 'b', 'B'));
    try std.testing.expectEqualStrings("aBc", compacted);

    const options = [_][]const u8{ "manual", "auto\n", "off" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(options[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(options[0..], "auto"));
}

test "rbtree cached reseed keeps traversal and leftmost aligned" {
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
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    entries[1].key = 1;
    _ = rbtree.addCached(&entries[1].node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 10, 15 }, order[0..count]);
}
