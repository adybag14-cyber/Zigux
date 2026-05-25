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

test "phase1 helper ports A replays masked bitmap clumps" {
    const word_bits = find_bit.bits_per_long;
    const nbits = word_bits + 5;

    var map = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&map, word_bits - 1, 4);
    bitmap.clearRange(&map, word_bits + 1, 1);

    try std.testing.expectEqual(word_bits - 1, find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(word_bits, find_bit.findNextBit(&map, nbits, word_bits));
    try std.testing.expectEqual(word_bits + 2, find_bit.findLastBit(&map, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(word_bits, find_bit.findNextClump8(&clump, &map, nbits, word_bits));
    try std.testing.expectEqual(@as(u8, 0b0000_0101), clump);

    var rendered: [32]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&map, nbits, &rendered);
    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(&expected, "{d}-{d},{d}", .{
        word_bits - 1,
        word_bits,
        word_bits + 2,
    });
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);

    var extended = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    bitmap.copyAndExtend(&extended, &map, nbits, word_bits * 2 + 1);
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&extended, word_bits * 2 + 1));
    try std.testing.expectEqual(word_bits + 1, find_bit.findNextZeroBit(&extended, word_bits * 2 + 1, word_bits));
    try std.testing.expectEqual(@as(bitmap.Word, 0), extended[2]);
}

test "phase1 helper ports A replays cached tree duplicates with string labels" {
    var entries = [_]TreeEntry{
        .{ .key = 8, .serial = 0, .label = "drivers/net" },
        .{ .key = 5, .serial = 1, .label = "drivers/tty" },
        .{ .key = 8, .serial = 2, .label = "drivers/block" },
        .{ .key = 12, .serial = 3, .label = "samples/zigux" },
    };
    var root = rbtree.RootCached.init();

    try std.testing.expect(rbtree.addCached(&entries[0].node, &root, TreeEntry.less) == &entries[0].node);
    try std.testing.expect(rbtree.addCached(&entries[1].node, &root, TreeEntry.less) == &entries[1].node);
    try std.testing.expect(rbtree.addCached(&entries[2].node, &root, TreeEntry.less) == null);
    try std.testing.expect(rbtree.addCached(&entries[3].node, &root, TreeEntry.less) == null);

    const leftmost = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 5), entryFrom(leftmost).key);

    const wanted = @as(i32, 8);
    var iter = rbtree.matchIterator(&wanted, &root.root, TreeEntry.cmp);
    var duplicate_serials: [2]usize = undefined;
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        duplicate_serials[duplicate_count] = entryFrom(node).serial;
        duplicate_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), duplicate_count);
    try std.testing.expectEqualSlices(usize, &.{ 0, 2 }, duplicate_serials[0..duplicate_count]);
    try std.testing.expect(string.strEndsWith(entries[0].label, "/net"));
    try std.testing.expect(string.strEndsWith(entries[2].label, "/block"));

    try std.testing.expectEqual(@as(usize, 8), string.strHasPrefix(entries[3].label, "samples/"));
    try std.testing.expect(string.strEndsWith(entries[3].label, "zigux"));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(".....", '.'));
    try std.testing.expectEqual(@as(?usize, 4), string.memchrInv("....!", '.'));
    try std.testing.expectEqual(@as(?usize, 7), string.strnchr(entries[2].label, entries[2].label.len, '/'));

    const promoted = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 8), entryFrom(promoted).key);
    try std.testing.expectEqual(@as(usize, 0), entryFrom(promoted).serial);
    try std.testing.expect(rbtree.firstCached(&root) == promoted);

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));

    var postorder_keys: [2]i32 = undefined;
    var postorder_count: usize = 0;
    var current = rbtree.firstPostorder(&root.root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        postorder_keys[postorder_count] = entryFrom(node).key;
        postorder_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), postorder_count);
    try std.testing.expectEqualSlices(i32, &.{ 12, 8 }, postorder_keys[0..postorder_count]);
}
