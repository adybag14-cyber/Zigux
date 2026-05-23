const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const CachedEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn cachedLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const CachedEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const CachedEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn firstCachedIdentity(root: *const rbtree.RootCached) ?struct { i32, usize } {
    const node = rbtree.firstCached(root) orelse return null;
    const entry: *const CachedEntry = @fieldParentPtr("node", node);
    return .{ entry.key, entry.serial };
}

test "lane06 replay keeps bitmap allocation helpers and exact-boundary copies aligned" {
    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 5;

    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(nbits) * @sizeOf(bitmap.Word)), bitmap.bitmap_size(nbits));

    var plain: ?[]bitmap.Word = try bitmap.bitmap_alloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &plain);
    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(nbits)), plain.?.len);

    var zeroed: ?[]bitmap.Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }

    bitmap.bitmap_fill(zeroed.?, nbits);
    try std.testing.expect(bitmap.bitmap_full(zeroed.?, nbits));
    bitmap.bitmap_zero(zeroed.?, nbits);
    try std.testing.expect(bitmap.bitmap_empty(zeroed.?, nbits));

    const exact_nbits = bitmap.bits_per_long;
    const src = [_]bitmap.Word{ 0b1011, 0x55aa };
    var direct = [_]bitmap.Word{ 0, 0x1111 };
    var alias = [_]bitmap.Word{ 0, 0x2222 };

    bitmap.copy(direct[0..1], src[0..1], exact_nbits);
    bitmap.bitmap_copy(alias[0..1], src[0..1], exact_nbits);

    try std.testing.expectEqual(src[0], direct[0]);
    try std.testing.expectEqual(src[0], alias[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 0x1111), direct[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0x2222), alias[1]);

    bitmap.bitmap_free(allocator, &plain);
    bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expect(plain == null);
    try std.testing.expect(zeroed == null);
}

test "lane06 replay keeps find_bit boundary and past-end returns explicit" {
    const nbits = find_bit.bits_per_long + 5;
    const boundary = nbits - 1;
    const tail_shift = 4;

    const set_map = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << tail_shift };
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << tail_shift),
    };
    const and_lhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << tail_shift };
    const and_rhs = and_lhs;
    const andnot_lhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << tail_shift };
    const andnot_rhs = [_]find_bit.Word{ 0, 0 };

    try std.testing.expectEqual(boundary, find_bit.findNextBit(&set_map, nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit.find_next_zero_bit(&zero_map, nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(boundary, find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary));

    const empty = [_]find_bit.Word{};
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextBit(&empty, 7, 8));
    try std.testing.expectEqual(@as(usize, 7), find_bit.find_next_zero_bit(&empty, 7, 11));
    try std.testing.expectEqual(@as(usize, 7), find_bit.find_next_and_bit(&empty, &empty, 7, 9));
    try std.testing.expectEqual(@as(usize, 7), find_bit.find_next_andnot_bit(&empty, &empty, 7, 99));
}

test "lane06 replay keeps string pad and bounded lookup helpers C-string aware" {
    var direct_pad = [_]u8{ 9, 9, 9, 9, 9, 9 };
    var alias_pad = [_]u8{ 8, 8, 8, 8, 8, 8 };

    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(direct_pad[0..], &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqual(@as(isize, 1), string.strscpy_pad(alias_pad[0..], &[_]u8{ 'z', 0, 'y' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &direct_pad);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 0, 0, 0, 0, 0 }, &alias_pad);

    try std.testing.expectEqualStrings("ready", string.skip_spaces(" \tready"));
    try std.testing.expect(string.streq(&[_]u8{ 'n', 'o', 'd', 'e', 0, 'x' }, "node"));

    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));

    const match_haystack = [_][]const u8{
        &[_]u8{ 'a', 'l', 'p', 'h', 'a', 0, 'x' },
        "beta",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(match_haystack[0..], "alpha"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("beta", 4, 'e'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));
}

test "lane06 replay keeps cached rbtree reseed and erase-init aliases aligned" {
    var primary_first = CachedEntry{ .key = 10, .serial = 0 };
    var alias_first = CachedEntry{ .key = 10, .serial = 0 };
    var primary_second = CachedEntry{ .key = 5, .serial = 1 };
    var alias_second = CachedEntry{ .key = 5, .serial = 1 };
    var primary_reseed = CachedEntry{ .key = 7, .serial = 2 };
    var alias_reseed = CachedEntry{ .key = 7, .serial = 2 };

    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_first.node), rbtree.addCached(&primary_first.node, &primary_root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_first.node), rbtree.rb_add_cached(&alias_first.node, &alias_root, cachedLess));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_second.node), rbtree.addCached(&primary_second.node, &primary_root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_second.node), rbtree.rb_add_cached(&alias_second.node, &alias_root, cachedLess));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));

    rbtree.eraseInitCached(&primary_second.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_second.node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_second.node));
    try std.testing.expect(rbtree.emptyNode(&alias_second.node));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 10, 0 }), firstCachedIdentity(&primary_root));

    rbtree.eraseInitCached(&primary_first.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_first.node, &alias_root);
    try std.testing.expect(primary_root.root.node == null);
    try std.testing.expect(alias_root.root.node == null);
    try std.testing.expectEqual(@as(?struct { i32, usize }, null), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(@as(?struct { i32, usize }, null), firstCachedIdentity(&alias_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_reseed.node), rbtree.addCached(&primary_reseed.node, &primary_root, cachedLess));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_reseed.node), rbtree.rb_add_cached(&alias_reseed.node, &alias_root, cachedLess));
    try std.testing.expectEqual(@as(?struct { i32, usize }, .{ 7, 2 }), firstCachedIdentity(&primary_root));
    try std.testing.expectEqual(firstCachedIdentity(&primary_root), firstCachedIdentity(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.firstCached(&alias_root));
}
