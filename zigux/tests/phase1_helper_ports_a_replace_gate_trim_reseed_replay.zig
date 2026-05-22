const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap replace and gate replay" {
    const nbits = bitmap.bits_per_long + 6;
    const boundary = bitmap.bits_per_long;

    const old = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) |
            (@as(bitmap.Word, 1) << 1) |
            (@as(bitmap.Word, 1) << (boundary - 1)),
        (@as(bitmap.Word, 1) << 1) |
            (@as(bitmap.Word, 1) << 5),
    };
    const new = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 2) |
            (@as(bitmap.Word, 1) << (boundary - 1)),
        (@as(bitmap.Word, 1) << 2) |
            (@as(bitmap.Word, 1) << 4),
    };
    const mask = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) |
            (@as(bitmap.Word, 1) << 2),
        (@as(bitmap.Word, 1) << 1) |
            (@as(bitmap.Word, 1) << 2) |
            (@as(bitmap.Word, 1) << 4),
    };

    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };
    bitmap.replace(&direct, &old, &new, &mask, nbits);
    bitmap.bitmap_replace(&alias, &old, &new, &mask, nbits);

    try std.testing.expect(bitmap.equal(&direct, &alias, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&direct, &alias, nbits));
    try std.testing.expectEqual(
        @as(bitmap.Word, ((old[1] & ~mask[1]) | (new[1] & mask[1])) & bitmap.lastWordMask(nbits)),
        direct[1],
    );

    const gate = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) |
            (@as(bitmap.Word, 1) << 2),
        (@as(bitmap.Word, 1) << 2) |
            (@as(bitmap.Word, 1) << 4),
    };
    var gated = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.andBits(&gated, &direct, &gate, nbits));
    try std.testing.expect(bitmap.subset(&gated, &direct, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&gated, nbits));
}

test "phase1 helper ports A find_bit gated scans replay" {
    const nbits = find_bit.bits_per_long + 6;
    const boundary = find_bit.bits_per_long;

    const words = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 7) |
            (@as(find_bit.Word, 1) << (boundary - 1)),
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4),
    };
    const gate = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << (boundary - 1)),
        (@as(find_bit.Word, 1) << 1),
    };

    try std.testing.expectEqual(@as(usize, boundary - 1), find_bit.findFirstAndBit(&words, &gate, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.findNextAndBit(&words, &gate, nbits, boundary));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findFirstAndNotBit(&words, &gate, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextAndNotBit(&words, &gate, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findLastBit(&words, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), find_bit.getValue8(&words, boundary));
}

test "phase1 helper ports A string trim and replace replay" {
    const spaced = " \tzig ux\n";
    try std.testing.expectEqualStrings("zig ux\n", string.skipSpaces(spaced));
    try std.testing.expectEqualStrings("zig ux\n", string.skip_spaces(spaced));

    var trimmed = [_]u8{ ' ', '\t', 'z', 'i', 'g', ' ', 'u', 'x', '\n', 0, 'x' };
    var alias_trimmed = trimmed;
    try std.testing.expectEqualStrings("zig ux", string.trimSpaces(trimmed[0..]));
    try std.testing.expectEqualStrings("zig ux", string.strstrip(alias_trimmed[0..]));

    var compact = [_]u8{ ' ', 'z', ' ', 'i', ' ', 'g', ' ', 0, 'x' };
    var alias_compact = compact;
    try std.testing.expectEqualStrings("zig", string.removeSpaces(compact[0..]));
    try std.testing.expectEqualStrings("zig", string.remove_spaces(alias_compact[0..]));

    var replaced = [_]u8{ 'z', 'i', 'g', '-', 'u', 'x', 0, 'x' };
    var alias_replaced = replaced;
    try std.testing.expectEqual(@as(usize, 6), string.replaceChar(replaced[0..], '-', '_'));
    try std.testing.expectEqual(@as(usize, 6), string.strreplace(alias_replaced[0..], '-', '_'));
    try std.testing.expectEqualSlices(u8, &replaced, &alias_replaced);
    try std.testing.expectEqualStrings("zig_ux", replaced[0..6]);
}

test "phase1 helper ports A rbtree duplicate detach and reseed replay" {
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

    const cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    var root_entry = Entry{ .key = 8 };
    var left_entry = Entry{ .key = 4 };
    var right_entry = Entry{ .key = 12 };
    var middle_entry = Entry{ .key = 10 };
    var last_entry = Entry{ .key = 14 };
    var duplicate_entry = Entry{ .key = 12 };
    var root = rbtree.Root.init();

    for (&[_]*Entry{ &root_entry, &left_entry, &right_entry, &middle_entry, &last_entry }) |entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = rbtree.findAdd(&duplicate_entry.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &right_entry.node), duplicate);
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_entry.node), rbtree.first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &last_entry.node), rbtree.last(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &right_entry.node), rbtree.prev(&last_entry.node));

    rbtree.eraseInit(&left_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&left_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.first(&root));

    left_entry.key = 6;
    rbtree.add(&left_entry.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_entry.node), rbtree.first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_entry.node), rbtree.prev(&root_entry.node));
}
