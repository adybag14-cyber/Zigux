const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap overlapping ranges render and compare only declared bits" {
    const nbits = bits_per_long + 13;
    var map = [_]Word{ 0, 0, ~@as(Word, 0) };
    var expected = [_]Word{ 0, 0, 0 };
    var noisy_expected = [_]Word{ 0, 0, 0x55aa };
    var buffer = [_]u8{0} ** 32;

    bitmap.setRange(&map, bits_per_long - 3, 10);
    bitmap.setRange(&map, bits_per_long + 4, 6);
    bitmap.setRange(&expected, bits_per_long - 3, 13);
    bitmap.setRange(&noisy_expected, bits_per_long - 3, 13);

    try std.testing.expectEqual(@as(usize, 13), bitmap.weight(&map, nbits));
    try std.testing.expect(bitmap.equal(&map, &expected, nbits));
    try std.testing.expect(bitmap.equal(&map, &noisy_expected, nbits));
    try std.testing.expect(bitmap.subset(&expected, &map, nbits));
    try std.testing.expect(bitmap.intersects(&map, &expected, nbits));

    bitmap.clearRange(&map, bits_per_long, 4);
    var expected_render = [_]u8{0} ** 32;
    const expected_text = try std.fmt.bufPrint(
        &expected_render,
        "{d}-{d},{d}-{d}",
        .{ bits_per_long - 3, bits_per_long - 1, bits_per_long + 4, bits_per_long + 9 },
    );
    const written = bitmap.scnprintf(&map, nbits, &buffer);
    try std.testing.expectEqualStrings(expected_text, buffer[0..written]);
}

test "find_bit andnot and last-bit scans ignore masked and out-of-range tail bits" {
    const nbits = bits_per_long + 10;
    var lhs = [_]Word{ 0, 0 };
    var rhs = [_]Word{ 0, 0 };

    lhs[0] |= @as(Word, 1) << @intCast(bits_per_long - 1);
    lhs[1] |= @as(Word, 1) << 2;
    lhs[1] |= @as(Word, 1) << 11;
    rhs[0] |= @as(Word, 1) << @intCast(bits_per_long - 1);

    try std.testing.expectEqual(bits_per_long + 2, find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(bits_per_long + 2, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bits_per_long));
    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bits_per_long + 3));
    try std.testing.expectEqual(bits_per_long + 2, find_bit.findLastBit(&lhs, nbits));

    try std.testing.expectEqual(bits_per_long + 2, find_bit.find_first_andnot_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(nbits, find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, nbits));
}

test "string dirty-byte and suffix helpers respect counted and C-string boundaries" {
    const padded = "xxxxxxxxxxxxxxxxQxxxx";
    const nul_tail = "drivers/foo.zig\x00.c";

    try std.testing.expectEqual(@as(?usize, 16), string.memchrInv(padded, 'x'));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv("yyyyyyyy", 'y'));
    try std.testing.expect(string.strEndsWith(nul_tail, ".zig\x00ignored"));
    try std.testing.expect(string.str_ends_with(nul_tail, "foo.zig"));
    try std.testing.expect(!string.strEndsWith(nul_tail, ".c"));
}

test "rbtree match iterators keep duplicate-key order after replacement" {
    const Entry = struct {
        key: i32,
        tag: u8,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const @This() = @fieldParentPtr("node", lhs);
            const rhs_entry: *const @This() = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }

        fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const @This() = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    };

    var root = rbtree.Root.init();
    var entries = [_]Entry{
        .{ .key = 5, .tag = 'a' },
        .{ .key = 3, .tag = 'b' },
        .{ .key = 5, .tag = 'c' },
        .{ .key = 7, .tag = 'd' },
        .{ .key = 5, .tag = 'e' },
    };
    var replacement = Entry{ .key = 5, .tag = 'r' };

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, Entry.less);
    }
    rbtree.replaceNode(&entries[2].node, &replacement.node, &root);

    const wanted: i32 = 5;
    var iter = rbtree.matchIterator(&wanted, &root, Entry.cmpKey);
    var tags = [_]u8{0} ** 3;
    var count: usize = 0;
    while (iter.next()) |node| : (count += 1) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        tags[count] = entry.tag;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'r', 'e' }, &tags);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextMatch(&wanted, &entries[3].node, Entry.cmpKey));
}
