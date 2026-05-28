const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "phase1 helper ports A replay keeps bitmap replace tail masking and locator scans aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const old = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << @intCast(bitmap.bits_per_long - 1)),
        @as(bitmap.Word, 1) << 1,
    };
    const new = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << @intCast(bitmap.bits_per_long - 1)),
        (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 6),
    };
    const mask = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 2),
        (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 6),
    };
    var replaced = [_]bitmap.Word{ 0, 0 };

    bitmap.replace(&replaced, &old, &new, &mask, nbits);

    try std.testing.expectEqual(old[0] | (@as(bitmap.Word, 1) << 2), replaced[0]);
    try std.testing.expectEqual((@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3), replaced[1]);
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndNotBit(&replaced, &old, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 3), find_bit.findNextBit(&replaced, nbits, bitmap.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 3), find_bit.findLastBit(&replaced, nbits));
    try std.testing.expect(bitmap.intersects(&replaced, &new, nbits));
    try std.testing.expect(bitmap.subset(&[_]bitmap.Word{ @as(bitmap.Word, 1) << 2, @as(bitmap.Word, 1) << 3 }, &replaced, nbits));
}

test "phase1 helper ports A replay keeps newline-aware string matching separate from exact lookup order" {
    const entries = [_][]const u8{
        "mode\n",
        "mode",
        "mode-alt",
    };

    try std.testing.expect(string.sysfsStreq("mode\n", "mode"));
    try std.testing.expect(!string.streq("mode\n", "mode"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&entries, "mode"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&entries, "mode"));
    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix("mode-alt", "mode"));
    try std.testing.expect(string.strEndsWith("mode-alt", "alt"));
    try std.testing.expectEqual(@as(?usize, 4), string.strnchr("mode=value", 10, '='));
}

test "phase1 helper ports A replay keeps cached rbtree replacement aligned with duplicate-key locators" {
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

    const cmp = struct {
        fn compare(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
            const key: *const i32 = @ptrCast(@alignCast(key_ptr));
            const entry: *const Entry = @fieldParentPtr("node", node);
            return if (key.* < entry.key)
                -1
            else if (key.* > entry.key)
                1
            else
                0;
        }
    }.compare;

    var first_duplicate = Entry{ .key = 5, .serial = 0 };
    var second_duplicate = Entry{ .key = 5, .serial = 1 };
    var tail = Entry{ .key = 9, .serial = 2 };
    var replacement = Entry{ .key = 5, .serial = 99 };
    var root = rbtree.RootCached.init();

    _ = rbtree.addCached(&first_duplicate.node, &root, less);
    _ = rbtree.addCached(&second_duplicate.node, &root, less);
    _ = rbtree.addCached(&tail.node, &root, less);

    const needle: i32 = 5;
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_duplicate.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_duplicate.node), rbtree.findFirst(&needle, &root.root, cmp));

    var iterator = rbtree.matchIterator(&needle, &root.root, cmp);
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_duplicate.node), iterator.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, &second_duplicate.node), iterator.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iterator.next());

    rbtree.replaceNodeCached(&first_duplicate.node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.findFirst(&needle, &root.root, cmp));

    iterator = rbtree.matchIterator(&needle, &root.root, cmp);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), iterator.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, &second_duplicate.node), iterator.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iterator.next());
}
