const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "phase1 helper ports A copy and replace keep masked tail semantics" {
    const nbits = bitmap.bits_per_long + 9;
    const tail_noise = @as(bitmap.Word, 1) << 13;
    const src = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 7),
        (@as(bitmap.Word, 1) << 2) | tail_noise,
    };

    var copied = [_]bitmap.Word{ 0, ~@as(bitmap.Word, 0) };
    bitmap.copyClearTail(&copied, &src, nbits);
    try std.testing.expectEqual(src[0], copied[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 1) << 2, copied[1]);
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&copied, nbits));

    const old = [_]bitmap.Word{ (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3), (@as(bitmap.Word, 1) << 1) | tail_noise };
    const new = [_]bitmap.Word{ @as(bitmap.Word, 1) << 5, (@as(bitmap.Word, 1) << 8) | tail_noise };
    const mask = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 8) | tail_noise };
    var replaced = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);

    try std.testing.expectEqual(old[0], replaced[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 1) << 8, replaced[1]);
    try std.testing.expect(!bitmap.bitmap_equal(&replaced, &old, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&replaced, &new, nbits));
}

test "phase1 helper ports A and andnot scans honor aliases and tail cutoffs" {
    const nbits = find_bit.bits_per_long + 10;
    const lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 5),
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 9) | (@as(find_bit.Word, 1) << 12),
    };
    const rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 7),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.findFirstAndBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.find_first_and_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 3));

    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 9), find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 10));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 9), find_bit.findLastBit(&lhs, nbits));
}

test "phase1 helper ports A trimming suffix and counted search preserve C-string limits" {
    var padded = [_]u8{ ' ', '\t', 'z', 'i', 'g', 'u', 'x', ' ', '\n', 0, 'x', 'x' };
    const trimmed = string.strim(&padded);
    try std.testing.expectEqualStrings("zigux", trimmed);
    try std.testing.expectEqual(@as(u8, 0), padded[7]);

    var compact = [_]u8{ 'a', ' ', 'b', ' ', 0, 'c' };
    const no_spaces = string.remove_spaces(&compact);
    try std.testing.expectEqualStrings("ab", no_spaces);
    try std.testing.expectEqual(@as(u8, 0), compact[2]);

    try std.testing.expect(string.strEndsWith(&[_]u8{ 'p', 'o', 'r', 't', 0, 'x' }, "ort"));
    try std.testing.expect(!string.str_ends_with(&[_]u8{ 'p', 'o', 'r', 't', 0, 'x' }, "tx"));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&[_]u8{ 'a', 'b', 'c', 0, 'd' }, 4, 'c'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 'b', 'c', 0, 'd' }, 5, 'd'));
}

test "phase1 helper ports A cached erase advances leftmost and clears removed node" {
    const Entry = struct {
        const Self = @This();

        key: i32,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Self = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Self = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    };

    var entries = [_]Entry{
        .{ .key = 4 },
        .{ .key = 2 },
        .{ .key = 6 },
        .{ .key = 1 },
        .{ .key = 3 },
    };
    var cached = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &cached, Entry.less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.rb_first_cached(&cached));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_erase_cached(&entries[3].node, &cached));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&cached));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[4].node), rbtree.rb_next(&entries[1].node));

    rbtree.rb_erase_init_cached(&entries[1].node, &cached);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[4].node), rbtree.rb_first_cached(&cached));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_next(&entries[4].node));
}
