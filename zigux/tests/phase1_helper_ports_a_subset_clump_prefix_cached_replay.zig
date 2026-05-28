const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

fn expectWordSlice(actual: []const bitmap.Word, expected: []const u64) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (actual, expected) |value, expected_value| {
        try std.testing.expectEqual(@as(bitmap.Word, @intCast(expected_value)), value);
    }
}

test "lane06 bitmap subset aliases keep masked tails and clump scans clamp tail windows" {
    const nbits = bitmap.bits_per_long + 5;

    const subset_lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };
    const subset_rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };
    try std.testing.expect(bitmap.bitmap_subset(&subset_lhs, &subset_rhs, nbits));
    try std.testing.expect(bitmap.__bitmap_subset(&subset_lhs, &subset_rhs, nbits));

    const unequal_rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 9) };
    try std.testing.expect(!bitmap.bitmap_equal(&subset_lhs, &unequal_rhs, nbits));
    try std.testing.expect(!bitmap.__bitmap_equal(&subset_lhs, &unequal_rhs, nbits));

    const src = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };
    var complement_dst = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_complement(&complement_dst, &src, nbits);
    try expectWordSlice(&complement_dst, &[_]u64{ ~@as(u64, 0), 0x15 });
    bitmap.__bitmap_complement(&complement_dst, &src, nbits);
    try expectWordSlice(&complement_dst, &[_]u64{ ~@as(u64, 0), 0x15 });

    const clump_map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &clump_map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&clump, &clump_map, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);
    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &clump_map, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "lane06 string prefix pad and count helpers keep c-string boundaries" {
    var padded = [_]u8{ 'h', 'i', 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(&padded, "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, &padded);

    var embedded = [_]u8{ 'x', 'y', 'z', 'w', 'q', 'r' };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&embedded, "ok\x00ignored"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &embedded);

    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix("prefix-tail", "pre"));
    try std.testing.expect(string.strstarts("prefix-tail", "prefix"));
    try std.testing.expect(string.str_ends_with("prefix-tail", "tail"));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr("ab-cd\x00ef", 7, '-'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("ab\x00-cd", 6, '-'));
}

test "lane06 rbtree cached aliases preserve leftmost through duplicate and replacement paths" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
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

    var first_entry = Entry{ .key = 10, .serial = 0 };
    var leftmost_entry = Entry{ .key = 5, .serial = 1 };
    var right_entry = Entry{ .key = 15, .serial = 2 };
    var duplicate = Entry{ .key = 10, .serial = 3 };
    var replacement = Entry{ .key = 10, .serial = 4 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.rb_add_cached(&first_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&leftmost_entry.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&right_entry.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.rb_first_cached(&root));

    const existing = rbtree.rb_find_add_cached(&duplicate.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &first_entry.node), existing);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.rb_first_cached(&root));

    rbtree.rb_replace_node_cached(&first_entry.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.rb_first_cached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_erase_cached(&right_entry.node, &root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.rb_first_cached(&root));

    const promoted = rbtree.rb_erase_cached(&leftmost_entry.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &replacement.node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_first_cached(&root));
}
