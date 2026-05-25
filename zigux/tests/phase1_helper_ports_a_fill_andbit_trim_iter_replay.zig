const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap fill and zero aliases aligned inside the declared tail window" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;

    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    bitmap.fill(&direct, nbits);
    bitmap.bitmap_fill(&alias, nbits);

    try std.testing.expectEqual(
        bitmap.bitsToWords(nbits) * @sizeOf(Word),
        bitmap.bitmap_size(nbits),
    );
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expect(bitmap.full(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_full(&alias, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weight(&alias, nbits));

    bitmap.zero(&direct, nbits);
    bitmap.bitmap_zero(&alias, nbits);

    try std.testing.expectEqualSlices(Word, &[_]Word{ 0, 0 }, &direct);
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expect(bitmap.empty(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_empty(&alias, nbits));
}

test "lane06 replay keeps and-bit scans clamped to the declared tail bits" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 5;
    const shared = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
    };
    const shared_peer = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 10),
    };
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findFirstAndBit(&shared, &shared_peer, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextAndBit(&shared, &shared_peer, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.find_next_and_bit(&shared, &shared_peer, nbits, find_bit.bits_per_long + 5),
    );
}

test "lane06 replay keeps string trim copy and sysfs helpers aligned with C-string boundaries" {
    const haystack = [_][]const u8{ "off", "auto\n", "on" };
    var padded = [_]u8{ 9, 9, 9, 9 };
    var trim_buf = [_]u8{ ' ', 'o', 'k', ' ', 0, 'x' };

    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(padded[0..], &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0 }, padded[0..]);
    try std.testing.expectEqualStrings("lead", string.skip_spaces(" \tlead"));
    try std.testing.expectEqualStrings("ok", string.strim(trim_buf[0..]));
    try std.testing.expectEqual(@as(?usize, 2), string.memchr_inv(&[_]u8{ 'a', 'a', 'b' }, 'a'));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "auto"));
}

test "lane06 replay keeps duplicate-aware cached insert and match iteration stable" {
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

    const cmp_node = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
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

    var cached_root = rbtree.RootCached.init();
    var cached_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    for (&cached_entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &cached_root, less);
    }

    var duplicate_probe = Entry{ .key = 10, .serial = 3 };
    const existing = rbtree.findAddCached(&duplicate_probe.node, &cached_root, cmp_node) orelse return error.TestUnexpectedResult;
    const existing_entry: *const Entry = @fieldParentPtr("node", existing);
    try std.testing.expectEqual(@as(i32, 10), existing_entry.key);
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[1].node), rbtree.firstCached(&cached_root));
    try std.testing.expectEqual(rbtree.first(&cached_root.root), rbtree.firstCached(&cached_root));

    var iter_root = rbtree.Root.init();
    var iter_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
    };
    for (&iter_entries) |*entry| {
        rbtree.add(&entry.node, &iter_root, less);
    }

    const wanted = @as(i32, 10);
    var iter = rbtree.matchIterator(&wanted, &iter_root, cmp_key);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);
}
