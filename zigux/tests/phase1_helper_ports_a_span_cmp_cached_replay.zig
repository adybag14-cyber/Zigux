const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "bitmap span predicates keep declared tails separate from storage tails" {
    const nbits = bitmap.bits_per_long + 9;
    const tail_poison = @as(bitmap.Word, 1) << 31;

    var lhs = [_]bitmap.Word{ 0, tail_poison };
    var rhs = [_]bitmap.Word{ 0, tail_poison };
    bitmap.setRange(&lhs, bitmap.bits_per_long - 3, 7);
    bitmap.setRange(&rhs, bitmap.bits_per_long - 1, 5);

    var and_result = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.bitmap_and(&and_result, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(&and_result, nbits));
    try std.testing.expectEqual(@as(bitmap.Word, 0), and_result[1] & tail_poison);

    var complement = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_complement(&complement, &and_result, nbits);
    try std.testing.expectEqual(@as(bitmap.Word, 0), complement[1] & ~bitmap.lastWordMask(nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&and_result, &complement, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&and_result, &lhs, nbits));
    try std.testing.expect(!bitmap.bitmap_equal(&lhs, &rhs, nbits));
}

test "find_bit aliases clamp span scans and clumps at declared limits" {
    const nbits = find_bit.bits_per_long + 10;
    var map = [_]find_bit.Word{ 0, 0 };
    map[0] |= @as(find_bit.Word, 1) << (find_bit.bits_per_long - 2);
    map[1] |= @as(find_bit.Word, 1) << 1;
    map[1] |= @as(find_bit.Word, 1) << 9;
    map[1] |= @as(find_bit.Word, 1) << 20;

    try std.testing.expectEqual(find_bit.bits_per_long - 2, find_bit.find_first_bit(&map, nbits));
    try std.testing.expectEqual(find_bit.bits_per_long + 1, find_bit.find_next_bit(&map, nbits, find_bit.bits_per_long - 1));
    try std.testing.expectEqual(find_bit.bits_per_long + 9, find_bit.find_last_bit(&map, nbits));
    try std.testing.expectEqual(nbits, find_bit.find_next_bit(&map, nbits, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(find_bit.bits_per_long - 8, find_bit.find_next_clump8(&clump, &map, nbits, find_bit.bits_per_long - 4));
    try std.testing.expectEqual(@as(u8, 0b0100_0000), clump);
    try std.testing.expectEqual(nbits, find_bit.find_next_clump8(&clump, &map, nbits, find_bit.bits_per_long + 10));
    try std.testing.expectEqual(@as(u8, 0b0100_0000), clump);
}

test "string counted comparisons stop at C-string and sysfs boundaries" {
    var path_buf = [_]u8{ '/', 's', 'y', 's', '/', 'd', 'e', 'v', 0, '/', 'x' };
    try std.testing.expectEqual(@as(usize, 4), string.str_has_prefix(&path_buf, "/sys"));
    try std.testing.expect(string.strstarts(&path_buf, "/sys"));
    try std.testing.expect(string.str_ends_with(&path_buf, "dev"));
    try std.testing.expect(!string.str_ends_with(&path_buf, "dev/x"));

    const haystack = [_][]const u8{ "ready\n", "ready-now", "offline\n" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(&haystack, "ready"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&haystack, "ready-now"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(haystack[0..1], "ready"));
    try std.testing.expectEqual(@as(?usize, 7), string.strnchr(&path_buf, path_buf.len, 'v'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&path_buf, 4, 'd'));
}

test "rbtree cached duplicate iterator survives leftmost erase and replacement" {
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

    const cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 3, .serial = 0 },
        .{ .key = 1, .serial = 1 },
        .{ .key = 3, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 3, .serial = 4 },
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(usize, 1), (@as(*const Entry, @fieldParentPtr("node", rbtree.rb_first_cached(&root).?))).serial);
    rbtree.rb_erase_init_cached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));

    var replacement = Entry{ .key = 3, .serial = 8 };
    rbtree.rb_replace_node_cached(&entries[2].node, &replacement.node, &root);

    const wanted = @as(i32, 3);
    var iterator = rbtree.matchIterator(&wanted, &root.root, cmp);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iterator.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 8, 4 }, serials[0..count]);
    try std.testing.expectEqual(@as(usize, 0), (@as(*const Entry, @fieldParentPtr("node", rbtree.rb_first_cached(&root).?))).serial);
}
