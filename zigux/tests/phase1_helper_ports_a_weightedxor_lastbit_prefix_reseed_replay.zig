const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A weighted xor aliases keep tail counts honest" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8) };
    const rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9) };
    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };

    const direct_weight = bitmap.weightedXor(&direct, &lhs, &rhs, nbits);
    const alias_weight = bitmap.bitmap_weighted_xor(&alias, &lhs, &rhs, nbits);

    try std.testing.expectEqual(@as(usize, 2), direct_weight);
    try std.testing.expectEqual(direct_weight, alias_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 9)), direct[1]);
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4)), direct[1] & bitmap.lastWordMask(nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct, nbits));
}

test "phase1 helper ports A last-bit and next-bit helpers clamp declared tail windows" {
    const nbits = find_bit.bits_per_long + 5;
    const map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 10),
    };
    const boundary = find_bit.bits_per_long + 3;

    try std.testing.expectEqual(boundary, find_bit.findNextBit(&map, nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit.find_next_bit(&map, nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(boundary, find_bit.find_last_bit(&map, nbits));

    const cleared = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 10 };
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&cleared, nbits, boundary));
    try std.testing.expectEqual(nbits, find_bit.find_next_bit(&cleared, nbits, boundary));
    try std.testing.expectEqual(nbits, find_bit.findLastBit(&cleared, nbits));
    try std.testing.expectEqual(nbits, find_bit.find_last_bit(&cleared, nbits));
}

test "phase1 helper ports A prefix and match aliases preserve C-string and sysfs boundaries" {
    const prefix_cstr = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x' };
    const haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    const exact_haystack = [_][]const u8{
        &[_]u8{ 'm', 'o', 'd', 'e', 0, 'x' },
        "module",
    };

    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix(&prefix_cstr, "mode"));
    try std.testing.expectEqual(@as(usize, 4), string.str_has_prefix(&prefix_cstr, "mode"));
    try std.testing.expect(string.strstarts(&prefix_cstr, "mod"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(exact_haystack[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(exact_haystack[0..], "mode"));
}

test "phase1 helper ports A cached reseed aliases keep leftmost state reusable" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    var direct_first = Entry{ .key = 10, .serial = 0 };
    var alias_first = Entry{ .key = 10, .serial = 0 };
    var direct_reseed = Entry{ .key = 6, .serial = 1 };
    var alias_reseed = Entry{ .key = 6, .serial = 1 };

    var direct_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &direct_first.node), rbtree.addCached(&direct_first.node, &direct_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_first.node), rbtree.rb_add_cached(&alias_first.node, &alias_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &direct_first.node), rbtree.firstCached(&direct_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_first.node), rbtree.rb_first_cached(&alias_root));

    rbtree.eraseInitCached(&direct_first.node, &direct_root);
    rbtree.rb_erase_init_cached(&alias_first.node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&direct_first.node));
    try std.testing.expect(rbtree.emptyNode(&alias_first.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&direct_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_first_cached(&alias_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &direct_reseed.node), rbtree.addCached(&direct_reseed.node, &direct_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_reseed.node), rbtree.rb_add_cached(&alias_reseed.node, &alias_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &direct_reseed.node), rbtree.firstCached(&direct_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_reseed.node), rbtree.rb_first_cached(&alias_root));
    try std.testing.expectEqual(rbtree.first(&direct_root.root), rbtree.firstCached(&direct_root));
    try std.testing.expectEqual(rbtree.rb_first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
}
