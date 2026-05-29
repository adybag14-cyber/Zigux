const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "bitmap tail-masked predicates ignore hidden bits" {
    const nbits = bitmap.bits_per_long + 9;
    var map = [_]bitmap.Word{ 0, 0 };

    try std.testing.expect(bitmap.empty(&map, nbits));

    bitmap.setRange(&map, 2, 3);
    bitmap.setRange(&map, bitmap.bits_per_long + 7, 1);
    map[1] |= @as(bitmap.Word, 1) << 12;

    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&map, nbits));
    try std.testing.expect(!bitmap.empty(&map, nbits));

    const same_in_window = [_]bitmap.Word{
        map[0],
        map[1] ^ (@as(bitmap.Word, 1) << 15),
    };
    try std.testing.expect(bitmap.equal(&map, &same_in_window, nbits));

    const declared_mask = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        bitmap.lastWordMask(nbits),
    };
    try std.testing.expect(bitmap.subset(&map, &declared_mask, nbits));
    var andnot = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(!bitmap.andNotBits(&andnot, &map, &declared_mask, nbits));
    try std.testing.expect(bitmap.empty(&andnot, nbits));

    var inverted = [_]bitmap.Word{ 0, 0 };
    bitmap.complement(&inverted, &map, nbits);
    try std.testing.expectEqual(@as(bitmap.Word, 0), inverted[1] & ~bitmap.lastWordMask(nbits));
}

test "find_bit andnot scans clamp starts and declared tails" {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9),
        (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 11),
    };
    const rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 3,
        @as(find_bit.Word, 1) << 11,
    };

    try std.testing.expectEqual(@as(usize, 9), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 10));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(find_bit.findFirstAndNotBit(&lhs, &rhs, nbits), find_bit._find_first_andnot_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 10), find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, 10));
}

test "string sysfs and suffix helpers stop at c-string boundaries" {
    const haystack = [_][]const u8{
        "ready\n",
        "offline\x00ignored",
        "armed\n\x00tail",
    };

    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&haystack, "ready"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&haystack, "offline"));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfs_match_string(&haystack, "armed"));
    try std.testing.expect(string.strEndsWith("driver-ready\x00ignored", "ready"));
    try std.testing.expect(!string.str_ends_with("driver-ready\x00ignored", "ignored"));
}

test "rbtree cached find-add aliases preserve leftmost and duplicate identity" {
    const Entry = struct {
        key: i32,
        serial: usize,
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

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
        .{ .key = 10, .serial = 3 },
    };

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&entries[0].node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&entries[1].node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&entries[2].node, &root, cmp));

    const duplicate = rbtree.rb_find_add_cached(&entries[3].node, &root, cmp) orelse return error.TestUnexpectedResult;
    const duplicate_entry: *const Entry = @fieldParentPtr("node", duplicate);
    try std.testing.expectEqual(@as(usize, 0), duplicate_entry.serial);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15 }, order[0..count]);
}
