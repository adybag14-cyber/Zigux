const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string_helpers = @import("string_helpers");
const rbtree = @import("rbtree");

test "lane06 replay keeps copy-clear-tail and extend windows bounded" {
    const count = bitmap.bits_per_long + 3;
    const size = bitmap.bits_per_long * 2 + 5;
    const src = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        (@as(bitmap.Word, 1) << 0) |
            (@as(bitmap.Word, 1) << 2) |
            (@as(bitmap.Word, 1) << 7),
    };
    var cleared = [_]bitmap.Word{ 0, 0 };
    var extended = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    var expected = [_]bitmap.Word{ 0, 0, 0 };

    bitmap.copyClearTail(&cleared, &src, count);
    try std.testing.expectEqual(~@as(bitmap.Word, 0), cleared[0]);
    try std.testing.expectEqual((@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 2), cleared[1]);

    bitmap.copyAndExtend(&extended, &src, count, size);
    expected[0] = cleared[0];
    expected[1] = cleared[1];

    try std.testing.expect(bitmap.equal(&extended, &expected, size));
    try std.testing.expect(bitmap.bitmap_subset(&extended, &expected, size));
    try std.testing.expect(bitmap.bitmap_intersects(&extended, &expected, size));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 2), bitmap.weight(&extended, size));
}

test "lane06 replay keeps clump scans and last-bit lookup inside the tail mask" {
    const nbits = find_bit.bits_per_long + 13;
    const words = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 9) | (@as(find_bit.Word, 1) << 10),
        (@as(find_bit.Word, 1) << 0) |
            (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 12) |
            (@as(find_bit.Word, 1) << 18),
    };
    var clump: u8 = 0;

    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstClump8(&clump, &words, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_0110), clump);

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findNextClump8(&clump, &words, nbits, 11),
    );
    try std.testing.expectEqual(@as(u8, 0b0001_0011), clump);

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 12),
        find_bit.findLastBit(&words, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextBit(&words, nbits, find_bit.bits_per_long + 13),
    );
}

test "lane06 replay keeps prefix trim and replace helpers stable" {
    try std.testing.expectEqual(
        @as(usize, 4),
        string_helpers.strHasPrefix(&[_]u8{ 'l', 'a', 'n', 'e', 0, 'x' }, "lane"),
    );
    try std.testing.expect(string_helpers.strEndsWith(&[_]u8{ 'l', 'a', 'n', 'e', '-', '0', '6', 0, 'x' }, "06"));
    try std.testing.expectEqualStrings("lane 06", string_helpers.skipSpaces(" \t lane 06"));

    var trim_buf = [_]u8{ ' ', '\t', 'l', 'a', 'n', 'e', ' ', '0', '6', '\n', 0, 'x' };
    try std.testing.expectEqualStrings("lane 06", string_helpers.trimSpaces(trim_buf[0..]));

    var remove_buf = [_]u8{ 'l', 'a', ' ', 'n', 'e', ' ', '0', '6', 0, 'x' };
    try std.testing.expectEqualStrings("lane06", string_helpers.removeSpaces(remove_buf[0..]));

    var replace_buf = [_]u8{ 'l', 'a', 'n', 'e', '-', '0', '6', 0, '-' };
    try std.testing.expectEqual(@as(usize, 7), string_helpers.strreplace(replace_buf[0..], '-', '_'));
    try std.testing.expectEqualStrings("lane_06", replace_buf[0..7]);
}

test "lane06 replay keeps plain-root replace and erase-init traversal stable" {
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

    var root = rbtree.Root.init();
    var entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 12 },
        .{ .key = 10 },
    };
    var replacement = Entry{ .key = 12 };

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    rbtree.replaceNode(&entries[2].node, &replacement.node, &root);

    const first = rbtree.first(&root) orelse return error.TestUnexpectedResult;
    const second = rbtree.next(first) orelse return error.TestUnexpectedResult;
    const third = rbtree.next(second) orelse return error.TestUnexpectedResult;
    const fourth = rbtree.next(third) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(i32, 4), (@as(*const Entry, @fieldParentPtr("node", first))).key);
    try std.testing.expectEqual(@as(i32, 8), (@as(*const Entry, @fieldParentPtr("node", second))).key);
    try std.testing.expectEqual(@as(i32, 10), (@as(*const Entry, @fieldParentPtr("node", third))).key);
    try std.testing.expectEqual(@as(i32, 12), (@as(*const Entry, @fieldParentPtr("node", fourth))).key);

    rbtree.eraseInit(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(rbtree.first(&root).?));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.next(rbtree.last(&root).?));
}
