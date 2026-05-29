const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = find_bit.Word;

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),

    fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
        const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
        const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
        if (lhs_entry.key != rhs_entry.key) {
            return lhs_entry.key < rhs_entry.key;
        }
        return lhs_entry.serial < rhs_entry.serial;
    }
};

fn bit(bit_index: usize) Word {
    return @as(Word, 1) << @intCast(bit_index & (find_bit.bits_per_long - 1));
}

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

test "phase1 ports A bitmap and find_bit agree on a sparse tail window" {
    const nbits = find_bit.bits_per_long + 9;
    var lhs = [_]Word{ 0, 0 };
    var rhs = [_]Word{ 0, 0 };
    var out = [_]Word{ 0, 0 };

    lhs[0] = bit(7) | bit(find_bit.bits_per_long - 1);
    lhs[1] = bit(2) | bit(8) | bit(18);
    rhs[1] = bit(8) | bit(18);

    try std.testing.expectEqual(@as(usize, 7), find_bit.findFirstBit(&lhs, nbits));
    try std.testing.expectEqual(find_bit.bits_per_long + 2, find_bit.findNextBit(&lhs, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(&lhs, nbits, find_bit.bits_per_long + 9));

    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(&lhs, nbits));
    try std.testing.expect(bitmap.andNotBits(&out, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&out, nbits));
    try std.testing.expectEqual(find_bit.bits_per_long + 2, find_bit.findNextBit(&out, nbits, find_bit.bits_per_long));

    bitmap.complement(&out, &lhs, nbits);
    try std.testing.expectEqual(nbits - 4, bitmap.weight(&out, nbits));
    try std.testing.expect(bitmap.full(&out, nbits) == false);
}

test "phase1 ports A string helpers preserve C-string and padding boundaries" {
    var pad = [_]u8{ 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(&pad, &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &pad);

    try std.testing.expectEqual(@as(?usize, 2), string.memchr_inv(&[_]u8{ 0xaa, 0xaa, 0xbb, 0xaa }, 0xaa));
    try std.testing.expectEqual(@as(?usize, null), string.memchr_inv(&[_]u8{ 0, 0, 0, 0 }, 0));

    var spaced = [_]u8{ ' ', 'a', ' ', 'b', 0, 'x' };
    const compact = string.remove_spaces(&spaced);
    try std.testing.expectEqualStrings("ab", compact);
    try std.testing.expectEqual(@as(usize, 2), string.strreplace(&spaced, 'b', 'c'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'c', 0, 'b', 0, 'x' }, &spaced);
}

test "phase1 ports A rbtree cached leftmost and successor aliases stay aligned" {
    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = 40, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 30, .serial = 2 },
        .{ .key = 20, .serial = 3 },
    };

    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, Entry.less);
    }

    const first = rbtree.rb_first_cached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 10), entryFromNode(first).key);

    const second = rbtree.rb_next(first) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 20), entryFromNode(second).key);

    rbtree.rb_erase_init_cached(@constCast(first), &root);
    try std.testing.expect(rbtree.emptyNode(first));

    const new_first = rbtree.rb_first_cached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 20), entryFromNode(new_first).key);
    try std.testing.expectEqual(@as(i32, 40), entryFromNode(rbtree.rb_last(&root.root).?).key);
}
