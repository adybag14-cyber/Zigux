const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const DuplicateEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn duplicateLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const DuplicateEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const DuplicateEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn duplicateKeyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const DuplicateEntry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "lane06 replay keeps bitmap allocation and format aliases aligned" {
    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 6;

    try std.testing.expectEqual(@as(usize, @sizeOf(bitmap.Word) * 2), bitmap.bitmap_size(nbits));

    var alias = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_set(&alias, 1, 3);
    bitmap.bitmap_set(&alias, bitmap.bits_per_long + 1, 2);

    var alias_buf: [64]u8 = undefined;
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, &alias_buf);
    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "1-3,{d}-{d}",
        .{ bitmap.bits_per_long + 1, bitmap.bits_per_long + 2 },
    );
    try std.testing.expectEqualStrings(expected_text, alias_buf[0..alias_len]);

    var zeroed_alias: ?[]bitmap.Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed_alias);
    try std.testing.expectEqual(@as(usize, 2), zeroed_alias.?.len);
    for (zeroed_alias.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }

    bitmap.bitmap_free(allocator, &zeroed_alias);
    try std.testing.expect(zeroed_alias == null);
}

test "lane06 replay keeps find_bit alias windows aligned at boundaries and past-end starts" {
    const nbits = find_bit.bits_per_long + 6;
    const set_map = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(find_bit.bits_per_long - 1),
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 4),
    };
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << 4),
    };
    const and_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4),
    };
    const and_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 4),
    };
    const andnot_rhs = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << 1,
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextBit(&set_map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_next_bit(&set_map, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_bit(&set_map, nbits, nbits));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_next_and_bit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndNotBit(&and_lhs, &andnot_rhs, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_andnot_bit(&and_lhs, &andnot_rhs, nbits, nbits));
}

test "lane06 replay keeps string locator and matcher aliases C-string aware" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "on" };
    const plain_haystack = [_][]const u8{ "blue", "green", "red" };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 2), string.matchString(plain_haystack[0..], "red"));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(plain_haystack[0..], "red"));
    try std.testing.expect(string.streq(&[_]u8{ 'o', 'k', 0, 'x' }, "ok"));
    try std.testing.expectEqualStrings("keep", string.skipSpaces("  keep"));
    try std.testing.expectEqualStrings("keep", string.skip_spaces("\tkeep"));
}

test "lane06 replay keeps rbtree duplicate iterators stable across first-match and iterator walks" {
    var entries = [_]DuplicateEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, duplicateLess);
    }

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &root, duplicateKeyCmp) orelse return error.TestUnexpectedResult;

    var direct_serials: [3]usize = undefined;
    var direct_count: usize = 0;

    var direct_cursor: *rbtree.Node = first_match;
    while (true) {
        const entry: *const DuplicateEntry = @fieldParentPtr("node", direct_cursor);
        direct_serials[direct_count] = entry.serial;
        direct_count += 1;
        direct_cursor = rbtree.nextMatch(&wanted, direct_cursor, duplicateKeyCmp) orelse break;
    }

    try std.testing.expectEqual(@as(usize, 3), direct_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, direct_serials[0..direct_count]);

    var direct_iter = rbtree.matchIterator(&wanted, &root, duplicateKeyCmp);
    var iter_count: usize = 0;
    while (true) {
        const direct_node = direct_iter.next();
        if (direct_node == null) break;
        iter_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), iter_count);
}
