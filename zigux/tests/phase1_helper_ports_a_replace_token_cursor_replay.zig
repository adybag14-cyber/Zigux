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

fn collectSetBits(map: []const Word, nbits: usize, out: []usize) usize {
    var count: usize = 0;
    var cursor = find_bit.findFirstBit(map, nbits);
    while (cursor < nbits) : (cursor = find_bit.findNextBit(map, nbits, cursor + 1)) {
        out[count] = cursor;
        count += 1;
    }
    return count;
}

test "replace mask output drives string token cursors and cached duplicate tree scans" {
    const nbits = bits_per_long + 12;
    var old = [_]Word{ 0, 0, 0 };
    var new = [_]Word{ 0, 0, 0 };
    var mask = [_]Word{ 0, 0, 0 };
    var replaced = [_]Word{ 0, 0, 0 };
    var extended = [_]Word{ 0, 0, 0 };

    bitmap.setRange(&old, 2, 2);
    bitmap.setRange(&old, bits_per_long + 1, 2);
    bitmap.setRange(&new, 6, 1);
    bitmap.setRange(&new, bits_per_long + 4, 4);
    bitmap.setRange(&mask, 0, 8);
    bitmap.setRange(&mask, bits_per_long, 8);

    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);
    bitmap.bitmap_copy_and_extend(&extended, &replaced, nbits, bits_per_long * 3);

    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&replaced, nbits));
    try std.testing.expect(bitmap.equal(&replaced, &extended, nbits));
    try std.testing.expectEqual(@as(Word, 0), extended[2]);

    var positions: [8]usize = undefined;
    const position_count = collectSetBits(&replaced, nbits, &positions);
    try std.testing.expectEqual(@as(usize, 5), position_count);
    try std.testing.expectEqualSlices(
        usize,
        &[_]usize{ 6, bits_per_long + 4, bits_per_long + 5, bits_per_long + 6, bits_per_long + 7 },
        positions[0..position_count],
    );

    var old_or_new = [_]Word{ 0, 0, 0 };
    bitmap.bitmap_or(&old_or_new, &old, &new, nbits);
    try std.testing.expectEqual(@as(usize, 6), find_bit.findFirstAndBit(&replaced, &old_or_new, nbits));
    try std.testing.expectEqual(@as(usize, 6), find_bit.findNextBit(&old_or_new, nbits, 4));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextZeroBit(&replaced, nbits, 6));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &replaced, nbits));
    try std.testing.expectEqual(@as(u8, 0b0100_0000), clump);
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextClump8(&clump, &replaced, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b1111_0000), clump);

    var range_buffer: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&replaced, nbits, &range_buffer);
    try std.testing.expectEqualStrings("6,68-71", range_buffer[0..rendered_len]);

    var token_buffer = [_]u8{ ' ', '6', ',', '6', '8', '-', '7', '1', '\n', 0, 'x', 'x' };
    const trimmed = string.strim(token_buffer[0..]);
    try std.testing.expectEqualStrings("6,68-71", trimmed);
    try std.testing.expect(string.sysfsStreq(trimmed, range_buffer[0..rendered_len]));

    const split_at = string.strnchr(trimmed, trimmed.len, ',') orelse return error.TestUnexpectedResult;
    const first_token = trimmed[0..split_at];
    const second_token = trimmed[split_at + 1 ..];
    try std.testing.expectEqualStrings("6", first_token);
    try std.testing.expectEqualStrings("68-71", second_token);

    const haystack = [_][]const u8{ first_token, second_token, "unused" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(haystack[0..], "68-71"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(second_token, second_token.len, '8'));

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = first_token.len, .serial = 0 },
        .{ .key = second_token.len, .serial = 1 },
        .{ .key = position_count, .serial = 2 },
        .{ .key = second_token.len, .serial = 3 },
    };

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    const duplicate_key = second_token.len;
    var iter = rbtree.matchIterator(&duplicate_key, &root.root, keyCmp);
    var serials: [3]usize = undefined;
    var serial_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[serial_count] = entry.serial;
        serial_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), serial_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 2, 3 }, serials[0..serial_count]);

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    const leftmost = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    const leftmost_entry: *const Entry = @fieldParentPtr("node", leftmost);
    try std.testing.expectEqual(@as(usize, second_token.len), leftmost_entry.key);
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
