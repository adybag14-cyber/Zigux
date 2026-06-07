const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

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

fn compareNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn compareKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn setBit(map: []Word, bit: usize) void {
    map[bit / bits_per_long] |= @as(Word, 1) << @intCast(bit & (bits_per_long - 1));
}

fn assertOrderedKeys(root: *const rbtree.RootCached, expected: []const i32) !void {
    var index: usize = 0;
    var cursor = rbtree.first(&root.root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        try std.testing.expect(index < expected.len);
        try std.testing.expectEqual(expected[index], entry.key);
        index += 1;
    }
    try std.testing.expectEqual(expected.len, index);
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(root));
}

test "phase1 helper ports A staggered sieve replay" {
    const nbits = bits_per_long * 2 + 11;
    var seed = [_]Word{ 0, 0, 0 };
    var overlay = [_]Word{ 0, 0, 0 };
    var mask = [_]Word{ 0, 0, 0 };

    for ([_]usize{ 1, 3, 9, bits_per_long - 1, bits_per_long + 2, bits_per_long + 6, bits_per_long * 2 + 4 }) |bit| {
        setBit(&seed, bit);
    }
    for ([_]usize{ 3, 4, bits_per_long + 2, bits_per_long + 8, bits_per_long * 2 + 1, bits_per_long * 2 + 8 }) |bit| {
        setBit(&overlay, bit);
    }
    bitmap.setRange(&mask, 2, 8);
    bitmap.setRange(&mask, bits_per_long + 1, 9);
    bitmap.setRange(&mask, bits_per_long * 2, 9);

    var replaced = [_]Word{ 0, 0, ~@as(Word, 0) };
    bitmap.bitmap_replace(&replaced, &seed, &overlay, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 8), bitmap.weight(&replaced, nbits));

    var xor_map = [_]Word{ 0, 0, 0 };
    bitmap.xorBits(&xor_map, &replaced, &seed, nbits);
    try std.testing.expectEqual(@as(usize, 7), bitmap.weight(&xor_map, nbits));

    var copied = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    bitmap.copyAndExtend(&copied, &xor_map, bits_per_long + 7, nbits);
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&copied, nbits));

    var shared = [_]Word{ 0, 0, 0 };
    try std.testing.expect(bitmap.andBits(&shared, &replaced, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&shared, nbits));

    var sieve = [_]Word{ 0, 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&sieve, &shared, &copied, nbits));
    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&sieve, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&sieve, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 2), find_bit.findNextBit(&sieve, nbits, 5));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 1), find_bit.findNextAndBit(&sieve, &overlay, nbits, bits_per_long + 9));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 8), find_bit.findLastBit(&sieve, nbits));
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextZeroBit(&sieve, nbits, 0));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&clump, &sieve, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextClump8(&clump, &sieve, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(u8, 0b0000_0100), clump);

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&sieve, nbits, &rendered);
    var text_buf: [96]u8 = undefined;
    const text = try std.fmt.bufPrint(&text_buf, "  sieve:{s}:done\n", .{rendered[0..rendered_len]});
    var token_buf: [96]u8 = @splat(0);
    @memcpy(token_buf[0..text.len], text);

    const trimmed = string.strim(token_buf[0..]);
    try std.testing.expect(string.str_has_prefix(trimmed, "sieve:") != 0);
    try std.testing.expect(string.strEndsWith(trimmed, ":done"));
    _ = string.strreplace(trimmed, ',', '|');
    try std.testing.expect((string.strnchr(trimmed, trimmed.len, '|') orelse trimmed.len) < trimmed.len);
    try std.testing.expect(string.strnchr(trimmed, trimmed.len, '\n') == null);
    try std.testing.expect(string.memchr_inv("......x", '.') == 6);

    const first_colon = string.strnchr(trimmed, trimmed.len, ':') orelse return error.TestUnexpectedResult;
    const after_label = trimmed[first_colon + 1 ..];
    const second_colon_rel = string.strnchr(after_label, after_label.len, ':') orelse return error.TestUnexpectedResult;
    const label = trimmed[0..first_colon];
    const ranges = after_label[0..second_colon_rel];
    const suffix = after_label[second_colon_rel + 1 ..];
    try std.testing.expectEqualStrings("sieve", label);
    try std.testing.expectEqualStrings("done", suffix);
    try std.testing.expect(string.match_string(&[_][]const u8{ label, ranges, suffix }, ranges) == 1);
    try std.testing.expect(string.sysfs_match_string(&[_][]const u8{ "idle", "done\n" }, "done") == 1);

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 4, .serial = 0 },
        .{ .key = 72, .serial = 1 },
        .{ .key = 74, .serial = 2 },
        .{ .key = 74, .serial = 3 },
        .{ .key = 132, .serial = 4 },
        .{ .key = 136, .serial = 5 },
    };
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }
    try assertOrderedKeys(&root, &[_]i32{ 4, 72, 74, 74, 132, 136 });

    const duplicate_key: i32 = 74;
    var duplicate_iter = rbtree.matchIterator(&duplicate_key, &root.root, compareKey);
    var duplicate_serials: [2]usize = undefined;
    var duplicate_count: usize = 0;
    while (duplicate_iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        duplicate_serials[duplicate_count] = entry.serial;
        duplicate_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), duplicate_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 3 }, duplicate_serials[0..duplicate_count]);

    var duplicate_probe = Entry{ .key = 74, .serial = 99 };
    const existing = rbtree.findAddCached(&duplicate_probe.node, &root, compareNode) orelse return error.TestUnexpectedResult;
    const existing_entry: *const Entry = @fieldParentPtr("node", existing);
    try std.testing.expectEqual(@as(i32, 74), existing_entry.key);
    try std.testing.expect(existing_entry.serial == 2 or existing_entry.serial == 3);

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try assertOrderedKeys(&root, &[_]i32{ 72, 74, 74, 132, 136 });

    var reseed = Entry{ .key = 1, .serial = 6 };
    try std.testing.expectEqual(@as(?*rbtree.Node, &reseed.node), rbtree.addCached(&reseed.node, &root, less));
    try assertOrderedKeys(&root, &[_]i32{ 1, 72, 74, 74, 132, 136 });
}
