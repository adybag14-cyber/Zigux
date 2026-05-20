const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

fn expectWordSlicesEqual(expected: []const bitmap.Word, actual: []const bitmap.Word) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |lhs, rhs| {
        try std.testing.expectEqual(lhs, rhs);
    }
}

test "phase1 helper ports A bitmap aliases reset state and optionals" {
    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 5;

    var direct_zero = [_]bitmap.Word{ 0xaa55, 0xaa55 };
    var alias_zero = [_]bitmap.Word{ 0xaa55, 0xaa55 };
    bitmap.zero(&direct_zero, nbits);
    bitmap.bitmap_zero(&alias_zero, nbits);
    try expectWordSlicesEqual(&direct_zero, &alias_zero);
    try std.testing.expect(bitmap.empty(&direct_zero, nbits));
    try std.testing.expect(bitmap.bitmap_empty(&alias_zero, nbits));

    var direct_fill = [_]bitmap.Word{ 0, 0 };
    var alias_fill = [_]bitmap.Word{ 0, 0 };
    bitmap.fill(&direct_fill, nbits);
    bitmap.bitmap_fill(&alias_fill, nbits);
    try expectWordSlicesEqual(&direct_fill, &alias_fill);
    try std.testing.expect(bitmap.full(&direct_fill, nbits));
    try std.testing.expect(bitmap.bitmap_full(&alias_fill, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct_fill, nbits), bitmap.bitmap_weight(&alias_fill, nbits));

    const src = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0), 0 };
    var direct_extend = [_]bitmap.Word{ 0xaa55, 0xaa55, 0xaa55 };
    var alias_extend = [_]bitmap.Word{ 0xaa55, 0xaa55, 0xaa55 };
    bitmap.copyAndExtend(&direct_extend, src[0..2], nbits, bitmap.bits_per_long * 3);
    bitmap.bitmap_copy_and_extend(&alias_extend, src[0..2], nbits, bitmap.bits_per_long * 3);
    try expectWordSlicesEqual(&direct_extend, &alias_extend);
    try std.testing.expectEqual(@as(bitmap.Word, bitmap.lastWordMask(nbits)), direct_extend[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct_extend[2]);

    var direct_alloc: ?[]bitmap.Word = try bitmap.alloc(allocator, nbits);
    defer bitmap.free(allocator, &direct_alloc);
    var alias_alloc: ?[]bitmap.Word = try bitmap.bitmap_alloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &alias_alloc);
    try std.testing.expectEqual(direct_alloc.?.len, alias_alloc.?.len);

    var direct_zeroed: ?[]bitmap.Word = try bitmap.zalloc(allocator, nbits);
    defer bitmap.free(allocator, &direct_zeroed);
    var alias_zeroed: ?[]bitmap.Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &alias_zeroed);
    for (direct_zeroed.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }
    for (alias_zeroed.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }

    bitmap.bitmap_free(allocator, &alias_alloc);
    bitmap.free(allocator, &direct_zeroed);
    try std.testing.expect(alias_alloc == null);
    try std.testing.expect(direct_zeroed == null);
}

