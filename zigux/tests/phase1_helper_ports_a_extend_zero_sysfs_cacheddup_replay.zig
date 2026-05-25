const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 bitmap copy-and-extend aliases clamp partial tails and zero-fill the extension" {
    const count = bitmap.bits_per_long + 5;
    const size = bitmap.bits_per_long * 3;
    const src = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << (bitmap.bits_per_long - 1)) | (@as(bitmap.Word, 1) << 1),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
        ~@as(bitmap.Word, 0),
    };

    var direct = [_]bitmap.Word{ 0xaa55, 0xaa55, 0xaa55 };
    var alias = [_]bitmap.Word{ 0xaa55, 0xaa55, 0xaa55 };
    bitmap.copyAndExtend(&direct, src[0..2], count, size);
    bitmap.bitmap_copy_and_extend(&alias, src[0..2], count, size);

    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(src[0], direct[0]);
    try std.testing.expectEqual(src[1] & bitmap.lastWordMask(count), direct[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct[2]);
    try std.testing.expect(bitmap.bitmap_equal(&direct, &alias, size));
}

test "lane06 find_bit zero aliases keep exact-boundary and tail windows aligned" {
    const nbits = find_bit.bits_per_long + 6;
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        (@as(find_bit.Word, 1) << 0) |
            (@as(find_bit.Word, 1) << 2) |
            (@as(find_bit.Word, 1) << 3) |
            (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findFirstZeroBit(&zero_map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.find_first_zero_bit(&zero_map, nbits));
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 5),
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 5),
        find_bit.find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_zero_bit(&zero_map, nbits, nbits));
}

test "lane06 string sysfs and parse aliases preserve newline-aware first matches" {
    const sysfs_entries = [_][]const u8{ "auto\n", "manual", "safe\n" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&sysfs_entries, "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(&sysfs_entries, "auto"));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfsMatchString(&sysfs_entries, "safe\n"));

    const plain_entries = [_][]const u8{ "amber", "blue", "cyan" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&plain_entries, "blue"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&plain_entries, "blue"));

    const parsed = string.memparse("-2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), parsed.value);
    try std.testing.expectEqualStrings("tail", parsed.rest);
    try std.testing.expect(string.strstarts("phase1-lane06", "phase1"));
    try std.testing.expect(string.str_ends_with("phase1-lane06", "lane06"));
}

test "lane06 rbtree cached duplicate and leftmost aliases keep the same root state" {
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

    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var primary_duplicate = Entry{ .key = 10, .serial = 3 };
    var alias_duplicate = Entry{ .key = 10, .serial = 3 };
    var primary_new_leftmost = Entry{ .key = 3, .serial = 4 };
    var alias_new_leftmost = Entry{ .key = 3, .serial = 4 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, less);
    }

    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_root, cmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &primary_entries[0].node), primary_existing);
    try std.testing.expectEqual(@as(*rbtree.Node, &alias_entries[0].node), alias_existing);
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_entries[1].node), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entries[1].node), rbtree.rb_first_cached(&alias_root));

    const primary_promoted = rbtree.eraseCached(&primary_entries[1].node, &primary_root) orelse return error.TestUnexpectedResult;
    const alias_promoted = rbtree.rb_erase_cached(&alias_entries[1].node, &alias_root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &primary_entries[0].node), primary_promoted);
    try std.testing.expectEqual(@as(*rbtree.Node, &alias_entries[0].node), alias_promoted);

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_new_leftmost.node), rbtree.addCached(&primary_new_leftmost.node, &primary_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_new_leftmost.node), rbtree.rb_add_cached(&alias_new_leftmost.node, &alias_root, less));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.rb_first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
}
