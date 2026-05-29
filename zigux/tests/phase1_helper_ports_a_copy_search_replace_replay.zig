const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap copy tail feeds find_bit clump scans" {
    const nbits = bits_per_long + 11;
    const tail_bit = bits_per_long + 10;
    const out_of_range_bit = bits_per_long + 14;
    var src = [_]Word{ 0, 0 };
    src[0] = (@as(Word, 1) << 5) | (@as(Word, 1) << 13);
    src[1] = (@as(Word, 1) << 2) | (@as(Word, 1) << 10) | (@as(Word, 1) << 14);

    var copied = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    bitmap.copyClearTail(&copied, &src, nbits);

    try std.testing.expectEqual(src[0], copied[0]);
    try std.testing.expect((copied[1] & (@as(Word, 1) << 10)) != 0);
    try std.testing.expect((copied[1] & (@as(Word, 1) << 14)) == 0);
    try std.testing.expectEqual(@as(usize, tail_bit), find_bit.findLastBit(&copied, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&copied, nbits, tail_bit + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&copied, nbits, out_of_range_bit));

    var clump: u8 = 0xaa;
    const clump_offset = find_bit.findNextClump8(&clump, &copied, nbits, bits_per_long + 1);
    try std.testing.expectEqual(@as(usize, bits_per_long), clump_offset);
    try std.testing.expectEqual(@as(u8, 0b0000_0100), clump & 0b0000_0100);
    try std.testing.expectEqual(@as(u8, 0), clump & 0b1111_1000);
}

test "string replacement and counted search stop at C-string boundaries" {
    var text = [_]u8{ 'a', ' ', 'b', ' ', 0, ' ', 'c' };
    try std.testing.expectEqual(@as(usize, 4), string.strreplace(&text, ' ', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 'b', '_', 0, ' ', 'c' }, &text);

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&text, text.len, '_'));
    try std.testing.expectEqual(@as(?usize, 4), string.strnchr(&text, text.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&text, text.len, 'c'));

    var padded = [_]u8{ 'k', 'e', 'y', 0, 'x', 'x' };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, &[_]u8{ 'o', 'k', 0, '!' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &padded);
}

test "rbtree cached replacement preserves leftmost and search aliases" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const @This() = @fieldParentPtr("node", lhs);
            const rhs_entry: *const @This() = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }

        fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const @This() = @fieldParentPtr("node", node);
            return switch (std.math.order(wanted.*, entry.key)) {
                .lt => -1,
                .eq => 0,
                .gt => 1,
            };
        }
    };

    var entries = [_]Entry{
        .{ .key = 20 },
        .{ .key = 10 },
        .{ .key = 30 },
        .{ .key = 25 },
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, Entry.less);
    }

    var replacement = Entry{ .key = 10 };
    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(&replacement.node, rbtree.firstCached(&root));
    try std.testing.expectEqual(&replacement.node, rbtree.rb_first_cached(&root));

    const key: i32 = 10;
    try std.testing.expectEqual(&replacement.node, rbtree.find(&key, &root.root, Entry.cmpKey));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_prev(&replacement.node));
    try std.testing.expectEqual(&entries[0].node, rbtree.rb_next(&replacement.node));
}
