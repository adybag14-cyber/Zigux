const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "bitmap replace and copy-and-extend keep tail masking and zero-fill aligned" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;

    const old = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 6) };
    const new = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 7) };
    const mask = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 6) | (@as(Word, 1) << 7) };

    var replaced = [_]Word{ 0xffff_ffff_ffff_ffff, 0xffff_ffff_ffff_ffff };
    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);
    try std.testing.expectEqual(@as(Word, 0), replaced[0]);
    try std.testing.expectEqual(@as(Word, 1) << 3, replaced[1]);

    const size = bitmap.bits_per_long * 2 + 3;
    var extended = [_]Word{
        0xffff_ffff_ffff_ffff,
        0xffff_ffff_ffff_ffff,
        0xffff_ffff_ffff_ffff,
    };
    bitmap.bitmap_copy_and_extend(&extended, &new, nbits, size);
    try std.testing.expectEqual(@as(Word, 0), extended[0]);
    try std.testing.expectEqual(@as(Word, 1) << 3, extended[1]);
    try std.testing.expectEqual(@as(Word, 0), extended[2]);
}

test "find-bit clump aliases keep cross-word bytes and past-end windows stable" {
    const Word = find_bit.Word;
    const boundary_offset = find_bit.bits_per_long - 8;
    const nbits = find_bit.bits_per_long + 5;
    const words = [_]Word{
        @as(Word, 0xa5) << @intCast(boundary_offset),
        (@as(Word, 1) << 3) | (@as(Word, 1) << 6),
    };

    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&words, boundary_offset));

    var clump: u8 = 0;
    try std.testing.expectEqual(boundary_offset, find_bit.findFirstClump8(&clump, &words, nbits));
    try std.testing.expectEqual(@as(u8, 0xa5), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&clump, &words, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&clump, &words, nbits, nbits + 4));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "string suffix and bounded searches stop at c-string edges" {
    const cstr = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', '-', 'v', 'a', 'l', 'u', 'e', 0, 'x' };
    try std.testing.expect(string.strstarts(&cstr, "prefix"));
    try std.testing.expect(string.strEndsWith(&cstr, "value"));
    try std.testing.expect(string.str_ends_with(&cstr, "value"));
    try std.testing.expectEqual(@as(?usize, 7), string.strnchr(&cstr, cstr.len, 'v'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, 6, 'v'));

    const embedded = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&embedded, embedded.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&embedded, embedded.len, 'c'));
}

test "cached rbtree singleton erase-init and non-leftmost replace keep first cached aligned" {
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

    var singleton = Entry{ .key = 11 };
    var singleton_root = rbtree.RootCached.init();
    _ = rbtree.addCached(&singleton.node, &singleton_root, less);
    rbtree.eraseInitCached(&singleton.node, &singleton_root);
    try std.testing.expect(rbtree.emptyRoot(&singleton_root.root));
    try std.testing.expect(rbtree.firstCached(&singleton_root) == null);
    try std.testing.expect(rbtree.emptyNode(&singleton.node));

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 20 },
    };
    var replacement = Entry{ .key = 20 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    const leftmost_before = rbtree.firstCached(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[1].node), leftmost_before);

    rbtree.replaceNodeCached(&entries[2].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.last(&root.root));
}
