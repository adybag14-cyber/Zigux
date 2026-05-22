const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap complement and render replay" {
    const nbits = bitmap.bits_per_long + 5;
    const boundary = bitmap.bits_per_long;

    var src = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&src, 0, 2);
    bitmap.setRange(&src, boundary + 1, 1);
    src[1] |= @as(bitmap.Word, 1) << 9;

    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };
    bitmap.complement(&direct, &src, nbits);
    bitmap.bitmap_complement(&alias, &src, nbits);

    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct[1]);

    try std.testing.expectEqual(boundary + 2, bitmap.weight(&direct, nbits));
    try std.testing.expect(bitmap.intersects(&direct, &[_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 2 }, nbits));
    try std.testing.expect(bitmap.subset(&[_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 2 }, &direct, nbits));

    var rendered: [96]u8 = undefined;
    var alias_rendered: [96]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&direct, nbits, &rendered);
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, &alias_rendered);
    try std.testing.expectEqual(rendered_len, alias_len);

    var expected: [48]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "2-{d},{d}-{d}",
        .{ boundary, boundary + 2, boundary + 4 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);
    try std.testing.expectEqualStrings(expected_text, alias_rendered[0..alias_len]);
}

test "phase1 helper ports A find_bit zero and clump replay" {
    const nbits = find_bit.bits_per_long + 5;
    const boundary = find_bit.bits_per_long;

    const zero_words = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << 4),
    };
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findFirstZeroBit(&zero_words, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.find_first_zero_bit(&zero_words, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextZeroBit(&zero_words, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.find_next_zero_bit(&zero_words, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_zero_bit(&zero_words, nbits, nbits));

    const clump_words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4),
    };

    var direct_clump: u8 = 0;
    var alias_clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextClump8(&direct_clump, &clump_words, nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_next_clump8(&alias_clump, &clump_words, nbits, boundary + 2));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findLastBit(&clump_words, nbits));
}

test "phase1 helper ports A string pad sysfs and dirty-byte replay" {
    var direct = [_]u8{ 1, 1, 1, 1, 1, 1 };
    var alias = [_]u8{ 1, 1, 1, 1, 1, 1 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(direct[0..], &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(alias[0..], &[_]u8{ 'o', 'k', 0, 'y' }));
    try std.testing.expectEqualSlices(u8, &direct, &alias);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, direct[0..]);

    const sysfs = [_][]const u8{ "off", "auto\n", "manual" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs[0..], "auto"));

    const exact = [_][]const u8{
        &[_]u8{ 'm', 'a', 'n', 0, 'x' },
        "manual",
        "auto",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(exact[0..], "man"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(exact[0..], "man"));

    var dirty = [_]u8{'a'} ** 24;
    dirty[@sizeOf(usize)] = 'b';
    try std.testing.expectEqual(@as(?usize, @sizeOf(usize)), string.memchrInv(dirty[0..], 'a'));
    try std.testing.expectEqual(string.memchrInv(dirty[0..], 'a'), string.memchr_inv(dirty[0..], 'a'));
}

test "phase1 helper ports A rbtree cached erase-init replay" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

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
    var duplicate_entry = Entry{ .key = 10, .serial = 3 };
    var replacement_entry = Entry{ .key = 15, .serial = 4 };
    var reseed_entry = Entry{ .key = 4, .serial = 5 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&root_entry.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&leftmost_entry.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.firstCached(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&right_entry.node, &root, cmp));
    const duplicate = rbtree.findAddCached(&duplicate_entry.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), duplicate);
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&right_entry.node, &replacement_entry.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&leftmost_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&leftmost_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&root_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&root_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&replacement_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&reseed_entry.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
