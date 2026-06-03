const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "copy extend tail clump feeds string match and cached erase replay" {
    const nbits = bits_per_long + 5;
    var src = [_]Word{
        (@as(Word, 1) << 3) | (@as(Word, 1) << 14),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
    };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };

    bitmap.copyAndExtend(&dst, &src, nbits, bits_per_long * 3);
    try std.testing.expectEqual(src[0], dst[0]);
    try std.testing.expectEqual(@as(Word, 0b10100), dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[2]);
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&dst, bits_per_long * 3));

    var clump: u8 = 0xaa;
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextClump8(&clump, &dst, bits_per_long * 3, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0001_0100), clump);
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&dst, nbits, bits_per_long + 5));

    const labels = [_][]const u8{
        "idle",
        "tail-clump\n",
        "cached-erase",
    };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&labels, "tail-clump"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&labels, "tail-clump"));

    var tree = CachedTree.init();
    for (&tree.entries) |*entry| {
        tree.insert(entry);
    }

    try std.testing.expectEqual(@as(i32, 3), tree.keyOf(rbtree.firstCached(&tree.root).?));
    try std.testing.expectEqual(@as(i32, 42), tree.keyOf(rbtree.last(&tree.root.root).?));

    const erased_leftmost = rbtree.eraseCached(&tree.entries[0].node, &tree.root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &tree.entries[2].node), erased_leftmost);
    try std.testing.expectEqual(@as(i32, 9), tree.keyOf(rbtree.firstCached(&tree.root).?));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&tree.root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        order[count] = tree.keyOf(node);
        count += 1;
    }
    try std.testing.expectEqualSlices(i32, &[_]i32{ 9, 17, 42 }, order[0..count]);
}

const CachedTree = struct {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    root: rbtree.RootCached = rbtree.RootCached.init(),
    entries: [4]Entry = .{
        .{ .key = 3 },
        .{ .key = 42 },
        .{ .key = 9 },
        .{ .key = 17 },
    },

    fn init() CachedTree {
        return .{};
    }

    fn keyOf(_: *const CachedTree, node: *const rbtree.Node) i32 {
        const entry: *const Entry = @fieldParentPtr("node", node);
        return entry.key;
    }

    fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
        const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
        const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
        return lhs_entry.key < rhs_entry.key;
    }

    fn insert(self: *CachedTree, entry: *Entry) void {
        _ = rbtree.addCached(&entry.node, &self.root, less);
    }
};
