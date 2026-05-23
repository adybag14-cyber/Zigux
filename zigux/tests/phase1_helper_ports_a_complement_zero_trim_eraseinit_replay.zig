const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports a bitmap complement aliases and size helpers stay aligned" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;
    const src = [_]Word{
        0b1010,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 7),
    };
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    bitmap.complement(&direct, &src, nbits);
    bitmap.bitmap_complement(&alias, &src, nbits);

    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expectEqual(~@as(Word, 0b1010), direct[0]);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct[1]);
    try std.testing.expectEqual(bitmap.sizeBytes(nbits), bitmap.bitmap_size(nbits));

    var zero_src = [_]Word{~@as(Word, 0)};
    var zero_dst = [_]Word{0x2468};
    bitmap.bitmap_complement(zero_dst[0..0], zero_src[0..0], 0);
    try std.testing.expectEqual(@as(Word, 0x2468), zero_dst[0]);

    var plain: ?[]Word = try bitmap.bitmap_alloc(std.testing.allocator, nbits);
    defer bitmap.bitmap_free(std.testing.allocator, &plain);
    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(nbits)), plain.?.len);

    var zeroed: ?[]Word = try bitmap.bitmap_zalloc(std.testing.allocator, nbits);
    defer bitmap.bitmap_free(std.testing.allocator, &zeroed);
    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(nbits)), zeroed.?.len);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }
}

test "phase1 helper ports a find_bit zero scans keep tail boundaries and aliases aligned" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 6;
    const zero_map = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(Word, 1) << 1) | (@as(Word, 1) << 4)),
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 1),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 5),
    );
    try std.testing.expectEqual(
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 2),
        find_bit.find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 2),
        find_bit._find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long + 2),
    );

    const boundary = [_]Word{
        ~(@as(Word, 1) << @intCast(find_bit.bits_per_long - 1)),
        ~@as(Word, 0),
    };
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long - 1),
        find_bit.findNextZeroBit(&boundary, find_bit.bits_per_long * 2, find_bit.bits_per_long - 1),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long * 2),
        find_bit.findNextZeroBit(&boundary, find_bit.bits_per_long * 2, find_bit.bits_per_long),
    );
}

test "phase1 helper ports a string trim and replace helpers keep C-string semantics" {
    try std.testing.expect(string.streq(&[_]u8{ 'a', 0, 'z' }, &[_]u8{ 'a', 0, 'x' }));
    try std.testing.expect(!string.streq("alpha", "beta"));
    try std.testing.expectEqualStrings("lead", string.skipSpaces("  \tlead"));
    try std.testing.expectEqualStrings("lead", string.skip_spaces(" \nlead"));

    var trim_buf = [_]u8{ ' ', 'a', ' ', 'b', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("a b", string.trimSpaces(trim_buf[0..]));

    var strim_buf = [_]u8{ ' ', 'o', 'k', 0, ' ', ' ', 0 };
    try std.testing.expectEqualStrings("ok", string.strim(strim_buf[0..]));

    var remove_buf = [_]u8{ 'a', ' ', 'b', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("ab", string.removeSpaces(remove_buf[0..]));

    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(replace_buf[0..], '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '+', 'b', 0, '-' }, replace_buf[0..]);
}

test "phase1 helper ports a rbtree erase-init replacement flow keeps traversal aliases aligned" {
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

    var primary_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var primary_replacement = Entry{ .key = 10 };
    var alias_replacement = Entry{ .key = 10 };
    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, less);
        rbtree.add(&alias_entry.node, &alias_root, less);
    }

    rbtree.eraseInit(&primary_entries[1].node, &primary_root);
    rbtree.erase(&alias_entries[1].node, &alias_root);
    rbtree.clearNode(&alias_entries[1].node);

    try std.testing.expect(rbtree.emptyNode(&primary_entries[1].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[1].node));

    rbtree.replaceNode(&primary_entries[0].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node(&alias_entries[0].node, &alias_replacement.node, &alias_root);

    var primary_order: [3]i32 = undefined;
    var alias_order: [3]i32 = undefined;
    var count: usize = 0;

    var primary_cursor = rbtree.first(&primary_root);
    var alias_cursor = rbtree.rb_first(&alias_root);
    while (primary_cursor != null and alias_cursor != null) {
        const primary_entry: *const Entry = @fieldParentPtr("node", primary_cursor.?);
        const alias_entry: *const Entry = @fieldParentPtr("node", alias_cursor.?);
        primary_order[count] = primary_entry.key;
        alias_order[count] = alias_entry.key;
        count += 1;
        primary_cursor = rbtree.next(primary_cursor.?);
        alias_cursor = rbtree.rb_next(alias_cursor.?);
    }

    try std.testing.expect(primary_cursor == null);
    try std.testing.expect(alias_cursor == null);
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, primary_order[0..count], alias_order[0..count]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 10, 15 }, primary_order[0..count]);

    const primary_first = rbtree.first(&primary_root) orelse return error.TestUnexpectedResult;
    const alias_first = rbtree.rb_first(&alias_root) orelse return error.TestUnexpectedResult;
    const primary_first_entry: *const Entry = @fieldParentPtr("node", primary_first);
    const alias_first_entry: *const Entry = @fieldParentPtr("node", alias_first);
    try std.testing.expectEqual(primary_first_entry.key, alias_first_entry.key);

    const primary_last = rbtree.last(&primary_root) orelse return error.TestUnexpectedResult;
    const alias_last = rbtree.rb_last(&alias_root) orelse return error.TestUnexpectedResult;
    const primary_last_entry: *const Entry = @fieldParentPtr("node", primary_last);
    const alias_last_entry: *const Entry = @fieldParentPtr("node", alias_last);
    try std.testing.expectEqual(primary_last_entry.key, alias_last_entry.key);

    const alias_prev = rbtree.rb_prev(alias_last) orelse return error.TestUnexpectedResult;
    const alias_prev_entry: *const Entry = @fieldParentPtr("node", alias_prev);
    try std.testing.expectEqual(@as(i32, 10), alias_prev_entry.key);
}
