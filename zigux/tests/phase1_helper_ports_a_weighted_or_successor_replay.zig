const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const Node = rbtree.Node;
const RootCached = rbtree.RootCached;

const Entry = struct {
    key: usize,
    slot: usize,
    node: Node = Node.init(),
};

fn entryLess(lhs: *const Node, rhs: *const Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
    return lhs_entry.slot < rhs_entry.slot;
}

fn firstIdentity(root: *const RootCached) ?struct { usize, usize } {
    const node = rbtree.rb_first_cached(root) orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", node);
    return .{ entry.key, entry.slot };
}

fn expectRenderedSuffix(words: []const Word, nbits: usize, expected_suffix: []const u8) !void {
    var rendered: [128]u8 = undefined;
    const written = bitmap.bitmap_scnprintf(words, nbits, &rendered);
    const view = rendered[0..written];
    try std.testing.expect(string.str_ends_with(view, expected_suffix));
    try std.testing.expect(string.memchr_inv(view, ',') != null);
}

test "phase1 ports A weighted OR drives cursor and cached successor replay" {
    const nbits = bitmap.bits_per_long + 13;
    var left = [_]Word{ 0, 0 };
    var right = [_]Word{ 0, 0 };
    var merged = [_]Word{ 0, 0 };
    var masked = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&left, 3, 2);
    bitmap.bitmap_set(&left, bitmap.bits_per_long - 1, 2);
    bitmap.bitmap_set(&right, 7, 1);
    bitmap.bitmap_set(&right, bitmap.bits_per_long + 4, 3);
    right[1] |= @as(Word, 1) << 30;

    const merged_weight = bitmap.bitmap_weighted_or(&merged, &left, &right, nbits);
    try std.testing.expectEqual(@as(usize, 8), merged_weight);
    try std.testing.expectEqual(@as(usize, 3), find_bit.find_first_bit(&merged, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 6), find_bit.find_last_bit(&merged, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_next_clump8(&clump, &merged, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0b1001_1000), clump);
    try std.testing.expectEqual(bitmap.bits_per_long - 8, find_bit.find_next_clump8(&clump, &merged, nbits, bitmap.bits_per_long - 8));
    try std.testing.expect((clump & 0x80) != 0);

    const has_andnot = bitmap.bitmap_andnot(&masked, &merged, &left, nbits);
    try std.testing.expect(has_andnot);
    try std.testing.expectEqual(@as(usize, 7), find_bit.find_first_bit(&masked, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 4), find_bit.find_next_bit(&masked, nbits, 8));
    try expectRenderedSuffix(&masked, nbits, "68-70");

    var label = [_]u8{ ' ', 'w', 'e', 'i', 'g', 'h', 't', 'e', 'd', '-', 'o', 'r', '-', '8', ' ', '\n', 0, 0 };
    const trimmed = string.strim(&label);
    try std.testing.expect(string.sysfs_streq(trimmed, "weighted-or-8"));
    try std.testing.expectEqual(@as(usize, "weighted-or-8".len), string.strreplace(trimmed, '-', '_'));
    try std.testing.expect(string.strstarts(trimmed, "weighted"));

    var entries = [_]Entry{
        .{ .key = 7, .slot = 0 },
        .{ .key = bitmap.bits_per_long + 4, .slot = 1 },
        .{ .key = bitmap.bits_per_long + 6, .slot = 2 },
        .{ .key = 3, .slot = 3 },
    };
    var root = RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, entryLess);
    }

    try std.testing.expectEqual(@as(?struct { usize, usize }, .{ 3, 3 }), firstIdentity(&root));
    try std.testing.expectEqual(@as(?struct { usize, usize }, .{ 7, 0 }), blk: {
        const promoted = rbtree.rb_erase_cached(&entries[3].node, &root) orelse break :blk null;
        const entry: *const Entry = @fieldParentPtr("node", promoted);
        break :blk .{ entry.key, entry.slot };
    });
    try std.testing.expectEqual(@as(?struct { usize, usize }, .{ 7, 0 }), firstIdentity(&root));

    rbtree.rb_erase_init_cached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?struct { usize, usize }, .{ bitmap.bits_per_long + 4, 1 }), firstIdentity(&root));
}
