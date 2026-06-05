const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "bitmap complement feeds clump scans and string matching" {
    const nbits = bitmap.bits_per_long + 9;
    var map = [_]bitmap.Word{ 0, 0 };
    var inverse = [_]bitmap.Word{ 0, 0 };
    var range_buffer = [_]u8{0} ** 32;
    var label_buffer = [_]u8{0} ** 48;

    bitmap.bitmap_zero(&map, nbits);
    bitmap.bitmap_set(&map, 3, 5);
    bitmap.bitmap_set(&map, bitmap.bits_per_long + 1, 3);
    bitmap.bitmap_clear(&map, 4, 2);

    try std.testing.expectEqual(@as(usize, 6), bitmap.bitmap_weight(&map, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.find_first_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 6), find_bit.find_next_bit(&map, nbits, 4));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 3), find_bit.find_last_bit(&map, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_clump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0xc8), clump);
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), find_bit.find_next_clump8(&clump, &map, nbits, 8));
    try std.testing.expectEqual(@as(u8, 0x0e), clump);

    bitmap.bitmap_complement(&inverse, &map, nbits);
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_bit(&inverse, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.find_next_bit(&inverse, nbits, 4));
    try std.testing.expectEqual(@as(usize, 3), find_bit.find_first_andnot_bit(&map, &inverse, nbits));

    const rendered_len = bitmap.bitmap_scnprintf(&map, nbits, &range_buffer);
    try std.testing.expectEqualStrings("3,6-7,65-67", range_buffer[0..rendered_len]);

    _ = try std.fmt.bufPrint(&label_buffer, " \tbits:{s}\n", .{range_buffer[0..rendered_len]});
    const trimmed = string.strim(&label_buffer);
    try std.testing.expectEqualStrings("bits:3,6-7,65-67", trimmed);
    try std.testing.expect(string.sysfs_streq(trimmed, "bits:3,6-7,65-67\n"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(&.{ "bits:3,6-7,65-67", "other" }, "bits:3,6-7,65-67\n"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(&.{ "bits:3,6-7,65-67", "other" }, "bits:3,6-7,65-67\n"));
    try std.testing.expectEqual(@as(?usize, 4), string.memchr_inv("aaaaBaaaa", 'a'));
}

test "rbtree postorder and replacement stay aligned with bitmap-derived keys" {
    const Entry = struct {
        key: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var map = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_set(&map, 3, 1);
    bitmap.bitmap_set(&map, 6, 1);
    bitmap.bitmap_set(&map, bitmap.bits_per_long + 2, 1);

    var entries = [_]Entry{
        .{ .key = find_bit.find_first_bit(&map, bitmap.bits_per_long + 9) },
        .{ .key = find_bit.find_next_bit(&map, bitmap.bits_per_long + 9, 4) },
        .{ .key = find_bit.find_last_bit(&map, bitmap.bits_per_long + 9) },
    };
    var replacement = Entry{ .key = 6 };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var postorder_count: usize = 0;
    var cursor = rbtree.rb_first_postorder(&root);
    while (cursor) |node| : (cursor = rbtree.rb_next_postorder(node)) {
        _ = @as(*const Entry, @fieldParentPtr("node", node));
        postorder_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), postorder_count);

    rbtree.rb_replace_node(&entries[1].node, &replacement.node, &root);
    rbtree.eraseInit(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));

    var order: [2]usize = undefined;
    var count: usize = 0;
    cursor = rbtree.rb_first(&root);
    while (cursor) |node| : (cursor = rbtree.rb_next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 6, bitmap.bits_per_long + 2 }, order[0..count]);
}
