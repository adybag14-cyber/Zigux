const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 bitmap weighted xor and andnot aliases clamp partial tails" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{
        0b101101,
        (@as(bitmap.Word, 1) << 0) |
            (@as(bitmap.Word, 1) << 2) |
            (@as(bitmap.Word, 1) << 4) |
            (@as(bitmap.Word, 1) << 9),
    };
    const rhs = [_]bitmap.Word{
        0b001111,
        (@as(bitmap.Word, 1) << 1) |
            (@as(bitmap.Word, 1) << 2) |
            (@as(bitmap.Word, 1) << 3) |
            (@as(bitmap.Word, 1) << 8),
    };

    var direct_xor = [_]bitmap.Word{ 0, 0 };
    var alias_xor = [_]bitmap.Word{ 0, 0 };
    const direct_weight = bitmap.weightedXor(&direct_xor, &lhs, &rhs, nbits);
    const alias_weight = bitmap.bitmap_weighted_xor(&alias_xor, &lhs, &rhs, nbits);
    try std.testing.expectEqual(direct_weight, alias_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_xor, &alias_xor);
    try std.testing.expectEqual(lhs[1] ^ rhs[1], direct_xor[1]);
    try std.testing.expectEqual(direct_weight, bitmap.weight(&direct_xor, nbits));
    try std.testing.expectEqual(
        (lhs[1] ^ rhs[1]) & bitmap.lastWordMask(nbits),
        direct_xor[1] & bitmap.lastWordMask(nbits),
    );

    var direct_andnot = [_]bitmap.Word{ 0, 0 };
    var alias_andnot = [_]bitmap.Word{ 0, 0 };
    const direct_nonzero = bitmap.andNotBits(&direct_andnot, &lhs, &rhs, nbits);
    const alias_nonzero = bitmap.bitmap_andnot(&alias_andnot, &lhs, &rhs, nbits);
    try std.testing.expectEqual(direct_nonzero, alias_nonzero);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_andnot, &alias_andnot);
    try std.testing.expect(bitmap.bitmap_subset(&direct_andnot, &lhs, nbits));
    try std.testing.expectEqual((lhs[1] & ~rhs[1]) & bitmap.lastWordMask(nbits), direct_andnot[1]);
}

test "lane06 find_bit andnot and last-bit aliases respect cross-word tail masks" {
    const nbits = find_bit.bits_per_long + 6;
    const lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 5) | (@as(find_bit.Word, 1) << 9),
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 5) |
            (@as(find_bit.Word, 1) << 9),
    };
    const rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 5,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4),
    };

    try std.testing.expectEqual(@as(usize, 9), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 9), find_bit.find_first_andnot_bit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 5),
        find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 10),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 5),
        find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, 10),
    );

    const tail_map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 5) | (@as(find_bit.Word, 1) << 9),
    };
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.findLastBit(&tail_map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.find_last_bit(&tail_map, nbits));
}

test "lane06 string pad and sysfs helpers keep newline-aware matches and zero fill aligned" {
    var direct = [_]u8{0xaa} ** 6;
    var alias = [_]u8{0xaa} ** 6;
    try std.testing.expectEqual(@as(isize, 3), string.strscpyPad(&direct, "zig"));
    try std.testing.expectEqual(@as(isize, 3), string.strscpy_pad(&alias, "zig"));
    try std.testing.expectEqualSlices(u8, &direct, &alias);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 0, 0, 0 }, &direct);

    try std.testing.expect(string.sysfsStreq("alpha\n", "alpha"));
    try std.testing.expect(string.sysfs_streq("beta", "beta\n"));

    const sysfs_entries = [_][]const u8{ "alpha\n", "beta", "gamma\n" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&sysfs_entries, "alpha"));
    try std.testing.expectEqual(@as(?usize, 2), string.sysfs_match_string(&sysfs_entries, "gamma"));

    const plain_entries = [_][]const u8{ "cat", "dog", "eel" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&plain_entries, "dog"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&plain_entries, "dog"));
    try std.testing.expect(string.strstarts("prefix-tail", "prefix"));
    try std.testing.expect(string.str_ends_with("prefix-tail", "tail"));
}

test "lane06 rbtree edge and duplicate traversal helpers stay in sync" {
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
        .{ .key = 10, .serial = 4 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const first = rbtree.first(&root) orelse return error.TestUnexpectedResult;
    const alias_first = rbtree.rb_first(&root) orelse return error.TestUnexpectedResult;
    const last = rbtree.last(&root) orelse return error.TestUnexpectedResult;
    const alias_last = rbtree.rb_last(&root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, first), alias_first);
    try std.testing.expectEqual(@as(*rbtree.Node, last), alias_last);

    const second = rbtree.next(first) orelse return error.TestUnexpectedResult;
    const before_last = rbtree.prev(last) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(?*rbtree.Node, second), rbtree.rb_next(first));
    try std.testing.expectEqual(@as(?*rbtree.Node, before_last), rbtree.rb_prev(last));

    const target_key: i32 = 10;
    const first_match = rbtree.findFirst(&target_key, &root, cmp_key) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);
    var direct_serials: [3]usize = undefined;
    direct_serials[0] = first_match_entry.serial;
    var direct_count: usize = 1;
    var current: ?*rbtree.Node = first_match;
    while (current) |node| {
        current = rbtree.nextMatch(&target_key, node, cmp_key);
        if (current) |next_match| {
            const next_entry: *const Entry = @fieldParentPtr("node", next_match);
            direct_serials[direct_count] = next_entry.serial;
            direct_count += 1;
        }
    }

    var iter = rbtree.matchIterator(&target_key, &root, cmp_key);
    var iter_serials: [3]usize = undefined;
    var iter_count: usize = 0;
    while (iter.next()) |node| : (iter_count += 1) {
        const iter_entry: *const Entry = @fieldParentPtr("node", node);
        iter_serials[iter_count] = iter_entry.serial;
    }

    try std.testing.expectEqual(@as(usize, 3), direct_count);
    try std.testing.expectEqualSlices(usize, direct_serials[0..direct_count], iter_serials[0..iter_count]);
    try std.testing.expect(current == null);
}
