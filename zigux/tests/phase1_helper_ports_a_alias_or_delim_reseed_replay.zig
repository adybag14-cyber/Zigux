const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap aliases ignore exact-word overflow storage" {
    const nbits = bitmap.bits_per_long;
    const lhs = [_]bitmap.Word{ 0b1011, @as(bitmap.Word, 1) << 4 };
    const rhs = [_]bitmap.Word{ 0b1011, @as(bitmap.Word, 1) << 9 };
    const outside_only = [_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 7 };
    var direct = [_]bitmap.Word{ 0xaaaa, 0xbbbb };
    var alias = [_]bitmap.Word{ 0xcccc, 0xdddd };

    try std.testing.expect(bitmap.equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expect(!bitmap.intersects(&outside_only, &outside_only, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&outside_only, &[_]bitmap.Word{ 0, 0 }, nbits));

    try std.testing.expect(!bitmap.andNotBits(&direct, &lhs, &rhs, nbits));
    try std.testing.expect(!bitmap.bitmap_andnot(&alias, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), alias[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0xbbbb), direct[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0xdddd), alias[1]);
}

test "phase1 helper ports A find_bit and-scan aliases clamp after the last live tail bit" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 6;
    const lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 10) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 11) };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5));

    try std.testing.expectEqual(
        find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
        find_bit.find_next_and_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
}

test "phase1 helper ports A string aliases keep prefix and match helpers on C-string boundaries" {
    const prefixed = [_]u8{ 'm', 'o', 'd', 'e', 0, '=' };
    const prefix = [_]u8{ 'm', 'o', 0, 'x' };
    const newline_mode = [_]u8{ 'm', 'o', 'd', 'e', '\n', 0 };
    const plain_mode = [_]u8{ 'm', 'o', 'd', 'e', 0 };
    const haystack = [_][]const u8{ "off", &newline_mode, "mode", "on" };

    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix(&prefixed, "mode"));
    try std.testing.expectEqual(@as(usize, 2), string.str_has_prefix(&prefixed, &prefix));
    try std.testing.expect(string.sysfsStreq(&newline_mode, &plain_mode));
    try std.testing.expect(string.sysfs_streq(&newline_mode, &plain_mode));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&haystack, "mode"));
    try std.testing.expectEqual(@as(?usize, 2), string.matchString(&haystack, "mode"));
}

test "phase1 helper ports A rbtree cached erase-init aliases reseed leftmost in order" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;
    const keyOf = struct {
        fn read(node: *const rbtree.Node) i32 {
            const entry: *const Entry = @fieldParentPtr("node", node);
            return entry.key;
        }
    }.read;

    var root = rbtree.RootCached.init();
    var middle = Entry{ .key = 10 };
    var left = Entry{ .key = 5 };
    var right = Entry{ .key = 15 };

    _ = rbtree.rb_add_cached(&middle.node, &root, less);
    _ = rbtree.rb_add_cached(&left.node, &root, less);
    _ = rbtree.rb_add_cached(&right.node, &root, less);

    try std.testing.expectEqual(@as(i32, 5), keyOf(rbtree.rb_first_cached(&root).?));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.rb_first_cached(&root));

    rbtree.rb_erase_init_cached(&left.node, &root);
    try std.testing.expect(rbtree.emptyNode(&left.node));
    try std.testing.expectEqual(@as(i32, 10), keyOf(rbtree.rb_first_cached(&root).?));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.rb_first_cached(&root));

    rbtree.rb_erase_init_cached(&middle.node, &root);
    try std.testing.expect(rbtree.emptyNode(&middle.node));
    try std.testing.expectEqual(@as(i32, 15), keyOf(rbtree.rb_first_cached(&root).?));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.rb_first_cached(&root));
}
