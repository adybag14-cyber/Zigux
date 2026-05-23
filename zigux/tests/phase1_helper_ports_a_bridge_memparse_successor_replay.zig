const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap empty-buffer and allocator aliases aligned" {
    var map = [_]bitmap.Word{0};
    var direct_buffer = [_]u8{ 0xaa, 0xbb, 0xcc };
    var alias_buffer = [_]u8{ 0xaa, 0xbb, 0xcc };

    const direct_len = bitmap.scnprintf(&map, 32, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&map, 32, &alias_buffer);
    try std.testing.expectEqual(@as(usize, 0), direct_len);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xbb, 0xcc }, &direct_buffer);
    try std.testing.expectEqualSlices(u8, &direct_buffer, &alias_buffer);

    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 5;

    var allocated = try bitmap.alloc(allocator, nbits);
    defer bitmap.free(allocator, &allocated);
    try std.testing.expect(allocated != null);
    try std.testing.expectEqual(bitmap.bitsToWords(nbits), allocated.?.len);

    var alias_allocated = try bitmap.bitmap_alloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &alias_allocated);
    try std.testing.expect(alias_allocated != null);
    try std.testing.expectEqual(bitmap.bitsToWords(nbits), alias_allocated.?.len);

    var zero_allocated = try bitmap.zalloc(allocator, nbits);
    defer bitmap.free(allocator, &zero_allocated);
    try std.testing.expect(zero_allocated != null);
    try std.testing.expectEqual(bitmap.bitsToWords(nbits), zero_allocated.?.len);
    for (zero_allocated.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }

    var alias_zero_allocated = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &alias_zero_allocated);
    try std.testing.expect(alias_zero_allocated != null);
    try std.testing.expectEqual(bitmap.bitsToWords(nbits), alias_zero_allocated.?.len);
    for (alias_zero_allocated.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }

    bitmap.free(allocator, &zero_allocated);
    try std.testing.expect(zero_allocated == null);

    bitmap.bitmap_free(allocator, &alias_zero_allocated);
    try std.testing.expect(alias_zero_allocated == null);
}

test "lane06 replay keeps cross-word find_bit byte bridging reachable" {
    const nbits = find_bit.bits_per_long + 8;
    const bitmap_words = [_]find_bit.Word{
        @as(find_bit.Word, 0xaa) << @intCast(find_bit.bits_per_long - 8),
        @as(find_bit.Word, 0x55),
    };

    try std.testing.expectEqual(@as(u8, 0xaa), find_bit.getValue8(&bitmap_words, find_bit.bits_per_long - 8));

    var direct_clump: u8 = 0;
    var alias_clump: u8 = 0;
    var underscore_clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long - 8),
        find_bit.findFirstClump8(&direct_clump, &bitmap_words, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long - 8),
        find_bit.find_first_clump8(&alias_clump, &bitmap_words, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long - 8),
        find_bit._find_first_clump8(&underscore_clump, &bitmap_words, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0xaa), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);
    try std.testing.expectEqual(direct_clump, underscore_clump);

    direct_clump = 0;
    alias_clump = 0;
    underscore_clump = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long - 8),
        find_bit.findNextClump8(&direct_clump, &bitmap_words, nbits, find_bit.bits_per_long - 4),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long - 8),
        find_bit.find_next_clump8(&alias_clump, &bitmap_words, nbits, find_bit.bits_per_long - 4),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long - 8),
        find_bit._find_next_clump8(&underscore_clump, &bitmap_words, nbits, find_bit.bits_per_long - 4),
    );
    try std.testing.expectEqual(@as(u8, 0xaa), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);
    try std.testing.expectEqual(direct_clump, underscore_clump);

    direct_clump = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findNextClump8(&direct_clump, &bitmap_words, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(@as(u8, 0x55), direct_clump);
}

test "lane06 replay keeps signed memparse boundaries and strnchr counts aligned" {
    const negative = string.memparse("-17 tail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -17))), negative.value);
    try std.testing.expectEqualStrings(" tail", negative.rest);

    const saturated = string.memparse("+9223372036854775808Ktail");
    try std.testing.expectEqual(@as(u64, std.math.maxInt(i64)), saturated.value);
    try std.testing.expectEqualStrings("tail", saturated.rest);

    const suffix_first = string.memparse("-2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), suffix_first.value);
    try std.testing.expectEqualStrings("tail", suffix_first.rest);

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abcd", 4, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abcd", 1, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));
    try std.testing.expectEqual(@as(?usize, 0), string.strnchr(&[_]u8{ 'z', 0, 'b' }, 1, 'z'));
}

test "lane06 replay keeps rbtree postorder unwinding and cached-leftmost successor stable" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    var primary_entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 6 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 6 },
    };
    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    const wire_shape = struct {
        fn apply(root: *rbtree.Root, entries: []Entry) void {
            root.node = &entries[0].node;
            entries[0].node.parent = null;
            entries[0].node.left = &entries[1].node;
            entries[0].node.right = null;

            entries[1].node.parent = &entries[0].node;
            entries[1].node.left = null;
            entries[1].node.right = &entries[2].node;

            entries[2].node.parent = &entries[1].node;
            entries[2].node.left = null;
            entries[2].node.right = null;
        }
    }.apply;

    wire_shape(&primary_root, &primary_entries);
    wire_shape(&alias_root, &alias_entries);

    var primary_order: [3]i32 = undefined;
    var alias_order: [3]i32 = undefined;

    var primary_count: usize = 0;
    var current = rbtree.firstPostorder(&primary_root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        primary_order[primary_count] = entry.key;
        primary_count += 1;
    }

    var alias_count: usize = 0;
    current = rbtree.rb_first_postorder(&alias_root);
    while (current) |node| : (current = rbtree.rb_next_postorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_order[alias_count] = entry.key;
        alias_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), primary_count);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 6, 4, 8 }, primary_order[0..primary_count]);
    try std.testing.expectEqualSlices(i32, primary_order[0..primary_count], alias_order[0..alias_count]);
    try std.testing.expect(rbtree.nextPostorder(null) == null);
    try std.testing.expect(rbtree.rb_next_postorder(null) == null);

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var cached_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 8 },
        .{ .key = 7 },
    };
    var cached_root = rbtree.RootCached.init();
    for (&cached_entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &cached_root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[1].node), rbtree.firstCached(&cached_root));

    const promoted_leftmost = rbtree.eraseCached(&cached_entries[1].node, &cached_root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &cached_entries[3].node), promoted_leftmost);
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[3].node), rbtree.firstCached(&cached_root));
    try std.testing.expectEqual(rbtree.first(&cached_root.root), rbtree.firstCached(&cached_root));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    current = rbtree.first(&cached_root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 7, 8, 10 }, order[0..count]);
}
