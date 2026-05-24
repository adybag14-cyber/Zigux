const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap copy aliases keep tail masking and aligned extension stable" {
    const count = bits_per_long + 5;
    const size = bits_per_long * 3;
    const src = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };

    var raw_copied = [_]Word{ 0, 0 };
    bitmap.bitmap_copy(&raw_copied, src[0..2], count);
    try std.testing.expectEqual(@as(Word, ~@as(Word, 0)), raw_copied[0]);
    try std.testing.expectEqual(@as(Word, ~@as(Word, 0)), raw_copied[1]);

    var cleared = [_]Word{ 0, 0, 0 };
    bitmap.bitmap_copy_clear_tail(&cleared, &src, count);
    try std.testing.expectEqual(@as(Word, ~@as(Word, 0)), cleared[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), cleared[1]);
    try std.testing.expectEqual(@as(Word, 0), cleared[2]);

    var aligned_extended = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    bitmap.bitmap_copy_and_extend(&aligned_extended, src[0..1], bits_per_long, size);
    try std.testing.expectEqualSlices(Word, &[_]Word{ src[0], 0, 0 }, &aligned_extended);

    var zero_extended = [_]Word{ 1, 2, 3 };
    bitmap.bitmap_copy_and_extend(&zero_extended, &[_]Word{}, 0, size);
    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, 0, 0 }, &zero_extended);
}

test "find_bit clump8 scans keep cross-word bytes visible and preserve caller state on empty windows" {
    const cross_word_nbits = bits_per_long + 8;
    const cross_word = [_]Word{
        @as(Word, 0xaa) << @intCast(bits_per_long - 8),
        @as(Word, 0x55),
    };

    try std.testing.expectEqual(@as(u8, 0xaa), find_bit.getValue8(&cross_word, bits_per_long - 8));

    var clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, bits_per_long - 8),
        find_bit.findFirstClump8(&clump, &cross_word, cross_word_nbits),
    );
    try std.testing.expectEqual(@as(u8, 0xaa), clump);

    clump = 0;
    try std.testing.expectEqual(
        @as(usize, bits_per_long),
        find_bit.findNextClump8(&clump, &cross_word, cross_word_nbits, bits_per_long),
    );
    try std.testing.expectEqual(@as(u8, 0x55), clump);

    const populated = [_]Word{@as(Word, 1) << 3};
    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &populated, 0));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);

    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &populated, 8, 8));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);

    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &populated, 8, 12));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "string strscpyPad aliases keep padding, embedded NUL, and truncation semantics" {
    var padded = [_]u8{0xaa} ** 6;
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, &padded);

    const src_cstr = [_]u8{ 'o', 'k', 0, 'x', 'y' };
    padded = [_]u8{0xaa} ** 6;
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(&padded, &src_cstr));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &padded);

    var truncated = [_]u8{0xaa} ** 4;
    try std.testing.expectEqual(@as(isize, -7), string.strscpyPad(&truncated, "hello"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'e', 'l', 0 }, &truncated);
}

test "rbtree cached-leftmost updates survive successor promotion and non-leftmost replacement" {
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
        .{ .key = 8 },
        .{ .key = 7 },
    };
    var replacement = Entry{ .key = 10 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[3].node), promoted_leftmost);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&entries[0].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 7, 8, 10 }, order[0..count]);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.last(&root.root));
}