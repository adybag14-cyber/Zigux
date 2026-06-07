const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const nbits = bitmap.bits_per_long + 17;
const nwords = bitmap.bitsToWords(nbits);

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

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn collect(root: *const rbtree.Root, out: []i32) usize {
    var count: usize = 0;
    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "lane06 cross hatch replay pins helper-port cursor and erase-init agreement" {
    var source = [_]Word{0} ** nwords;
    var overlay = [_]Word{0} ** nwords;
    var replacement = [_]Word{0} ** nwords;
    var selected = [_]Word{0} ** nwords;
    var gaps = [_]Word{0} ** nwords;

    bitmap.bitmap_set(&source, 3, 4);
    bitmap.bitmap_set(&source, bitmap.bits_per_long - 2, 5);
    bitmap.bitmap_set(&source, bitmap.bits_per_long + 9, 3);

    bitmap.bitmap_set(&overlay, 1, 7);
    bitmap.bitmap_set(&overlay, bitmap.bits_per_long + 1, 8);

    bitmap.bitmap_set(&replacement, 2, 1);
    bitmap.bitmap_set(&replacement, bitmap.bits_per_long + 4, 3);
    bitmap.bitmap_set(&replacement, bitmap.bits_per_long + 14, 2);

    try std.testing.expect(bitmap.bitmap_and(&selected, &source, &overlay, nbits));
    try std.testing.expect(bitmap.bitmap_andnot(&gaps, &replacement, &selected, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&source, &overlay, nbits));
    try std.testing.expect(!bitmap.bitmap_subset(&replacement, &selected, nbits));
    try std.testing.expectEqual(@as(usize, 6), bitmap.bitmap_weight(&selected, nbits));
    try std.testing.expectEqual(@as(usize, 6), bitmap.bitmap_weight(&gaps, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&selected, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 1), find_bit.findNextBit(&selected, nbits, 7));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 4), find_bit.findNextAndNotBit(&replacement, &selected, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 15), find_bit.findLastBit(&gaps, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), find_bit.findNextClump8(&clump, &gaps, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b01110000), clump);

    var rendered: [48]u8 = [_]u8{0} ** 48;
    const written = try std.fmt.bufPrint(&rendered, "  cross:{d}-{d}-{d}  ", .{
        find_bit.findFirstBit(&selected, nbits),
        find_bit.findNextAndNotBit(&replacement, &selected, nbits, bitmap.bits_per_long),
        find_bit.findLastBit(&gaps, nbits),
    });
    rendered[written.len] = 0;

    const trimmed = string.strim(&rendered);
    try std.testing.expectEqualSlices(u8, "cross:3-68-79", trimmed);
    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix(trimmed, "cross:"));
    try std.testing.expect(string.strEndsWith(trimmed, "79"));
    try std.testing.expectEqual(@as(?usize, 1), string.memchrInv(trimmed, 'c'));
    try std.testing.expect(string.sysfsStreq("cross:3-68-79\n", trimmed));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&[_][]const u8{ "skip", "cross:3-68-79", "other" }, trimmed));

    var entries = [_]Entry{
        .{ .key = @intCast(find_bit.findFirstBit(&selected, nbits)), .serial = 0 },
        .{ .key = @intCast(find_bit.findNextAndNotBit(&replacement, &selected, nbits, bitmap.bits_per_long)), .serial = 1 },
        .{ .key = @intCast(find_bit.findLastBit(&gaps, nbits)), .serial = 2 },
        .{ .key = @intCast(find_bit.findFirstBit(&selected, nbits)), .serial = 3 },
        .{ .key = @intCast(find_bit.findNextBit(&selected, nbits, 7)), .serial = 4 },
    };
    var duplicate_probe = Entry{ .key = entries[0].key, .serial = 99 };
    var root = rbtree.Root.init();

    for (entries[0..3]) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = rbtree.findAdd(&duplicate_probe.node, &root, cmpNode) orelse return error.TestUnexpectedResult;
    const duplicate_entry: *const Entry = @fieldParentPtr("node", duplicate);
    try std.testing.expectEqual(@as(usize, 0), duplicate_entry.serial);

    rbtree.add(&entries[3].node, &root, less);
    rbtree.add(&entries[4].node, &root, less);

    const duplicate_key = entries[0].key;
    var iter = rbtree.matchIterator(&duplicate_key, &root, cmpKey);
    var serials: [2]usize = undefined;
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[duplicate_count] = entry.serial;
        duplicate_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), duplicate_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 3 }, serials[0..duplicate_count]);

    rbtree.eraseInit(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));

    var order: [4]i32 = undefined;
    const count = collect(&root, &order);
    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 3, 65, 79 }, order[0..count]);
}
