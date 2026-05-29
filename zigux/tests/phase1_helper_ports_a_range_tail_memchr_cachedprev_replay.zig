const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "bitmap cross-word range helpers preserve untouched neighbors" {
    const Word = bitmap.Word;
    const word_bits = bitmap.bits_per_long;

    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    bitmap.setRange(&direct, word_bits - 3, 7);
    bitmap.bitmap_set(&alias, word_bits - 3, 7);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    const first_expected = (@as(Word, 1) << @intCast(word_bits - 3)) |
        (@as(Word, 1) << @intCast(word_bits - 2)) |
        (@as(Word, 1) << @intCast(word_bits - 1));
    const second_expected = (@as(Word, 1) << 0) |
        (@as(Word, 1) << 1) |
        (@as(Word, 1) << 2) |
        (@as(Word, 1) << 3);
    try std.testing.expectEqual(first_expected, direct[0]);
    try std.testing.expectEqual(second_expected, direct[1]);

    bitmap.clearRange(&direct, word_bits - 1, 3);
    bitmap.bitmap_clear(&alias, word_bits - 1, 3);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    const trimmed_first = (@as(Word, 1) << @intCast(word_bits - 3)) |
        (@as(Word, 1) << @intCast(word_bits - 2));
    const trimmed_second = (@as(Word, 1) << 2) |
        (@as(Word, 1) << 3);
    try std.testing.expectEqual(trimmed_first, direct[0]);
    try std.testing.expectEqual(trimmed_second, direct[1]);
}

test "find_bit last and clump scans clamp tail noise" {
    const Word = find_bit.Word;
    const word_bits = find_bit.bits_per_long;
    const nbits = word_bits + 8;

    const tail_noise = ~find_bit.lastWordMask(nbits);
    const map = [_]Word{
        @as(Word, 1) << @intCast(word_bits - 2),
        tail_noise | (@as(Word, 1) << 1) | (@as(Word, 1) << 7),
    };

    try std.testing.expectEqual(word_bits + 7, find_bit.findLastBit(&map, nbits));

    var clump: u8 = 0xaa;
    try std.testing.expectEqual(word_bits, find_bit.findNextClump8(&clump, &map, nbits, word_bits));
    try std.testing.expectEqual(@as(u8, 0b1000_0010), clump);
    try std.testing.expectEqual(nbits, find_bit.findNextClump8(&clump, &map, nbits, nbits));
}

test "string memchr and bounded character scans stop at C boundaries" {
    const buf = [_]u8{ 'a', 'a', 'b', 'a', 0, 'b' };

    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(buf[0..2], 'a'));
    try std.testing.expectEqual(@as(?usize, 2), string.memchr_inv(&buf, 'a'));

    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&buf, buf.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&buf, 2, 'b'));
    try std.testing.expectEqual(@as(?usize, 4), string.strnchr(&buf, buf.len, 0));

    const after_nul = [_]u8{ 'x', 0, 'y' };
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&after_nul, after_nul.len, 'y'));
}

test "rbtree cached replacement keeps predecessor and successor walks coherent" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),

        fn keyOf(node: *const rbtree.Node) i32 {
            const entry: *const @This() = @fieldParentPtr("node", node);
            return entry.key;
        }

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            return keyOf(lhs) < keyOf(rhs);
        }
    };

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 20 },
        .{ .key = 10 },
        .{ .key = 30 },
    };

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, Entry.less);
    }

    try std.testing.expectEqual(@as(i32, 10), Entry.keyOf(rbtree.firstCached(&root).?));

    var replacement = Entry{ .key = 10 };
    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);

    const first = rbtree.rb_first_cached(&root).?;
    try std.testing.expect(first == &replacement.node);

    const middle = rbtree.rb_next(first).?;
    try std.testing.expectEqual(@as(i32, 20), Entry.keyOf(middle));
    try std.testing.expect(rbtree.rb_prev(middle).? == &replacement.node);
    try std.testing.expectEqual(@as(i32, 30), Entry.keyOf(rbtree.rb_next(middle).?));

    const new_leftmost = rbtree.eraseCached(&replacement.node, &root).?;
    try std.testing.expect(new_leftmost == middle);
    try std.testing.expect(rbtree.firstCached(&root).? == middle);
}
