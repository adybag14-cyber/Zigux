const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap weighted aliases aligned across tail-clamped windows" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 6;
    const lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 5) | (@as(Word, 1) << 8) };

    var direct_or = [_]Word{ 0, 0 };
    var alias_or = [_]Word{ 0, 0 };
    const direct_or_weight = bitmap.weightedOr(&direct_or, &lhs, &rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 3), direct_or_weight);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try std.testing.expect(bitmap.equal(&direct_or, &alias_or, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&direct_or, nbits));

    var direct_xor = [_]Word{ 0, 0 };
    var alias_xor = [_]Word{ 0, 0 };
    const direct_xor_weight = bitmap.weightedXor(&direct_xor, &lhs, &rhs, nbits);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&alias_xor, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_xor_weight);
    try std.testing.expectEqual(direct_xor_weight, alias_xor_weight);
    try std.testing.expect(bitmap.equal(&direct_xor, &alias_xor, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_xor, nbits));
}

test "lane06 replay keeps clump scans aligned to live bytes and tail masks" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 5;
    const clump_bitmap = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 7),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findFirstClump8(&clump, &clump_bitmap, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0b0000_1010), clump);

    clump = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.find_next_clump8(&clump, &clump_bitmap, nbits, find_bit.bits_per_long + 1),
    );
    try std.testing.expectEqual(@as(u8, 0b0000_1010), clump);

    clump = 0x5a;
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit._find_next_clump8(&clump, &clump_bitmap, nbits, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "lane06 replay keeps string parse saturation and match helpers aligned" {
    const positive = string.memparse("+9223372036854775808");
    try std.testing.expectEqual(@as(u64, @intCast(std.math.maxInt(i64))), positive.value);
    try std.testing.expectEqualStrings("", positive.rest);

    const negative = string.memparse("-0x2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), negative.value);
    try std.testing.expectEqualStrings("tail", negative.rest);

    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto"));

    const cstring_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(cstring_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(cstring_haystack[1..], "alpha"));
}

test "lane06 replay keeps cached duplicate insert and leftmost reseed behavior aligned" {
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

    var first = Entry{ .key = 10 };
    var leftmost = Entry{ .key = 5 };
    var right = Entry{ .key = 12 };
    var duplicate = Entry{ .key = 5 };
    var replacement = Entry{ .key = 10 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&first.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &first.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&leftmost.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&right.node, &root, cmp));

    const existing = rbtree.findAddCached(&duplicate.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &leftmost.node), existing);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&leftmost.node, &root);
    try std.testing.expect(rbtree.emptyNode(&leftmost.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &first.node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&first.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
