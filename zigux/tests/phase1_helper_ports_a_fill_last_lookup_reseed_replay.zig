const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap fill and clear aliases keep tail state and formatting aligned" {
    const nbits = bitmap.bits_per_long + 5;
    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };

    bitmap.fill(&direct, nbits);
    bitmap.bitmap_fill(&alias, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expect(bitmap.full(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_full(&alias, nbits));
    try std.testing.expectEqual(nbits, bitmap.weight(&direct, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weight(&alias, nbits));

    bitmap.clearRange(&direct, bitmap.bits_per_long + 1, 3);
    bitmap.bitmap_clear(&alias, bitmap.bits_per_long + 1, 3);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 2), bitmap.weight(&direct, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weight(&alias, nbits));

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&direct, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "0-{d},{d}",
        .{ bitmap.bits_per_long, bitmap.bits_per_long + 4 },
    );
    try std.testing.expectEqualStrings(expected_text, direct_buffer[0..direct_len]);
    try std.testing.expectEqualStrings(expected_text, alias_buffer[0..alias_len]);

    bitmap.zero(&direct, nbits);
    bitmap.bitmap_zero(&alias, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expect(bitmap.empty(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_empty(&alias, nbits));
}

test "phase1 helper ports A tail scans keep last-bit and andnot windows clamped" {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 1 };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findLastBit(&lhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &lhs, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &lhs, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "phase1 helper ports A string lookups keep newline aware matches and C-string boundaries" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));

    const exact_haystack = [_][]const u8{
        &[_]u8{ 'p', 'r', 'e', 0, 'x' },
        "prefix",
        "present",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(exact_haystack[0..], "pre"));
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&[_]u8{ 'p', 'r', 'e', 0, 'x' }, "pre"));
    try std.testing.expect(string.strstarts("prefix", "pre"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 3, 0));
}

test "phase1 helper ports A cached erase-init keeps leftmost handoff reusable" {
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

    var first_entry = Entry{ .key = 10 };
    var leftmost_entry = Entry{ .key = 5 };
    var right_entry = Entry{ .key = 15 };
    var reseed_entry = Entry{ .key = 6 };
    var root = rbtree.RootCached.init();

    _ = rbtree.addCached(&first_entry.node, &root, less);
    _ = rbtree.addCached(&leftmost_entry.node, &root, less);
    _ = rbtree.addCached(&right_entry.node, &root, less);

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&leftmost_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&leftmost_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    _ = rbtree.addCached(&reseed_entry.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
