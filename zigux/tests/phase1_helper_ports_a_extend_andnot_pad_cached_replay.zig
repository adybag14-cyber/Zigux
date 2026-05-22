const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string_helpers = @import("string_helpers");
const rbtree = @import("rbtree");

test "lane06 replay keeps copy-and-extend sparse beyond the copied tail" {
    const count = bitmap.bits_per_long + 3;
    const size = (bitmap.bits_per_long * 2) + 5;
    const src = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << (bitmap.bits_per_long - 1)),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 9),
    };
    var dst = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
    };
    var buffer: [64]u8 = undefined;
    var expected: [48]u8 = undefined;

    bitmap.bitmap_copy_and_extend(&dst, &src, count, size);

    try std.testing.expectEqual(src[0], dst[0]);
    try std.testing.expectEqual(
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 2),
        dst[1],
    );
    try std.testing.expectEqual(@as(bitmap.Word, 0), dst[2]);

    const rendered_len = bitmap.bitmap_scnprintf(&dst, size, &buffer);
    const rendered = buffer[0..rendered_len];
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "0,{d},{d}-{d}",
        .{
            bitmap.bits_per_long - 1,
            bitmap.bits_per_long + 1,
            bitmap.bits_per_long + 2,
        },
    );
    try std.testing.expectEqualStrings(expected_text, rendered);
}

test "lane06 replay keeps andnot scans pinned to in-range tail bits" {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 7),
        (@as(find_bit.Word, 1) << 0) |
            (@as(find_bit.Word, 1) << 2) |
            (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 8),
    };
    const rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 4),
    };

    try std.testing.expectEqual(
        @as(usize, 7),
        find_bit.find_first_andnot_bit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 2),
        find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, 8),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 3),
    );
}

test "lane06 replay keeps padded C-string copies and bounded scans aligned" {
    var buffer = [_]u8{0xaa} ** 8;
    const source = [_]u8{ 'o', 'k', 0, 'x', 'y' };

    try std.testing.expectEqual(@as(isize, 2), string_helpers.strscpy_pad(&buffer, &source));
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 'o', 'k', 0, 0, 0, 0, 0, 0 },
        buffer[0..],
    );
    try std.testing.expectEqual(@as(?usize, 2), string_helpers.strnchr(buffer[0..], buffer.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string_helpers.strnchr(&source, source.len, 'x'));

    const sysfs_values = [_][]const u8{ "off", "ok\n", "ok", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.sysfs_match_string(sysfs_values[0..], "ok"));
}

test "lane06 replay keeps cached duplicate rejection and leftmost handoff stable" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

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
        .{ .key = 5 },
        .{ .key = 10 },
        .{ .key = 15 },
    };
    var duplicate = Entry{ .key = 5 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&entry.node, &root, cmp));
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_first_cached(&root));

    const existing = rbtree.rb_find_add_cached(&duplicate.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), existing);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), duplicate.node.parent);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), duplicate.node.left);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), duplicate.node.right);

    rbtree.rb_erase_init_cached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));
}
