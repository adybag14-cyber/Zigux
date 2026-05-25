const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const TreeEntry = struct {
    key: i32,
    serial: usize,
    label: []const u8,
    node: rbtree.Node = rbtree.Node.init(),

    fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
        const lhs_entry = entryFrom(lhs);
        const rhs_entry = entryFrom(rhs);
        if (lhs_entry.key != rhs_entry.key) {
            return lhs_entry.key < rhs_entry.key;
        }
        return lhs_entry.serial < rhs_entry.serial;
    }

    fn cmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
        const wanted: *const i32 = @ptrCast(@alignCast(key));
        const entry = entryFrom(node);
        if (wanted.* < entry.key) return -1;
        if (wanted.* > entry.key) return 1;
        return 0;
    }
};

fn entryFrom(node: *const rbtree.Node) *const TreeEntry {
    return @fieldParentPtr("node", node);
}

test "phase1 helper ports A replays carved byte windows across a word boundary" {
    const word_bits = find_bit.bits_per_long;
    const nbits = word_bits + 8;

    var map = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&map, word_bits - 8, 16);
    bitmap.clearRange(&map, word_bits + 3, 2);

    try std.testing.expectEqual(word_bits - 8, find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(word_bits, find_bit.findNextBit(&map, nbits, word_bits));
    try std.testing.expectEqual(word_bits + 7, find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(word_bits + 3, find_bit.findNextZeroBit(&map, nbits, word_bits));

    var first_clump: u8 = 0;
    try std.testing.expectEqual(word_bits - 8, find_bit.findFirstClump8(&first_clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0xff), first_clump);

    var second_clump: u8 = 0;
    try std.testing.expectEqual(word_bits, find_bit.findNextClump8(&second_clump, &map, nbits, word_bits));
    try std.testing.expectEqual(@as(u8, 0b1110_0111), second_clump);

    try std.testing.expectEqual(@as(usize, 14), bitmap.weight(&map, nbits));

    var copied = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    bitmap.copyClearTail(&copied, &map, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &map, &copied);

    var rendered: [32]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&copied, nbits, &rendered);
    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(&expected, "{d}-{d},{d}-{d}", .{
        word_bits - 8,
        word_bits + 2,
        word_bits + 5,
        word_bits + 7,
    });
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);
}

test "phase1 helper ports A replays cached leftmost promotion with newline-aware labels" {
    var entries = [_]TreeEntry{
        .{ .key = 2, .serial = 0, .label = "modes/auto\n" },
        .{ .key = 5, .serial = 1, .label = "modes/manual\n" },
        .{ .key = 5, .serial = 2, .label = "modes/manual" },
        .{ .key = 9, .serial = 3, .label = "modes/disabled" },
    };
    var root = rbtree.RootCached.init();

    try std.testing.expect(rbtree.addCached(&entries[0].node, &root, TreeEntry.less) == &entries[0].node);
    try std.testing.expect(rbtree.addCached(&entries[1].node, &root, TreeEntry.less) == null);
    try std.testing.expect(rbtree.addCached(&entries[2].node, &root, TreeEntry.less) == null);
    try std.testing.expect(rbtree.addCached(&entries[3].node, &root, TreeEntry.less) == null);

    const labels = [_][]const u8{
        entries[1].label,
        entries[2].label,
        entries[3].label,
    };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&labels, "modes/manual"));
    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix(entries[3].label, "modes/"));
    try std.testing.expect(string.strEndsWith(entries[3].label, "disabled"));

    const wanted = @as(i32, 5);
    var iter = rbtree.matchIterator(&wanted, &root.root, TreeEntry.cmp);
    var duplicate_serials: [2]usize = undefined;
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        duplicate_serials[duplicate_count] = entryFrom(node).serial;
        duplicate_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), duplicate_count);
    try std.testing.expectEqualSlices(usize, &.{ 1, 2 }, duplicate_serials[0..duplicate_count]);

    var replacement = TreeEntry{
        .key = 2,
        .serial = 4,
        .label = "modes/auto",
    };
    rbtree.replaceNodeCached(&entries[0].node, &replacement.node, &root);
    const leftmost_after_replace = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 2), entryFrom(leftmost_after_replace).key);
    try std.testing.expectEqual(@as(usize, 4), entryFrom(leftmost_after_replace).serial);

    const promoted = rbtree.eraseCached(&replacement.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 5), entryFrom(promoted).key);
    try std.testing.expectEqual(@as(usize, 1), entryFrom(promoted).serial);
    try std.testing.expect(rbtree.firstCached(&root) == promoted);
    try std.testing.expect(string.sysfsStreq(entryFrom(promoted).label, "modes/manual"));
    try std.testing.expectEqual(@as(?usize, 5), string.strnchr(entryFrom(promoted).label, entryFrom(promoted).label.len, '/'));

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));

    var postorder_keys: [2]i32 = undefined;
    var postorder_count: usize = 0;
    var current = rbtree.firstPostorder(&root.root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        postorder_keys[postorder_count] = entryFrom(node).key;
        postorder_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), postorder_count);
    try std.testing.expectEqualSlices(i32, &.{ 9, 5 }, postorder_keys[0..postorder_count]);
}
