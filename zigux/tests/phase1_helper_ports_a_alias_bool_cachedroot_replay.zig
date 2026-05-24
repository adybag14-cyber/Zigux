const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase 1 helper ports A replay keeps bitmap alias helpers aligned on size state and allocation" {
    const allocator = std.testing.allocator;
    const nbits = find_bit.bits_per_long + 5;

    try std.testing.expectEqual(bitmap.bitsToWords(nbits) * @sizeOf(bitmap.Word), bitmap.bitmap_size(nbits));

    var direct = [_]bitmap.Word{ 0xaa55, 0xaa55 };
    var alias = [_]bitmap.Word{ 0xaa55, 0xaa55 };
    bitmap.zero(&direct, nbits);
    bitmap.bitmap_zero(&alias, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(bitmap.empty(&direct, nbits), bitmap.bitmap_empty(&alias, nbits));

    bitmap.fill(&direct, nbits);
    bitmap.bitmap_fill(&alias, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(bitmap.full(&direct, nbits), bitmap.bitmap_full(&alias, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weight(&alias, nbits));

    var plain_direct: ?[]bitmap.Word = try bitmap.alloc(allocator, nbits);
    defer bitmap.free(allocator, &plain_direct);
    var plain_alias: ?[]bitmap.Word = try bitmap.bitmap_alloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &plain_alias);
    try std.testing.expectEqual(plain_direct.?.len, plain_alias.?.len);

    var zeroed_direct: ?[]bitmap.Word = try bitmap.zalloc(allocator, nbits);
    defer bitmap.free(allocator, &zeroed_direct);
    var zeroed_alias: ?[]bitmap.Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed_alias);
    try std.testing.expectEqual(zeroed_direct.?.len, zeroed_alias.?.len);
    for (zeroed_alias.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }

    bitmap.bitmap_free(allocator, &plain_alias);
    bitmap.bitmap_free(allocator, &zeroed_alias);
    try std.testing.expect(plain_alias == null);
    try std.testing.expect(zeroed_alias == null);
}

test "phase 1 helper ports A replay keeps find_bit aliases aligned on boundary and clump routes" {
    const nbits = find_bit.bits_per_long + 5;
    const bit_map = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 7),
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 10),
    };
    const zero_map = [_]find_bit.Word{
        ~(@as(find_bit.Word, 1) << 4),
        find_bit.lastWordMask(nbits),
    };

    try std.testing.expectEqual(find_bit.findFirstBit(&bit_map, nbits), find_bit.find_first_bit(&bit_map, nbits));
    try std.testing.expectEqual(find_bit.findFirstZeroBit(&zero_map, nbits), find_bit.find_first_zero_bit(&zero_map, nbits));
    try std.testing.expectEqual(find_bit.findNextBit(&bit_map, nbits, 8), find_bit.find_next_bit(&bit_map, nbits, 8));

    var clump_direct: u8 = 0;
    var clump_alias: u8 = 0;
    const clump_map = [_]find_bit.Word{@as(find_bit.Word, 1)};
    try std.testing.expectEqual(find_bit.findFirstClump8(&clump_direct, &clump_map, 8), find_bit.find_first_clump8(&clump_alias, &clump_map, 8));
    try std.testing.expectEqual(clump_direct, clump_alias);
    try std.testing.expectEqual(find_bit.findNextClump8(&clump_direct, &clump_map, 8, 0), find_bit.find_next_clump8(&clump_alias, &clump_map, 8, 0));
    try std.testing.expectEqual(clump_direct, clump_alias);

    try std.testing.expectEqual(find_bit.findFirstBit(&bit_map, nbits), find_bit._find_first_bit(&bit_map, nbits));
    try std.testing.expectEqual(find_bit.findFirstZeroBit(&zero_map, nbits), find_bit._find_first_zero_bit(&zero_map, nbits));
    try std.testing.expectEqual(find_bit.findNextBit(&bit_map, nbits, 8), find_bit._find_next_bit(&bit_map, nbits, 8));
}

test "phase 1 helper ports A replay keeps string bool padding and byte-search helpers aligned" {
    try std.testing.expect(try string.strtobool("Y"));
    try std.testing.expect(!(try string.strtobool("0")));
    try std.testing.expectError(error.Invalid, string.strtobool("maybe"));

    var padded = [_]u8{ 1, 1, 1, 1, 1, 1 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(padded[0..], &[_]u8{ 'h', 'i', 0, 'x', 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, padded[0..]);

    var alias_padded = [_]u8{ 1, 1, 1, 1 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(alias_padded[0..], "ok"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0 }, alias_padded[0..]);

    const duplicated = try string.memdup(std.testing.allocator, "abc");
    defer std.testing.allocator.free(duplicated);
    try std.testing.expectEqualStrings("abc", duplicated);
    try std.testing.expectEqual(@as(?usize, 19), string.memchrInv(&([_]u8{0} ** 19 ++ [_]u8{1} ++ [_]u8{0} ** 12), 0));
    try std.testing.expectEqual(string.memchrInv(&[_]u8{ 0, 0, 1 }, 0), string.memchr_inv(&[_]u8{ 0, 0, 1 }, 0));
}

test "phase 1 helper ports A replay keeps rbtree cached-root helpers aligned through duplicate misses and leftmost updates" {
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

    const cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const firstIdentity = struct {
        fn read(root: *const rbtree.RootCached) ?struct { i32, usize } {
            const node = rbtree.firstCached(root) orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", node);
            return .{ entry.key, entry.serial };
        }
    }.read;

    const nodeIdentity = struct {
        fn read(node: ?*rbtree.Node) ?struct { i32, usize } {
            const current = node orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", current);
            return .{ entry.key, entry.serial };
        }
    }.read;

    var primary_first = Entry{ .key = 10, .serial = 0 };
    var alias_first = Entry{ .key = 10, .serial = 0 };
    var primary_second = Entry{ .key = 5, .serial = 1 };
    var alias_second = Entry{ .key = 5, .serial = 1 };
    var primary_third = Entry{ .key = 15, .serial = 2 };
    var alias_third = Entry{ .key = 15, .serial = 2 };
    var primary_duplicate = Entry{ .key = 10, .serial = 3 };
    var alias_duplicate = Entry{ .key = 10, .serial = 3 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_first.node), rbtree.addCached(&primary_first.node, &primary_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_first.node), rbtree.rb_add_cached(&alias_first.node, &alias_root, less));
    try std.testing.expectEqual(firstIdentity(&primary_root), firstIdentity(&alias_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_second.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_second.node, &alias_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_third.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_third.node, &alias_root, cmp));

    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_root, cmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cmp) orelse return error.TestUnexpectedResult;
    const primary_existing_entry: *const Entry = @fieldParentPtr("node", primary_existing);
    const alias_existing_entry: *const Entry = @fieldParentPtr("node", alias_existing);
    try std.testing.expectEqual(primary_existing_entry.key, alias_existing_entry.key);
    try std.testing.expectEqual(primary_existing_entry.serial, alias_existing_entry.serial);

    try std.testing.expectEqual(
        nodeIdentity(rbtree.eraseCached(&primary_second.node, &primary_root)),
        nodeIdentity(rbtree.rb_erase_cached(&alias_second.node, &alias_root)),
    );
    try std.testing.expectEqual(firstIdentity(&primary_root), firstIdentity(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));

    rbtree.eraseInitCached(&primary_first.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_first.node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_first.node));
    try std.testing.expect(rbtree.emptyNode(&alias_first.node));
    try std.testing.expectEqual(firstIdentity(&primary_root), firstIdentity(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
}
