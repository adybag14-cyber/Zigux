const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const nbits = bitmap.bits_per_long * 2 + 9;
const nwords = bitmap.bitsToWords(nbits);

const Entry = struct {
    key: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const usize = @ptrCast(@alignCast(key_ptr));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (key.* < entry.key) return -1;
    if (key.* > entry.key) return 1;
    return 0;
}

fn collectForward(root: *const rbtree.RootCached, out: []usize) usize {
    var count: usize = 0;
    var current = rbtree.firstCached(root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "merge cascade replay spans bitmap find_bit string and rbtree helpers" {
    var base = [_]Word{0} ** nwords;
    var promoted = [_]Word{0} ** nwords;
    var gate = [_]Word{0} ** nwords;
    var cascade = [_]Word{0} ** nwords;
    var promoted_gate = [_]Word{0} ** nwords;
    var base_remainder = [_]Word{0} ** nwords;
    var bridge = [_]Word{0} ** nwords;
    var remainder = [_]Word{0} ** nwords;
    var rebuilt = [_]Word{0} ** nwords;

    bitmap.setRange(&base, 3, 3);
    bitmap.setRange(&base, 31, 4);
    bitmap.setRange(&base, 64, 3);
    bitmap.setRange(&base, 95, 1);
    bitmap.setRange(&base, 127, 6);

    bitmap.setRange(&promoted, 5, 3);
    bitmap.setRange(&promoted, 33, 4);
    bitmap.setRange(&promoted, 68, 1);
    bitmap.setRange(&promoted, 95, 4);
    bitmap.setRange(&promoted, 120, 4);

    bitmap.setRange(&gate, 4, 3);
    bitmap.setRange(&gate, 32, 4);
    bitmap.setRange(&gate, 64, 6);
    bitmap.setRange(&gate, 96, 2);
    bitmap.setRange(&gate, 128, 3);

    try std.testing.expect(bitmap.andBits(&promoted_gate, &promoted, &gate, nbits));
    try std.testing.expect(bitmap.andNotBits(&base_remainder, &base, &gate, nbits));
    bitmap.orBits(&cascade, &promoted_gate, &base_remainder, nbits);
    try std.testing.expectEqual(@as(usize, 14), bitmap.weight(&cascade, nbits));
    try std.testing.expect(bitmap.andBits(&bridge, &cascade, &gate, nbits));
    try std.testing.expect(bitmap.andNotBits(&remainder, &cascade, &gate, nbits));
    bitmap.orBits(&rebuilt, &bridge, &remainder, nbits);
    try std.testing.expect(bitmap.equal(&cascade, &rebuilt, nbits));
    try std.testing.expect(bitmap.subset(&bridge, &gate, nbits));
    try std.testing.expect(!bitmap.subset(&cascade, &gate, nbits));

    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&cascade, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextBit(&cascade, nbits, 4));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstAndBit(&cascade, &gate, nbits));
    try std.testing.expectEqual(@as(usize, 68), find_bit.findNextAndBit(&cascade, &gate, nbits, 36));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstAndNotBit(&cascade, &gate, nbits));
    try std.testing.expectEqual(@as(usize, 95), find_bit.findNextAndNotBit(&cascade, &gate, nbits, 32));
    try std.testing.expectEqual(@as(usize, 132), find_bit.findLastBit(&cascade, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &cascade, nbits));
    try std.testing.expectEqual(@as(u8, 0b01101000), clump);
    try std.testing.expectEqual(@as(usize, 32), find_bit.findNextClump8(&clump, &cascade, nbits, 32));
    try std.testing.expectEqual(@as(u8, 0b00001110), clump);

    var rendered: [96]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&cascade, nbits, &rendered);
    const expected_rendered = "3,5-6,31,33-35,68,95-97,127,131-132";
    try std.testing.expectEqualStrings(expected_rendered, rendered[0..rendered_len]);

    var padded: [128]u8 = undefined;
    @memset(&padded, 0);
    @memcpy(padded[0..2], "  ");
    @memcpy(padded[2 .. 2 + rendered_len], rendered[0..rendered_len]);
    @memcpy(padded[2 + rendered_len .. 5 + rendered_len], " \n ");
    const trimmed = string.trimSpaces(&padded);
    try std.testing.expectEqualStrings(expected_rendered, trimmed);
    try std.testing.expectEqual(@as(usize, 1), string.strHasPrefix(trimmed, "3"));
    try std.testing.expect(string.strEndsWith(trimmed, "131-132"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(trimmed, trimmed.len, ','));
    try std.testing.expectEqual(@as(?usize, 1), string.memchrInv(trimmed[0..2], '3'));
    try std.testing.expect(string.sysfsStreq(trimmed, expected_rendered ++ "\n"));

    _ = string.replaceChar(trimmed, ',', '|');
    try std.testing.expectEqualStrings("3|5-6|31|33-35|68|95-97|127|131-132", trimmed);

    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&cascade, nbits) },
        .{ .key = find_bit.findNextAndBit(&cascade, &gate, nbits, 6) },
        .{ .key = find_bit.findNextAndNotBit(&cascade, &gate, nbits, 90) },
        .{ .key = find_bit.findLastBit(&cascade, nbits) },
        .{ .key = find_bit.findNextBit(&cascade, nbits, 30) },
        .{ .key = find_bit.findNextAndBit(&cascade, &gate, nbits, 69) },
    };

    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    var order: [entries.len]usize = undefined;
    var count = collectForward(&root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 3, 6, 31, 95, 96, 132 }, order[0..count]);

    const lookup_key: usize = 95;
    const found = rbtree.find(&lookup_key, &root.root, cmpKey) orelse return error.MissingExpectedNode;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(usize, 95), found_entry.key);

    rbtree.eraseInitCached(found, &root);
    try std.testing.expect(rbtree.emptyNode(found));

    count = collectForward(&root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 3, 6, 31, 96, 132 }, order[0..count]);
    try std.testing.expectEqual(@as(usize, 3), (@as(*const Entry, @fieldParentPtr("node", rbtree.firstCached(&root).?))).key);
}
