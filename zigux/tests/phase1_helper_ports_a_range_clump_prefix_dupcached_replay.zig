const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 bitmap range aliases keep cross-word formatting aligned" {
    const nbits = bitmap.bits_per_long + 6;
    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };

    bitmap.setRange(&direct, bitmap.bits_per_long - 2, 5);
    bitmap.bitmap_set(&alias, bitmap.bits_per_long - 2, 5);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);

    bitmap.clearRange(&direct, bitmap.bits_per_long + 1, 1);
    bitmap.bitmap_clear(&alias, bitmap.bits_per_long + 1, 1);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&direct, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);
    try std.testing.expectEqualStrings("62-64,66", direct_buffer[0..direct_len]);
}

test "lane06 find_bit clump and andnot scans stay tail-aware" {
    const nbits = find_bit.bits_per_long + 8;
    const lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 3) |
            (@as(find_bit.Word, 1) << 7),
    };
    const rhs = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << 1,
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 3),
        find_bit.findFirstAndNotBit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 3),
        find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 7),
        find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 4),
    );

    var clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findFirstClump8(&clump, &lhs, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0b1000_1010), clump);

    clump = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.find_next_clump8(&clump, &lhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(@as(u8, 0b1000_1010), clump);
}

test "lane06 string prefix and sysfs helpers keep bounded matches aligned" {
    try std.testing.expectEqual(@as(usize, 6), string.strHasPrefix("prefix-tail", "prefix"));
    try std.testing.expectEqual(@as(usize, 6), string.str_has_prefix("prefix-tail", "prefix"));
    try std.testing.expect(string.strstarts("prefix-tail", "prefix"));

    const sysfs_entries = [_][]const u8{ "alpha\n", "beta", "gamma\n" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&sysfs_entries, "alpha"));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfs_match_string(&sysfs_entries, "gamma"));

    const plain_entries = [_][]const u8{ "cat", "dog", "eel" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&plain_entries, "dog"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&plain_entries, "dog"));

    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string.replaceChar(replace_buf[0..], '-', '+'));
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(replace_buf[0..], '+', '-'));
    try std.testing.expectEqual(@as(?usize, 5), string.memchrInv("aaaaab", 'a'));
    try std.testing.expectEqual(@as(?usize, 5), string.memchr_inv("aaaaab", 'a'));
}

test "lane06 rbtree duplicate and cached helpers keep first-match and leftmost aligned" {
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
        .{ .key = 10, .serial = 2 },
        .{ .key = 15, .serial = 3 },
    };
    var cached_root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &cached_root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&cached_root));
    try std.testing.expectEqual(rbtree.first(&cached_root.root), rbtree.firstCached(&cached_root));

    const wanted: i32 = 10;
    const first_match = rbtree.findFirst(&wanted, &cached_root.root, cmp_key) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_match_entry.serial);

    const second_match = rbtree.nextMatch(&wanted, first_match, cmp_key) orelse return error.TestUnexpectedResult;
    const second_match_entry: *const Entry = @fieldParentPtr("node", second_match);
    try std.testing.expectEqual(@as(usize, 2), second_match_entry.serial);
    try std.testing.expect(rbtree.nextMatch(&wanted, second_match, cmp_key) == null);

    var iter = rbtree.matchIterator(&wanted, &cached_root.root, cmp_key);
    var iter_serials: [2]usize = undefined;
    var iter_count: usize = 0;
    while (iter.next()) |node| : (iter_count += 1) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        iter_serials[iter_count] = entry.serial;
    }
    try std.testing.expectEqual(@as(usize, 2), iter_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2 }, iter_serials[0..iter_count]);

    var replacement = Entry{ .key = 15, .serial = 4 };
    rbtree.replaceNodeCached(&entries[3].node, &replacement.node, &cached_root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&cached_root));
    try std.testing.expectEqual(rbtree.first(&cached_root.root), rbtree.firstCached(&cached_root));
}
