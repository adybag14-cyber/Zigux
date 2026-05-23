const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn cmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn keyOf(node: ?*rbtree.Node) ?i32 {
    const current = node orelse return null;
    const entry: *const Entry = @fieldParentPtr("node", current);
    return entry.key;
}

test "lane06 replay keeps bitmap range and render helpers alias-aligned across word boundaries" {
    const nbits = bitmap.bits_per_long + 8;
    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };

    bitmap.setRange(&direct, bitmap.bits_per_long - 2, 5);
    bitmap.bitmap_set(&alias, bitmap.bits_per_long - 2, 5);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);

    bitmap.clearRange(&direct, bitmap.bits_per_long, 1);
    bitmap.bitmap_clear(&alias, bitmap.bits_per_long, 1);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);

    var direct_buf = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    var alias_buf = [_]u8{ 0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0xbb };
    const direct_len = bitmap.scnprintf(&direct, nbits, direct_buf[0..5]);
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, alias_buf[0..5]);

    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualSlices(u8, direct_buf[0..direct_len], alias_buf[0..alias_len]);
    try std.testing.expectEqual(@as(u8, 0), direct_buf[direct_len]);
    try std.testing.expectEqual(@as(u8, 0), alias_buf[alias_len]);
    try std.testing.expectEqualStrings("62-6", direct_buf[0..direct_len]);
}

test "lane06 replay keeps find_bit byte-window helpers stable at aligned and empty boundaries" {
    const last_aligned_byte = find_bit.bits_per_long - 8;
    const byte_map = [_]find_bit.Word{
        @as(find_bit.Word, 0xa5) << @intCast(last_aligned_byte),
        @as(find_bit.Word, 0x11) << 8,
    };

    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&byte_map, last_aligned_byte));
    try std.testing.expectEqual(@as(u8, 0x11), find_bit.getValue8(&byte_map, find_bit.bits_per_long + 8));

    var clump: u8 = 0x5a;
    const empty = [_]find_bit.Word{0};
    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstClump8(&clump, &empty, 8));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
    try std.testing.expectEqual(@as(usize, 8), find_bit.find_next_clump8(&clump, &empty, 8, 12));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);

    const singleton = [_]find_bit.Word{@as(find_bit.Word, 1) << 3};
    clump = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &singleton, 8));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);
}

test "lane06 replay keeps string whitespace and sysfs helpers C-string aware" {
    try std.testing.expectEqualStrings("lead", string.skipSpaces(" \tlead"));
    try std.testing.expectEqualStrings("lead", string.skip_spaces(" \nlead"));

    var trim_buf = [_]u8{ ' ', 'a', ' ', 'b', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("a b", string.trimSpaces(trim_buf[0..]));

    var strim_buf = [_]u8{ ' ', 'o', 'k', 0, ' ', 0 };
    try std.testing.expectEqualStrings("ok", string.strim(strim_buf[0..]));

    var strip_buf = [_]u8{ '\t', 'z', 'e', 'd', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("zed", string.strstrip(strip_buf[0..]));

    var remove_buf = [_]u8{ 'a', ' ', 'b', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("ab", string.removeSpaces(remove_buf[0..]));

    var alias_remove_buf = [_]u8{ 'c', ' ', 'd', ' ', 0, 'y' };
    try std.testing.expectEqualStrings("cd", string.remove_spaces(alias_remove_buf[0..]));

    try std.testing.expect(string.sysfsStreq("mode\n", "mode"));
    try std.testing.expect(string.sysfs_streq("mode\n", "mode"));
    try std.testing.expect(!string.sysfsStreq("mode\n", "modes"));
}

test "lane06 replay keeps non-cached rbtree duplicate replacement and reset behavior stable" {
    var root = rbtree.Root.init();
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var duplicate_probe = Entry{ .key = 10, .serial = 99 };
    const existing = rbtree.findAdd(&duplicate_probe.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 10), keyOf(existing).?);

    var replacement = Entry{ .key = 20, .serial = 4 };
    rbtree.replaceNode(&entries[2].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?i32, 20), keyOf(rbtree.last(&root)));

    rbtree.eraseInit(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?i32, 15), keyOf(rbtree.last(&root)));

    var detached = rbtree.Node.init();
    rbtree.clearNode(&detached);
    try std.testing.expect(rbtree.emptyNode(&detached));
}
