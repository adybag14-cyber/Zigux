const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 scan-match bitmap helpers keep weighted logical aliases aligned on tail windows" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | (@as(Word, 1) << 10) };
    var direct_or = [_]Word{ 0, 0 };
    var alias_or = [_]Word{ 0, 0 };
    var direct_xor = [_]Word{ 0, 0 };
    var alias_xor = [_]Word{ 0, 0 };
    var tail_source = [_]Word{ 0, 0 };
    var tail_copy = [_]Word{ 0, 0 };

    const direct_or_weight = bitmap.weightedOr(&direct_or, &lhs, &rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 3), direct_or_weight);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try std.testing.expectEqualSlices(Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&direct_or, nbits));

    const direct_xor_weight = bitmap.weightedXor(&direct_xor, &lhs, &rhs, nbits);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&alias_xor, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_xor_weight);
    try std.testing.expectEqual(direct_xor_weight, alias_xor_weight);
    try std.testing.expectEqualSlices(Word, &direct_xor, &alias_xor);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_xor, nbits));

    bitmap.bitmap_set(&tail_source, bitmap.bits_per_long - 1, 3);
    bitmap.bitmap_copy_clear_tail(&tail_copy, &tail_source, nbits);
    try std.testing.expect(bitmap.bitmap_intersects(&tail_copy, &tail_copy, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&tail_copy, nbits));
}

test "lane06 scan-match find-bit helpers keep shared andnot tail scans aligned" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 6;
    const lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 10) };
    const zeros = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(Word, 1) << 2) | (@as(Word, 1) << 5)),
    };

    try std.testing.expectEqual(
        find_bit.findFirstAndBit(&lhs, &rhs, nbits),
        find_bit.find_first_and_bit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
        find_bit.find_next_and_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        find_bit.findFirstAndNotBit(&lhs, &rhs, nbits),
        find_bit.find_first_andnot_bit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
        find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        find_bit.findFirstZeroBit(&zeros, nbits),
        find_bit.find_first_zero_bit(&zeros, nbits),
    );
    try std.testing.expectEqual(
        find_bit.findNextZeroBit(&zeros, nbits, find_bit.bits_per_long + 3),
        find_bit.find_next_zero_bit(&zeros, nbits, find_bit.bits_per_long + 3),
    );
    try std.testing.expectEqual(
        find_bit.findLastBit(&lhs, nbits),
        find_bit.find_last_bit(&lhs, nbits),
    );
}

test "lane06 scan-match string helpers keep first-match and bounded scans aligned" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    const match_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    const bounded = [_]u8{ 'x', 'y', 0, 'z', 'w' };
    var dirty = [_]u8{0} ** 24;
    dirty[13] = 7;

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(
        string.sysfsMatchString(sysfs_haystack[0..], "auto"),
        string.sysfs_match_string(sysfs_haystack[0..], "auto"),
    );
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(match_haystack[0..], "a"));
    try std.testing.expectEqual(
        string.matchString(match_haystack[0..], "a"),
        string.match_string(match_haystack[0..], "a"),
    );
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, 5, 'z'));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&bounded, 2, 'y'));
    try std.testing.expectEqual(
        string.memchrInv(dirty[0..], 0),
        string.memchr_inv(dirty[0..], 0),
    );

    const parsed = string.memparse("-16 trailing");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -16))), parsed.value);
    try std.testing.expectEqualStrings(" trailing", parsed.rest);
}