test "phase1 helper ports A find_bit aliases preserve inclusive boundaries and empty windows" {
    const boundary = find_bit.bits_per_long - 1;
    const nbits = find_bit.bits_per_long + 5;

    const set_map = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary),
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 9),
    };
    const zero_map = [_]find_bit.Word{
        ~(@as(find_bit.Word, 1) << @intCast(boundary)),
        find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << 2),
    };
    const and_lhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary),
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 9),
    };
    const and_rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary),
        @as(find_bit.Word, 1) << 2,
    };
    const andnot_rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary),
        0,
    };

    try std.testing.expectEqual(
        find_bit.findNextBit(&set_map, nbits, boundary),
        find_bit.find_next_bit(&set_map, nbits, boundary),
    );
    try std.testing.expectEqual(
        find_bit.findNextBit(&set_map, nbits, boundary),
        find_bit._find_next_bit(&set_map, nbits, boundary),
    );
    try std.testing.expectEqual(
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long),
        find_bit.find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary),
        find_bit.find_next_and_bit(&and_lhs, &and_rhs, nbits, boundary),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndNotBit(&and_lhs, &andnot_rhs, nbits, find_bit.bits_per_long),
        find_bit.find_next_andnot_bit(&and_lhs, &andnot_rhs, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        find_bit.findLastBit(&set_map, nbits),
        find_bit.find_last_bit(&set_map, nbits),
    );

    var clump: u8 = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &set_map, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_clump8(&clump, &set_map, nbits, nbits + 4));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&clump, &set_map, nbits, nbits + 8));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "phase1 helper ports A string aliases preserve pad and C-string stop behavior" {
    const padded_src = [_]u8{ 'h', 'i', 0, 'x', 'x' };
    var direct_pad = [_]u8{ 1, 1, 1, 1, 1, 1 };
    var alias_pad = [_]u8{ 1, 1, 1, 1, 1, 1 };
    try std.testing.expectEqual(string.strscpyPad(direct_pad[0..], &padded_src), string.strscpy_pad(alias_pad[0..], &padded_src));
    try std.testing.expectEqualSlices(u8, &direct_pad, &alias_pad);

    var direct_single = [_]u8{7};
    var alias_single = [_]u8{8};
    try std.testing.expectEqual(string.strscpy(&direct_single, "x"), string.strscpyPad(&alias_single, "y"));
    try std.testing.expectEqual(@as(u8, 0), direct_single[0]);
    try std.testing.expectEqual(@as(u8, 0), alias_single[0]);

    var direct_replace = [_]u8{ 'a', 0, 'b', 'a' };
    var alias_replace = [_]u8{ 'a', 0, 'b', 'a' };
    try std.testing.expectEqual(
        string.replaceChar(direct_replace[0..], 'a', 'z'),
        string.strreplace(alias_replace[0..], 'a', 'z'),
    );
    try std.testing.expectEqualSlices(u8, &direct_replace, &alias_replace);

    var zero_scan = [_]u8{0} ** 32;
    zero_scan[19] = 1;
    try std.testing.expectEqual(string.memchrInv(zero_scan[0..], 0), string.memchr_inv(zero_scan[0..], 0));
    try std.testing.expectEqual(@as(?usize, 19), string.memchrInv(zero_scan[0..], 0));

    const haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(string.sysfsMatchString(haystack[0..], "auto"), string.sysfs_match_string(haystack[0..], "auto"));
}

test "phase1 helper ports A rbtree cached aliases preserve leftmost state across reset and reseed" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const keyOf = struct {
        fn read(node: ?*rbtree.Node) ?i32 {
            const current = node orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", current);
            return entry.key;
        }
    }.read;

    var direct_first = Entry{ .key = 10, .serial = 0 };
    var alias_first = Entry{ .key = 10, .serial = 0 };
    var direct_left = Entry{ .key = 5, .serial = 1 };
    var alias_left = Entry{ .key = 5, .serial = 1 };
    var direct_right = Entry{ .key = 15, .serial = 2 };
    var alias_right = Entry{ .key = 15, .serial = 2 };
    var direct_reseed = Entry{ .key = 6, .serial = 3 };
    var alias_reseed = Entry{ .key = 6, .serial = 3 };
    var direct_replacement = Entry{ .key = 15, .serial = 4 };
    var alias_replacement = Entry{ .key = 15, .serial = 4 };

    var direct_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &direct_first.node), rbtree.addCached(&direct_first.node, &direct_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_first.node), rbtree.rb_add_cached(&alias_first.node, &alias_root, less));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&direct_left.node, &direct_root, struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_left.node, &alias_root, struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare));
    _ = rbtree.addCached(&direct_right.node, &direct_root, less);
    _ = rbtree.rb_add_cached(&alias_right.node, &alias_root, less);

    try std.testing.expectEqual(keyOf(rbtree.firstCached(&direct_root)), keyOf(rbtree.rb_first_cached(&alias_root)));

    rbtree.eraseInitCached(&direct_left.node, &direct_root);
    rbtree.rb_erase_init_cached(&alias_left.node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&direct_left.node));
    try std.testing.expect(rbtree.emptyNode(&alias_left.node));
    try std.testing.expectEqual(keyOf(rbtree.firstCached(&direct_root)), keyOf(rbtree.rb_first_cached(&alias_root)));

    _ = rbtree.addCached(&direct_reseed.node, &direct_root, less);
    _ = rbtree.rb_add_cached(&alias_reseed.node, &alias_root, less);
    try std.testing.expectEqual(keyOf(rbtree.firstCached(&direct_root)), keyOf(rbtree.rb_first_cached(&alias_root)));

    rbtree.replaceNodeCached(&direct_right.node, &direct_replacement.node, &direct_root);
    rbtree.rb_replace_node_cached(&alias_right.node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(keyOf(rbtree.firstCached(&direct_root)), keyOf(rbtree.rb_first_cached(&alias_root)));

    rbtree.eraseInitCached(&direct_first.node, &direct_root);
    rbtree.rb_erase_init_cached(&alias_first.node, &alias_root);
    try std.testing.expectEqual(keyOf(rbtree.firstCached(&direct_root)), keyOf(rbtree.rb_first_cached(&alias_root)));
}
