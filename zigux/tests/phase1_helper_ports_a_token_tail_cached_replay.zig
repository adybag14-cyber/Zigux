const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string_lib = @import("string");

const Word = bitmap.Word;

const Entry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn lessByKey(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn keyOf(node: *const rbtree.Node) i32 {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

test "phase1 helper ports A replay token tail bitmap and cached rbtree state" {
    var tokens = [_]u8{ ' ', '3', '-', '5', ',', '6', 0, 'x' };
    const trimmed = string_lib.strim(tokens[0..]);
    try std.testing.expectEqualStrings("3-5,6", trimmed);
    try std.testing.expectEqual(@as(?usize, 1), string_lib.strnchr(trimmed, trimmed.len, '-'));
    try std.testing.expectEqual(@as(?usize, 3), string_lib.strnchr(trimmed, trimmed.len, ','));
    try std.testing.expect(string_lib.strEndsWith(trimmed, "6"));

    const comma = string_lib.strnchr(trimmed, trimmed.len, ',') orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("3-5", trimmed[0..comma]);
    try std.testing.expectEqualStrings("6", trimmed[comma + 1 ..]);

    const nbits = bitmap.bits_per_long + 6;
    var map = [_]Word{ 0, 0 };
    bitmap.bitmap_set(&map, 3, 4);
    bitmap.bitmap_set(&map, bitmap.bits_per_long + 3, 1);
    map[1] |= @as(Word, 1) << 9;

    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(&map, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.find_first_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.find_next_bit(&map, nbits, 4));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 3), find_bit.find_last_bit(&map, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_clump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0111_1000), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), find_bit.find_next_clump8(&clump, &map, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    var printed: [32]u8 = undefined;
    const printed_len = bitmap.bitmap_scnprintf(&map, nbits, &printed);
    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "3-6,{d}",
        .{bitmap.bits_per_long + 3},
    );
    try std.testing.expectEqualStrings(expected_text, printed[0..printed_len]);

    var entries = [_]Entry{
        .{ .key = @intCast(find_bit.find_first_bit(&map, nbits)) },
        .{ .key = @intCast(find_bit.find_next_bit(&map, nbits, 4)) },
        .{ .key = @intCast(find_bit.find_last_bit(&map, nbits)) },
    };
    var root = rbtree.RootCached.init();
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_add_cached(&entries[1].node, &root, lessByKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_add_cached(&entries[0].node, &root, lessByKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&entries[2].node, &root, lessByKey));
    try std.testing.expectEqual(@as(i32, 3), keyOf(rbtree.rb_first_cached(&root).?));

    rbtree.rb_erase_init_cached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(i32, 4), keyOf(rbtree.rb_first_cached(&root).?));
    try std.testing.expectEqual(rbtree.rb_first(&root.root), rbtree.rb_first_cached(&root));
}
