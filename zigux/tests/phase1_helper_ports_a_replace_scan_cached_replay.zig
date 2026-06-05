const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

test "replace scan replay keeps declared tails and text summaries aligned" {
    const nbits = bitmap.bits_per_long + 9;
    const old = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << 8),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 7) | (@as(Word, 1) << 12),
    };
    const new = [_]Word{
        (@as(Word, 1) << 5) | (@as(Word, 1) << 8),
        (@as(Word, 1) << 4) | (@as(Word, 1) << 8) | (@as(Word, 1) << 14),
    };
    const mask = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << 5),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 8) | (@as(Word, 1) << 14),
    };
    var replaced = [_]Word{ 0, 0 };
    var copied = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };

    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);
    bitmap.bitmap_copy_clear_tail(copied[0..2], &replaced, nbits);

    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&replaced, nbits));
    try std.testing.expectEqualSlices(Word, &replaced, copied[0..2]);
    try std.testing.expectEqual(@as(Word, ~@as(Word, 0)), copied[2]);
    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextBit(&replaced, nbits, 6));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 8), find_bit.findLastBit(&replaced, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 7), find_bit.findNextAndBit(&replaced, &old, nbits, bitmap.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&replaced, nbits, bitmap.bits_per_long + 9));

    var ranges: [64]u8 = @splat(0xaa);
    const rendered_len = bitmap.scnprintf(&replaced, nbits, &ranges);
    var stable_ranges: [64]u8 = @splat(0);
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpyPad(&stable_ranges, ranges[0..rendered_len]));
    try std.testing.expectEqualStrings(ranges[0..rendered_len], stable_ranges[0..rendered_len]);
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(stable_ranges[rendered_len + 1 ..], 0));

    var summary = [_]u8{ ' ', 'r', 'e', 'p', 'l', 'a', 'c', 'e', ' ', 's', 'c', 'a', 'n', ' ', 0, 'x' };
    const trimmed = string.strim(&summary);
    try std.testing.expectEqualStrings("replace scan", trimmed);
    try std.testing.expectEqual(@as(usize, 12), string.replaceChar(trimmed, ' ', '-'));
    try std.testing.expectEqualStrings("replace-scan", trimmed[0..12]);
    try std.testing.expectEqual(@as(usize, 7), string.strHasPrefix(trimmed, "replace"));
    try std.testing.expectEqual(@as(?usize, 0), string.memchrInv(summary[0..15], 0));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(summary[13..15], 0));
}

test "cached rbtree replay uses bitmap-derived keys after string normalization" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var key_map = [_]Word{ 0, 0 };
    bitmap.setRange(&key_map, 3, 1);
    bitmap.setRange(&key_map, 11, 1);
    bitmap.setRange(&key_map, bitmap.bits_per_long + 4, 1);
    const first_key: i32 = @intCast(find_bit.findFirstBit(&key_map, bitmap.bits_per_long + 8));
    const second_key: i32 = @intCast(find_bit.findNextBit(&key_map, bitmap.bits_per_long + 8, 4));
    const third_key: i32 = @intCast(find_bit.findLastBit(&key_map, bitmap.bits_per_long + 8));

    var label = [_]u8{ ' ', '3', ' ', '1', '1', ' ', 't', 'a', 'i', 'l', ' ', 0, 'x' };
    const normalized = string.removeSpaces(string.strim(&label));
    try std.testing.expectEqualStrings("311tail", normalized);

    var entries = [_]Entry{
        .{ .key = second_key, .serial = 0 },
        .{ .key = first_key, .serial = 1 },
        .{ .key = third_key, .serial = 2 },
        .{ .key = second_key, .serial = 3 },
    };
    var replacement = Entry{ .key = first_key, .serial = 4 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    var duplicate_iter = rbtree.matchIterator(&second_key, &root.root, cmp);
    var serials: [2]usize = undefined;
    var count: usize = 0;
    while (duplicate_iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 3 }, serials[0..count]);

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    _ = rbtree.addCached(&replacement.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
