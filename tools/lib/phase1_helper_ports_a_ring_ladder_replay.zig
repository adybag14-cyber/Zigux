const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: usize,
    ordinal: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn lessByKey(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.ordinal < rhs_entry.ordinal;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn collectForward(root: *const rbtree.RootCached, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.firstCached(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

fn collectReverse(root: *const rbtree.RootCached, out: []usize) usize {
    var count: usize = 0;
    var cursor = rbtree.last(&root.root);
    while (cursor) |node| : (cursor = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "phase1 helper ports A ring ladder replay" {
    const nbits = bits_per_long * 2 + 19;
    const low = bits_per_long - 5;
    const mid = bits_per_long + 9;
    const high = bits_per_long * 2 + 7;

    var base = [_]Word{ 0, 0, 0 };
    var overlay = [_]Word{ 0, 0, 0 };
    var mask = [_]Word{ 0, 0, 0 };
    var replaced = [_]Word{ 0, 0, 0 };
    var pruned = [_]Word{ 0, 0, 0 };

    bitmap.setRange(&base, 2, 4);
    bitmap.setRange(&base, low, 3);
    bitmap.setRange(&base, mid, 2);
    bitmap.setRange(&base, high, 1);

    bitmap.setRange(&overlay, 4, 2);
    bitmap.setRange(&overlay, low + 6, 2);
    bitmap.setRange(&overlay, mid + 4, 1);
    bitmap.setRange(&overlay, high + 3, 2);

    bitmap.setRange(&mask, 3, 6);
    bitmap.setRange(&mask, low, 10);
    bitmap.setRange(&mask, mid, 6);
    bitmap.setRange(&mask, high + 3, 3);

    bitmap.replace(&replaced, &base, &overlay, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 9), bitmap.weight(&replaced, nbits));
    try std.testing.expect(bitmap.intersects(&replaced, &overlay, nbits));
    try std.testing.expect(bitmap.subset(&overlay, &replaced, nbits));

    const removed = bitmap.andNotBits(&pruned, &replaced, &overlay, nbits);
    try std.testing.expect(removed);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&pruned, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstBit(&pruned, nbits));
    try std.testing.expectEqual(@as(usize, high), find_bit.findNextBit(&pruned, nbits, low));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&pruned, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findFirstAndBit(&replaced, &overlay, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndNotBit(&replaced, &overlay, nbits));
    try std.testing.expectEqual(@as(usize, high), find_bit.findLastBit(&pruned, nbits));

    var clump: u8 = 0;
    const clump_offset = find_bit.findNextClump8(&clump, &replaced, nbits, low + 1);
    try std.testing.expectEqual(@as(usize, low + 5), clump_offset);
    try std.testing.expectEqual(@as(u8, 0b0000_0110), clump);

    var rendered: [96]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&replaced, nbits, &rendered);
    var decorated: [112]u8 = undefined;
    const decorated_text = try std.fmt.bufPrint(
        &decorated,
        "  ladder:{s}:tail\n",
        .{rendered[0..rendered_len]},
    );
    var text_buf: [112]u8 = @splat(0);
    @memcpy(text_buf[0..decorated_text.len], decorated_text);

    const trimmed = string.strim(&text_buf);
    try std.testing.expect(string.strstarts(trimmed, "ladder:"));
    try std.testing.expect(string.strEndsWith(trimmed, ":tail"));
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(&[_][]const u8{ trimmed, "missing" }, trimmed));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&[_][]const u8{ "on\n", "off" }, "on"));
    try std.testing.expectEqual(@as(?usize, 1), string.memchrInv(trimmed[0..8], 'l'));
    try std.testing.expectEqual(@as(?usize, 6), string.strnchr(trimmed, 12, ':'));

    var entries = [_]Entry{
        .{ .key = high, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = low + 5, .ordinal = 2 },
        .{ .key = mid + 4, .ordinal = 3 },
        .{ .key = 4, .ordinal = 4 },
        .{ .key = high + 3, .ordinal = 5 },
        .{ .key = low + 6, .ordinal = 6 },
        .{ .key = high + 4, .ordinal = 7 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, lessByKey);
    }

    var forward: [entries.len]usize = undefined;
    const forward_count = collectForward(&root, &forward);
    try std.testing.expectEqualSlices(
        usize,
        &[_]usize{ 2, 4, low + 5, low + 6, mid + 4, high, high + 3, high + 4 },
        forward[0..forward_count],
    );

    var wanted: usize = high;
    const found = rbtree.find(&wanted, &root.root, cmpKey) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(high, found_entry.key);

    const promoted = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    const promoted_entry: *const Entry = @fieldParentPtr("node", promoted);
    try std.testing.expectEqual(@as(usize, 4), promoted_entry.key);
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    var reverse: [entries.len]usize = undefined;
    const reverse_count = collectReverse(&root, &reverse);
    try std.testing.expectEqualSlices(
        usize,
        &[_]usize{ high + 4, high + 3, mid + 4, low + 6, low + 5, 4 },
        reverse[0..reverse_count],
    );
}
