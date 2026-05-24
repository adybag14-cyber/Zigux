const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "lane06 replay keeps low-level bitmap replacement aliases tail-masked" {
    const nbits = bits_per_long + 5;
    const old = [_]Word{
        0b0101,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 10),
    };
    const new = [_]Word{
        0b1010,
        (@as(Word, 1) << 0) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
    };
    const mask = [_]Word{
        0b1111,
        (@as(Word, 1) << 0) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9),
    };
    var primary = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    bitmap.replace(&primary, &old, &new, &mask, nbits);
    bitmap.__bitmap_replace(&alias, &old, &new, &mask, nbits);

    try std.testing.expectEqualSlices(Word, &primary, &alias);
    try std.testing.expectEqual(@as(Word, 0b1010), primary[0]);
    try std.testing.expectEqual(@as(Word, (@as(Word, 1) << 0) | (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 4)), primary[1]);
    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&primary, nbits));
    try std.testing.expectEqual(@as(usize, 6), bitmap.__bitmap_weight(&alias, nbits));
}

test "lane06 replay keeps next-andnot scans and low-level aliases aligned at tail boundaries" {
    const nbits = bits_per_long + 5;
    const lhs = [_]Word{
        @as(Word, 1) << 5,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 10),
    };
    const rhs = [_]Word{
        @as(Word, 1) << 9,
        (@as(Word, 1) << 3) | (@as(Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 0));
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 6));
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, bits_per_long + 4));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, bits_per_long + 5));
}

test "lane06 replay keeps bounded NUL-aware string scans and parse tails explicit" {
    const embedded = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x', 'y' };
    const dirty = [_]u8{ 0xaa, 0xaa, 0x55, 0xaa, 0xaa };

    try std.testing.expectEqual(@as(?usize, 2), string.memchrInv(&dirty, 0xaa));
    try std.testing.expectEqual(@as(?usize, 2), string.memchr_inv(&dirty, 0xaa));
    try std.testing.expectEqual(@as(?usize, 4), string.strnchr(&embedded, embedded.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&embedded, 2, 0));

    const signed = string.memparse("-2Ktail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), signed.value);
    try std.testing.expectEqualStrings("tail", signed.rest);

    const saturated = string.memparse("18446744073709551615Krest");
    try std.testing.expectEqual(std.math.maxInt(u64), saturated.value);
    try std.testing.expectEqualStrings("rest", saturated.rest);
}

test "lane06 replay keeps duplicate-range iterators and cached aliases in lockstep" {
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
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var cached_root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &cached_root, less);
    }

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &cached_root.root, cmp) orelse return error.TestUnexpectedResult;
    const same_match = rbtree.find(&wanted, &cached_root.root, cmp) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_match);
    const same_entry: *const Entry = @fieldParentPtr("node", same_match);
    try std.testing.expectEqual(@as(usize, 0), first_entry.serial);
    try std.testing.expectEqual(@as(i32, 10), same_entry.key);

    var iter = rbtree.matchIterator(&wanted, &cached_root.root, cmp);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);

    var replacement = Entry{ .key = 20, .serial = 99 };
    rbtree.rb_replace_node_cached(&entries[1].node, &replacement.node, &cached_root);
    const leftmost = rbtree.rb_first_cached(&cached_root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[3].node), leftmost);

    const next_leftmost = rbtree.rb_erase_cached(&entries[3].node, &cached_root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), next_leftmost);
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), rbtree.rb_first_cached(&cached_root).?);
}
