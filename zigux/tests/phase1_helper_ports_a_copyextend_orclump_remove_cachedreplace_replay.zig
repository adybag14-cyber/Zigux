const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap copy-and-extend masks source tail and zeroes new words" {
    const count = bits_per_long + 5;
    const size = bits_per_long * 3 + 9;
    const tail_noise = (@as(Word, 1) << 5) | (@as(Word, 1) << 12) | (@as(Word, 1) << 31);
    const src = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << (bits_per_long - 1)),
        (@as(Word, 1) << 3) | tail_noise,
    };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };

    bitmap.copyAndExtend(&dst, &src, count, size);

    try std.testing.expectEqual(src[0], dst[0]);
    try std.testing.expectEqual(@as(Word, @as(Word, 1) << 3), dst[1]);
    try std.testing.expectEqual(@as(Word, 0), dst[2]);
    try std.testing.expectEqual(@as(Word, 0), dst[3]);
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&dst, size));
}

test "find-bit or and clump scans clamp noisy partial tails" {
    const nbits = bits_per_long + 13;
    const lhs = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 20) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 10) | (@as(Word, 1) << 17) };
    const tail_noise_only = [_]Word{ 0, @as(Word, 1) << 17 };
    const clump_map = [_]Word{ 0, (@as(Word, 1) << 11) | (@as(Word, 1) << 14) };

    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextOrBit(&lhs, &rhs, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 10), find_bit.findNextOrBit(&lhs, &rhs, nbits, bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextOrBit(&lhs, &rhs, nbits, bits_per_long + 11));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(&tail_noise_only, nbits));

    var clump: u8 = 0xaa;
    try std.testing.expectEqual(@as(usize, bits_per_long + 8), find_bit.findNextClump8(&clump, &clump_map, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);
}

test "string compaction and padding stop at the first C terminator" {
    var compact = [_]u8{ ' ', 'z', ' ', 'i', 0, ' ', 'g', 0xff };
    const compacted = string.removeSpaces(&compact);
    try std.testing.expectEqualSlices(u8, "zi", compacted);
    try std.testing.expectEqual(@as(u8, 0), compact[2]);
    try std.testing.expectEqual(@as(u8, ' '), compact[5]);

    var padded = [_]u8{ 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, "xy\x00ignored"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'x', 'y', 0, 0, 0, 0 }, &padded);

    var raw = [_]u8{ 0xee, 0xee, 0xee, 0xee, 0xee };
    string.strtomem_pad(&raw, "ab\x00tail", '.');
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', '.', '.', '.' }, &raw);
}

test "cached rbtree replacement preserves leftmost and neighbor traversal" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const @This() = @fieldParentPtr("node", lhs);
            const rhs_entry: *const @This() = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    };

    var entries = [_]Entry{
        .{ .key = 20 },
        .{ .key = 10 },
        .{ .key = 30 },
        .{ .key = 25 },
    };
    var replacement = Entry{ .key = 5 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, Entry.less);
    }
    try std.testing.expectEqual(&entries[1].node, rbtree.firstCached(&root).?);

    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(&replacement.node, rbtree.firstCached(&root).?);

    const next = rbtree.next(&replacement.node).?;
    const next_entry: *const Entry = @fieldParentPtr("node", next);
    try std.testing.expectEqual(@as(i32, 20), next_entry.key);

    const prev = rbtree.prev(&entries[3].node).?;
    const prev_entry: *const Entry = @fieldParentPtr("node", prev);
    try std.testing.expectEqual(@as(i32, 20), prev_entry.key);
}
