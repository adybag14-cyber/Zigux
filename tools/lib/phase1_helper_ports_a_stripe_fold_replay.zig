const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const Node = rbtree.Node;

const StripeNode = struct {
    node: Node = Node.init(),
    key: usize,
};

fn owner(node: *const Node) *const StripeNode {
    return @fieldParentPtr("node", node);
}

fn ownerMut(node: *Node) *StripeNode {
    return @fieldParentPtr("node", node);
}

fn less(lhs: *const Node, rhs: *const Node) bool {
    const left = owner(lhs);
    const right = owner(rhs);
    return left.key < right.key;
}

fn cmpKey(key_ptr: *const anyopaque, node: *const Node) i32 {
    const key: *const usize = @ptrCast(@alignCast(key_ptr));
    const item = owner(node);
    if (key.* < item.key) return -1;
    if (key.* > item.key) return 1;
    return 0;
}

fn setMany(map: []Word, positions: []const usize) void {
    for (positions) |pos| {
        bitmap.bitmap_set(map, pos, 1);
    }
}

fn collectForward(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.first(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        out[count] = owner(node).key;
        count += 1;
    }
    return count;
}

test "phase1 helper ports A stripe fold replay" {
    const nbits = bitmap.bits_per_long * 2 + 19;
    const nwords = 3;

    var base = [_]Word{0} ** nwords;
    var stripe = [_]Word{0} ** nwords;
    var mask = [_]Word{0} ** nwords;
    var folded = [_]Word{0} ** nwords;
    var overlap = [_]Word{0} ** nwords;
    var stripe_only = [_]Word{0} ** nwords;
    var rendered = [_]u8{0} ** 96;

    setMany(&base, &[_]usize{ 2, 5, 17, 33, 64, 82, 98, 129 });
    setMany(&stripe, &[_]usize{ 5, 8, 17, 41, 66, 82, 111, 129 });
    bitmap.bitmap_set(&mask, 4, 40);
    bitmap.bitmap_set(&mask, 64, 24);
    bitmap.bitmap_set(&mask, 110, 8);

    bitmap.bitmap_replace(&folded, &base, &stripe, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 10), bitmap.bitmap_weight(&folded, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&folded, nbits));
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextBit(&folded, nbits, 6));
    try std.testing.expectEqual(@as(usize, 32), find_bit.findNextZeroBit(&folded, nbits, 32));
    try std.testing.expectEqual(@as(usize, 129), find_bit.findLastBit(&folded, nbits));

    try std.testing.expect(bitmap.bitmap_and(&overlap, &folded, &stripe, nbits));
    try std.testing.expectEqual(@as(usize, 8), bitmap.bitmap_weight(&overlap, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstAndBit(&folded, &stripe, nbits));

    try std.testing.expect(bitmap.bitmap_andnot(&stripe_only, &folded, &base, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.bitmap_weight(&stripe_only, nbits));
    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstAndNotBit(&folded, &base, nbits));
    try std.testing.expectEqual(@as(usize, 41), find_bit.findNextAndNotBit(&folded, &base, nbits, 40));

    var clump: u8 = 0;
    const clump_offset = find_bit.findNextClump8(&clump, &folded, nbits, 64);
    try std.testing.expectEqual(@as(usize, 64), clump_offset);
    try std.testing.expectEqual(@as(u8, 0b00000100), clump);

    const rendered_len = bitmap.bitmap_scnprintf(&folded, nbits, &rendered);
    const rendered_slice = rendered[0..rendered_len];
    try std.testing.expect(string.strstarts(rendered_slice, "2,5,8"));
    try std.testing.expect(string.strEndsWith(rendered_slice, "129"));

    var token_buffer = [_]u8{0} ** 64;
    const token_len = string.strlcpy(&token_buffer, "  stripe-fold:2,5,8,17,41,66,82,111,129  ");
    try std.testing.expect(token_len > 32);
    const token = string.strim(&token_buffer);
    _ = string.strreplace(token, ':', '=');
    try std.testing.expectEqual(@as(usize, 12), string.strHasPrefix(token, "stripe-fold="));
    try std.testing.expect(string.strEndsWith(token, "129"));
    try std.testing.expectEqual(@as(?usize, 1), string.memchr_inv(token[0..12], 's'));
    const choices = [_][]const u8{ "plain", "stripe-fold=2,5,8,17,41,66,82,111,129", "other" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&choices, token));
    try std.testing.expect(string.sysfsStreq("stripe-fold\n", "stripe-fold"));

    const keys = [_]usize{
        find_bit.findFirstBit(&folded, nbits),
        find_bit.findNextBit(&folded, nbits, 6),
        find_bit.findNextAndNotBit(&folded, &base, nbits, 40),
        find_bit.findLastBit(&folded, nbits),
    };
    var nodes = [_]StripeNode{
        .{ .key = keys[2] },
        .{ .key = keys[0] },
        .{ .key = keys[3] },
        .{ .key = keys[1] },
    };
    var root = rbtree.RootCached.init();
    for (&nodes) |*item| {
        _ = rbtree.addCached(&item.node, &root, less);
    }

    try std.testing.expectEqual(@as(usize, keys[0]), owner(rbtree.firstCached(&root).?).key);
    try std.testing.expectEqual(@as(usize, keys[3]), owner(rbtree.last(&root.root).?).key);

    const found = rbtree.find(&keys[2], &root.root, cmpKey) orelse return error.MissingStripeKey;
    try std.testing.expectEqual(@as(usize, keys[2]), owner(found).key);

    var order = [_]usize{0} ** 4;
    try std.testing.expectEqual(@as(usize, 4), collectForward(&root.root, &order));
    try std.testing.expectEqualSlices(usize, &[_]usize{ keys[0], keys[1], keys[2], keys[3] }, &order);

    const removed = rbtree.eraseCached(found, &root);
    try std.testing.expectEqual(@as(?*Node, null), removed);
    rbtree.clearNode(&ownerMut(found).node);
    try std.testing.expect(rbtree.emptyNode(found));

    var after = [_]usize{0} ** 3;
    try std.testing.expectEqual(@as(usize, 3), collectForward(&root.root, &after));
    try std.testing.expectEqualSlices(usize, &[_]usize{ keys[0], keys[1], keys[3] }, &after);
}
