const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const MatchEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const MatchEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const MatchEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const target: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const MatchEntry = @fieldParentPtr("node", node);
    if (target.* < entry.key) return -1;
    if (target.* > entry.key) return 1;
    return 0;
}

fn nodeIdentity(node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const MatchEntry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

test "lane06 replay keeps bitmap range formatting and replacements alias-aligned" {
    const start = bitmap.bits_per_long - 2;
    const len = 6;
    const nbits = bitmap.bits_per_long * 2 + 4;

    var primary = [_]bitmap.Word{ 0, 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0, 0 };

    bitmap.setRange(&primary, start, len);
    bitmap.bitmap_set(&alias, start, len);
    try std.testing.expectEqualSlices(bitmap.Word, &primary, &alias);

    var primary_render = [_]u8{0} ** 32;
    var alias_render = [_]u8{0} ** 32;
    const primary_len = bitmap.scnprintf(&primary, nbits, &primary_render);
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, &alias_render);
    var expected_buf = [_]u8{0} ** 32;
    const expected = try std.fmt.bufPrint(&expected_buf, "{d}-{d}", .{ start, start + len - 1 });
    try std.testing.expectEqual(primary_len, alias_len);
    try std.testing.expectEqualStrings(expected, primary_render[0..primary_len]);
    try std.testing.expectEqualStrings(expected, alias_render[0..alias_len]);

    const old = [_]bitmap.Word{
        primary[0],
        primary[1] | (@as(bitmap.Word, 1) << 9),
        0,
    };
    const new = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 9),
        0,
    };
    const mask = [_]bitmap.Word{
        primary[0],
        primary[1],
        0,
    };
    var replaced = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.replace(&replaced, &old, &new, &mask, nbits);
    try std.testing.expectEqual(@as(bitmap.Word, 0), replaced[0]);
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 9)), replaced[1]);

    var and_dst = [_]bitmap.Word{ 0, 0, 0 };
    try std.testing.expect(bitmap.andBits(&and_dst, &replaced, &new, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &[_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 9), 0 }, &and_dst);

    var andnot_dst = [_]bitmap.Word{ 0, 0, 0 };
    try std.testing.expect(!bitmap.andNotBits(&andnot_dst, &replaced, &new, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &[_]bitmap.Word{ 0, 0, 0 }, &andnot_dst);

    bitmap.clearRange(&primary, start, len);
    bitmap.bitmap_clear(&alias, start, len);
    try std.testing.expectEqualSlices(bitmap.Word, &[_]bitmap.Word{ 0, 0, 0 }, &primary);
    try std.testing.expectEqualSlices(bitmap.Word, &primary, &alias);
}

test "lane06 replay keeps find_bit clump scans and last-bit aliases aligned" {
    const nbits = find_bit.bits_per_long + 11;
    const map = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 10) | (@as(find_bit.Word, 1) << @intCast(find_bit.bits_per_long - 1)),
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 7),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstClump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_0100), clump);

    try std.testing.expectEqual(@as(usize, 8), find_bit.find_first_clump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_0100), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long - 8), find_bit.findNextClump8(&clump, &map, nbits, 11));
    try std.testing.expectEqual(@as(u8, 0b1000_0000), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit._find_next_clump8(&clump, &map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b1000_0100), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 7), find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 7), find_bit.find_last_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 7), find_bit._find_last_bit(&map, nbits));
}

test "lane06 replay keeps string whitespace and sysfs helpers C-string aware" {
    try std.testing.expectEqualStrings("alpha", string.skipSpaces(" \t\nalpha"));
    try std.testing.expectEqualStrings("beta", string.skip_spaces("  beta"));

    var trimmed = [_]u8{ ' ', '\t', 'o', 'k', ' ', '\n', 0, 'x' };
    try std.testing.expectEqualStrings("ok", string.trimSpaces(&trimmed));

    var stripped = [_]u8{ ' ', 'a', ' ', 'b', ' ', 'c', ' ', 0, 'z' };
    try std.testing.expectEqualStrings("abc", string.removeSpaces(&stripped));
    try std.testing.expectEqualStrings("abc", string.remove_spaces(&stripped));

    var replaced = [_]u8{ 'a', '-', 'b', '-', 0, 'c' };
    try std.testing.expectEqual(@as(usize, 4), string.replaceChar(&replaced, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 'b', '_', 0, 'c' }, &replaced);
    try std.testing.expectEqual(@as(usize, 4), string.strreplace(&replaced, '_', '-'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '-', 'b', '-', 0, 'c' }, &replaced);

    try std.testing.expect(string.sysfsStreq("auto\n", "auto"));
    try std.testing.expect(string.sysfs_streq("off", "off\n"));
    try std.testing.expect(!string.sysfsStreq("auto", "autoX"));
}

test "lane06 replay keeps cached rbtree match iteration and leftmost replacement stable" {
    var root = rbtree.RootCached.init();
    var first = MatchEntry{ .key = 5, .serial = 0 };
    var second = MatchEntry{ .key = 5, .serial = 1 };
    var middle = MatchEntry{ .key = 7, .serial = 2 };
    var tail = MatchEntry{ .key = 9, .serial = 3 };

    try std.testing.expectEqual(@as(?*rbtree.Node, &first.node), rbtree.addCached(&first.node, &root, entryLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&second.node, &root, entryLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&middle.node, &root, entryLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&tail.node, &root, entryLess));

    const key: i32 = 5;
    var iter = rbtree.matchIterator(&key, &root.root, keyCmp);
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 0 }), nodeIdentity(iter.next()));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 1 }), nodeIdentity(iter.next()));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iter.next());

    var replacement = MatchEntry{ .key = 5, .serial = 99 };
    rbtree.replaceNodeCached(&first.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 99 }), nodeIdentity(rbtree.firstCached(&root)));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 99 }), nodeIdentity(rbtree.findFirst(&key, &root.root, keyCmp)));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 9, 3 }), nodeIdentity(rbtree.last(&root.root)));

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 5, 1 }), nodeIdentity(rbtree.rb_first_cached(&root)));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 7, 2 }), nodeIdentity(rbtree.rb_next(&second.node)));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 7, 2 }), nodeIdentity(rbtree.rb_prev(&tail.node)));
}
