const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap clear tail keeps find-bit zero and last scans in range" {
    const nbits = bits_per_long + 6;
    var map = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&map, bits_per_long - 2, 8);
    bitmap.bitmap_clear(&map, bits_per_long + 1, 3);
    map[1] |= @as(Word, 1) << 12;

    try std.testing.expectEqual(@as(usize, bits_per_long - 2), find_bit.find_first_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.find_next_zero_bit(&map, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 5), find_bit.find_last_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(&map, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long - 8), find_bit.find_next_clump8(&clump, &map, nbits, bits_per_long - 6));
    try std.testing.expect((clump & 0b1100_0000) != 0);
}

test "string NUL bounded searches keep sysfs matches distinct" {
    const path = [_]u8{ '/', 'd', 'e', 'v', '/', 'n', 'o', 'd', 'e', 0, '/', 'x' };

    try std.testing.expectEqual(@as(?usize, 0), string.strnchr(&path, path.len, '/'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&path, path.len, 'x'));

    const choices = [_][]const u8{ "manual", "auto\n", "auto", "off" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(choices[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(choices[0..], "auto"));
}

test "rbtree parent links survive cached replacement and iterator scans" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const @This() = @fieldParentPtr("node", lhs);
            const rhs_entry: *const @This() = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }

        fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
            const key: *const i32 = @ptrCast(@alignCast(key_ptr));
            const entry: *const @This() = @fieldParentPtr("node", node);
            if (key.* < entry.key) return -1;
            if (key.* > entry.key) return 1;
            return 0;
        }
    };

    var entries = [_]Entry{
        .{ .key = 20 },
        .{ .key = 10 },
        .{ .key = 30 },
        .{ .key = 25 },
        .{ .key = 40 },
    };
    var replacement = Entry{ .key = 10 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, Entry.less);
    }

    try std.testing.expectEqual(&entries[1].node, rbtree.rb_first_cached(&root).?);
    rbtree.rb_replace_node_cached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(&replacement.node, rbtree.firstCached(&root).?);
    try std.testing.expect(replacement.node.parent != &replacement.node);
    try std.testing.expect(!rbtree.emptyNode(&entries[1].node));

    const key: i32 = 25;
    var iter = rbtree.matchIterator(&key, &root.root, Entry.cmpKey);
    const found = iter.next().?;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(i32, 25), found_entry.key);
    try std.testing.expect(iter.next() == null);

    const promoted = rbtree.rb_erase_cached(&replacement.node, &root).?;
    try std.testing.expectEqual(&entries[0].node, promoted);
    rbtree.clearNode(&replacement.node);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
}
