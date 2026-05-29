const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "bitmap single-word aliases keep counted windows and rendered ranges aligned" {
    var map = [_]bitmap.Word{0};
    bitmap.bitmap_set(&map, 2, 5);

    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(&map, 13));
    try std.testing.expect(!bitmap.bitmap_empty(&map, 13));

    var rendered = [_]u8{0xaa} ** 16;
    const rendered_len = bitmap.bitmap_scnprintf(&map, 13, &rendered);
    try std.testing.expectEqualStrings("2-6", rendered[0..rendered_len]);
    try std.testing.expectEqual(@as(u8, 0), rendered[rendered_len]);

    bitmap.bitmap_clear(&map, 4, 2);
    map[0] |= @as(bitmap.Word, 1) << 15;

    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&map, 13));
    try std.testing.expect(bitmap.bitmap_subset(&map, &[_]bitmap.Word{map[0] | (@as(bitmap.Word, 1) << 7)}, 13));
    try std.testing.expect(!bitmap.bitmap_full(&map, 13));
}

test "find-bit single-word scans clamp starts and tail noise across aliases" {
    const nbits = 13;
    const map = [_]find_bit.Word{(@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 5) | (@as(find_bit.Word, 1) << 12) | (@as(find_bit.Word, 1) << 15)};

    try std.testing.expectEqual(@as(usize, 5), find_bit.find_next_bit(&map, nbits, 2));
    try std.testing.expectEqual(@as(usize, 12), find_bit.find_last_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_bit(&map, nbits, nbits));

    const full_except = [_]find_bit.Word{~(@as(find_bit.Word, 1) << 4)};
    try std.testing.expectEqual(@as(usize, 4), find_bit.find_next_zero_bit(&full_except, nbits, 0));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_zero_bit(&full_except, nbits, 5));

    const andnot_lhs = [_]find_bit.Word{(@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 8) | (@as(find_bit.Word, 1) << 14)};
    const andnot_rhs = [_]find_bit.Word{@as(find_bit.Word, 1) << 3};
    try std.testing.expectEqual(@as(usize, 8), find_bit.find_next_andnot_bit(&andnot_lhs, &andnot_rhs, 10, 4));
    try std.testing.expectEqual(@as(usize, 10), find_bit._find_next_andnot_bit(&andnot_lhs, &andnot_rhs, 10, 9));
}

test "string counted character lookup preserves NUL and count boundaries" {
    const cstr = [_]u8{ 'a', 'b', 0, 'b', 'c' };

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&cstr, cstr.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, 1, 'b'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&cstr, cstr.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, 2, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, 'c'));
}

test "rbtree cached erase-init and replacement keep leftmost traversal stable" {
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
    };
    var replacement = Entry{ .key = 12 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_add_cached(&entries[0].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_add_cached(&entries[1].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[2].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.rb_add_cached(&entries[3].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.rb_first_cached(&root));

    rbtree.eraseInitCached(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));

    rbtree.rb_replace_node_cached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_first(&root.root));

    var count: usize = 0;
    var cursor = rbtree.rb_first_postorder(&root.root);
    while (cursor) |node| : (cursor = rbtree.rb_next_postorder(node)) {
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), count);
}
