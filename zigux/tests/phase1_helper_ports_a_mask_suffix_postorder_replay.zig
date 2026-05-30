const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Entry = struct {
    key: usize,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn appendPostorder(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var current = rbtree.rb_first_postorder(root);
    while (current) |node| : (current = rbtree.rb_next_postorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.serial;
        count += 1;
    }
    return count;
}

test "mask-generated bitmap window drives find-bit and string suffix checks" {
    const nbits = bitmap.bits_per_long + 9;
    var requested = [_]bitmap.Word{ 0, 0 };
    var available = [_]bitmap.Word{ 0, 0 };
    var combined = [_]bitmap.Word{ 0, 0 };

    bitmap.bitmap_set(&requested, 3, 2);
    bitmap.bitmap_set(&requested, bitmap.bits_per_long + 4, 2);
    bitmap.bitmap_set(&available, 4, 1);
    bitmap.bitmap_set(&available, bitmap.bits_per_long + 5, 1);
    bitmap.bitmap_set(&available, bitmap.bits_per_long + 8, 1);

    try std.testing.expect(bitmap.bitmap_and(&combined, &requested, &available, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&combined, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.find_first_bit(&combined, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 5), find_bit.find_next_bit(&combined, nbits, 5));
    try std.testing.expectEqual(nbits, find_bit.find_next_bit(&combined, nbits, bitmap.bits_per_long + 6));

    var label = [_]u8{ ' ', 'm', 'a', 's', 'k', '-', 's', 'u', 'f', 'f', 'i', 'x', '-', 'p', 'o', 's', 't', 'o', 'r', 'd', 'e', 'r', '\n', 0 };
    const trimmed = string.strim(&label);
    try std.testing.expect(string.strstarts(trimmed, "mask"));
    try std.testing.expect(string.str_ends_with(trimmed, "postorder"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&[_][]const u8{ "prefix", "mask-suffix-postorder", "other" }, trimmed));
}

test "bitmap-selected rbtree entries keep cached leftmost and postorder aliases stable" {
    const nbits = bitmap.bits_per_long + 8;
    var selection = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_set(&selection, 2, 1);
    bitmap.bitmap_set(&selection, 7, 1);
    bitmap.bitmap_set(&selection, bitmap.bits_per_long + 3, 1);

    var entries = [_]Entry{
        .{ .key = find_bit.find_first_bit(&selection, nbits), .serial = 0 },
        .{ .key = find_bit.find_next_bit(&selection, nbits, 3), .serial = 1 },
        .{ .key = find_bit.find_next_bit(&selection, nbits, 8), .serial = 2 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.rb_last(&root.root));

    const wanted = entries[1].key;
    const found = rbtree.find(&wanted, &root.root, keyCmp) orelse return error.MissingMatch;
    try std.testing.expectEqual(@as(usize, 1), (@as(*const Entry, @fieldParentPtr("node", found))).serial);

    var postorder_before: [3]usize = undefined;
    try std.testing.expectEqual(@as(usize, 3), appendPostorder(&root.root, &postorder_before));

    rbtree.rb_erase_init_cached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));

    var postorder_after: [2]usize = undefined;
    const after_count = appendPostorder(&root.root, &postorder_after);
    try std.testing.expectEqual(@as(usize, 2), after_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 1 }, postorder_after[0..after_count]);
}
