const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index);
}

fn nodeEntry(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn keyCmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_key = nodeEntry(lhs).key;
    const rhs_key = nodeEntry(rhs).key;
    if (lhs_key < rhs_key) return -1;
    if (lhs_key > rhs_key) return 1;
    return 0;
}

fn lookupCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const current = nodeEntry(node).key;
    if (wanted.* < current) return -1;
    if (wanted.* > current) return 1;
    return 0;
}

test "bitmap slice replacement feeds find-bit window scans" {
    const nbits = bits_per_long + 13;
    var old = [_]Word{ 0, 0 };
    var new = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };
    var dst = [_]Word{ 0, 0 };

    old[0] = bit(1) | bit(5) | bit(11);
    old[1] = bit(2) | bit(10) | (bit(bits_per_long - 1));
    new[0] = bit(3) | bit(5) | bit(12);
    new[1] = bit(4) | bit(12) | (bit(bits_per_long - 1));
    mask[0] = bit(3) | bit(5) | bit(12);
    mask[1] = bit(4) | bit(12) | (bit(bits_per_long - 1));

    bitmap.replace(&dst, &old, &new, &mask, nbits);

    try std.testing.expectEqual(bit(1) | bit(3) | bit(5) | bit(11) | bit(12), dst[0]);
    try std.testing.expectEqual(bit(2) | bit(4) | bit(10) | bit(12), dst[1]);
    try std.testing.expectEqual(@as(usize, 9), bitmap.weight(&dst, nbits));
    var merged = [_]Word{ 0, 0 };
    bitmap.orBits(&merged, &dst, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextBit(&merged, nbits, 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findNextAndNotBit(&dst, &new, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 12), find_bit.findLastBit(&dst, nbits));

    var rendered = [_]u8{0} ** 48;
    const rendered_len = bitmap.scnprintf(&dst, nbits, &rendered);
    try std.testing.expectEqualStrings("1,3,5,11-12,66,68,74,76", rendered[0..rendered_len]);
}

test "string padding and bounded scans stop at C boundaries" {
    const raw = [_]u8{ 'a', 'b', 0, 'c', 'd', 'e' };
    var padded = [_]u8{0xaa} ** 7;

    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, &raw));

    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 0, 0, 0, 0, 0 }, &padded);
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&raw, raw.len, 'd'));
    try std.testing.expectEqual(@as(?usize, 3), string.memchrInv(&[_]u8{ 0, 0, 0, 1, 0 }, 0));

    var label = [_]u8{ ' ', 'a', ' ', 'b', ' ', 0, 'c' };
    const compact = string.removeSpaces(&label);
    try std.testing.expectEqualStrings("ab", compact);
    try std.testing.expectEqual(@as(usize, 2), string.strreplace(&label, 'b', 'B'));
    try std.testing.expectEqualStrings("aB", label[0..2]);
}

test "cached rbtree lookup and removal preserve leftmost handoff" {
    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 9 },
        .{ .key = 3 },
        .{ .key = 7 },
        .{ .key = 11 },
        .{ .key = 7 },
    };

    try std.testing.expect(rbtree.findAddCached(&entries[0].node, &root, keyCmp) == null);
    try std.testing.expect(rbtree.findAddCached(&entries[1].node, &root, keyCmp) == null);
    try std.testing.expect(rbtree.findAddCached(&entries[2].node, &root, keyCmp) == null);
    try std.testing.expect(rbtree.findAddCached(&entries[3].node, &root, keyCmp) == null);
    try std.testing.expectEqual(&entries[2].node, rbtree.findAddCached(&entries[4].node, &root, keyCmp));

    try std.testing.expectEqual(&entries[1].node, rbtree.firstCached(&root));
    const key_7: i32 = 7;
    try std.testing.expectEqual(&entries[2].node, rbtree.find(&key_7, &root.root, lookupCmp));

    const handed_off = rbtree.eraseCached(&entries[1].node, &root);
    try std.testing.expectEqual(&entries[2].node, handed_off);
    try std.testing.expectEqual(&entries[2].node, rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&entries[2].node));

    var seen = [_]i32{0} ** 3;
    var idx: usize = 0;
    var node = rbtree.first(&root.root);
    while (node) |current| : (node = rbtree.next(current)) {
        seen[idx] = nodeEntry(current).key;
        idx += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), idx);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 7, 9, 11 }, &seen);
}
