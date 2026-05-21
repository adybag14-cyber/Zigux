const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const RbtreeEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryOf(node: *const rbtree.Node) *const RbtreeEntry {
    return @fieldParentPtr("node", node);
}

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry = entryOf(lhs);
    const rhs_entry = entryOf(rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn entryCmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry = entryOf(lhs);
    const rhs_entry = entryOf(rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry = entryOf(node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "phase1 helper ports A suffix-last-reseed replay keeps masked bitmap merges formatted across word boundaries" {
    const nbits = bitmap.bits_per_long + 10;
    var lhs = [_]bitmap.Word{ 0, 0 };
    var rhs = [_]bitmap.Word{ 0, 0 };

    bitmap.bitmap_set(lhs[0..], bitmap.bits_per_long - 2, 4);
    bitmap.bitmap_set(rhs[0..], 5, 2);
    rhs[1] |= (@as(bitmap.Word, 1) << 9) | (@as(bitmap.Word, 1) << 20);

    var merged = [_]bitmap.Word{ 0, 0 };
    const merged_weight = bitmap.bitmap_weighted_or(merged[0..], lhs[0..], rhs[0..], nbits);
    try std.testing.expectEqual(@as(usize, 7), merged_weight);
    try std.testing.expectEqual(@as(usize, 7), bitmap.bitmap_weight(merged[0..], nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 9), find_bit.findLastBit(merged[0..], nbits));

    var tail_cleared = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_copy_clear_tail(tail_cleared[0..], merged[0..], nbits);
    try std.testing.expectEqual(merged[0], tail_cleared[0]);
    try std.testing.expectEqual(merged[1] & bitmap.lastWordMask(nbits), tail_cleared[1]);
    try std.testing.expect(merged[1] != tail_cleared[1]);

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(tail_cleared[0..], nbits, &rendered);

    var expected: [64]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "5-6,{d}-{d},{d}",
        .{ bitmap.bits_per_long - 2, bitmap.bits_per_long + 1, bitmap.bits_per_long + 9 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);
}

test "phase1 helper ports A suffix-last-reseed replay keeps tail clumps and last-bit scans aligned" {
    const nbits = find_bit.bits_per_long + 11;
    const set_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 0) |
            (@as(find_bit.Word, 1) << 3) |
            (@as(find_bit.Word, 1) << 10) |
            (@as(find_bit.Word, 1) << 17),
    };
    const masked_out = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 0 };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 10), find_bit.findLastBit(set_map[0..], nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findNextClump8(&clump, set_map[0..], nbits, find_bit.bits_per_long + 1),
    );
    try std.testing.expectEqual(@as(u8, 0b0000_1001), clump);

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 8),
        find_bit.findNextClump8(&clump, set_map[0..], nbits, find_bit.bits_per_long + 9),
    );
    try std.testing.expectEqual(@as(u8, 0b0000_0100), clump);

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 3),
        find_bit.findNextAndNotBit(set_map[0..], masked_out[0..], nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 10),
        find_bit.findNextAndNotBit(set_map[0..], masked_out[0..], nbits, find_bit.bits_per_long + 4),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextAndNotBit(set_map[0..], masked_out[0..], nbits, nbits),
    );
}

test "phase1 helper ports A suffix-last-reseed replay keeps string suffix parsing and sysfs matching bounded" {
    try std.testing.expectEqual(@as(usize, 4), string.str_has_prefix("mode=64", "mode"));
    try std.testing.expect(string.strEndsWith("kernel.bin", ".bin"));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("mode=64", 4, '='));
    try std.testing.expectEqual(@as(?usize, 4), string.strnchr("mode=64", 7, '='));

    const choices = [_][]const u8{ "off", "auto\n", "manual" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(choices[0..2], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(choices[0..1], "auto"));

    const parsed = string.memparse("-32Krest");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -32768))), parsed.value);
    try std.testing.expectEqualStrings("rest", parsed.rest);
}

test "phase1 helper ports A suffix-last-reseed replay keeps cached duplicate walks stable across leftmost reseed" {
    var entries = [_]RbtreeEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var duplicate_probe = RbtreeEntry{ .key = 10, .serial = 4 };
    var replacement = RbtreeEntry{ .key = 15, .serial = 5 };
    var new_leftmost = RbtreeEntry{ .key = 3, .serial = 6 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, entryLess);
    }

    const first_before = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 5), entryOf(first_before).key);

    const existing = rbtree.findAddCached(&duplicate_probe.node, &root, entryCmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 10), entryOf(existing).key);
    try std.testing.expectEqual(@as(usize, 0), entryOf(existing).serial);

    const wanted = @as(i32, 10);
    var before_iter = rbtree.matchIterator(&wanted, &root.root, keyCmp);
    var before_serials: [2]usize = undefined;
    var before_count: usize = 0;
    while (before_iter.next()) |node| {
        before_serials[before_count] = entryOf(node).serial;
        before_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), before_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2 }, before_serials[0..before_count]);

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    const first_after_erase = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 10), entryOf(first_after_erase).key);
    try std.testing.expectEqual(@as(usize, 0), entryOf(first_after_erase).serial);

    rbtree.replaceNodeCached(&entries[3].node, &replacement.node, &root);
    const first_after_replace = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 10), entryOf(first_after_replace).key);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.last(&root.root));

    _ = rbtree.addCached(&new_leftmost.node, &root, entryLess);
    const first_after_reseed = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 3), entryOf(first_after_reseed).key);
    try std.testing.expectEqual(@as(usize, 6), entryOf(first_after_reseed).serial);

    var after_iter = rbtree.matchIterator(&wanted, &root.root, keyCmp);
    var after_serials: [2]usize = undefined;
    var after_count: usize = 0;
    while (after_iter.next()) |node| {
        after_serials[after_count] = entryOf(node).serial;
        after_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), after_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2 }, after_serials[0..after_count]);
}
