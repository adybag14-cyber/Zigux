const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn cmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

test "lane06 replay keeps bitmap allocation and range formatting helpers stable" {
    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 5;

    try std.testing.expectEqual(@as(usize, @sizeOf(bitmap.Word) * 2), bitmap.bitmap_size(nbits));

    var map: ?[]bitmap.Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &map);

    for (map.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }

    bitmap.bitmap_set(map.?, 1, 3);
    bitmap.bitmap_set(map.?, bitmap.bits_per_long + 1, 2);
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(map.?, nbits));
    try std.testing.expect(!bitmap.bitmap_empty(map.?, nbits));

    var buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    const len = bitmap.bitmap_scnprintf(map.?, nbits, &buffer);
    try std.testing.expectEqual(@as(usize, 3), len);
    try std.testing.expectEqualStrings("1-3", buffer[0..len]);
    try std.testing.expectEqual(@as(u8, 0), buffer[len]);

    bitmap.bitmap_fill(map.?, nbits);
    try std.testing.expect(bitmap.bitmap_full(map.?, nbits));

    bitmap.bitmap_free(allocator, &map);
    try std.testing.expect(map == null);
}

test "lane06 replay keeps find_bit clump helpers byte-aligned and miss-stable" {
    const nbits = find_bit.bits_per_long + 8;
    const bitmap_words = [_]find_bit.Word{
        (@as(find_bit.Word, 0xa5) << 8),
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6),
    };

    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&bitmap_words, 8));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstClump8(&clump, &bitmap_words, nbits));
    try std.testing.expectEqual(@as(u8, 0xa5), clump);

    clump = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.find_next_clump8(&clump, &bitmap_words, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(@as(u8, 0b0100_1000), clump);

    clump = 0x5a;
    try std.testing.expectEqual(
        @as(usize, 8),
        find_bit._find_next_clump8(&clump, &[_]find_bit.Word{@as(find_bit.Word, 1) << 3}, 8, 9),
    );
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "lane06 replay keeps string bool copy and prefix-suffix helpers C-string aware" {
    try std.testing.expect(try string.strtobool("Y"));
    try std.testing.expect(!(try string.strtobool("off")));
    try std.testing.expectError(error.Invalid, string.strtobool("maybe"));

    var padded = [_]u8{ 9, 9, 9, 9, 9 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(padded[0..], "hi"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0 }, padded[0..]);

    var alias_padded = [_]u8{ 1, 1, 1, 1 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(alias_padded[0..], "ok"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0 }, alias_padded[0..]);

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&[_]u8{ 'a', 'b', 'c', 0, 'x' }, "abc"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix("abcdef", "abc"));
    try std.testing.expect(string.strstarts("kernel", "ker"));
    try std.testing.expect(string.strEndsWith(&[_]u8{ 'a', 'b', 'c', 0, 'x' }, "bc"));
    try std.testing.expect(string.str_ends_with("kernel", "nel"));
}

test "lane06 replay keeps rbtree duplicate findAdd and erase-init lifecycle stable" {
    var root = rbtree.Root.init();

    var root_entry = Entry{ .key = 10, .serial = 0 };
    var left_entry = Entry{ .key = 5, .serial = 1 };
    var right_entry = Entry{ .key = 15, .serial = 2 };
    var duplicate_entry = Entry{ .key = 10, .serial = 3 };
    var later_entry = Entry{ .key = 12, .serial = 4 };

    rbtree.add(&root_entry.node, &root, less);
    rbtree.add(&left_entry.node, &root, less);
    rbtree.add(&right_entry.node, &root, less);

    const duplicate = rbtree.findAdd(&duplicate_entry.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), duplicate);
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_entry.node), rbtree.first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &right_entry.node), rbtree.last(&root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAdd(&later_entry.node, &root, cmp));

    rbtree.eraseInit(&left_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&left_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.first(&root));

    rbtree.eraseInit(&root_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&root_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &later_entry.node), rbtree.first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &right_entry.node), rbtree.last(&root));
    try std.testing.expect(!rbtree.emptyRoot(&root));
}
