const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap tail copy subset and render replay" {
    const nbits = bitmap.bits_per_long + 5;
    const boundary = bitmap.bits_per_long;

    var src = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&src, boundary - 1, 2);
    bitmap.setRange(&src, boundary + 4, 1);
    src[1] |= @as(bitmap.Word, 1) << 9;

    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };
    bitmap.copyClearTail(&direct, &src, nbits);
    bitmap.bitmap_copy_clear_tail(&alias, &src, nbits);

    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct[1] & ~bitmap.lastWordMask(nbits));

    const superset = [_]bitmap.Word{
        direct[0],
        direct[1] | (@as(bitmap.Word, 1) << 1),
    };
    try std.testing.expect(bitmap.subset(&direct, &superset, nbits));
    try std.testing.expect(bitmap.intersects(&direct, &superset, nbits));

    var rendered: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&direct, nbits, &rendered);
    var alias_rendered: [64]u8 = undefined;
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, &alias_rendered);
    try std.testing.expectEqual(direct_len, alias_len);

    var expected: [48]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{ boundary - 1, boundary, boundary + 4 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..direct_len]);
    try std.testing.expectEqualStrings(expected_text, alias_rendered[0..alias_len]);
}

test "phase1 helper ports A find_bit tail clump and last-bit replay" {
    const nbits = find_bit.bits_per_long + 5;
    const boundary = find_bit.bits_per_long;
    const tail_mask = find_bit.lastWordMask(nbits);

    const bitmap_words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 9),
    };
    const gate_words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 9),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findFirstClump8(&clump, &bitmap_words, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextAndNotBit(&bitmap_words, &gate_words, nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findLastBit(&bitmap_words, nbits));

    const shared = [_]find_bit.Word{
        0,
        bitmap_words[1] & gate_words[1] & tail_mask,
    };
    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.findFirstAndBit(&bitmap_words, &gate_words, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.findFirstBit(&shared, nbits));
}

test "phase1 helper ports A string prefix suffix and match replay" {
    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix("prefix-mode", "prefix"));
    try std.testing.expect(string.strstarts("prefix-mode", "prefix"));
    try std.testing.expect(string.strEndsWith("prefix-mode", "mode"));
    try std.testing.expectEqual(@as(?usize, 7), string.strnchr("prefix-mode", 11, 'm'));

    const sysfs = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs[0..], "auto"));

    const exact = [_][]const u8{
        &[_]u8{ 'p', 'r', 'e', 0, 'x' },
        "prefix",
        "mode",
    };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(exact[0..], "prefix"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(exact[0..], "pref"));
}

test "phase1 helper ports A rbtree cached iterator and postorder replay" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const key_cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 15, .serial = 3 },
        .{ .key = 10, .serial = 4 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    const needle = @as(i32, 10);
    var iter = rbtree.matchIterator(&needle, &root.root, key_cmp);
    var serials: [3]usize = undefined;
    var match_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[match_count] = entry.serial;
        match_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), match_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..match_count]);

    const promoted = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), promoted);
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var postorder_count: usize = 0;
    var current = rbtree.firstPostorder(&root.root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        postorder_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 4), postorder_count);
}
