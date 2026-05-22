const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap boundary fill clear and equality replay" {
    const nbits = bitmap.bits_per_long;
    const start = bitmap.bits_per_long - 2;
    const len = bitmap.bits_per_long + 4;
    var direct = [_]bitmap.Word{ 0, 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0, 0 };

    bitmap.setRange(&direct, start, len);
    bitmap.bitmap_set(&alias, start, len);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(bitmap.firstWordMask(start), direct[0]);
    try std.testing.expectEqual(~@as(bitmap.Word, 0), direct[1]);
    try std.testing.expectEqual(bitmap.lastWordMask(start + len), direct[2]);

    const exact_lhs = [_]bitmap.Word{ 0b1011, @as(bitmap.Word, 1) << 7 };
    const exact_rhs = [_]bitmap.Word{ 0b1011, @as(bitmap.Word, 1) << 13 };
    try std.testing.expect(bitmap.equal(&exact_lhs, &exact_rhs, nbits));

    bitmap.clearRange(&direct, start, len);
    bitmap.bitmap_clear(&alias, start, len);
    try std.testing.expectEqualSlices(bitmap.Word, &[_]bitmap.Word{ 0, 0, 0 }, &direct);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
}

test "phase1 helper ports A find_bit inclusive boundary replay" {
    const head_boundary = find_bit.bits_per_long - 1;
    const head_nbits = find_bit.bits_per_long * 2;
    const head_set = [_]find_bit.Word{ @as(find_bit.Word, 1) << @intCast(head_boundary), 0 };
    const head_zero = [_]find_bit.Word{ ~(@as(find_bit.Word, 1) << @intCast(head_boundary)), ~@as(find_bit.Word, 0) };
    try std.testing.expectEqual(@as(usize, head_boundary), find_bit.findNextBit(&head_set, head_nbits, head_boundary));
    try std.testing.expectEqual(@as(usize, head_boundary), find_bit.findNextZeroBit(&head_zero, head_nbits, head_boundary));

    const tail_bits: usize = 5;
    const tail_boundary = find_bit.bits_per_long + tail_bits - 1;
    const tail_nbits = tail_boundary + 1;
    const tail_set = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << @intCast(tail_bits - 1)) | (@as(find_bit.Word, 1) << @intCast(tail_bits + 2)),
    };
    const tail_andnot_lhs = tail_set;
    const tail_andnot_rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << @intCast(tail_bits + 2) };
    try std.testing.expectEqual(@as(usize, tail_boundary), find_bit.findNextBit(&tail_set, tail_nbits, tail_boundary));
    try std.testing.expectEqual(@as(usize, tail_boundary), find_bit.findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, tail_nbits, tail_boundary));
    try std.testing.expectEqual(@as(usize, tail_nbits), find_bit.findNextBit(&tail_set, tail_nbits, tail_boundary + 1));
}

test "phase1 helper ports A string span and nul-search replay" {
    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix("prefix-mode", "prefix"));
    try std.testing.expect(string.strstarts("prefix-mode", "prefix"));
    try std.testing.expect(string.strEndsWith("prefix-mode", "mode"));
    try std.testing.expectEqual(@as(?usize, 7), string.strnchr("prefix-mode", 11, 'm'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));

    const sysfs = [_][]const u8{ "manual\n", "auto", "off" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(sysfs[0..], "manual"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(sysfs[0..], "manual"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(sysfs[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(sysfs[0..], "auto"));
}

test "phase1 helper ports A rbtree cached replacement and reseed replay" {
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

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 20 },
    };
    var replacement = Entry{ .key = 20 };
    var reseed = Entry{ .key = 6 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    rbtree.replaceNodeCached(&entries[2].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);

    _ = rbtree.addCached(&reseed.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
