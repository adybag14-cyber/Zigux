const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap tail-clearing and extension semantics aligned" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;
    const src = [_]Word{
        ~@as(Word, 0),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 8),
        ~@as(Word, 0),
    };

    var cleared = [_]Word{ 0, 0, 0 };
    bitmap.copyClearTail(&cleared, src[0..2], nbits);
    try std.testing.expectEqual(~@as(Word, 0), cleared[0]);
    try std.testing.expectEqual(@as(Word, 1) << 2, cleared[1]);
    try std.testing.expectEqual(@as(Word, 0), cleared[2]);

    var extended = [_]Word{ 0xaa55, 0xaa55, 0xaa55 };
    bitmap.copyAndExtend(&extended, src[0..2], nbits, bitmap.bits_per_long * 3);
    try std.testing.expectEqual(cleared[0], extended[0]);
    try std.testing.expectEqual(cleared[1], extended[1]);
    try std.testing.expectEqual(@as(Word, 0), extended[2]);
    try std.testing.expect(bitmap.equal(&cleared, extended[0..2], nbits));
}

test "lane06 replay keeps find_bit last and zero scans aligned on partial tails" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 6;
    const map = [_]Word{
        ~@as(Word, 0),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 5) | (@as(Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextZeroBit(&map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.findNextZeroBit(&map, nbits, find_bit.bits_per_long + 1));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&clump, &map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0010_0010), clump);
}

test "lane06 replay keeps string match and byte-boundary helpers aligned" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    const exact_haystack = [_][]const u8{ "off", "auto", "on" };
    const padded = [_]u8{ 'x', 'x', 'x', 'y', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x' };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(exact_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 3), string.memchrInv(&padded, 'x'));
    try std.testing.expectEqual(@as(?usize, 5), string.strnchr("alpha9!", 6, '9'));
    try std.testing.expectEqualStrings("lead", string.skipSpaces(" \tlead"));
}

test "lane06 replay keeps cached replacement and postorder traversal aligned" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 20, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 30, .serial = 2 },
        .{ .key = 25, .serial = 3 },
    };
    var replacement = Entry{ .key = 10, .serial = 4 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    const first_before = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 10), (@as(*const Entry, @fieldParentPtr("node", first_before))).key);

    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);

    const first_after = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_after);
    try std.testing.expectEqual(@as(i32, 10), first_entry.key);
    try std.testing.expectEqual(@as(usize, 4), first_entry.serial);

    var postorder_keys: [4]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.firstPostorder(&root.root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        postorder_keys[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 10, 25, 30, 20 }, postorder_keys[0..count]);

    const next_leftmost = rbtree.eraseCached(&replacement.node, &root) orelse return error.TestUnexpectedResult;
    const next_entry: *const Entry = @fieldParentPtr("node", next_leftmost);
    try std.testing.expectEqual(@as(i32, 20), next_entry.key);
    try std.testing.expectEqual(next_leftmost, rbtree.firstCached(&root).?);
}
