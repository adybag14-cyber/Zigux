const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap range updates and zero scans share declared-tail boundaries" {
    const nbits = bits_per_long + 6;
    var map = [_]Word{ 0, 0 };

    bitmap.setRange(&map, 0, nbits);
    map[1] |= ~bitmap.lastWordMask(nbits);

    try std.testing.expect(bitmap.full(&map, nbits));
    try std.testing.expectEqual(nbits, bitmap.weight(&map, nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextZeroBit(&map, nbits, 0));
    try std.testing.expectEqual(nbits, find_bit.find_next_zero_bit(&map, nbits, bits_per_long + 5));

    const gap_start = bits_per_long - 2;
    bitmap.clearRange(&map, gap_start, 5);

    try std.testing.expect(!bitmap.full(&map, nbits));
    try std.testing.expectEqual(nbits - 5, bitmap.weight(&map, nbits));
    try std.testing.expectEqual(gap_start, find_bit.findNextZeroBit(&map, nbits, gap_start - 1));
    try std.testing.expectEqual(bits_per_long, find_bit._find_next_zero_bit(&map, nbits, bits_per_long));
    try std.testing.expectEqual(nbits, find_bit.findNextZeroBit(&map, nbits, nbits));

    bitmap.setRange(&map, gap_start, 5);
    try std.testing.expect(bitmap.full(&map, nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextZeroBit(&map, nbits, 0));
}

test "bitmap aliases preserve range masks while tail garbage stays invisible" {
    const nbits = bits_per_long + 3;
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    bitmap.setRange(&direct, 1, bits_per_long + 2);
    bitmap.bitmap_set(&alias, 1, bits_per_long + 2);
    direct[1] |= ~bitmap.lastWordMask(nbits);
    alias[1] |= ~bitmap.lastWordMask(nbits);

    try std.testing.expect(bitmap.equal(&direct, &alias, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&direct, &alias, nbits));
    try std.testing.expect(bitmap.subset(&direct, &alias, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&alias, &direct, nbits));
    try std.testing.expectEqual(@as(usize, nbits - 1), bitmap.weight(&direct, nbits));

    bitmap.clearRange(&direct, bits_per_long, 2);
    bitmap.bitmap_clear(&alias, bits_per_long, 2);

    try std.testing.expect(bitmap.equal(&direct, &alias, nbits));
    try std.testing.expectEqual(@as(usize, nbits - 3), bitmap.bitmap_weight(&alias, nbits));
}

test "string prefix suffix and counted character scans stop at C boundaries" {
    const with_nul = [_]u8{ 'z', 'i', 'g', 0, 'u', 'x' };
    const accept_nul = [_]u8{ 'g', 0, 'x' };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&with_nul, "zig"));
    try std.testing.expect(string.strstarts(&with_nul, "zig"));
    try std.testing.expect(string.strEndsWith(&with_nul, "ig"));
    try std.testing.expect(string.str_ends_with(&with_nul, &accept_nul));
    try std.testing.expect(!string.strEndsWith(&with_nul, "ux"));

    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&with_nul, with_nul.len, 'g'));
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr(&with_nul, with_nul.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&with_nul, with_nul.len, 'u'));
}

test "rbtree reverse traversal and aliases keep empty-node stops explicit" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const @This() = @fieldParentPtr("node", lhs);
            const rhs_entry: *const @This() = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    };

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 20 },
        .{ .key = 15 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, Entry.less);
    }

    var order: [4]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.rb_last(&root);
    while (current) |node| : (current = rbtree.rb_prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 20, 15, 10, 5 }, order[0..count]);

    rbtree.clearNode(&entries[0].node);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_prev(&entries[0].node));
}
