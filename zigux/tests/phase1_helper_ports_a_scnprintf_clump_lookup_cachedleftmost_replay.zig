const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "phase1 helper ports A bitmap scnprintf and complement stay tail-aware" {
    const nbits = find_bit.bits_per_long + 5;
    const src = [_]find_bit.Word{
        0b1010,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 3) |
            (@as(find_bit.Word, 1) << 9),
    };
    var direct = [_]find_bit.Word{ 0, 0 };
    var alias = [_]find_bit.Word{ 0, 0 };

    bitmap.complement(&direct, &src, nbits);
    bitmap.bitmap_complement(&alias, &src, nbits);
    try std.testing.expectEqualSlices(find_bit.Word, &direct, &alias);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct[1]);
    try std.testing.expect(bitmap.intersects(&direct, &alias, nbits));
    try std.testing.expect(bitmap.subset(&alias, &direct, nbits));

    var range_map = [_]find_bit.Word{ 0, 0 };
    bitmap.setRange(&range_map, find_bit.bits_per_long - 1, 3);
    bitmap.bitmap_set(&range_map, find_bit.bits_per_long + 4, 1);

    var buffer: [64]u8 = undefined;
    const len = bitmap.bitmap_scnprintf(&range_map, nbits, &buffer);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{
            find_bit.bits_per_long - 1,
            find_bit.bits_per_long + 1,
            find_bit.bits_per_long + 4,
        },
    );
    try std.testing.expectEqualStrings(expected_text, buffer[0..len]);
}

test "phase1 helper ports A clump and andnot scans keep partial tails honest" {
    const nbits = find_bit.bits_per_long + 5;
    const clump_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6),
    };
    var clump: u8 = 0;

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findFirstClump8(&clump, &clump_map, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.find_next_clump8(&clump, &clump_map, nbits, find_bit.bits_per_long + 1),
    );
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findLastBit(&clump_map, nbits));

    const lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 3) |
            (@as(find_bit.Word, 1) << 6),
    };
    const rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 1 };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 3),
        find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 4),
    );
}

test "phase1 helper ports A string lookup helpers keep newline and dirty-byte boundaries" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto"));

    const cstring_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(cstring_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(cstring_haystack[0..], "a"));

    var dirty = [_]u8{0} ** 24;
    dirty[13] = 4;
    try std.testing.expectEqual(@as(?usize, 13), string.memchrInv(dirty[0..], 0));
    try std.testing.expectEqual(@as(?usize, 13), string.memchr_inv(dirty[0..], 0));

    const parsed = string.memparse("-16 tail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -16))), parsed.value);
    try std.testing.expectEqualStrings(" tail", parsed.rest);
}

test "phase1 helper ports A cached leftmost aliases stay stable across duplicate and promotion paths" {
    const Entry = struct {
        const Self = @This();

        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Self = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Self = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }

        fn cmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Self = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Self = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    };

    var root_entry = Entry{ .key = 10, .serial = 0 };
    var left_entry = Entry{ .key = 5, .serial = 1 };
    var right_entry = Entry{ .key = 15, .serial = 2 };
    var duplicate_probe = Entry{ .key = 10, .serial = 3 };
    var replacement = Entry{ .key = 15, .serial = 4 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.rb_add_cached(&root_entry.node, &root, Entry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_entry.node), rbtree.rb_add_cached(&left_entry.node, &root, Entry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&right_entry.node, &root, Entry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_entry.node), rbtree.rb_first_cached(&root));

    const existing = rbtree.rb_find_add_cached(&duplicate_probe.node, &root, Entry.cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), existing);
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_entry.node), rbtree.rb_first_cached(&root));

    rbtree.rb_replace_node_cached(&right_entry.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_entry.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_last(&root.root));

    const promoted = rbtree.rb_erase_cached(&left_entry.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(rbtree.rb_first(&root.root), rbtree.rb_first_cached(&root));
}
