const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: usize,
    node: rbtree.Node = .{},
};

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index & (bits_per_long - 1));
}

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn less(lhs_node: *const rbtree.Node, rhs_node: *const rbtree.Node) bool {
    return entryFromNode(lhs_node).key < entryFromNode(rhs_node).key;
}

fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const usize = @ptrCast(@alignCast(key_ptr));
    const entry = entryFromNode(node);
    if (key.* < entry.key) return -1;
    if (key.* > entry.key) return 1;
    return 0;
}

fn collectForward(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.first(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        out[count] = entryFromNode(node).key;
        count += 1;
    }
    return count;
}

test "wave bridge bitmap cut feeds string and find-bit cursors" {
    const nbits = bits_per_long * 2 + 19;
    var base = [_]Word{0} ** 3;
    var mask = [_]Word{0} ** 3;
    var bridge = [_]Word{0} ** 3;

    bitmap.setRange(&base, 2, 5);
    bitmap.setRange(&base, bits_per_long - 3, 7);
    bitmap.setRange(&base, bits_per_long + 11, 9);
    bitmap.setRange(&base, bits_per_long * 2 + 3, 6);
    base[2] |= bit(bits_per_long * 2 + 31);

    bitmap.setRange(&mask, 4, 2);
    bitmap.setRange(&mask, bits_per_long, 2);
    bitmap.setRange(&mask, bits_per_long + 15, 1);
    bitmap.setRange(&mask, bits_per_long * 2 + 6, 7);

    try std.testing.expect(bitmap.andNotBits(&bridge, &base, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 19), bitmap.weight(&bridge, nbits));
    try std.testing.expect(!bitmap.subset(&base, &bridge, nbits));
    try std.testing.expect(bitmap.subset(&bridge, &base, nbits));
    try std.testing.expect(bitmap.intersects(&bridge, &base, nbits));

    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&bridge, nbits));
    try std.testing.expectEqual(@as(usize, 6), find_bit.findNextAndNotBit(&base, &mask, nbits, 4));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findNextAndNotBit(&base, &mask, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 5), find_bit.findLastBit(&bridge, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &bridge, nbits));
    try std.testing.expectEqual(@as(u8, 0x4c), clump);
    try std.testing.expectEqual(@as(usize, bits_per_long - 8), find_bit.findNextClump8(&clump, &bridge, nbits, 7));
    try std.testing.expectEqual(@as(u8, 0xe0), clump);

    const expected_ranges = "2-3,6,61-63,66-67,75-78,80-83,131-133";
    var rendered: [96]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&bridge, nbits, &rendered);
    try std.testing.expectEqualStrings(expected_ranges, rendered[0..rendered_len]);

    var padded: [64]u8 = undefined;
    try std.testing.expectEqual(@as(isize, @intCast(expected_ranges.len)), string.strscpyPad(&padded, rendered[0..rendered_len]));
    try std.testing.expectEqual(@as(u8, 0), padded[expected_ranges.len + 1]);
    try std.testing.expectEqual(@as(u8, 0), padded[63]);

    var label = " \t2-3,6,61-63,66-67,75-78,80-83,131-133\n\x00xx".*;
    const trimmed = string.strim(&label);
    try std.testing.expectEqualStrings(rendered[0..rendered_len], trimmed);
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(trimmed, "2-3"));
    try std.testing.expect(string.strEndsWith(trimmed, "131-133"));
    try std.testing.expectEqual(expected_ranges.len, string.strreplace(trimmed, ',', '|'));

    const labels = [_][]const u8{ "idle", "2-3|6|61-63|66-67|75-78|80-83|131-133", "done" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&labels, trimmed));
    try std.testing.expect(string.sysfsStreq("wave-bridge\n", "wave-bridge"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&[_][]const u8{ "cold", "wave-bridge\n", "hot" }, "wave-bridge"));
}

test "wave bridge cursors remain ordered through cached rbtree updates" {
    var entries = [_]Entry{
        .{ .key = bits_per_long + 2 },
        .{ .key = 2 },
        .{ .key = bits_per_long * 2 + 5 },
        .{ .key = bits_per_long + 11 },
        .{ .key = 6 },
        .{ .key = bits_per_long + 16 },
        .{ .key = bits_per_long - 3 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(usize, 2), entryFromNode(rbtree.firstCached(&root).?).key);
    var key: usize = bits_per_long + 11;
    try std.testing.expectEqual(key, entryFromNode(rbtree.find(&key, &root.root, cmpKey).?).key);

    var duplicate = Entry{ .key = bits_per_long + 11 };
    const existing = rbtree.findAddCached(&duplicate.node, &root, struct {
        fn cmp(lhs_node: *const rbtree.Node, rhs_node: *const rbtree.Node) i32 {
            const lhs = entryFromNode(lhs_node).key;
            const rhs = entryFromNode(rhs_node).key;
            if (lhs < rhs) return -1;
            if (lhs > rhs) return 1;
            return 0;
        }
    }.cmp);
    try std.testing.expect(existing != null);
    try std.testing.expect(duplicate.node.parent == null);
    try std.testing.expect(duplicate.node.left == null);
    try std.testing.expect(duplicate.node.right == null);

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(usize, 6), entryFromNode(rbtree.firstCached(&root).?).key);

    var replacement = Entry{ .key = bits_per_long + 12 };
    rbtree.replaceNodeCached(&entries[3].node, &replacement.node, &root);
    rbtree.clearNode(&entries[3].node);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));

    var ordered: [8]usize = undefined;
    const count = collectForward(&root.root, &ordered);
    try std.testing.expectEqual(@as(usize, 6), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{
        6,
        bits_per_long - 3,
        bits_per_long + 2,
        bits_per_long + 12,
        bits_per_long + 16,
        bits_per_long * 2 + 5,
    }, ordered[0..count]);

    var drain_count: usize = 0;
    while (rbtree.firstCached(&root)) |node| {
        rbtree.eraseInitCached(node, &root);
        drain_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 6), drain_count);
    try std.testing.expect(rbtree.emptyRoot(&root.root));
}
