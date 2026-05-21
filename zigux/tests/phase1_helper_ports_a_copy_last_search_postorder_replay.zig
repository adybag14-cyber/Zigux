const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string_helpers = @import("string_helpers");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap tail copy and extension behavior aligned" {
    const count = bitmap.bits_per_long + 5;
    const size = bitmap.bits_per_long * 3;
    const src = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0), 0 };
    var copied = [_]bitmap.Word{ 0, 0, 0 };
    var extended = [_]bitmap.Word{ 0x55aa, 0x55aa, 0x55aa };

    bitmap.copyClearTail(&copied, src[0..2], count);
    try std.testing.expectEqual(~@as(bitmap.Word, 0), copied[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), copied[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), copied[2]);

    bitmap.copyAndExtend(&extended, src[0..2], count, size);
    try std.testing.expectEqual(~@as(bitmap.Word, 0), extended[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), extended[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), extended[2]);
}

test "lane06 replay keeps find-last and clump tail aliases stable" {
    const nbits = find_bit.bits_per_long + 5;
    const bitmap_words = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 7,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9),
    };
    var clump: u8 = 0;

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findLastBit(&bitmap_words, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.find_last_bit(&bitmap_words, nbits));
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_clump8(&clump, &bitmap_words, nbits));
    try std.testing.expectEqual(@as(u8, 0b1000_0000), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&clump, &bitmap_words, nbits, find_bit.bits_per_long + 4));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "lane06 replay keeps string prefix newline and bounded-search overlap stable" {
    const sysfs_values = [_][]const u8{ "off", "lane\n", "lane", "on" };
    const exact_values = [_][]const u8{
        &[_]u8{ 'l', 'a', 'n', 'e', 0, 'x' },
        "lane",
        "other",
    };

    try std.testing.expectEqual(
        @as(usize, 4),
        string_helpers.strHasPrefix(&[_]u8{ 'l', 'a', 'n', 'e', 0, 'x' }, "lane"),
    );
    try std.testing.expect(string_helpers.strstarts("lane-helper", "lane"));
    try std.testing.expect(string_helpers.strEndsWith(&[_]u8{ 'h', 'e', 'l', 'p', 'e', 'r', 0, 'x' }, "per"));
    try std.testing.expect(string_helpers.sysfsStreq("lane\n", "lane"));
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.sysfsMatchString(sysfs_values[0..], "lane"));
    try std.testing.expectEqual(@as(?usize, 0), string_helpers.matchString(exact_values[0..], "lane"));
    try std.testing.expectEqual(@as(?usize, 2), string_helpers.strnchr("abc", 3, 'c'));

    var backing = [_]u8{0} ** 32;
    backing[17] = 1;
    try std.testing.expectEqual(@as(?usize, 17), string_helpers.memchrInv(backing[0..], 0));
    try std.testing.expectEqual(@as(?usize, 17), string_helpers.memchr_inv(backing[0..], 0));
}

test "lane06 replay keeps cached postorder walks stable after leftmost removal" {
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
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 12 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var cursor = rbtree.firstPostorder(&root.root);
    while (cursor) |node| : (cursor = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 10, 15, 12 }, order[0..count]);
    try std.testing.expectEqual(rbtree.firstPostorder(&root.root), rbtree.rb_first_postorder(&root.root));
}
