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

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
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

test "ports A rotate bitmap ranges through trim and cached rbtree traversal" {
    const nbits = bitmap.bits_per_long + 13;
    var source = [_]Word{ 0, 0 };
    var rotated = [_]Word{ 0, 0 };
    var extended = [_]Word{ 0xaa55, 0xaa55, 0xaa55 };

    bitmap.setRange(&source, 2, 3);
    bitmap.setRange(&source, 9, 1);
    bitmap.setRange(&source, bitmap.bits_per_long + 6, 3);
    try std.testing.expectEqual(@as(usize, 7), bitmap.weight(&source, nbits));

    var bit = find_bit.findFirstBit(&source, nbits);
    while (bit < nbits) : (bit = find_bit.findNextBit(&source, nbits, bit + 1)) {
        bitmap.setRange(&rotated, (bit + 5) % nbits, 1);
    }

    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(&rotated, nbits));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextBit(&rotated, nbits, 1));
    try std.testing.expectEqual(@as(usize, 14), find_bit.findNextBit(&rotated, nbits, 10));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 12), find_bit.findLastBit(&rotated, nbits));
    try std.testing.expect(bitmap.subset(&rotated, &rotated, nbits));

    bitmap.copyAndExtend(&extended, &rotated, nbits, bitmap.bits_per_long * 3);
    try std.testing.expectEqual(@as(Word, 0), extended[2]);
    try std.testing.expect(bitmap.equal(&extended, &rotated, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &rotated, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0b1000_0001), clump);
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &rotated, nbits, 8));
    try std.testing.expectEqual(@as(u8, 0b0100_0011), clump);

    var rendered: [64]u8 = @splat(0);
    const rendered_len = bitmap.scnprintf(&rotated, nbits, &rendered);
    try std.testing.expectEqualStrings("0,7-9,14,75-76", rendered[0..rendered_len]);

    var padded: [96]u8 = @splat(0x5a);
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpyPad(padded[2..], rendered[0..rendered_len]));
    padded[0] = ' ';
    padded[1] = '\t';
    padded[2 + rendered_len] = ' ';
    padded[3 + rendered_len] = '\n';
    padded[4 + rendered_len] = 0;

    const trimmed = string.trimSpaces(padded[0..]);
    try std.testing.expectEqualStrings("0,7-9,14,75-76", trimmed);
    try std.testing.expectEqual(@as(usize, 2), string.strHasPrefix(trimmed, "0,"));
    try std.testing.expect(std.mem.endsWith(u8, trimmed, "75-76"));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(padded[5 + rendered_len .. 12 + rendered_len], 0));

    const exact_tokens = [_][]const u8{ "0,7-9,14,75-76", "missing" };
    const sysfs_tokens = [_][]const u8{ "disabled", "0,7-9,14,75-76\n" };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(exact_tokens[0..], trimmed));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_tokens[0..], trimmed));

    var entries = [_]Entry{
        .{ .key = 14, .serial = 0 },
        .{ .key = 7, .serial = 1 },
        .{ .key = 76, .serial = 2 },
        .{ .key = 0, .serial = 3 },
        .{ .key = 9, .serial = 4 },
        .{ .key = 75, .serial = 5 },
        .{ .key = 8, .serial = 6 },
        .{ .key = 14, .serial = 7 },
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(usize, 0), entryKey(rbtree.firstCached(&root).?));
    try std.testing.expectEqual(@as(usize, 76), entryKey(rbtree.last(&root.root).?));

    const duplicate_key: usize = 14;
    var iterator = rbtree.matchIterator(&duplicate_key, &root.root, cmpKey);
    try std.testing.expectEqual(@as(usize, 0), entrySerial(iterator.next().?));
    try std.testing.expectEqual(@as(usize, 7), entrySerial(iterator.next().?));
    try std.testing.expect(iterator.next() == null);

    rbtree.eraseInitCached(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try std.testing.expectEqual(@as(usize, 7), entryKey(rbtree.firstCached(&root).?));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}

test "ports A rotated complement keeps string miss and cached singleton boundaries explicit" {
    const nbits = bitmap.bits_per_long + 5;
    var source = [_]Word{ 0, 0 };
    var complement = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };

    bitmap.setRange(&source, 0, 1);
    bitmap.setRange(&source, bitmap.bits_per_long + 4, 1);
    bitmap.fill(&mask, nbits);
    bitmap.clearRange(&mask, 0, 1);
    bitmap.clearRange(&mask, bitmap.bits_per_long + 4, 1);
    try std.testing.expect(bitmap.andNotBits(&complement, &mask, &source, nbits));
    try std.testing.expectEqual(@as(usize, nbits - 2), bitmap.weight(&complement, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&complement, nbits));
    try std.testing.expectEqual(@as(usize, nbits - 2), find_bit.findLastBit(&complement, nbits));

    var buffer: [96]u8 = @splat(0);
    const len = bitmap.scnprintf(&complement, nbits, &buffer);
    try std.testing.expectEqualStrings("1-67", buffer[0..len]);
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&[_][]const u8{ "0", "68" }, buffer[0..len]));

    var entry = Entry{ .key = len, .serial = 0 };
    var root = rbtree.RootCached.init();
    try std.testing.expectEqual(@as(?*rbtree.Node, &entry.node), rbtree.addCached(&entry.node, &root, less));
    try std.testing.expect(rbtree.eraseCached(&entry.node, &root) == null);
    try std.testing.expect(root.root.node == null);
    try std.testing.expect(rbtree.firstCached(&root) == null);
}
