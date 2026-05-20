const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 helper ports A replay keeps bitmap formatting and tail searches aligned" {
    const nbits = bitmap.bits_per_long + 8;
    const boundary = bitmap.bits_per_long - 2;

    var bounded = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&bounded, boundary, 5);
    bitmap.setRange(&bounded, bitmap.bits_per_long + 6, 1);
    bounded[1] |= @as(bitmap.Word, 1) << 12;

    try std.testing.expectEqual(boundary, find_bit.findFirstBit(&bounded, nbits));
    try std.testing.expectEqual(bitmap.bits_per_long + 6, find_bit.findLastBit(&bounded, nbits));

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&bounded, nbits, &rendered);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{ boundary, bitmap.bits_per_long + 2, bitmap.bits_per_long + 6 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);

    const tail_noise_only = [_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 12 };
    try std.testing.expectEqual(nbits, find_bit.findFirstBit(&tail_noise_only, nbits));
    try std.testing.expect(bitmap.subset(&tail_noise_only, &[_]bitmap.Word{ 0, 0 }, nbits));
}

test "lane06 helper ports A replay keeps shared string search and match boundaries pinned" {
    const sysfs_modes = [_][]const u8{
        "disabled",
        "auto\n",
        "manual",
        "auto",
    };
    const exact_modes = [_][]const u8{
        "disabled",
        "manual",
        "manual",
        "auto",
    };

    const auto_cstr = [_]u8{ 'a', 'u', 't', 'o', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs_modes, &auto_cstr));
    try std.testing.expectEqual(@as(?usize, 3), string.matchString(&exact_modes, &auto_cstr));

    const prefixed = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0, 'x' };
    const prefix = [_]u8{ 'p', 'r', 'e', 0, 'y' };
    const suffix = [_]u8{ 'f', 'i', 'x', 0, 'z' };
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&prefixed, &prefix));
    try std.testing.expect(string.strstarts(&prefixed, &prefix));
    try std.testing.expect(string.strEndsWith(&prefixed, &suffix));

    const counted = [_]u8{ 'a', 'b', '.', 'c', 0, '.', 'x' };
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&counted, 4, '.'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&counted, 2, '.'));

    var dirty = [_]u8{'x'} ** 24;
    dirty[17] = 'y';
    try std.testing.expectEqual(@as(?usize, 17), string.memchrInv(&dirty, 'x'));
}

test "lane06 helper ports A replay keeps postorder aliases on the same exact walk" {
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
        .{ .key = 4 },
        .{ .key = 2 },
        .{ .key = 6 },
        .{ .key = 1 },
        .{ .key = 3 },
        .{ .key = 5 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    try std.testing.expectEqual(rbtree.firstPostorder(&root), rbtree.rb_first_postorder(&root));

    var order: [6]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.firstPostorder(&root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 6), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 3, 2, 5, 6, 4 }, order[0..count]);

    var alias_order: [6]i32 = undefined;
    var alias_count: usize = 0;
    var alias_current = rbtree.rb_first_postorder(&root);
    while (alias_current) |node| : (alias_current = rbtree.rb_next_postorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_order[alias_count] = entry.key;
        alias_count += 1;
    }

    try std.testing.expectEqual(count, alias_count);
    try std.testing.expectEqualSlices(i32, order[0..count], alias_order[0..alias_count]);
    try std.testing.expect(rbtree.nextPostorder(null) == null);
    try std.testing.expect(rbtree.rb_next_postorder(null) == null);
}
