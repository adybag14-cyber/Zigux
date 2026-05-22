const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap extend zalloc and free replay" {
    const count = bitmap.bits_per_long + 3;
    const size = bitmap.bits_per_long * 2 + 5;

    var src = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.setRange(&src, bitmap.bits_per_long - 1, 2);
    bitmap.setRange(&src, bitmap.bits_per_long + 2, 1);
    src[1] |= @as(bitmap.Word, 1) << 9;

    var direct = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    bitmap.copyAndExtend(&direct, src[0..2], count, size);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct[2]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct[1] & ~bitmap.lastWordMask(count));

    const allocated = (try bitmap.bitmap_zalloc(std.testing.allocator, size)) orelse return error.TestUnexpectedResult;
    defer std.testing.allocator.free(allocated);
    try std.testing.expect(bitmap.empty(allocated, size));

    bitmap.copy(allocated, direct[0..bitmap.bitsToWords(size)], size);
    try std.testing.expectEqual(bitmap.weight(&direct, size), bitmap.weight(allocated, size));

    var owned: ?[]bitmap.Word = try bitmap.bitmap_alloc(std.testing.allocator, count);
    try std.testing.expect(owned != null);
    bitmap.bitmap_free(std.testing.allocator, &owned);
    try std.testing.expectEqual(@as(?[]bitmap.Word, null), owned);
}

test "phase1 helper ports A find_bit zero progression and clump replay" {
    const nbits = find_bit.bits_per_long + 5;
    const boundary = find_bit.bits_per_long;

    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.findFirstZeroBit(&zero_map, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextZeroBit(&zero_map, nbits, boundary + 2));

    const clump_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 7),
    };
    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextClump8(&clump, &clump_map, nbits, boundary + 1));
    try std.testing.expectEqual(@as(u8, 0b1000_1010), clump);
    try std.testing.expectEqual(@as(usize, boundary + 3), find_bit.findLastBit(&clump_map, nbits));
}

test "phase1 helper ports A string whitespace prefix suffix and bounded search replay" {
    var trim_buf = [_]u8{ ' ', 'z', 'i', 'g', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("zig", string.trimSpaces(&trim_buf));

    var remove_buf = [_]u8{ 'z', ' ', 'i', ' ', 'g', 0, 'x' };
    try std.testing.expectEqualStrings("zig", string.removeSpaces(&remove_buf));

    var replace_buf = [_]u8{ 'z', '-', 'i', '-', 'g', 0, '-' };
    try std.testing.expectEqual(@as(usize, 5), string.replaceChar(&replace_buf, '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', '+', 'i', '+', 'g', 0, '-' }, &replace_buf);

    try std.testing.expectEqualStrings("padded", string.skip_spaces(" \t padded"));
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix("zig-mode", "zig"));
    try std.testing.expect(string.strEndsWith("zig-mode", "mode"));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr("zig-mode", 4, 'g'));
}

test "phase1 helper ports A rbtree cached replace erase and postorder replay" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const cmp_node = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            if (lhs_entry.serial < rhs_entry.serial) return -1;
            if (lhs_entry.serial > rhs_entry.serial) return 1;
            return 0;
        }
    }.compare;

    const cmp_key = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var inserted = Entry{ .key = 12, .serial = 3 };
    var replacement = Entry{ .key = 10, .serial = 4 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&inserted.node, &root, cmp_node));

    const needle = @as(i32, 10);
    const before_replace = rbtree.find(&needle, &root.root, cmp_key) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), before_replace);

    rbtree.rb_replace_node_cached(&entries[0].node, &replacement.node, &root);
    const after_replace = rbtree.find(&needle, &root.root, cmp_key) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &replacement.node), after_replace);

    rbtree.rb_erase_init_cached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));

    var postorder: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.rb_first_postorder(&root.root);
    while (current) |node| : (current = rbtree.rb_next_postorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        postorder[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    const root_node = root.root.node orelse return error.TestUnexpectedResult;
    const root_entry: *const Entry = @fieldParentPtr("node", root_node);
    try std.testing.expectEqual(root_entry.key, postorder[count - 1]);

    std.mem.sort(i32, postorder[0..count], {}, std.sort.asc(i32));
    try std.testing.expectEqualSlices(i32, &[_]i32{ 10, 12, 15 }, postorder[0..count]);
}
