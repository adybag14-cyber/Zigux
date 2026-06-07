const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;
const nbits = bits_per_long * 2 + 21;
const nwords = bitmap.bitsToWords(nbits);

fn bit(pos: usize) Word {
    return @as(Word, 1) << @intCast(pos & (bits_per_long - 1));
}

fn setBit(words: []Word, pos: usize) void {
    words[pos / bits_per_long] |= bit(pos);
}

test "ripple carry bitmap cursors and string label stay tail bounded" {
    var seed = [_]Word{0} ** nwords;
    var carry = [_]Word{0} ** nwords;
    var mask = [_]Word{0} ** nwords;
    var combined = [_]Word{0} ** nwords;
    var carry_only = [_]Word{0} ** nwords;
    var rendered = [_]u8{0} ** 128;

    setBit(&seed, bits_per_long - 1);
    setBit(&seed, bits_per_long);
    setBit(&seed, bits_per_long + 5);
    setBit(&seed, bits_per_long * 2 + 3);

    setBit(&carry, 2);
    setBit(&carry, bits_per_long);
    setBit(&carry, bits_per_long + 6);
    setBit(&carry, bits_per_long * 2 + 18);
    setBit(&carry, bits_per_long * 2 + 26);

    bitmap.bitmap_set(&mask, 0, 3);
    bitmap.bitmap_set(&mask, bits_per_long - 1, 9);
    bitmap.bitmap_set(&mask, bits_per_long * 2 + 3, 19);

    bitmap.bitmap_replace(&combined, &seed, &carry, &mask, nbits);
    try std.testing.expect(bitmap.bitmap_andnot(&carry_only, &combined, &seed, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&combined, &mask, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&carry_only, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 4), bitmap.bitmap_weight(&combined, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&carry_only, nbits));

    try std.testing.expectEqual(@as(usize, 2), find_bit.find_first_bit(&combined, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.find_next_bit(&combined, nbits, bits_per_long - 1));
    try std.testing.expectEqual(@as(usize, bits_per_long + 6), find_bit.find_next_andnot_bit(&combined, &seed, nbits, bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 18), find_bit.find_last_bit(&combined, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_next_clump8(&clump, &combined, nbits, 0));
    try std.testing.expectEqual(@as(u8, 0b0000_0100), clump);

    const len = bitmap.bitmap_scnprintf(&combined, nbits, &rendered);
    try std.testing.expect(len > 0);
    try std.testing.expect(string.str_has_prefix(rendered[0..len], "2") != 0);
    try std.testing.expect(string.strEndsWith(rendered[0..len], "146"));

    var label = [_]u8{ ' ', 'r', 'i', 'p', 'p', 'l', 'e', '-', 'c', 'a', 'r', 'r', 'y', '\n', 0 };
    const trimmed = string.strstrip(&label);
    _ = string.strreplace(trimmed, '-', '_');
    try std.testing.expect(string.sysfs_streq(trimmed, "ripple_carry\n"));
}

test "ripple carry cursor keys drain through cached rbtree" {
    const Entry = struct {
        key: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    const cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const usize = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var map = [_]Word{0} ** nwords;
    setBit(&map, 2);
    setBit(&map, bits_per_long);
    setBit(&map, bits_per_long + 6);
    setBit(&map, bits_per_long * 2 + 3);
    setBit(&map, bits_per_long * 2 + 18);

    var entries = [_]Entry{
        .{ .key = find_bit.find_next_bit(&map, nbits, bits_per_long + 1) },
        .{ .key = find_bit.find_first_bit(&map, nbits) },
        .{ .key = find_bit.find_last_bit(&map, nbits) },
        .{ .key = find_bit.find_next_bit(&map, nbits, bits_per_long * 2) },
        .{ .key = find_bit.find_next_bit(&map, nbits, bits_per_long - 1) },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    const wanted = entries[0].key;
    const found = rbtree.find(&wanted, &root.root, cmp) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(bits_per_long + 6, found_entry.key);

    var ordered: [entries.len]usize = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        ordered[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{
        2,
        bits_per_long,
        bits_per_long + 6,
        bits_per_long * 2 + 3,
        bits_per_long * 2 + 18,
    }, ordered[0..count]);

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[4].node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[4].node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
}
