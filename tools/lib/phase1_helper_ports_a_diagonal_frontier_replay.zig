const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.ordinal < rhs_entry.ordinal;
}

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn keyOf(node: *const rbtree.Node) i32 {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.key;
}

fn ordinalOf(node: *const rbtree.Node) usize {
    const entry: *const Entry = @fieldParentPtr("node", node);
    return entry.ordinal;
}

fn collectForward(root: *const rbtree.RootCached, out: []i32) usize {
    var count: usize = 0;
    var cursor = rbtree.firstCached(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        out[count] = keyOf(node);
        count += 1;
    }
    return count;
}

test "lane06 diagonal frontier replay spans bitmap find-bit string and rbtree" {
    const nbits = bitmap.bits_per_long + 17;
    var base = [_]Word{ 0, 0 };
    var overlay = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };
    var replaced = [_]Word{ 0, 0 };
    var frontier = [_]Word{ 0, 0 };
    var shared = [_]Word{ 0, 0 };
    var diagonal_only = [_]Word{ 0, 0 };
    var complement = [_]Word{ 0, 0 };

    bitmap.setRange(&base, 2, 3);
    bitmap.setRange(&base, 13, 2);
    bitmap.setRange(&base, bitmap.bits_per_long + 1, 3);
    bitmap.setRange(&base, bitmap.bits_per_long + 11, 1);

    bitmap.setRange(&overlay, 1, 2);
    bitmap.setRange(&overlay, 8, 1);
    bitmap.setRange(&overlay, bitmap.bits_per_long + 3, 3);
    bitmap.setRange(&overlay, bitmap.bits_per_long + 15, 1);

    bitmap.setRange(&mask, 1, 8);
    bitmap.setRange(&mask, bitmap.bits_per_long + 3, 6);

    bitmap.bitmap_replace(&replaced, &base, &overlay, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 11), bitmap.weight(&replaced, nbits));
    try std.testing.expect(bitmap.andBits(&shared, &replaced, &overlay, nbits));
    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&shared, nbits));
    try std.testing.expect(bitmap.andNotBits(&diagonal_only, &replaced, &overlay, nbits));
    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&diagonal_only, nbits));

    try std.testing.expectEqual(@as(usize, 6), bitmap.weightedXor(&frontier, &replaced, &overlay, nbits));
    try std.testing.expect(bitmap.andNotBits(&diagonal_only, &frontier, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&diagonal_only, nbits));
    try std.testing.expect(!bitmap.subset(&diagonal_only, &mask, nbits));
    try std.testing.expect(bitmap.intersects(&frontier, &base, nbits));

    bitmap.complement(&complement, &replaced, nbits);
    try std.testing.expectEqual(nbits - 11, bitmap.weight(&complement, nbits));

    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 13), find_bit.findNextBit(&replaced, nbits, 9));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 6), find_bit.findNextZeroBit(&replaced, nbits, bitmap.bits_per_long + 4));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 11), find_bit.findLastBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 15), find_bit.findFirstAndNotBit(&overlay, &replaced, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 15), find_bit.findNextAndNotBit(&overlay, &replaced, nbits, bitmap.bits_per_long + 6));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &replaced, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_0110), clump);
    clump = 0;
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), find_bit.findNextClump8(&clump, &replaced, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0011_1110), clump);

    var rendered: [96]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&replaced, nbits, &rendered);
    try std.testing.expectEqualStrings("1-2,8,13-14,65-69,75", rendered[0..rendered_len]);

    var token_buf: [128]u8 = undefined;
    var token_source: [128]u8 = undefined;
    const token_text = try std.fmt.bufPrint(&token_source, "  diag:{s} \n", .{rendered[0..rendered_len]});
    const copied = string.strlcpy(token_buf[0..], token_text);
    try std.testing.expectEqual(token_text.len, copied);

    const trimmed = string.strim(token_buf[0..]);
    try std.testing.expectEqual(@as(usize, 5), string.strHasPrefix(trimmed, "diag:"));
    try std.testing.expect(string.strEndsWith(trimmed, "75"));
    try std.testing.expectEqual(@as(?usize, 4), string.strnchr(trimmed, trimmed.len, ':'));
    try std.testing.expectEqual(@as(?usize, 6), string.strnchr(trimmed, trimmed.len, '-'));

    var compact_buf = token_buf;
    const compact = string.removeSpaces(compact_buf[0..]);
    _ = string.strreplace(compact, ',', '|');
    try std.testing.expectEqualStrings("diag:1-2|8|13-14|65-69|75", compact);
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&[_][]const u8{ "diag:1-2|8|13-14|65-69|75\n", "other" }, compact));

    var clean_bytes: [32]u8 = @splat('|');
    clean_bytes[9] = ':';
    try std.testing.expectEqual(@as(?usize, 9), string.memchrInv(clean_bytes[0..], '|'));

    const first_key: i32 = @intCast(find_bit.findFirstBit(&replaced, nbits));
    const zero_key: i32 = @intCast(find_bit.findFirstZeroBit(&replaced, nbits));
    const last_key: i32 = @intCast(find_bit.findLastBit(&replaced, nbits));
    const clump_key: i32 = @intCast(find_bit.findNextClump8(&clump, &replaced, nbits, bitmap.bits_per_long));

    var entries = [_]Entry{
        .{ .key = zero_key, .ordinal = 0 },
        .{ .key = first_key, .ordinal = 1 },
        .{ .key = last_key, .ordinal = 2 },
        .{ .key = clump_key, .ordinal = 3 },
        .{ .key = first_key, .ordinal = 4 },
    };
    var replacement_entry = Entry{ .key = zero_key, .ordinal = 99 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, entryLess);
    }

    try std.testing.expectEqual(@as(i32, zero_key), keyOf(rbtree.firstCached(&root).?));
    try std.testing.expectEqual(@as(i32, last_key), keyOf(rbtree.last(&root.root).?));

    var order: [5]i32 = undefined;
    const count = collectForward(&root, &order);
    try std.testing.expectEqual(@as(usize, 5), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ zero_key, first_key, first_key, clump_key, last_key }, order[0..count]);

    const duplicate_first = rbtree.findFirst(&first_key, &root.root, keyCmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), ordinalOf(duplicate_first));
    const duplicate_second = rbtree.nextMatch(&first_key, duplicate_first, keyCmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 4), ordinalOf(duplicate_second));
    try std.testing.expect(rbtree.nextMatch(&first_key, duplicate_second, keyCmp) == null);

    rbtree.replaceNodeCached(&entries[0].node, &replacement_entry.node, &root);
    try std.testing.expectEqual(@as(i32, zero_key), keyOf(rbtree.find(&zero_key, &root.root, keyCmp).?));

    const promoted = rbtree.eraseCached(&replacement_entry.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[1].node), promoted);
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[1].node), rbtree.firstCached(&root).?);

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(i32, first_key), keyOf(rbtree.firstCached(&root).?));

    var reverse: [3]i32 = undefined;
    var reverse_count: usize = 0;
    var cursor = rbtree.last(&root.root);
    while (cursor) |node| : (cursor = rbtree.prev(node)) {
        reverse[reverse_count] = keyOf(node);
        reverse_count += 1;
    }
    try std.testing.expectEqualSlices(i32, &[_]i32{ last_key, clump_key, first_key }, reverse[0..reverse_count]);
}
