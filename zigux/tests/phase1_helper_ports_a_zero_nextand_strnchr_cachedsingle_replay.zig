const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn orderToInt(order: std.math.Order) i32 {
    return switch (order) {
        .lt => -1,
        .eq => 0,
        .gt => 1,
    };
}

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return orderToInt(std.math.order(lhs_entry.key, rhs_entry.key));
}

fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const i32 = @ptrCast(@alignCast(key_ptr));
    const entry: *const Entry = @fieldParentPtr("node", node);
    return orderToInt(std.math.order(key.*, entry.key));
}

test "Lane 06 bitmap zero and aligned tail operations preserve untouched storage" {
    var zero_dst = [_]Word{0x55aa55aa55aa55aa};
    bitmap.zero(zero_dst[0..0], 0);
    try std.testing.expectEqual(@as(Word, 0x55aa55aa55aa55aa), zero_dst[0]);

    var fill_dst = [_]Word{0};
    bitmap.fill(&fill_dst, bits_per_long);
    try std.testing.expectEqual(~@as(Word, 0), fill_dst[0]);
    try std.testing.expect(bitmap.full(&fill_dst, bits_per_long));

    const src = [_]Word{ 0x1234, ~@as(Word, 0) };
    var copied = [_]Word{ 0, 0xbeef };
    bitmap.copyClearTail(copied[0..1], src[0..1], bits_per_long);
    try std.testing.expectEqual(src[0], copied[0]);
    try std.testing.expectEqual(@as(Word, 0xbeef), copied[1]);

    var extended = [_]Word{ 0xffff, 0xffff, 0xffff };
    bitmap.copyAndExtend(&extended, src[0..2], bits_per_long, bits_per_long * 3);
    try std.testing.expectEqual(src[0], extended[0]);
    try std.testing.expectEqual(@as(Word, 0), extended[1]);
    try std.testing.expectEqual(@as(Word, 0), extended[2]);
}

test "Lane 06 find_bit next-and aliases clamp tail bits and exhausted starts" {
    const nbits = bits_per_long + 6;
    const lhs = [_]Word{ @as(Word, 1) << 9, (@as(Word, 1) << 2) | (@as(Word, 1) << 11) };
    const rhs = [_]Word{ @as(Word, 1) << 9, (@as(Word, 1) << 2) | (@as(Word, 1) << 5) };

    try std.testing.expectEqual(@as(usize, 9), find_bit.findNextAndBit(&lhs, &rhs, nbits, 0));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.find_next_and_bit(&lhs, &rhs, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_and_bit(&lhs, &rhs, nbits, bits_per_long + 3));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 6));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 11));
}

test "Lane 06 string strnchr honors bounded C-string windows" {
    const cbuf = [_]u8{ 'z', 'i', 'g', 0, 'u', 'x', 0 };

    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cbuf, 2, 0));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&cbuf, cbuf.len, 'i'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&cbuf, cbuf.len, 'g'));
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr(&cbuf, cbuf.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cbuf, 3, 0));
}

test "Lane 06 cached rbtree singleton and duplicate insert paths stay observable" {
    var singleton = Entry{ .key = 7 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &singleton.node), rbtree.addCached(&singleton.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &singleton.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.eraseCached(&singleton.node, &root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));

    rbtree.clearNode(&singleton.node);
    try std.testing.expect(rbtree.emptyNode(&singleton.node));

    var first = Entry{ .key = 4 };
    var duplicate = Entry{ .key = 4 };
    var unique = Entry{ .key = 9 };
    var duplicate_root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&first.node, &duplicate_root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, &first.node), rbtree.findAddCached(&duplicate.node, &duplicate_root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&unique.node, &duplicate_root, cmpNode));

    const key: i32 = 4;
    try std.testing.expectEqual(@as(?*rbtree.Node, &first.node), rbtree.find(&key, &duplicate_root.root, cmpKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, &unique.node), rbtree.next(&first.node));
}
