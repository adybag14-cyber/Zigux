const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

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

fn collectForward(root: *const rbtree.RootCached, out: []i32) usize {
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "scatter bitmap cursors feed trimmed strings and cached rbtree reseed" {
    const nbits = bits_per_long + 12;
    var map = [_]Word{ 0, 0 };

    bitmap.bitmap_set(&map, 2, 4);
    bitmap.bitmap_set(&map, 15, 3);
    bitmap.bitmap_set(&map, bits_per_long + 1, 5);
    bitmap.bitmap_clear(&map, 16, 1);

    try std.testing.expectEqual(@as(usize, 2), find_bit.find_first_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 6), find_bit.find_next_zero_bit(&map, nbits, 2));
    try std.testing.expectEqual(@as(usize, 15), find_bit.find_next_bit(&map, nbits, 6));
    try std.testing.expectEqual(@as(usize, bits_per_long + 5), find_bit.find_last_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 11), bitmap.bitmap_weight(&map, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_clump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0011_1100), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.find_next_clump8(&clump, &map, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0011_1110), clump);

    var rendered: [64]u8 = @splat(0);
    const rendered_len = bitmap.bitmap_scnprintf(&map, nbits, &rendered);
    try std.testing.expectEqualStrings("2-5,15,17,65-69", rendered[0..rendered_len]);

    var padded: [80]u8 = @splat(' ');
    padded[0] = ' ';
    @memcpy(padded[1 .. 1 + rendered_len], rendered[0..rendered_len]);
    padded[1 + rendered_len] = ' ';
    padded[2 + rendered_len] = '\n';
    padded[3 + rendered_len] = 0;

    const trimmed = string.strim(&padded);
    try std.testing.expectEqualStrings("2-5,15,17,65-69", trimmed);
    try std.testing.expect(string.strstarts(trimmed, "2-5"));
    try std.testing.expect(string.strEndsWith(trimmed, "65-69"));
    try std.testing.expectEqual(@as(?usize, 1), string.memchr_inv(trimmed[3..5], ','));

    var tokens = [_][]const u8{ "idle\n", trimmed, "active" };
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(tokens[0..], trimmed));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(tokens[0..], "idle"));

    var entries = [_]Entry{
        .{ .key = 17, .serial = 0 },
        .{ .key = 2, .serial = 1 },
        .{ .key = 69, .serial = 2 },
        .{ .key = 15, .serial = 3 },
        .{ .key = 5, .serial = 4 },
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));

    var order: [5]i32 = undefined;
    var count = collectForward(&root, &order);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 5, 15, 17, 69 }, order[0..count]);

    rbtree.rb_erase_init_cached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[4].node), rbtree.rb_first_cached(&root));

    var reseed = Entry{ .key = 1, .serial = 5 };
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.rb_add_cached(&reseed.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.rb_first_cached(&root));

    count = collectForward(&root, &order);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 5, 15, 17, 69 }, order[0..count]);
}
