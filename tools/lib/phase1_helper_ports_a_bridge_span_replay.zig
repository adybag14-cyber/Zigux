const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;
const nbits = bits_per_long * 2 + 19;
const nwords = bitmap.bitsToWords(nbits);

fn bit(pos: usize) Word {
    return @as(Word, 1) << @intCast(pos & (bits_per_long - 1));
}

fn setBit(words: []Word, pos: usize) void {
    words[pos / bits_per_long] |= bit(pos);
}

test "bridge span bitmap and string cursors stay bounded" {
    var low = [_]Word{0} ** nwords;
    var high = [_]Word{0} ** nwords;
    var bridge = [_]Word{0} ** nwords;
    var tail_gap = [_]Word{0} ** nwords;
    var rendered = [_]u8{0} ** 96;

    setBit(&low, 3);
    setBit(&low, 8);
    setBit(&low, bits_per_long - 2);
    setBit(&low, bits_per_long + 4);
    setBit(&low, bits_per_long * 2 + 5);

    setBit(&high, 8);
    setBit(&high, bits_per_long + 4);
    setBit(&high, bits_per_long + 12);
    setBit(&high, bits_per_long * 2 + 5);
    setBit(&high, bits_per_long * 2 + 17);

    try std.testing.expect(bitmap.andBits(&bridge, &low, &high, nbits));
    try std.testing.expect(bitmap.andNotBits(&tail_gap, &high, &low, nbits));
    try std.testing.expect(bitmap.intersects(&bridge, &tail_gap, nbits) == false);
    try std.testing.expect(bitmap.subset(&bridge, &low, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&bridge, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&tail_gap, nbits));

    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstBit(&bridge, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextBit(&bridge, nbits, 9));
    try std.testing.expectEqual(@as(usize, bits_per_long + 12), find_bit.findNextAndNotBit(&high, &low, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 17), find_bit.findLastBit(&tail_gap, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findNextClump8(&clump, &bridge, nbits, 0));
    try std.testing.expectEqual(@as(u8, 1), clump);

    const rendered_len = bitmap.bitmap_scnprintf(&bridge, nbits, &rendered);
    try std.testing.expect(rendered_len > 0);
    try std.testing.expect(string.strHasPrefix(rendered[0..rendered_len], "8") != 0);
    try std.testing.expect(string.strEndsWith(rendered[0..rendered_len], "133"));

    var label = [_]u8{ ' ', 'b', 'r', 'i', 'd', 'g', 'e', '-', 's', 'p', 'a', 'n', '\n', 0 };
    const trimmed = string.strim(&label);
    try std.testing.expectEqualSlices(u8, "bridge-span", trimmed);
    _ = string.strreplace(trimmed, '-', '_');
    try std.testing.expect(string.sysfsStreq(trimmed, "bridge_span\n"));
}

test "bridge span keys drain through cached rbtree order" {
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

    const cmp_key = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const usize = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = bits_per_long + 4 },
        .{ .key = bits_per_long + 12 },
        .{ .key = bits_per_long * 2 + 5 },
        .{ .key = bits_per_long * 2 + 17 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(&entries[0].node, rbtree.firstCached(&root).?);

    var bridge_key: usize = bits_per_long * 2 + 5;
    const found: *const Entry = @fieldParentPtr("node", rbtree.find(&bridge_key, &root.root, cmp_key).?);
    try std.testing.expectEqual(bridge_key, found.key);

    _ = rbtree.eraseCached(&entries[0].node, &root);
    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));

    var order: [3]usize = undefined;
    var count: usize = 0;
    var current = rbtree.firstCached(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqualSlices(usize, &[_]usize{
        bits_per_long + 12,
        bits_per_long * 2 + 5,
        bits_per_long * 2 + 17,
    }, order[0..count]);
}
