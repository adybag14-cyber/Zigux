const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "bitmap list formatting preserves declared windows" {
    const nbits = bitmap.bits_per_long + 6;
    var map = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.empty(&map, nbits));

    bitmap.setRange(&map, 2, 3);
    bitmap.setRange(&map, bitmap.bits_per_long + 1, 2);

    var rendered = [_]u8{0} ** 32;
    const rendered_len = bitmap.scnprintf(&map, nbits, &rendered);

    var expected = [_]u8{0} ** 32;
    const expected_text = try std.fmt.bufPrint(&expected, "2-4,{d}-{d}", .{
        bitmap.bits_per_long + 1,
        bitmap.bits_per_long + 2,
    });

    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&map, nbits));
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);
}

test "find_bit andnot scans clamp starts and tail noise" {
    const nbits = find_bit.bits_per_long + 4;
    const tail_bit = @as(find_bit.Word, 1) << 2;
    const out_of_range_tail_noise = @as(find_bit.Word, 1) << 9;
    const lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 5),
        tail_bit | out_of_range_tail_noise,
    };
    const rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 5,
        out_of_range_tail_noise,
    };

    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 4));
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 3));
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, nbits));
}

test "string bool and memparse helpers keep Linux boundary behavior" {
    try std.testing.expect(try string.strtobool("YES"));
    try std.testing.expect(!(try string.strtobool("off")));
    try std.testing.expectError(error.Invalid, string.strtobool("o"));
    try std.testing.expectError(error.Invalid, string.strtobool(null));

    const parsed = string.memparse("0x10Ktail");
    try std.testing.expectEqual(@as(u64, 16 * 1024), parsed.value);
    try std.testing.expectEqualStrings("tail", parsed.rest);

    const invalid = string.memparse("not-a-number");
    try std.testing.expectEqual(@as(u64, 0), invalid.value);
    try std.testing.expectEqualStrings("not-a-number", invalid.rest);
}

test "rbtree cached replacement updates leftmost traversal and stale nodes can be cleared" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),

        fn fromNode(node: *const rbtree.Node) *const @This() {
            return @fieldParentPtr("node", node);
        }

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            return fromNode(lhs).key < fromNode(rhs).key;
        }
    };

    var entries = [_]Entry{
        .{ .key = 20 },
        .{ .key = 10 },
        .{ .key = 30 },
    };
    var replacement = Entry{ .key = 10 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(&entries[0].node, rbtree.rb_add_cached(&entries[0].node, &root, Entry.less).?);
    try std.testing.expectEqual(&entries[1].node, rbtree.rb_add_cached(&entries[1].node, &root, Entry.less).?);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[2].node, &root, Entry.less));

    try std.testing.expectEqual(&entries[1].node, rbtree.rb_first_cached(&root).?);

    rbtree.rb_replace_node_cached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(&replacement.node, rbtree.rb_first_cached(&root).?);

    const next_after_replacement = rbtree.rb_next(&replacement.node).?;
    try std.testing.expectEqual(@as(i32, 20), Entry.fromNode(next_after_replacement).key);

    rbtree.clearNode(&entries[1].node);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
}
