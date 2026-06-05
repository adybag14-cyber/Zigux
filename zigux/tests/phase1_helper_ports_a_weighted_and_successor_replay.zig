const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn setBit(map: []Word, bit: usize) void {
    map[bit / bits_per_long] |= @as(Word, 1) << @intCast(bit & (bits_per_long - 1));
}

fn entryFromNode(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn lessByKey(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    return entryFromNode(lhs).key < entryFromNode(rhs).key;
}

test "bitmap weighted AND results feed find_bit scans and string suffix matching" {
    const nbits = bits_per_long * 2 + 9;
    var lhs = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var rhs = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var both = [_]Word{0} ** bitmap.bitsToWords(nbits);
    var lhs_only = [_]Word{0} ** bitmap.bitsToWords(nbits);

    setBit(&lhs, 2);
    setBit(&lhs, 9);
    setBit(&lhs, bits_per_long + 4);
    setBit(&lhs, bits_per_long * 2 + 5);
    setBit(&lhs, nbits + 3);

    setBit(&rhs, 9);
    setBit(&rhs, bits_per_long + 4);
    setBit(&rhs, bits_per_long * 2 + 5);
    setBit(&rhs, nbits + 2);

    try std.testing.expect(bitmap.andBits(&both, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&both, nbits));
    try std.testing.expectEqual(@as(usize, 9), find_bit.findFirstAndBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextAndBit(&lhs, &rhs, nbits, 10));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 5), find_bit.findNextAndBit(&lhs, &rhs, nbits, bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&lhs, &rhs, nbits, bits_per_long * 2 + 6));
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 5), find_bit.findLastBit(&both, nbits));

    try std.testing.expect(bitmap.andNotBits(&lhs_only, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 1), bitmap.weight(&lhs_only, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 3));

    var rendered = [_]u8{0} ** 64;
    const rendered_len = bitmap.scnprintf(&both, nbits, &rendered);
    var expected_rendered_buf: [64]u8 = undefined;
    const expected_rendered = try std.fmt.bufPrint(&expected_rendered_buf, "9,{d},{d}", .{ bits_per_long + 4, bits_per_long * 2 + 5 });
    try std.testing.expectEqualStrings(expected_rendered, rendered[0..rendered_len]);

    var label_source_buf: [80]u8 = undefined;
    const label_source = try std.fmt.bufPrint(&label_source_buf, "and:{s}", .{rendered[0..rendered_len]});
    var label = [_]u8{0xaa} ** 80;
    try std.testing.expectEqual(label_source.len, string.strlcpy(&label, label_source));
    try std.testing.expect(string.strEndsWith(&label, rendered[0..rendered_len]));

    var newline_label_buf: [84]u8 = undefined;
    const newline_label = try std.fmt.bufPrint(&newline_label_buf, "{s}\n", .{label_source});
    const haystack = [_][]const u8{
        "or:9",
        newline_label,
        "andnot:2",
    };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&haystack, label_source));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&haystack, label_source));
}

test "bitmap-derived keys keep rbtree successor order stable" {
    const nbits = bits_per_long * 2 + 9;
    const keys = [_]usize{
        bits_per_long * 2 + 5,
        9,
        bits_per_long + 4,
        2,
    };
    var entries: [keys.len]Entry = undefined;
    for (&entries, keys) |*entry, key| {
        entry.* = .{ .key = key };
    }

    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, lessByKey);
    }

    const first = rbtree.rb_first(&root) orelse return error.MissingFirstNode;
    try std.testing.expectEqual(@as(usize, 2), entryFromNode(first).key);

    const second = rbtree.rb_next(first) orelse return error.MissingSecondNode;
    try std.testing.expectEqual(@as(usize, 9), entryFromNode(second).key);

    const third = rbtree.rb_next(second) orelse return error.MissingThirdNode;
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), entryFromNode(third).key);

    const fourth = rbtree.rb_next(third) orelse return error.MissingFourthNode;
    try std.testing.expectEqual(@as(usize, bits_per_long * 2 + 5), entryFromNode(fourth).key);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_next(fourth));

    const last = rbtree.rb_last(&root) orelse return error.MissingLastNode;
    try std.testing.expectEqual(fourth, last);
    try std.testing.expectEqual(third, rbtree.rb_prev(last).?);

    _ = nbits;
}
