const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 bitmap complement and weighted tail masks stay aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const src = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 8),
    };

    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };
    bitmap.complement(&direct, &src, nbits);
    bitmap.bitmap_complement(&alias, &src, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct[1]);

    try std.testing.expectEqual(@as(usize, 65), bitmap.weight(&direct, nbits));
    try std.testing.expectEqual(@as(usize, 65), bitmap.bitmap_weight(&alias, nbits));
}

test "lane06 find_bit shared and zero scans stay tail-aware" {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 9),
    };
    const rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 10),
    };
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findFirstAndBit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.find_next_and_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5),
    );

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findFirstZeroBit(&zero_map, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 5),
    );
}

test "lane06 string prefix suffix and newline-aware helpers stay aligned" {
    try std.testing.expectEqual(@as(usize, 5), string.strHasPrefix("kernel", "kerne"));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix("kernel", "kernx"));
    try std.testing.expect(string.strstarts("kernel", "ker"));
    try std.testing.expect(!string.strstarts("kernel", "ern"));
    try std.testing.expect(string.strEndsWith("phase1-lane06", "lane06"));
    try std.testing.expect(!string.strEndsWith("phase1-lane06", "lane07"));

    try std.testing.expect(string.sysfsStreq("mode\n", "mode"));
    try std.testing.expect(string.sysfs_streq("ready", "ready\n"));

    const entries = [_][]const u8{ "amber", "blue", "cyan" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&entries, "blue"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&entries, "blue"));
    try std.testing.expectEqual(@as(?usize, 5), string.memchrInv("aaaaab", 'a'));
    try std.testing.expectEqual(@as(?usize, 5), string.memchr_inv("aaaaab", 'a'));
}

test "lane06 rbtree cached add and duplicate aliases keep leftmost state aligned" {
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

    var primary_first = Entry{ .key = 10, .serial = 0 };
    var alias_first = Entry{ .key = 10, .serial = 0 };
    var primary_leftmost = Entry{ .key = 5, .serial = 1 };
    var alias_leftmost = Entry{ .key = 5, .serial = 1 };
    var primary_duplicate = Entry{ .key = 10, .serial = 2 };
    var alias_duplicate = Entry{ .key = 10, .serial = 2 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(
        @as(?*rbtree.Node, &primary_first.node),
        rbtree.addCached(&primary_first.node, &primary_root, less),
    );
    try std.testing.expectEqual(
        @as(?*rbtree.Node, &alias_first.node),
        rbtree.rb_add_cached(&alias_first.node, &alias_root, less),
    );
    try std.testing.expectEqual(
        @as(?*rbtree.Node, &primary_leftmost.node),
        rbtree.addCached(&primary_leftmost.node, &primary_root, less),
    );
    try std.testing.expectEqual(
        @as(?*rbtree.Node, &alias_leftmost.node),
        rbtree.rb_add_cached(&alias_leftmost.node, &alias_root, less),
    );
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.firstCached(&alias_root));

    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_root, cmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &primary_first.node), primary_existing);
    try std.testing.expectEqual(@as(*rbtree.Node, &alias_first.node), alias_existing);
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.firstCached(&alias_root));
}
