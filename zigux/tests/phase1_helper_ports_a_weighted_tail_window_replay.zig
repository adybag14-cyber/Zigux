const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index);
}

test "weighted bitmap windows drive find_bit string and cached rbtree boundaries" {
    const nbits = bits_per_long + 9;
    const tail_noise = bit(12);
    const lhs = [_]Word{
        bit(1) | bit(4) | bit(8),
        bit(1) | bit(4) | tail_noise,
    };
    const rhs = [_]Word{
        bit(4) | bit(6),
        bit(4) | bit(7) | tail_noise,
    };

    var or_map = [_]Word{ 0, 0 };
    var xor_map = [_]Word{ 0, 0 };
    try std.testing.expectEqual(@as(usize, 7), bitmap.weightedOr(&or_map, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 5), bitmap.weightedXor(&xor_map, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(Word, bit(1) | bit(4) | bit(6) | bit(8)), or_map[0]);
    try std.testing.expectEqual(@as(Word, bit(1) | bit(4) | bit(7) | tail_noise), or_map[1]);
    try std.testing.expectEqual(@as(Word, bit(1) | bit(6) | bit(8)), xor_map[0]);
    try std.testing.expectEqual(@as(Word, bit(1) | bit(7)), xor_map[1]);

    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&xor_map, nbits));
    try std.testing.expectEqual(@as(usize, 6), find_bit.findNextBit(&xor_map, nbits, 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 7), find_bit.findLastBit(&xor_map, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findFirstAndBit(&or_map, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 6), find_bit.findNextAndBit(&or_map, &rhs, nbits, 5));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextAndBit(&or_map, &rhs, nbits, bits_per_long));

    var full_tail = [_]Word{ ~@as(Word, 0), bitmap.lastWordMask(nbits) };
    full_tail[1] &= ~bit(6);
    try std.testing.expectEqual(@as(usize, bits_per_long + 6), find_bit.findFirstZeroBit(&full_tail, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&full_tail, nbits, bits_per_long + 7));

    var rendered = [_]u8{0} ** 64;
    const rendered_len = bitmap.scnprintf(&xor_map, nbits, &rendered);
    try std.testing.expect(std.mem.eql(u8, rendered[0..rendered_len], "1,6,8,65,71"));
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpyPad(rendered[rendered_len + 1 ..], rendered[0..rendered_len]));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(rendered[rendered_len + 1 + rendered_len + 1 .. rendered.len], 0));

    const names = [_][]const u8{ "idle", "1,6,8,65,71\n", "tail" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&names, rendered[0..rendered_len]));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&names, rendered[0..rendered_len]));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(rendered[0..rendered_len], rendered_len, '6'));
}

test "cached rbtree leftmost follows weighted bitmap replay keys" {
    const Entry = struct {
        key: usize,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs_node: *const rbtree.Node, rhs_node: *const rbtree.Node) bool {
            const lhs: *const @This() = @fieldParentPtr("node", lhs_node);
            const rhs: *const @This() = @fieldParentPtr("node", rhs_node);
            return lhs.key < rhs.key;
        }

        fn cmpNode(lhs_node: *const rbtree.Node, rhs_node: *const rbtree.Node) i32 {
            const lhs: *const @This() = @fieldParentPtr("node", lhs_node);
            const rhs: *const @This() = @fieldParentPtr("node", rhs_node);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }

        fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
            const key: *const usize = @ptrCast(@alignCast(key_ptr));
            const entry: *const @This() = @fieldParentPtr("node", node);
            if (key.* < entry.key) return -1;
            if (key.* > entry.key) return 1;
            return 0;
        }
    };

    var entries = [_]Entry{
        .{ .key = bits_per_long + 7 },
        .{ .key = 8 },
        .{ .key = 1 },
        .{ .key = bits_per_long + 1 },
        .{ .key = 6 },
    };
    var duplicate = Entry{ .key = 8 };
    var smaller = Entry{ .key = 0 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, Entry.less);
    }

    try std.testing.expectEqual(@as(usize, 1), (@as(*const Entry, @fieldParentPtr("node", rbtree.firstCached(&root).?))).key);
    try std.testing.expectEqual(&entries[1].node, rbtree.findAddCached(&duplicate.node, &root, Entry.cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&smaller.node, &root, Entry.cmpNode));
    try std.testing.expectEqual(@as(usize, 0), (@as(*const Entry, @fieldParentPtr("node", rbtree.firstCached(&root).?))).key);

    const wanted: usize = 8;
    var iter = rbtree.matchIterator(&wanted, &root.root, Entry.cmpKey);
    const first_match = iter.next().?;
    try std.testing.expectEqual(@as(usize, 8), (@as(*const Entry, @fieldParentPtr("node", first_match))).key);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iter.next());

    _ = rbtree.eraseCached(&smaller.node, &root);
    rbtree.clearNode(&smaller.node);
    try std.testing.expectEqual(@as(usize, 1), (@as(*const Entry, @fieldParentPtr("node", rbtree.firstCached(&root).?))).key);

    var ordered: [5]usize = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        ordered[count] = (@as(*const Entry, @fieldParentPtr("node", node))).key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 5), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 6, 8, bits_per_long + 1, bits_per_long + 7 }, ordered[0..count]);
}
