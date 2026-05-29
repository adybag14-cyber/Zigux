const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap scnprintf keeps declared ranges and truncates without tail leakage" {
    const nbits = bits_per_long + 7;
    var map = [_]Word{ 0, 0 };
    bitmap.setRange(&map, 1, 3);
    bitmap.setRange(&map, bits_per_long + 2, 3);
    map[1] |= @as(Word, 1) << 12;

    var full = [_]u8{0} ** 32;
    const full_len = bitmap.scnprintf(&map, nbits, full[0..]);
    try std.testing.expectEqualStrings("1-3,66-68", full[0..full_len]);
    try std.testing.expectEqual(@as(u8, 0), full[full_len]);

    var short = [_]u8{0} ** 8;
    const short_len = bitmap.bitmap_scnprintf(&map, nbits, short[0..]);
    try std.testing.expectEqual(@as(usize, 7), short_len);
    try std.testing.expectEqualStrings("1-3,66-", short[0..short_len]);
    try std.testing.expectEqual(@as(u8, 0), short[short_len]);
}

test "find last bit ignores final word bits outside nbits" {
    const nbits = bits_per_long + 9;
    var map = [_]Word{ 0, 0 };
    map[0] = @as(Word, 1) << (bits_per_long - 2);
    map[1] = (@as(Word, 1) << 8) | (@as(Word, 1) << 15);

    try std.testing.expectEqual(@as(usize, bits_per_long + 8), find_bit.findLastBit(&map, nbits));

    map[1] &= ~(@as(Word, 1) << 8);
    try std.testing.expectEqual(@as(usize, bits_per_long - 2), find_bit.find_last_bit(&map, nbits));

    map[0] = 0;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_last_bit(&map, nbits));
}

test "string counted search stops at NUL and count boundaries" {
    const buf = [_]u8{ 'a', 'b', 'c', 0, 'c', 'd' };

    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&buf, 6, 'c'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&buf, 2, 'c'));
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr(&buf, 6, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&buf, 3, 0));
}

test "rbtree cached erase init clears nodes while preserving the next leftmost" {
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
        .{ .key = 5 },
        .{ .key = 10 },
        .{ .key = 15 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));

    rbtree.rb_erase_init_cached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.firstCached(&root));
}
