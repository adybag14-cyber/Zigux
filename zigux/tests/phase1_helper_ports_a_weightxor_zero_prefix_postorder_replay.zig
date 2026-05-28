const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "phase1 helper ports A weighted xor and complement ignore tail noise" {
    const nbits = bitmap.bits_per_long + 6;
    const live_tail = @as(bitmap.Word, 1) << 5;
    const tail_noise = @as(bitmap.Word, 1) << 11;
    const lhs = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 7),
        (@as(bitmap.Word, 1) << 1) | live_tail | tail_noise,
    };
    const rhs = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 7) | (@as(bitmap.Word, 1) << 12),
        (@as(bitmap.Word, 1) << 4) | tail_noise,
    };

    var xor_map = [_]bitmap.Word{ 0, 0 };
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weighted_xor(&xor_map, &lhs, &rhs, nbits));
    try std.testing.expectEqual(lhs[0] ^ rhs[0], xor_map[0]);
    try std.testing.expectEqual((@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | live_tail, xor_map[1] & bitmap.lastWordMask(nbits));

    const expected = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 12),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | live_tail,
    };
    try std.testing.expect(bitmap.bitmap_equal(&xor_map, &expected, nbits));

    var complement = [_]bitmap.Word{ 0, ~@as(bitmap.Word, 0) };
    bitmap.bitmap_complement(&complement, &lhs, nbits);
    try std.testing.expectEqual(@as(bitmap.Word, 0), complement[1] & ~bitmap.lastWordMask(nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&complement, &lhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&expected, &[_]bitmap.Word{ ~@as(bitmap.Word, 0), bitmap.lastWordMask(nbits) }, nbits));
}

test "phase1 helper ports A zero scans clamp starts and declared windows" {
    const nbits = find_bit.bits_per_long + 6;
    var map = [_]find_bit.Word{ ~@as(find_bit.Word, 0), find_bit.lastWordMask(nbits) };
    map[0] &= ~(@as(find_bit.Word, 1) << 9);
    map[1] &= ~(@as(find_bit.Word, 1) << 3);

    try std.testing.expectEqual(@as(usize, 9), find_bit.findFirstZeroBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 9), find_bit.find_first_zero_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findNextZeroBit(&map, nbits, 10));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.find_next_zero_bit(&map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&map, nbits, find_bit.bits_per_long + 4));

    map[0] |= @as(find_bit.Word, 1) << 9;
    map[1] |= @as(find_bit.Word, 1) << 3;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findFirstZeroBit(&map, nbits));
}

test "phase1 helper ports A prefix and match helpers stop at C-string limits" {
    const embedded = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0, 'x' };
    const exact_prefix = [_]u8{ 'p', 'r', 'e', 0, 'z' };
    const too_long = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 'x', 0 };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&embedded, &exact_prefix));
    try std.testing.expect(string.strstarts(&embedded, &exact_prefix));
    try std.testing.expectEqual(@as(usize, 0), string.strHasPrefix(&embedded, &too_long));

    const haystack = [_][]const u8{
        &[_]u8{ 'm', 'a', 'n', 'u', 'a', 'l', 0, 'x' },
        &[_]u8{ 'a', 'u', 't', 'o', '\n' },
        &[_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0, 'y' },
        &[_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0, 'z' },
    };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&haystack, "auto"));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(&haystack, &embedded));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&haystack, &too_long));
}

test "phase1 helper ports A postorder keeps replacement traversal stable" {
    const Entry = struct {
        const Self = @This();

        key: i32,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Self = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Self = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    };

    var entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 12 },
        .{ .key = 2 },
        .{ .key = 6 },
    };
    var replacement = Entry{ .key = 4 };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, Entry.less);
    }

    rbtree.rb_replace_node(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.rb_first_postorder(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[4].node), rbtree.rb_next_postorder(&entries[3].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_next_postorder(&entries[4].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.rb_next_postorder(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_next_postorder(&entries[2].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_next_postorder(&entries[0].node));
}
