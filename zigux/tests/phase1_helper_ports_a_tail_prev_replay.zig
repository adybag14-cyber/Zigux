const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "bitmap tail predicates ignore storage beyond the declared window" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;
    const tail_bit = @as(Word, 1) << 2;
    const tail_noise = ~bitmap.lastWordMask(nbits);

    var lhs = [_]Word{ 0, tail_bit | tail_noise };
    var rhs = [_]Word{ 0, tail_bit };

    try std.testing.expect(bitmap.equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.subset(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.intersects(&lhs, &rhs, nbits));

    rhs[1] = 0;
    try std.testing.expect(!bitmap.subset(&lhs, &rhs, nbits));
    try std.testing.expect(!bitmap.intersects(&lhs, &rhs, nbits));
}

test "find_bit andnot scans clamp noisy tail words" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 3;
    const boundary = find_bit.bits_per_long;
    const in_range = @as(Word, 1) << 1;
    const out_of_range = @as(Word, 1) << 7;

    const lhs = [_]Word{ 0, in_range | out_of_range };
    const rhs = [_]Word{ 0, out_of_range };

    try std.testing.expectEqual(boundary + 1, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, boundary));
    try std.testing.expectEqual(boundary + 1, find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, boundary + 1));
    try std.testing.expectEqual(nbits, find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, boundary + 2));
}

test "string replace aliases stop at NUL and report the C-string boundary" {
    var direct = [_]u8{ 'a', '-', 'b', 0, '-', 'c' };
    var alias = direct;

    try std.testing.expectEqual(@as(usize, 3), string.replaceChar(&direct, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '_', 'b', 0, '-', 'c' }, &direct);

    try std.testing.expectEqual(@as(usize, 3), string.strreplace(&alias, '-', '_'));
    try std.testing.expectEqualSlices(u8, &direct, &alias);
}

test "rbtree prev aliases walk predecessor chain across subtrees" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 7 },
        .{ .key = 20 },
        .{ .key = 15 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var order: [entries.len]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.rb_last(&root);
    while (current) |node| : (current = rbtree.rb_prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 20, 15, 10, 7, 5 }, order[0..count]);
    try std.testing.expect(rbtree.prev(&entries[1].node) == null);
}
