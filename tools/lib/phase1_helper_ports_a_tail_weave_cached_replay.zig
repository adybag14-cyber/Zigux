const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

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

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
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

fn collectForward(root: *const rbtree.RootCached, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.firstCached(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        out[count] = entryKey(node);
        count += 1;
    }
    return count;
}

test "tail-weaved bitmap cursors feed string and cached rbtree checks" {
    const nbits = bits_per_long + 6;
    var base = [_]Word{ 0, 0 };
    var overlay = [_]Word{ 0, 0 };
    var merged = [_]Word{ 0, 0 };
    var diff = [_]Word{ 0, 0 };
    var xor_map = [_]Word{ 0, 0 };

    bitmap.setRange(&base, 1, 3);
    bitmap.setRange(&base, 9, 1);
    bitmap.setRange(&base, bits_per_long + 1, 1);
    bitmap.setRange(&base, bits_per_long + 4, 1);
    base[1] |= @as(Word, 1) << 9;

    bitmap.setRange(&overlay, 2, 1);
    bitmap.setRange(&overlay, 4, 1);
    bitmap.setRange(&overlay, bits_per_long + 1, 1);
    bitmap.setRange(&overlay, bits_per_long + 5, 1);
    overlay[1] |= @as(Word, 1) << 10;

    try std.testing.expectEqual(@as(usize, 8), bitmap.weightedOr(&merged, &base, &overlay, nbits));
    try std.testing.expectEqual(@as(usize, 8), bitmap.weight(&merged, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&merged, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findNextBit(&merged, nbits, 4));
    try std.testing.expectEqual(@as(usize, bits_per_long + 5), find_bit.findLastBit(&merged, nbits));

    try std.testing.expect(bitmap.andNotBits(&diff, &base, &overlay, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&diff, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstAndNotBit(&base, &overlay, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextAndNotBit(&base, &overlay, nbits, 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextAndNotBit(&base, &overlay, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findNextZeroBit(&merged, nbits, bits_per_long + 2));

    bitmap.xorBits(&xor_map, &base, &overlay, nbits);
    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&xor_map, nbits));
    try std.testing.expect(!bitmap.intersects(&diff, &overlay, nbits));
    try std.testing.expect(bitmap.subset(&diff, &merged, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &merged, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_1110), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &merged, nbits, 8));
    try std.testing.expectEqual(@as(u8, 0b0000_0010), clump);
    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &merged, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&merged, nbits, &rendered);
    var expected_rendered: [48]u8 = undefined;
    const expected = try std.fmt.bufPrint(
        &expected_rendered,
        "1-4,9,{d},{d}-{d}",
        .{ bits_per_long + 1, bits_per_long + 4, bits_per_long + 5 },
    );
    try std.testing.expectEqualStrings(expected, rendered[0..rendered_len]);

    var padded: [80]u8 = undefined;
    const padded_text = try std.fmt.bufPrint(&padded, "  {s}\n", .{rendered[0..rendered_len]});
    const trimmed = string.trimSpaces(padded_text);
    try std.testing.expectEqualStrings(rendered[0..rendered_len], trimmed);
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(trimmed, "1-4"));
    try std.testing.expect(string.strEndsWith(trimmed, expected[expected.len - 2 ..]));
    try std.testing.expectEqual(@as(?usize, 2), string.memchrInv(&[_]u8{ 0, 0, 7, 0 }, 0));

    var sysfs_buf: [80]u8 = undefined;
    const sysfs_entry = try std.fmt.bufPrint(&sysfs_buf, "{s}\n", .{trimmed});
    const options = [_][]const u8{ "idle", sysfs_entry, "fallback" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&options, trimmed));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&options, trimmed));

    var entries = [_]Entry{
        .{ .key = 1, .serial = 0 },
        .{ .key = 4, .serial = 1 },
        .{ .key = 9, .serial = 2 },
        .{ .key = bits_per_long + 1, .serial = 3 },
        .{ .key = bits_per_long + 5, .serial = 4 },
        .{ .key = 4, .serial = 5 },
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    const duplicate_key = @as(usize, 4);
    const first_match = rbtree.findFirst(&duplicate_key, &root.root, keyCmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), entrySerial(first_match));
    const second_match = rbtree.nextMatch(&duplicate_key, first_match, keyCmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 5), entrySerial(second_match));
    try std.testing.expect(rbtree.nextMatch(&duplicate_key, second_match, keyCmp) == null);

    var replacement = Entry{ .key = 1, .serial = 6 };
    rbtree.replaceNodeCached(&entries[0].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));

    const promoted = rbtree.eraseCached(&replacement.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 4), entryKey(promoted));
    try std.testing.expectEqual(@as(?*rbtree.Node, promoted), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[5].node), rbtree.firstCached(&root));

    var order: [5]usize = undefined;
    const count = collectForward(&root, &order);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 4, 9, bits_per_long + 1, bits_per_long + 5 }, order[0..count]);
}
