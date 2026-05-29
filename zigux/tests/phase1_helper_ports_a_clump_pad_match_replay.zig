const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

test "bitmap subset and intersects ignore storage bits past nbits" {
    const nbits = bitmap.bits_per_long + 5;
    const declared_tail = bitmap.lastWordMask(nbits);
    const common = @as(Word, 1) << 3;
    const hidden_tail = @as(Word, 1) << 12;

    const lhs = [_]Word{ common, hidden_tail };
    const rhs = [_]Word{ common, 0 };
    const tail_only = [_]Word{ 0, hidden_tail };

    try std.testing.expect(bitmap.subset(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.__bitmap_subset(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expect(!bitmap.intersects(&tail_only, &rhs, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&tail_only, &rhs, nbits));
    try std.testing.expectEqual(@as(Word, 0), tail_only[1] & declared_tail);
}

test "find_bit clump scans return aligned byte and preserve clump on miss" {
    const nbits = find_bit.bits_per_long + 8;
    const second_word_clump: Word = (@as(Word, 1) << 5) | (@as(Word, 1) << 7);
    const words = [_]Word{ 0, second_word_clump };

    var clump: u8 = 0;
    try std.testing.expectEqual(find_bit.bits_per_long, find_bit.findNextClump8(&clump, &words, nbits, 1));
    try std.testing.expectEqual(@as(u8, 0b1010_0000), clump);

    clump = 0;
    try std.testing.expectEqual(find_bit.bits_per_long, find_bit.find_next_clump8(&clump, &words, nbits, 63));
    try std.testing.expectEqual(@as(u8, 0b1010_0000), clump);

    clump = 0x5a;
    try std.testing.expectEqual(nbits, find_bit._find_next_clump8(&clump, &words, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "string strscpyPad copies C prefix and zero pads remaining storage" {
    var direct = [_]u8{0xaa} ** 8;
    var alias = [_]u8{0xaa} ** 8;
    const src = [_]u8{ 'o', 'k', 0, 'x', 'x' };

    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&direct, &src));
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(&alias, &src));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0, 0, 0 }, &direct);
    try std.testing.expectEqualSlices(u8, &direct, &alias);
}

test "rbtree match iterator walks duplicate keys then stops before next key" {
    const Entry = struct {
        key: i32,
        tag: u8,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const helpers = struct {
        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }

        fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
            const key: *const i32 = @ptrCast(@alignCast(key_ptr));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (key.* < entry.key) return -1;
            if (key.* > entry.key) return 1;
            return 0;
        }
    };

    var entries = [_]Entry{
        .{ .key = 4, .tag = 1 },
        .{ .key = 2, .tag = 2 },
        .{ .key = 4, .tag = 3 },
        .{ .key = 4, .tag = 4 },
        .{ .key = 6, .tag = 5 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, helpers.less);
    }

    const key: i32 = 4;
    try std.testing.expectEqual(&entries[0].node, rbtree.findFirst(&key, &root, helpers.cmpKey).?);

    var iterator = rbtree.matchIterator(&key, &root, helpers.cmpKey);
    try std.testing.expectEqual(@as(u8, 1), (@as(*const Entry, @fieldParentPtr("node", iterator.next().?))).tag);
    try std.testing.expectEqual(@as(u8, 3), (@as(*const Entry, @fieldParentPtr("node", iterator.next().?))).tag);
    try std.testing.expectEqual(@as(u8, 4), (@as(*const Entry, @fieldParentPtr("node", iterator.next().?))).tag);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iterator.next());
}
