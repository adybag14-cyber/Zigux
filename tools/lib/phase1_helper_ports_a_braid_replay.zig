const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn lessByKey(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn readKey(node: *const rbtree.Node) i32 {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn collectForward(root: *const rbtree.Root, out: []i32) usize {
    var count: usize = 0;
    var cursor = rbtree.first(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        out[count] = readKey(node);
        count += 1;
    }
    return count;
}

test "phase1 helper ports A braid bitmap cursors strings and cached rbtree" {
    const nbits = bits_per_long + 12;
    var old = [_]Word{ 0, 0 };
    var new = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };
    var braided = [_]Word{ 0, 0 };

    bitmap.setRange(&old, 1, 3);
    bitmap.setRange(&old, bits_per_long + 8, 2);
    bitmap.setRange(&new, 4, 2);
    bitmap.setRange(&new, bits_per_long + 2, 5);
    bitmap.setRange(&mask, 3, 4);
    bitmap.setRange(&mask, bits_per_long + 2, 5);
    bitmap.bitmap_replace(&braided, &old, &new, &mask, nbits);

    try std.testing.expectEqual(@as(usize, 11), bitmap.weight(&braided, nbits));
    try std.testing.expect(bitmap.intersects(&braided, &new, nbits));
    try std.testing.expect(!bitmap.subset(&old, &braided, nbits));

    var andnot = [_]Word{ 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&andnot, &old, &braided, nbits));
    try std.testing.expectEqual(@as(usize, 1), bitmap.weight(&andnot, nbits));

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&braided, nbits, &rendered);
    try std.testing.expectEqualStrings("1-2,4-5,66-70,72-73", rendered[0..rendered_len]);

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &braided, nbits));
    try std.testing.expectEqual(@as(u8, 0b0011_0110), clump);
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextClump8(&clump, &braided, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0111_1100), clump);
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findNextAndBit(&braided, &mask, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstAndNotBit(&old, &braided, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 9), find_bit.findLastBit(&braided, nbits));

    var label = [_]u8{ ' ', 'b', 'r', 'a', 'i', 'd', ':', '1', '-', '2', ',', '4', '-', '5', ',', '6', '6', '-', '7', '0', ',', '7', '2', '-', '7', '3', ' ', 0, 'x' };
    const trimmed = string.strim(label[0..]);
    try std.testing.expectEqualStrings("braid:1-2,4-5,66-70,72-73", trimmed);
    try std.testing.expectEqual(@as(usize, 6), string.str_has_prefix(trimmed, "braid:"));
    try std.testing.expect(string.strEndsWith(trimmed, "73"));

    var copied = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 5), string.strscpy_pad(copied[0..], "node5"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'n', 'o', 'd', 'e', '5', 0, 0, 0 }, copied[0..]);
    try std.testing.expect(string.sysfs_streq("braid\n", "braid"));
    try std.testing.expectEqual(@as(?usize, 3), string.match_string(&[_][]const u8{ "old", "new", "mask", "braid" }, "braid"));

    var entries = [_]Entry{
        .{ .key = @intCast(find_bit.findFirstBit(&braided, nbits)), .serial = 0 },
        .{ .key = @intCast(find_bit.findNextBit(&braided, nbits, 3)), .serial = 1 },
        .{ .key = @intCast(find_bit.findLastBit(&braided, nbits)), .serial = 2 },
        .{ .key = @intCast(string.str_has_prefix(trimmed, "braid:")), .serial = 3 },
    };
    var replacement = Entry{ .key = 4, .serial = 4 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, lessByKey);
    }
    try std.testing.expectEqual(@as(i32, 1), readKey(rbtree.firstCached(&root).?));

    const removed_leftmost = rbtree.eraseCached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 4), readKey(removed_leftmost));
    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);

    var order: [4]i32 = undefined;
    const count = collectForward(&root.root, &order);
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 4, 6, 73 }, order[0..count]);
    try std.testing.expectEqual(@as(i32, 4), readKey(rbtree.firstCached(&root).?));

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(i32, 6), readKey(rbtree.firstCached(&root).?));
}
