const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay bitmap copy-and-extend keeps subset and tail-only noise explicit" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 6;
    const size = bitmap.bits_per_long * 3;
    const src = [_]Word{
        0b10101,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 5) | (@as(Word, 1) << 8),
        ~@as(Word, 0),
    };
    var extended = [_]Word{ ~@as(Word, 0), ~@as(Word, 0), ~@as(Word, 0) };
    const tail_noise = [_]Word{ 0, @as(Word, 1) << 8, 0 };

    bitmap.bitmap_copy_and_extend(&extended, src[0..2], nbits, size);

    try std.testing.expectEqual(src[0], extended[0]);
    try std.testing.expectEqual(src[1] & bitmap.lastWordMask(nbits), extended[1]);
    try std.testing.expectEqual(@as(Word, 0), extended[2]);
    try std.testing.expect(bitmap.bitmap_subset(src[0..2], extended[0..2], nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(extended[0..2], tail_noise[0..2], nbits));
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(extended[0..2], nbits));
}

test "lane06 replay find-bit clumps and shared tails stay reachable across byte and word boundaries" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 16;
    const map = [_]Word{
        (@as(Word, 1) << 9) | (@as(Word, 1) << 14),
        (@as(Word, 1) << 0) | (@as(Word, 1) << 7),
    };
    const shared = [_]Word{ 0, @as(Word, 1) << 7 };
    var clump: u8 = 0xaa;

    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &map, nbits, 10));
    try std.testing.expectEqual(@as(u8, 0b0100_0010), clump);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextBit(&map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 7), find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 7), find_bit.findFirstAndBit(&map, &shared, nbits));
}

test "lane06 replay string suffix and bounded sysfs searches honor C-string edges" {
    const edge = [_]u8{ 'l', 'o', 'g', 0, 'x', 'x' };
    const modes = [_][]const u8{ "off\n", "auto", "auto\n", "on" };

    try std.testing.expect(string.strEndsWith(edge[0..], "og"));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(edge[0..], edge.len, 'x'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(edge[0..], edge.len, 'g'));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(modes[0..], "auto"));
}

test "lane06 replay cached rbtree promotion preserves duplicate iteration order" {
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

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 10, .serial = 3 },
        .{ .key = 12, .serial = 4 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.rb_first_cached(&root));
    const promoted = rbtree.rb_erase_cached(&entries[2].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_first_cached(&root));

    const duplicate = @as(i32, 10);
    var iter = rbtree.matchIterator(&duplicate, &root.root, cmp);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 1, 3 }, serials[0..count]);
}
