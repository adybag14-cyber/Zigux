const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap replace keeps masked tail semantics aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const old = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 7),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    const new = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 7),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8),
    };
    const mask = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 7),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8),
    };
    const expected = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 7),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4),
    };

    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };
    bitmap.replace(&direct, &old, &new, &mask, nbits);
    bitmap.bitmap_replace(&alias, &old, &new, &mask, nbits);

    try std.testing.expect(bitmap.equal(&direct, &expected, nbits));
    try std.testing.expect(bitmap.equal(&alias, &expected, nbits));
    try std.testing.expect(bitmap.subset(&old, &expected, nbits));
    try std.testing.expect(bitmap.intersects(&direct, &new, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.weight(&alias, nbits));
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct[1] & ~bitmap.lastWordMask(nbits));
    try std.testing.expectEqual(@as(bitmap.Word, 0), alias[1] & ~bitmap.lastWordMask(nbits));
}

test "phase1 helper ports A find_bit tail scans keep last and andnot callers clamped" {
    const nbits = find_bit.bits_per_long + 6;
    const bitmap_words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 5),
    };
    const andnot_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 5),
    };
    const andnot_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 5),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.findLastBit(&bitmap_words, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.find_last_bit(&bitmap_words, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&bitmap_words, nbits, nbits));
}

test "phase1 helper ports A string memparse and catalog helpers keep rest and matching stable" {
    const parsed_negative = string.memparse("-2Ktail");
    const parsed_positive = string.memparse("+42done");
    const sysfs_modes = [_][]const u8{ "auto\n", "manual", "off\n" };
    const catalog = [_][]const u8{
        &[_]u8{ 'z', 'i', 'g', 0, 'x' },
        "zigux",
        "tools",
    };
    const module_name = [_]u8{ 'h', 'e', 'l', 'p', 'e', 'r', '.', 'z', 'i', 'g', 0, 'x' };

    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), parsed_negative.value);
    try std.testing.expectEqualStrings("tail", parsed_negative.rest);
    try std.testing.expectEqual(@as(u64, 42), parsed_positive.value);
    try std.testing.expectEqualStrings("done", parsed_positive.rest);
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(sysfs_modes[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(sysfs_modes[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(catalog[0..], "zig"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(catalog[0..], "zigux"));
    try std.testing.expect(string.strEndsWith(&module_name, ".zig"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(catalog[0..], "missing"));
}

test "phase1 helper ports A cached rbtree handoff keeps leftmost and postorder stable after replacement" {
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

    const cmp_key = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var first_entry = Entry{ .key = 2, .serial = 0 };
    var second_entry = Entry{ .key = 4, .serial = 1 };
    var third_entry = Entry{ .key = 6, .serial = 2 };
    var replacement = Entry{ .key = 2, .serial = 9 };
    var root = rbtree.RootCached.init();
    const needle: i32 = 2;

    _ = rbtree.addCached(&second_entry.node, &root, less);
    _ = rbtree.addCached(&first_entry.node, &root, less);
    _ = rbtree.addCached(&third_entry.node, &root, less);

    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&first_entry.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.find(&needle, &root.root, cmp_key));

    var postorder_count: usize = 0;
    var postorder = rbtree.firstPostorder(&root.root);
    while (postorder) |node| {
        postorder_count += 1;
        postorder = rbtree.nextPostorder(node);
    }
    try std.testing.expectEqual(@as(usize, 3), postorder_count);

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &second_entry.node), rbtree.firstCached(&root));
}
