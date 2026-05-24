const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 bitmap replace and weighted-or aliases clamp masked tails" {
    const nbits = bitmap.bits_per_long + 6;
    const old = [_]bitmap.Word{
        0b101001,
        (@as(bitmap.Word, 1) << 0) |
            (@as(bitmap.Word, 1) << 2) |
            (@as(bitmap.Word, 1) << 5) |
            (@as(bitmap.Word, 1) << 9),
    };
    const new = [_]bitmap.Word{
        0b010110,
        (@as(bitmap.Word, 1) << 1) |
            (@as(bitmap.Word, 1) << 2) |
            (@as(bitmap.Word, 1) << 4) |
            (@as(bitmap.Word, 1) << 7),
    };
    const mask = [_]bitmap.Word{
        0b001111,
        (@as(bitmap.Word, 1) << 1) |
            (@as(bitmap.Word, 1) << 4) |
            (@as(bitmap.Word, 1) << 5) |
            (@as(bitmap.Word, 1) << 8),
    };

    var direct_replace = [_]bitmap.Word{ 0, 0 };
    var alias_replace = [_]bitmap.Word{ 0, 0 };
    bitmap.replace(&direct_replace, &old, &new, &mask, nbits);
    bitmap.bitmap_replace(&alias_replace, &old, &new, &mask, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_replace, &alias_replace);
    try std.testing.expectEqual(
        ((old[1] & ~mask[1]) | (new[1] & mask[1])) & bitmap.lastWordMask(nbits),
        direct_replace[1],
    );
    try std.testing.expect(bitmap.bitmap_intersects(&direct_replace, &new, nbits));

    var direct_or = [_]bitmap.Word{ 0, 0 };
    var alias_or = [_]bitmap.Word{ 0, 0 };
    const direct_weight = bitmap.weightedOr(&direct_or, &direct_replace, &new, nbits);
    const alias_weight = bitmap.bitmap_weighted_or(&alias_or, &alias_replace, &new, nbits);
    try std.testing.expectEqual(direct_weight, alias_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_or, &alias_or);
    try std.testing.expectEqual(bitmap.weight(&direct_or, nbits), alias_weight);
    try std.testing.expect(bitmap.bitmap_subset(&direct_replace, &direct_or, nbits));
}

test "lane06 find_bit zero and clump helpers keep cross-word windows aligned" {
    const nbits = find_bit.bits_per_long + 10;
    const zero_map = [_]find_bit.Word{
        ~(@as(find_bit.Word, 1) << (find_bit.bits_per_long - 2)),
        ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 9)),
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long - 2),
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long - 3),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long),
    );

    const clump_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 0) |
            (@as(find_bit.Word, 1) << 3) |
            (@as(find_bit.Word, 1) << 9),
    };
    var direct_clump: u8 = 0;
    var alias_clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findNextClump8(&direct_clump, &clump_map, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.find_next_clump8(&alias_clump, &clump_map, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(@as(u8, 0b0000_1001), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 8),
        find_bit.findNextClump8(&direct_clump, &clump_map, nbits, find_bit.bits_per_long + 8),
    );
    try std.testing.expectEqual(@as(u8, 0b0000_0010), direct_clump);
}

test "lane06 string sysfs and search helpers keep c-string boundaries aligned" {
    const sysfs_entries = [_][]const u8{ "alpha\n", "beta", "gamma\n" };
    try std.testing.expect(string.sysfsStreq("beta", "beta\n"));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfsMatchString(&sysfs_entries, "gamma"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&[_][]const u8{ "red", "green", "blue" }, "green"));
    try std.testing.expect(string.strstarts("prefix-tail", "prefix"));
    try std.testing.expect(string.str_ends_with("prefix-tail", "tail"));
    try std.testing.expectEqual(@as(?usize, 3), string.memchrInv(&[_]u8{ 0, 0, 0, 5, 0 }, 0));
}

test "lane06 rbtree cached erase helpers keep leftmost tracking in sync" {
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

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };

    var root = rbtree.RootCached.init();
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.addCached(&entries[0].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.addCached(&entries[1].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[2].node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&entries[3].node, &root, less));

    const first_cached = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    const alias_first_cached = rbtree.rb_first_cached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, first_cached), alias_first_cached);
    try std.testing.expectEqual(@as(i32, 5), (@as(*const Entry, @fieldParentPtr("node", first_cached))).key);

    const next_leftmost = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    const next_leftmost_entry: *const Entry = @fieldParentPtr("node", next_leftmost);
    try std.testing.expectEqual(@as(i32, 10), next_leftmost_entry.key);
    try std.testing.expectEqual(@as(?*rbtree.Node, next_leftmost), rbtree.firstCached(&root));

    const alias_next_leftmost = rbtree.rb_erase_cached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    const alias_next_entry: *const Entry = @fieldParentPtr("node", alias_next_leftmost);
    try std.testing.expectEqual(@as(i32, 10), alias_next_entry.key);
    try std.testing.expectEqual(@as(usize, 2), alias_next_entry.serial);
    try std.testing.expectEqual(@as(?*rbtree.Node, alias_next_leftmost), rbtree.rb_first_cached(&root));

    rbtree.rb_erase_init_cached(&entries[2].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));
    const final_leftmost = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    const final_entry: *const Entry = @fieldParentPtr("node", final_leftmost);
    try std.testing.expectEqual(@as(i32, 15), final_entry.key);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.next(final_leftmost));
}
