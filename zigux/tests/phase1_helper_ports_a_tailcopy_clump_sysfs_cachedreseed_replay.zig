const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "phase1 helper ports A tail copy keeps clumps and shared bits aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const src = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 5) | (@as(bitmap.Word, 1) << 9),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 7),
    };
    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };

    bitmap.copyClearTail(&direct, &src, nbits);
    bitmap.bitmap_copy_clear_tail(&alias, &src, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3)), direct[1]);
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&direct, nbits));

    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstBit(&direct, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextAndBit(&direct, &alias, nbits, find_bit.bits_per_long));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &direct, nbits));
    try std.testing.expectEqual(@as(u8, 0b0010_0000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&clump, &direct, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_1010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&clump, &direct, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(u8, 0b0000_1010), clump);
}

test "phase1 helper ports A sysfs and memtostr helpers keep C-string boundaries stable" {
    var padded = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 4), string.strscpyPad(padded[0..], "mode"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'm', 'o', 'd', 'e', 0 }, padded[0..]);

    var truncated = [_]u8{ 0xbb, 0xbb, 0xbb };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(truncated[0..], &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0 }, truncated[0..]);

    const haystack = [_][]const u8{ "off", "auto\n", "manual" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&[_][]const u8{ "boot", "cfg", "cfg" }, "cfg"));
}

test "phase1 helper ports A cached rbtree reseed keeps leftmost and duplicate ownership stable" {
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
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    var root_entry = Entry{ .key = 10, .serial = 0 };
    var leftmost_entry = Entry{ .key = 5, .serial = 1 };
    var right_entry = Entry{ .key = 15, .serial = 2 };
    var reseed_entry = Entry{ .key = 7, .serial = 3 };
    var duplicate_entry = Entry{ .key = 7, .serial = 4 };
    var root = rbtree.RootCached.init();

    _ = rbtree.addCached(&root_entry.node, &root, less);
    _ = rbtree.addCached(&leftmost_entry.node, &root, less);
    _ = rbtree.addCached(&right_entry.node, &root, less);

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&leftmost_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&leftmost_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed_entry.node), rbtree.addCached(&reseed_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    const existing = rbtree.findAddCached(&duplicate_entry.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &reseed_entry.node), existing);
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed_entry.node), rbtree.firstCached(&root));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 7, 10, 15 }, order[0..count]);
}
