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

fn duplicateCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const DuplicateEntry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "lane06 replay keeps bitmap formatting helpers alias-aligned across range truncation edges" {
    const nbits = bitmap.bits_per_long + 8;
    var map = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&map, bitmap.bits_per_long - 2, 5);
    bitmap.setRange(&map, bitmap.bits_per_long + 6, 1);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&map, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&map, nbits, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{ bitmap.bits_per_long - 2, bitmap.bits_per_long + 2, bitmap.bits_per_long + 6 },
    );
    try std.testing.expectEqualStrings(expected_text, direct_buffer[0..direct_len]);

    var terminator_only = [_]u8{0xaa};
    const terminator_only_len = bitmap.bitmap_scnprintf(&map, nbits, terminator_only[0..1]);
    try std.testing.expectEqual(@as(usize, 0), terminator_only_len);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);

    var truncated = [_]u8{ 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc };
    const truncated_len = bitmap.scnprintf(&map, nbits, &truncated);
    try std.testing.expectEqual(@as(usize, 5), truncated_len);
    try std.testing.expectEqualStrings(expected_text[0..truncated_len], truncated[0..truncated_len]);
    try std.testing.expectEqual(@as(u8, 0), truncated[truncated_len]);
}

test "lane06 replay keeps clump and last-bit helpers stable across alias and tail windows" {
    const nbits = find_bit.bits_per_long + 5;
    const bitmap_words = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 3 };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &bitmap_words, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&clump, &bitmap_words, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit._find_next_clump8(&clump, &bitmap_words, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findLastBit(&bitmap_words, nbits));
    try std.testing.expectEqual(find_bit.findLastBit(&bitmap_words, nbits), find_bit.find_last_bit(&bitmap_words, nbits));

    const boundary = find_bit.bits_per_long - 8;
    const byte_bitmap = [_]find_bit.Word{
        @as(find_bit.Word, 0xa5) << @intCast(boundary),
        @as(find_bit.Word, 0x11),
    };
    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&byte_bitmap, boundary));
    try std.testing.expectEqual(@as(u8, 0x11), find_bit.getValue8(&byte_bitmap, find_bit.bits_per_long));
}

test "lane06 replay keeps string prefix search and basename helpers C-string aware" {
    const prefix_cstr = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'x' };
    const suffix_cstr = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'y' };
    const embedded = [_]u8{ 'a', 0, 'b', 'c' };
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "manual", "on" };
    const match_haystack = [_][]const u8{ "blue", "green", "red" };
    const cstr = [_]u8{ 'a', 'b', 0, 'c' };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&prefix_cstr, "ker"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix(&prefix_cstr, "ker"));
    try std.testing.expect(string.strEndsWith(&suffix_cstr, "nel"));
    try std.testing.expect(string.str_ends_with(&suffix_cstr, "nel"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs_haystack, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&sysfs_haystack, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&match_haystack, "green"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&match_haystack, "green"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abcd", 4, 'b'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&cstr, cstr.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&embedded, embedded.len, 'b'));
}

test "lane06 replay keeps duplicate-range and postorder rbtree traversal aligned" {
    var entries = [_]DuplicateEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, duplicateLess);
    }

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &root, duplicateCmp) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const DuplicateEntry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_match_entry.serial);

    var iter = rbtree.matchIterator(&wanted, &root, duplicateCmp);
    var direct_serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const DuplicateEntry = @fieldParentPtr("node", node);
        direct_serials[count] = entry.serial;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, direct_serials[0..count]);

    var postorder: [6]i32 = undefined;
    var post_count: usize = 0;
    var current = rbtree.firstPostorder(&root);
    try std.testing.expectEqual(current, rbtree.rb_first_postorder(&root));
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const DuplicateEntry = @fieldParentPtr("node", node);
        postorder[post_count] = entry.key;
        try std.testing.expectEqual(rbtree.nextPostorder(node), rbtree.rb_next_postorder(node));
        post_count += 1;
    }
    try std.testing.expectEqual(@as(usize, entries.len), post_count);
    try std.testing.expectEqual(@as(i32, 5), postorder[0]);
    try std.testing.expectEqual(@as(i32, 10), postorder[post_count - 1]);
}
