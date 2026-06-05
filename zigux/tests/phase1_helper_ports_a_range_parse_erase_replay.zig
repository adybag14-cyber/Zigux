const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "bitmap formatted ranges feed find-bit tail scans" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 9;
    var map = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&map, 2, 3);
    bitmap.bitmap_set(&map, bitmap.bits_per_long + 4, 2);
    bitmap.bitmap_set(&map, bitmap.bits_per_long + 8, 1);

    var rendered: [48]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(&map, nbits, &rendered);

    var expected: [48]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "2-4,{d}-{d},{d}",
        .{ bitmap.bits_per_long + 4, bitmap.bits_per_long + 5, bitmap.bits_per_long + 8 },
    );

    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);
    try std.testing.expectEqual(@as(usize, 2), find_bit.find_first_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 4), find_bit.find_next_bit(&map, nbits, 5));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 8), find_bit.find_last_bit(&map, nbits));

    bitmap.bitmap_clear(&map, bitmap.bits_per_long + 4, 5);
    try std.testing.expectEqual(@as(usize, 4), find_bit.find_last_bit(&map, nbits));
}

test "string parse and bounded searches preserve C-string boundaries" {
    const parsed = string.memparse("15K:tail");
    try std.testing.expectEqual(@as(u64, 15 << 10), parsed.value);
    try std.testing.expectEqualStrings(":tail", parsed.rest);

    const c_string = [_]u8{ 'r', 'a', 'n', 'g', 'e', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&c_string, c_string.len, 'n'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&c_string, c_string.len, 'x'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&c_string, 3, 'g'));

    var token = [_]u8{ ' ', 'r', 'a', 'n', 'g', 'e', ' ', 0, 'x' };
    const trimmed = string.strim(&token);
    try std.testing.expectEqualStrings("range", trimmed);
    try std.testing.expect(string.sysfs_streq("range\n", trimmed));
}

test "rbtree erase and reseed keep traversal order stable" {
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
        .{ .key = 3 },
        .{ .key = 11 },
        .{ .key = 5 },
    };
    var replacement = Entry{ .key = 8 };
    var reseed = Entry{ .key = 1 };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    rbtree.eraseInit(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    rbtree.replaceNode(&entries[0].node, &replacement.node, &root);
    rbtree.add(&reseed.node, &root, less);

    var order: [4]i32 = undefined;
    var count: usize = 0;
    var cursor = rbtree.first(&root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 5, 8, 11 }, order[0..count]);
}
