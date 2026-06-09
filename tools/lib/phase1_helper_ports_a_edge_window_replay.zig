const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn lessByKeyThenSerial(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn compareKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn entryKey(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn entrySerial(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.serial;
}

fn collectKeys(root: *const rbtree.Root, out: []usize) usize {
    var count: usize = 0;
    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        out[count] = entryKey(node);
        count += 1;
    }
    return count;
}

test "lane06 edge-window replay carries bitmap cursors through strings and cached rbtree" {
    const nbits: usize = 130;
    const nwords: usize = 3;
    try std.testing.expectEqual(@as(usize, 3), nwords);
    try std.testing.expectEqual(nwords, bitmap.bitsToWords(nbits));

    var base = [_]Word{0} ** nwords;
    bitmap.setRange(&base, 0, 2);
    bitmap.setRange(&base, 62, 5);
    bitmap.setRange(&base, 126, 4);

    var overlay = [_]Word{0} ** nwords;
    bitmap.setRange(&overlay, 1, 1);
    bitmap.setRange(&overlay, 64, 3);
    bitmap.setRange(&overlay, 128, 1);

    var mask = [_]Word{0} ** nwords;
    bitmap.setRange(&mask, 0, 3);
    bitmap.setRange(&mask, 63, 4);
    bitmap.setRange(&mask, 126, 4);

    var edge = [_]Word{0} ** nwords;
    bitmap.replace(&edge, &base, &overlay, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&edge, nbits));
    try std.testing.expect(!bitmap.empty(&edge, nbits));
    try std.testing.expect(!bitmap.full(&edge, nbits));

    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&edge, nbits));
    try std.testing.expectEqual(@as(usize, 62), find_bit.findNextBit(&edge, nbits, 2));
    try std.testing.expectEqual(@as(usize, 63), find_bit.findNextZeroBit(&edge, nbits, 62));
    try std.testing.expectEqual(@as(usize, 64), find_bit.findNextBit(&edge, nbits, 63));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findNextAndBit(&base, &overlay, nbits, 0));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextAndNotBit(&base, &overlay, nbits, 0));
    try std.testing.expectEqual(@as(usize, 128), find_bit.findLastBit(&edge, nbits));

    var clump: u8 = 0xaa;
    try std.testing.expectEqual(@as(usize, 56), find_bit.findNextClump8(&clump, &edge, nbits, 2));
    try std.testing.expectEqual(@as(u8, 0x40), clump);
    try std.testing.expectEqual(@as(usize, 128), find_bit.findNextClump8(&clump, &edge, nbits, 120));
    try std.testing.expectEqual(@as(u8, 0x01), clump);

    var rendered = [_]u8{0} ** 48;
    const rendered_len = bitmap.scnprintf(&edge, nbits, &rendered);
    try std.testing.expectEqualSlices(u8, "1,62,64-66,128", rendered[0..rendered_len]);
    try std.testing.expectEqual(@as(u8, 0), rendered[rendered_len]);

    var padded = [_]u8{0xee} ** 48;
    const copied = string.strscpyPad(&padded, rendered[0 .. rendered_len + 1]);
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), copied);
    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix(&padded, "1,62"));
    try std.testing.expect(string.strEndsWith(&padded, "128"));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(padded[rendered_len + 1 ..], 0));

    const sysfs_choices = [_][]const u8{
        "0-1,62\n",
        "1,62,64-66,128\n",
        "missing\n",
    };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_choices[0..], padded[0 .. rendered_len + 1]));

    var label = [_]u8{ ' ', 'e', 'd', 'g', 'e', ' ', 'w', 'i', 'n', 'd', 'o', 'w', ' ', 0 };
    const trimmed = string.strim(&label);
    try std.testing.expectEqualSlices(u8, "edge window", trimmed);
    const compact = string.removeSpaces(trimmed);
    try std.testing.expectEqualSlices(u8, "edgewindow", compact);
    try std.testing.expectEqual(@as(?usize, 4), string.strnchr(compact, compact.len, 'w'));

    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&edge, nbits), .serial = 0 },
        .{ .key = find_bit.findNextBit(&edge, nbits, 2), .serial = 1 },
        .{ .key = find_bit.findNextBit(&edge, nbits, 63), .serial = 2 },
        .{ .key = find_bit.findLastBit(&edge, nbits), .serial = 3 },
        .{ .key = find_bit.findNextBit(&edge, nbits, 63), .serial = 4 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, lessByKeyThenSerial);
    }

    try std.testing.expectEqual(@as(usize, 1), entryKey(rbtree.firstCached(&root).?));
    var ordered: [5]usize = undefined;
    const count = collectKeys(&root.root, &ordered);
    try std.testing.expectEqual(@as(usize, 5), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 62, 64, 64, 128 }, ordered[0..count]);

    const duplicate_key: usize = 64;
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, compareKey);
    var duplicate_serials: [2]usize = undefined;
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        duplicate_serials[duplicate_count] = entrySerial(node);
        duplicate_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), duplicate_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 4 }, duplicate_serials[0..duplicate_count]);

    const promoted = rbtree.rb_erase_cached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 62), entryKey(promoted));
    try std.testing.expectEqual(@as(usize, 62), entryKey(rbtree.firstCached(&root).?));

    rbtree.rb_erase_init_cached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(usize, 64), entryKey(rbtree.firstCached(&root).?));

    const remaining = collectKeys(&root.root, &ordered);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 64, 64, 128 }, ordered[0..remaining]);
}
