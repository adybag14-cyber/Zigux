const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap helpers clamp tail-only overlap while keeping in-range xor bits visible" {
    const nbits = bits_per_long + 3;
    const lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 7) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 2) | (@as(Word, 1) << 7) };

    var and_dst = [_]Word{ 0xaaaa_aaaa_aaaa_aaaa, 0x5555_5555_5555_5555 };
    try std.testing.expect(!bitmap.bitmap_and(and_dst[0..], lhs[0..], rhs[0..], nbits));
    try std.testing.expectEqual(@as(Word, 0), and_dst[0]);
    try std.testing.expectEqual(@as(Word, 0), and_dst[1]);

    var xor_dst = [_]Word{ 0, 0 };
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weighted_xor(xor_dst[0..], lhs[0..], rhs[0..], nbits));
    try std.testing.expectEqual(@as(Word, 0), xor_dst[0]);
    try std.testing.expectEqual((@as(Word, 1) << 1) | (@as(Word, 1) << 2), xor_dst[1]);
}

test "find_bit inclusive next scans keep boundary and masked tail semantics aligned" {
    const nbits = bits_per_long + 6;
    const boundary = bits_per_long - 1;
    const map = [_]Word{
        @as(Word, 1) << @intCast(boundary),
        (@as(Word, 1) << 0) | (@as(Word, 1) << 5) | (@as(Word, 1) << 8),
    };
    const andnot_lhs = map;
    const andnot_rhs = [_]Word{
        0,
        (@as(Word, 1) << 0) | (@as(Word, 1) << 8),
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextBit(map[0..], nbits, boundary));
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextBit(map[0..], nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 5), find_bit.findNextBit(map[0..], nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(map[0..], nbits, bits_per_long + 6));

    try std.testing.expectEqual(@as(usize, bits_per_long + 5), find_bit.findNextAndNotBit(andnot_lhs[0..], andnot_rhs[0..], nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(andnot_lhs[0..], andnot_rhs[0..], nbits, bits_per_long + 6));
}

test "string copy-pad helpers zero-fill the visible tail after C-string termination" {
    var dst = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x' };
    const src = [_]u8{ 'o', 'k', 0, '!', '!' };

    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(dst[0..], src[0..]));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0, 0, 0 }, dst[0..]);
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(dst[2..], 0));
    try std.testing.expectEqualStrings("zigux", string.skip_spaces(" \tzigux"));
}

test "rbtree cached replacement promotes a new leftmost node without disturbing order" {
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
        .{ .key = 20 },
        .{ .key = 10 },
        .{ .key = 30 },
        .{ .key = 5 },
    };
    var replacement = Entry{ .key = 5 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&entries[3].node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));

    var order: [4]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 20, 30 }, order[0..count]);
}
