const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap replace masks tail bits and keeps aliases aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const old = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 7),
    };
    const new = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 6),
    };
    const mask = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 6),
    };
    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };

    bitmap.replace(&direct, &old, &new, &mask, nbits);
    bitmap.__bitmap_replace(&alias, &old, &new, &mask, nbits);

    const expected = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 1) };
    try std.testing.expectEqualSlices(bitmap.Word, &expected, &direct);
    try std.testing.expectEqualSlices(bitmap.Word, &expected, &alias);
    try std.testing.expect(bitmap.equal(&direct, &alias, nbits));
    try std.testing.expect(bitmap.subset(&direct, &old, nbits) == false);
    try std.testing.expect(bitmap.intersects(&direct, &new, nbits));
}

test "phase1 helper ports A find_bit tail zero and andnot scans stay inclusive and exhausted correctly" {
    const nbits = find_bit.bits_per_long + 5;
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    const andnot_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) };
    const andnot_rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 4 };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit._find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, nbits));
}

test "phase1 helper ports A string pad and sysfs helpers keep c-string boundaries visible" {
    var padded = [_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
    const copied = string.strscpyPad(&padded, &[_]u8{ 'z', 'i', 'g', 0, 'x' });

    try std.testing.expectEqual(@as(isize, 3), copied);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 0, 0, 0 }, &padded);

    const sysfs_modes = [_][]const u8{ "off\n", "owner\n", "auto" };
    try std.testing.expect(string.sysfsStreq("owner\n", "owner"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_modes[0..], "owner"));

    const module_name = [_]u8{ 'l', 'a', 'n', 'e', '0', '6', '.', 'z', 'i', 'g', 0, 'x' };
    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix(&module_name, "lane06"));
    try std.testing.expect(string.strEndsWith(&module_name, ".zig"));

    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'b' };
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&cstr, cstr.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, 'c'));
}

test "phase1 helper ports A cached rbtree erase handoff preserves prev and postorder traversal anchors" {
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
        .{ .key = 5 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.eraseCached(&entries[1].node, &root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    const last = rbtree.last(&root.root).?;
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), last);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.prev(last));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.rb_prev(last));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.firstPostorder(&root.root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 6, 5 }, order[0..count]);
    try std.testing.expectEqual(rbtree.firstPostorder(&root.root), rbtree.rb_first_postorder(&root.root));
    try std.testing.expectEqual(rbtree.nextPostorder(rbtree.firstPostorder(&root.root)), rbtree.rb_next_postorder(rbtree.rb_first_postorder(&root.root)));
}
