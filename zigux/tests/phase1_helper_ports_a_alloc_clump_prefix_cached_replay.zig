const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string_helpers = @import("string_helpers");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap allocation, tail formatting, and reset semantics aligned" {
    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 3;

    try std.testing.expectEqual(@as(?[]bitmap.Word, null), try bitmap.bitmap_alloc(allocator, 0));
    try std.testing.expectEqual(@as(?[]bitmap.Word, null), try bitmap.bitmap_zalloc(allocator, 0));

    var zeroed = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expect(zeroed != null);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }

    bitmap.bitmap_set(zeroed.?, 1, 2);
    bitmap.bitmap_set(zeroed.?, bitmap.bits_per_long + 1, 1);
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(zeroed.?, nbits));

    var rendered: [64]u8 = undefined;
    const len = bitmap.bitmap_scnprintf(zeroed.?, nbits, &rendered);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "1-2,{d}",
        .{bitmap.bits_per_long + 1},
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..len]);

    bitmap.bitmap_zero(zeroed.?, nbits);
    try std.testing.expect(bitmap.bitmap_empty(zeroed.?, nbits));

    bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expectEqual(@as(?[]bitmap.Word, null), zeroed);
}

test "lane06 replay keeps clump windows and shared tail scans aligned" {
    const nbits = find_bit.bits_per_long + 8;
    const bitmap_words = [_]find_bit.Word{
        (@as(find_bit.Word, 0b0011_0000) << 8),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 7),
    };
    const andnot_rhs = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << 7,
    };

    var clump: u8 = 0xaa;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstClump8(&clump, &bitmap_words, nbits));
    try std.testing.expectEqual(@as(u8, 0b0011_0000), clump);

    clump = 0xbb;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &bitmap_words, nbits, 13));
    try std.testing.expectEqual(@as(u8, 0b0011_0000), clump);

    clump = 0xbb;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&clump, &bitmap_words, nbits, 16));
    try std.testing.expectEqual(@as(u8, 0b1000_0010), clump);

    clump = 0xcc;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &bitmap_words, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0xcc), clump);

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findNextAndNotBit(&bitmap_words, &andnot_rhs, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextAndNotBit(&bitmap_words, &andnot_rhs, nbits, find_bit.bits_per_long + 2),
    );
}

test "lane06 replay keeps prefix, bounded NUL, and newline-aware matches stable" {
    try std.testing.expectEqual(
        @as(usize, 4),
        string_helpers.strHasPrefix(&[_]u8{ 'l', 'a', 'n', 'e', 0, 'x' }, "lane"),
    );
    try std.testing.expectEqual(
        @as(?usize, 2),
        string_helpers.strnchr(&[_]u8{ 'o', 'k', '!', 0, 'x' }, 4, '!'),
    );
    try std.testing.expectEqual(
        @as(?usize, null),
        string_helpers.strnchr(&[_]u8{ 'o', 'k', 0, '!', 'x' }, 5, '!'),
    );

    const sysfs_values = [_][]const u8{ "off", "lane\n", "lane", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.sysfsMatchString(sysfs_values[0..], "lane"));

    const exact_values = [_][]const u8{
        &[_]u8{ 'l', 'a', 'n', 'e', 0, 'x' },
        "lane-helper",
        "other",
    };
    try std.testing.expectEqual(@as(?usize, 0), string_helpers.matchString(exact_values[0..], "lane"));
}

test "lane06 replay keeps cached leftmost updates and reverse traversal aligned" {
    const Entry = struct {
        key: i32,
        serial: i32,
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

    var entries = [_]Entry{
        .{ .key = 5, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var replacement = Entry{ .key = 15, .serial = 9 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&entries[2].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    const last_node = rbtree.last(&root.root) orelse return error.TestUnexpectedResult;
    const previous = rbtree.rb_prev(last_node) orelse return error.TestUnexpectedResult;
    const previous_entry: *const Entry = @fieldParentPtr("node", previous);
    try std.testing.expectEqual(@as(i32, 10), previous_entry.key);

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
}
