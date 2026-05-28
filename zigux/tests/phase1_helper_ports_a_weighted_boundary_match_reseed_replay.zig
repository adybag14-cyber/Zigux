const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A weighted bitmap helpers clamp partial tails consistently" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8) };
    const rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9) };
    var or_dst = [_]bitmap.Word{ 0, 0 };
    var xor_dst = [_]bitmap.Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 3), bitmap.weightedOr(&or_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 9)), or_dst[1]);
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&or_dst, nbits));

    try std.testing.expectEqual(@as(usize, 2), bitmap.weightedXor(&xor_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 8) | (@as(bitmap.Word, 1) << 9)), xor_dst[1]);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&xor_dst, nbits));
}

test "phase1 helper ports A inclusive find_bit boundary scans keep the last in-range bit reachable" {
    const boundary = find_bit.bits_per_long - 1;
    const nbits = find_bit.bits_per_long * 2;
    const set_map = [_]find_bit.Word{ (@as(find_bit.Word, 1) << @intCast(boundary)), 0 };
    const and_lhs = [_]find_bit.Word{ (@as(find_bit.Word, 1) << @intCast(boundary)), 0 };
    const and_rhs = [_]find_bit.Word{ (@as(find_bit.Word, 1) << @intCast(boundary)), 0 };
    const andnot_lhs = [_]find_bit.Word{ (@as(find_bit.Word, 1) << 5) | (@as(find_bit.Word, 1) << @intCast(boundary)), 0 };
    const andnot_rhs = [_]find_bit.Word{ @as(find_bit.Word, 1) << 5, 0 };
    const zero_map = [_]find_bit.Word{ ~(@as(find_bit.Word, 1) << @intCast(boundary)), ~@as(find_bit.Word, 0) };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextBit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextZeroBit(&zero_map, nbits, boundary));

    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&set_map, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, boundary + 1));
}

test "phase1 helper ports A string match helpers preserve first-match order across newline-aware tables" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    const literal_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
        "beta",
    };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs_haystack, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&sysfs_haystack, "auto\n"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(&[_][]const u8{"off"}, "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(&literal_haystack, "a"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&literal_haystack, "beta"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&literal_haystack, "missing"));
}

test "phase1 helper ports A cached rbtree helpers reseed leftmost state after detach" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    var first_entry = Entry{ .key = 10, .serial = 0 };
    var second_entry = Entry{ .key = 6, .serial = 1 };
    var alias_entry = Entry{ .key = 4, .serial = 2 };
    var root = rbtree.RootCached.init();

    _ = rbtree.addCached(&first_entry.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&first_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&first_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));

    _ = rbtree.addCached(&second_entry.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &second_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.rb_erase_init_cached(&second_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&second_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entry.node), rbtree.rb_add_cached(&alias_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entry.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(rbtree.rb_first(&root.root), rbtree.rb_first_cached(&root));
}
