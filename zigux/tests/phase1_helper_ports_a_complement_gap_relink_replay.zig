const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Entry = struct {
    node: rbtree.Node = rbtree.Node.init(),
    key: usize,
    serial: usize,
};

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key == rhs_entry.key) {
        return lhs_entry.serial < rhs_entry.serial;
    }
    return lhs_entry.key < rhs_entry.key;
}

fn entryCmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    if (lhs_entry.serial < rhs_entry.serial) return -1;
    if (lhs_entry.serial > rhs_entry.serial) return 1;
    return 0;
}

fn collectKeys(root: *const rbtree.RootCached, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.first(&root.root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "phase1 helper ports A complement gaps relink through cached tree" {
    const nbits = bitmap.bits_per_long * 2 + 9;

    var allowed = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.setRange(&allowed, 1, 3);
    bitmap.setRange(&allowed, bitmap.bits_per_long + 2, 3);
    bitmap.setRange(&allowed, bitmap.bits_per_long * 2 + 4, 1);
    allowed[2] |= @as(bitmap.Word, 1) << 12;

    var blocked = [_]bitmap.Word{ 0, 0, 0 };
    blocked[0] |= @as(bitmap.Word, 1) << 2;
    blocked[1] |= @as(bitmap.Word, 1) << 3;
    blocked[2] |= @as(bitmap.Word, 1) << 4;
    blocked[2] |= @as(bitmap.Word, 1) << 14;

    var complement = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.complement(&complement, &blocked, nbits);

    var gap_map = [_]bitmap.Word{ 0, 0, 0 };
    try std.testing.expect(bitmap.andBits(&gap_map, &allowed, &complement, nbits));

    var andnot_map = [_]bitmap.Word{ 0, 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&andnot_map, &allowed, &blocked, nbits));
    try std.testing.expect(bitmap.equal(&gap_map, &andnot_map, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&gap_map, nbits));

    const first_gap = find_bit.findFirstAndNotBit(&allowed, &blocked, nbits);
    const second_gap = find_bit.findNextAndNotBit(&allowed, &blocked, nbits, first_gap + 1);
    const third_gap = find_bit.findNextBit(&gap_map, nbits, second_gap + 1);
    const fourth_gap = find_bit.findNextBit(&gap_map, nbits, third_gap + 1);
    try std.testing.expectEqual(@as(usize, 1), first_gap);
    try std.testing.expectEqual(@as(usize, 3), second_gap);
    try std.testing.expectEqual(bitmap.bits_per_long + 2, third_gap);
    try std.testing.expectEqual(bitmap.bits_per_long + 4, fourth_gap);
    try std.testing.expectEqual(fourth_gap, find_bit.findLastBit(&gap_map, nbits));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&gap_map, nbits, fourth_gap + 1));

    var clump: u8 = 0;
    try std.testing.expectEqual(bitmap.bits_per_long, find_bit.findNextClump8(&clump, &gap_map, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0001_0100), clump);

    var rendered = [_]u8{0} ** 48;
    const rendered_len = bitmap.scnprintf(&gap_map, nbits, &rendered);
    var expected_rendered = [_]u8{0} ** 48;
    const expected_text = try std.fmt.bufPrint(
        &expected_rendered,
        "1,3,{d},{d}",
        .{ bitmap.bits_per_long + 2, bitmap.bits_per_long + 4 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);

    var labelled = [_]u8{0} ** 64;
    labelled[0] = ' ';
    labelled[1] = ' ';
    _ = string.strscpyPad(labelled[2..], "gap:");
    @memcpy(labelled[6 .. 6 + rendered_len], rendered[0..rendered_len]);
    labelled[6 + rendered_len] = '\n';
    labelled[7 + rendered_len] = 0;

    const trimmed = string.trimSpaces(&labelled);
    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix(trimmed, "gap:"));
    try std.testing.expect(string.strEndsWith(trimmed, expected_text));
    _ = string.replaceChar(trimmed, ',', '|');
    const choices = [_][]const u8{
        "gap:1|3|missing",
        trimmed,
        "gap:blocked",
    };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&choices, trimmed));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&choices, labelled[2 .. 7 + rendered_len]));

    var entries = [_]Entry{
        .{ .key = fourth_gap, .serial = 0 },
        .{ .key = second_gap, .serial = 1 },
        .{ .key = third_gap, .serial = 2 },
        .{ .key = first_gap, .serial = 3 },
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&entry.node, &root, entryCmp));
    }
    try std.testing.expectEqual(first_gap, (@as(*const Entry, @fieldParentPtr("node", rbtree.firstCached(&root).?))).key);

    rbtree.eraseInitCached(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try std.testing.expectEqual(second_gap, (@as(*const Entry, @fieldParentPtr("node", rbtree.firstCached(&root).?))).key);

    entries[3].key = 0;
    entries[3].serial = 4;
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&entries[3].node, &root, entryCmp));
    try std.testing.expectEqual(@as(usize, 0), (@as(*const Entry, @fieldParentPtr("node", rbtree.firstCached(&root).?))).key);

    var keys: [4]usize = undefined;
    const count = collectKeys(&root, &keys);
    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, second_gap, third_gap, fourth_gap }, keys[0..count]);

    _ = rbtree.eraseCached(&entries[3].node, &root);
    rbtree.clearNode(&entries[3].node);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try std.testing.expectEqual(second_gap, (@as(*const Entry, @fieldParentPtr("node", rbtree.firstCached(&root).?))).key);

    _ = entryLess;
}
