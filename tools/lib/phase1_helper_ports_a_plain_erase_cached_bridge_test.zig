const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;

const Entry = struct {
    key: i32,
    serial: usize = 0,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn collect(root: *const rbtree.Root, out: []i32) usize {
    var count: usize = 0;
    var cursor = rbtree.first(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

fn nodeKey(node: ?*rbtree.Node) ?i32 {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return entry.key;
}

fn setBit(map: []Word, bit: usize) void {
    map[bit / bitmap.bits_per_long] |= @as(Word, 1) << @intCast(bit & (bitmap.bits_per_long - 1));
}

fn expectPlainEraseAliasShapeWhenPresent() !void {
    if (@hasDecl(rbtree, "rb_erase")) {
        const expected: fn (*rbtree.Node, *rbtree.Root) void = rbtree.rb_erase;
        _ = expected;
    }
    if (@hasDecl(rbtree, "rb_erase_init")) {
        const expected: fn (*rbtree.Node, *rbtree.Root) void = rbtree.rb_erase_init;
        _ = expected;
    }
}

test "plain erase helpers and cached Linux aliases share derived cursor behavior" {
    try expectPlainEraseAliasShapeWhenPresent();

    var mask = [_]Word{0} ** 2;
    var old_bits = [_]Word{0} ** 2;
    var new_bits = [_]Word{0} ** 2;
    for ([_]usize{ 1, 3, 5, 8, 13 }) |bit| setBit(&mask, bit);
    for ([_]usize{ 3, 8, 21 }) |bit| setBit(&old_bits, bit);
    for ([_]usize{ 1, 5, 13, 21, 63 }) |bit| setBit(&new_bits, bit);

    var merged = old_bits;
    bitmap.replace(&merged, &old_bits, &new_bits, &mask, 24);
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&merged, 24));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextZeroBit(&merged, 24, 3));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextBit(&merged, 24, 4));
    try std.testing.expectEqual(@as(usize, 21), find_bit.findLastBit(&merged, 24));

    var andnot = [_]Word{0} ** 2;
    try std.testing.expect(bitmap.andNotBits(&andnot, &merged, &old_bits, 24));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstAndNotBit(&merged, &old_bits, 24));

    var rendered: [32]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&andnot, 24, &rendered);
    var padded: [32]u8 = undefined;
    try std.testing.expect(string.strscpyPad(&padded, rendered[0..rendered_len]) >= 0);
    const trimmed = string.strim(&padded);
    try std.testing.expect(string.strHasPrefix(trimmed, "1") > 0);
    try std.testing.expect(string.sysfsStreq(trimmed, "1,5,13\n"));
    try std.testing.expectEqual(@as(?usize, 1), string.memchr_inv(trimmed, '1'));

    var plain_entries = [_]Entry{
        .{ .key = 1 },
        .{ .key = 5 },
        .{ .key = 13 },
    };
    var cached_entries = [_]Entry{
        .{ .key = 1 },
        .{ .key = 5 },
        .{ .key = 13 },
    };
    var plain_root = rbtree.Root.init();
    var cached_root = rbtree.RootCached.init();

    for (&plain_entries, &cached_entries) |*plain_entry, *cached_entry| {
        rbtree.add(&plain_entry.node, &plain_root, less);
        _ = rbtree.addCached(&cached_entry.node, &cached_root, less);
    }
    try std.testing.expectEqual(nodeKey(rbtree.first(&plain_root)), nodeKey(rbtree.firstCached(&cached_root)));

    rbtree.erase(&plain_entries[1].node, &plain_root);
    try std.testing.expect(rbtree.rb_erase_cached(&cached_entries[1].node, &cached_root) == null);

    var plain_order: [3]i32 = undefined;
    var cached_order: [3]i32 = undefined;
    const plain_count = collect(&plain_root, &plain_order);
    const cached_count = collect(&cached_root.root, &cached_order);
    try std.testing.expectEqual(@as(usize, 2), plain_count);
    try std.testing.expectEqual(plain_count, cached_count);
    try std.testing.expectEqualSlices(i32, plain_order[0..plain_count], cached_order[0..cached_count]);

    rbtree.eraseInit(&plain_entries[0].node, &plain_root);
    rbtree.rb_erase_init_cached(&cached_entries[0].node, &cached_root);
    try std.testing.expect(rbtree.emptyNode(&plain_entries[0].node));
    try std.testing.expect(rbtree.emptyNode(&cached_entries[0].node));
    try std.testing.expectEqual(nodeKey(rbtree.first(&plain_root)), nodeKey(rbtree.firstCached(&cached_root)));
}
