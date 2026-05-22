const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const expect = std.testing.expect;
const expectEqual = std.testing.expectEqual;
const expectEqualSlices = std.testing.expectEqualSlices;

test "lane06 replay keeps bitmap tail predicates and terminator slots aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const in_range_tail = (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3);
    const lhs = [_]bitmap.Word{
        0b1010,
        in_range_tail | (@as(bitmap.Word, 1) << 9),
    };
    const rhs = [_]bitmap.Word{
        0b1010,
        in_range_tail | (@as(bitmap.Word, 1) << 11),
    };
    const superset = [_]bitmap.Word{
        0b1110,
        in_range_tail | (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 13),
    };
    var buffer = [_]u8{0xaa};

    try expect(bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try expect(bitmap.bitmap_subset(&lhs, &superset, nbits));
    try expect(!bitmap.bitmap_subset(&superset, &lhs, nbits));

    const len = bitmap.bitmap_scnprintf(&lhs, nbits, buffer[0..1]);
    try expectEqual(@as(usize, 0), len);
    try expectEqual(@as(u8, 0), buffer[0]);
}

test "lane06 replay keeps find-bit boundary scans and tail clumps reachable" {
    const head_boundary = find_bit.bits_per_long - 1;
    const tail_bits: usize = 5;
    const tail_boundary = find_bit.bits_per_long + tail_bits - 1;
    const tail_nbits = tail_boundary + 1;
    const head_map = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << @intCast(head_boundary)),
        0,
    };
    const tail_map = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << @intCast(tail_bits - 1),
    };
    var clump: u8 = 0x5a;

    try expectEqual(
        @as(usize, head_boundary),
        find_bit.findNextBit(&head_map, find_bit.bits_per_long * 2, head_boundary),
    );
    try expectEqual(
        @as(usize, tail_boundary),
        find_bit.find_next_bit(&tail_map, tail_nbits, tail_boundary),
    );
    try expectEqual(
        @as(usize, tail_boundary),
        find_bit.findLastBit(&tail_map, tail_nbits),
    );
    try expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findFirstClump8(&clump, &tail_map, tail_nbits),
    );
    try expectEqual(@as(u8, 0b0001_0000), clump);
    try expectEqual(
        @as(usize, tail_nbits),
        find_bit.findNextClump8(&clump, &tail_map, tail_nbits, tail_nbits),
    );
    try expectEqual(@as(u8, 0b0001_0000), clump);
}

test "lane06 replay keeps C-string terminator helpers aligned at embedded NULs" {
    const cstr = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x', 'y' };
    const exact = [_]u8{ 'm', 'o', 'd', 'e', 0, 'z' };
    const suffix = [_]u8{ 'd', 'e', 0, 'w' };
    const sysfs_modes = [_][]const u8{ "auto\n", "mode", "mode\n" };
    const exact_modes = [_][]const u8{ &exact, "mode", "other" };

    try expect(string.streq(&cstr, &exact));
    try expectEqual(@as(usize, 4), string.strHasPrefix(&cstr, "mode"));
    try expect(string.strstarts(&cstr, "mode"));
    try expect(string.strEndsWith(&cstr, &suffix));
    try expectEqual(@as(?usize, 2), string.strnchr(&cstr, cstr.len, 'd'));
    try expectEqual(@as(?usize, 4), string.strnchr(&cstr, cstr.len, 0));
    try expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, 'x'));
    try expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs_modes, "mode"));
    try expectEqual(@as(?usize, 0), string.matchString(&exact_modes, "mode"));
}

test "lane06 replay keeps cached leftmost updates aligned with postorder traversal" {
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

    var leftmost = Entry{ .key = 1 };
    var root_entry = Entry{ .key = 2 };
    var right = Entry{ .key = 3 };
    var replacement = Entry{ .key = 4 };
    var root = rbtree.RootCached.init();

    _ = rbtree.addCached(&root_entry.node, &root, less);
    _ = rbtree.addCached(&leftmost.node, &root, less);
    _ = rbtree.addCached(&right.node, &root, less);

    var initial_postorder: [3]i32 = undefined;
    var initial_count: usize = 0;
    var cursor = rbtree.firstPostorder(&root.root);
    while (cursor) |node| : (cursor = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        initial_postorder[initial_count] = entry.key;
        initial_count += 1;
    }
    try expectEqual(@as(usize, 3), initial_count);
    try expectEqualSlices(i32, &[_]i32{ 1, 3, 2 }, initial_postorder[0..initial_count]);

    const promoted = rbtree.eraseCached(&leftmost.node, &root) orelse return error.TestUnexpectedResult;
    try expectEqual(@as(*rbtree.Node, &root_entry.node), promoted);
    try expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.rb_first_cached(&root));

    var after_erase_postorder: [2]i32 = undefined;
    var after_erase_count: usize = 0;
    cursor = rbtree.rb_first_postorder(&root.root);
    while (cursor) |node| : (cursor = rbtree.rb_next_postorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        after_erase_postorder[after_erase_count] = entry.key;
        after_erase_count += 1;
    }
    try expectEqual(@as(usize, 2), after_erase_count);
    try expectEqualSlices(i32, &[_]i32{ 3, 2 }, after_erase_postorder[0..after_erase_count]);

    rbtree.rb_replace_node_cached(&right.node, &replacement.node, &root);
    try expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.firstCached(&root));
    try expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.first(&root.root));

    var final_postorder: [2]i32 = undefined;
    var final_count: usize = 0;
    cursor = rbtree.firstPostorder(&root.root);
    while (cursor) |node| : (cursor = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        final_postorder[final_count] = entry.key;
        final_count += 1;
    }
    try expectEqual(@as(usize, 2), final_count);
    try expectEqualSlices(i32, &[_]i32{ 4, 2 }, final_postorder[0..final_count]);
}