test "lane06 scan-match rbtree cached duplicate iterators stay aligned through replacement" {
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
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const key_cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
        .{ .key = 10, .serial = 3 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
        .{ .key = 10, .serial = 3 },
    };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(
        @as(?*rbtree.Node, &primary_entries[0].node),
        rbtree.addCached(&primary_entries[0].node, &primary_root, less),
    );
    try std.testing.expectEqual(
        @as(?*rbtree.Node, &alias_entries[0].node),
        rbtree.rb_add_cached(&alias_entries[0].node, &alias_root, less),
    );

    for (primary_entries[1..], alias_entries[1..]) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, less);
    }

    const initial_primary_leftmost = rbtree.firstCached(&primary_root) orelse return error.TestUnexpectedResult;
    const initial_alias_leftmost = rbtree.rb_first_cached(&alias_root) orelse return error.TestUnexpectedResult;
    const initial_primary_entry: *const Entry = @fieldParentPtr("node", initial_primary_leftmost);
    const initial_alias_entry: *const Entry = @fieldParentPtr("node", initial_alias_leftmost);
    try std.testing.expectEqual(initial_primary_entry.key, initial_alias_entry.key);
    try std.testing.expectEqual(initial_primary_entry.serial, initial_alias_entry.serial);

    const duplicate = Entry{ .key = 10, .serial = 99 };
    var primary_duplicate = duplicate;
    var alias_duplicate = duplicate;
    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_root, cmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cmp) orelse return error.TestUnexpectedResult;
    const primary_existing_entry: *const Entry = @fieldParentPtr("node", primary_existing);
    const alias_existing_entry: *const Entry = @fieldParentPtr("node", alias_existing);
    try std.testing.expectEqual(primary_existing_entry.key, alias_existing_entry.key);
    try std.testing.expectEqual(primary_existing_entry.serial, alias_existing_entry.serial);

    const wanted = @as(i32, 10);
    var primary_iter = rbtree.matchIterator(&wanted, &primary_root.root, key_cmp);
    var alias_iter = rbtree.matchIterator(&wanted, &alias_root.root, key_cmp);
    var primary_serials: [2]usize = undefined;
    var alias_serials: [2]usize = undefined;
    var count: usize = 0;
    while (true) {
        const primary_node = primary_iter.next();
        const alias_node = alias_iter.next();
        try std.testing.expectEqual(primary_node == null, alias_node == null);
        const primary = primary_node orelse break;
        const alias = alias_node orelse break;
        const primary_entry: *const Entry = @fieldParentPtr("node", primary);
        const alias_entry: *const Entry = @fieldParentPtr("node", alias);
        primary_serials[count] = primary_entry.serial;
        alias_serials[count] = alias_entry.serial;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 3 }, primary_serials[0..count]);
    try std.testing.expectEqualSlices(usize, primary_serials[0..count], alias_serials[0..count]);

    var primary_replacement = Entry{ .key = 10, .serial = 10 };
    var alias_replacement = Entry{ .key = 10, .serial = 10 };
    rbtree.replaceNodeCached(&primary_entries[1].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_entries[1].node, &alias_replacement.node, &alias_root);
    const replaced_primary_leftmost = rbtree.firstCached(&primary_root) orelse return error.TestUnexpectedResult;
    const replaced_alias_leftmost = rbtree.rb_first_cached(&alias_root) orelse return error.TestUnexpectedResult;
    const replaced_primary_entry: *const Entry = @fieldParentPtr("node", replaced_primary_leftmost);
    const replaced_alias_entry: *const Entry = @fieldParentPtr("node", replaced_alias_leftmost);
    try std.testing.expectEqual(replaced_primary_entry.key, replaced_alias_entry.key);
    try std.testing.expectEqual(replaced_primary_entry.serial, replaced_alias_entry.serial);

    const primary_next_leftmost = rbtree.eraseCached(&primary_replacement.node, &primary_root);
    const alias_next_leftmost = rbtree.rb_erase_cached(&alias_replacement.node, &alias_root);
    const erased_primary_entry: ?struct { i32, usize } = if (primary_next_leftmost) |node| blk: {
        const entry: *const Entry = @fieldParentPtr("node", node);
        break :blk .{ entry.key, entry.serial };
    } else null;
    const erased_alias_entry: ?struct { i32, usize } = if (alias_next_leftmost) |node| blk: {
        const entry: *const Entry = @fieldParentPtr("node", node);
        break :blk .{ entry.key, entry.serial };
    } else null;
    try std.testing.expectEqual(erased_primary_entry, erased_alias_entry);

    const final_primary_leftmost = rbtree.firstCached(&primary_root) orelse return error.TestUnexpectedResult;
    const final_alias_leftmost = rbtree.rb_first_cached(&alias_root) orelse return error.TestUnexpectedResult;
    const final_primary_entry: *const Entry = @fieldParentPtr("node", final_primary_leftmost);
    const final_alias_entry: *const Entry = @fieldParentPtr("node", final_alias_leftmost);
    try std.testing.expectEqual(final_primary_entry.key, final_alias_entry.key);
    try std.testing.expectEqual(final_primary_entry.serial, final_alias_entry.serial);
}
