const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap aliases keep tail masking and formatting aligned" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]Word{ 0b1011, (@as(Word, 1) << 1) | (@as(Word, 1) << 8) };
    const rhs = [_]Word{ 0b1100, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };

    var direct_or = [_]Word{ 0, 0 };
    var alias_or = [_]Word{ 0, 0 };
    try std.testing.expectEqual(
        bitmap.weightedOr(&direct_or, &lhs, &rhs, nbits),
        bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits),
    );
    try std.testing.expectEqualSlices(Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&direct_or, nbits));

    var direct_andnot = [_]Word{ 0, 0 };
    var alias_andnot = [_]Word{ 0, 0 };
    try std.testing.expectEqual(
        bitmap.andNotBits(&direct_andnot, &lhs, &rhs, nbits),
        bitmap.bitmap_andnot(&alias_andnot, &lhs, &rhs, nbits),
    );
    try std.testing.expectEqualSlices(Word, &direct_andnot, &alias_andnot);
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&direct_andnot, nbits));

    var direct_map = [_]Word{ 0, 0 };
    var alias_map = [_]Word{ 0, 0 };
    bitmap.setRange(&direct_map, bitmap.bits_per_long - 2, 5);
    bitmap.bitmap_set(&alias_map, bitmap.bits_per_long - 2, 5);
    bitmap.clearRange(&direct_map, bitmap.bits_per_long + 1, 1);
    bitmap.bitmap_clear(&alias_map, bitmap.bits_per_long + 1, 1);
    try std.testing.expectEqualSlices(Word, &direct_map, &alias_map);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&direct_map, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&alias_map, nbits, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);
    try std.testing.expectEqualStrings("62-64,66", direct_buffer[0..direct_len]);
}

test "phase1 helper ports A find_bit aliases keep boundary and past-end scans aligned" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 6;
    const set_map = [_]Word{
        @as(Word, 1) << @intCast(find_bit.bits_per_long - 1),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 8),
    };
    const andnot_lhs = [_]Word{
        @as(Word, 1) << @intCast(find_bit.bits_per_long - 1),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 8),
    };
    const andnot_rhs = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 8),
    };
    const zero_map = [_]Word{
        ~(@as(Word, 1) << @intCast(find_bit.bits_per_long - 1)),
        find_bit.lastWordMask(nbits) & ~(@as(Word, 1) << 4),
    };

    const boundary = find_bit.bits_per_long - 1;
    try std.testing.expectEqual(
        find_bit.findNextBit(&set_map, nbits, boundary),
        find_bit.find_next_bit(&set_map, nbits, boundary),
    );
    try std.testing.expectEqual(
        find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long),
        find_bit._find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 2),
        find_bit.find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        find_bit.findLastBit(&set_map, nbits),
        find_bit.find_last_bit(&set_map, nbits),
    );

    var direct_clump: u8 = 0x5a;
    var alias_clump: u8 = 0x5a;
    try std.testing.expectEqual(
        find_bit.findNextClump8(&direct_clump, &set_map, nbits, nbits),
        find_bit.find_next_clump8(&alias_clump, &set_map, nbits, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0x5a), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);
}

test "phase1 helper ports A string aliases keep padding trimming and lookup semantics aligned" {
    var direct_pad = [_]u8{ 9, 9, 9, 9, 9 };
    var alias_pad = [_]u8{ 9, 9, 9, 9, 9 };
    try std.testing.expectEqual(
        string.strscpyPad(direct_pad[0..], &[_]u8{ 'o', 'k', 0, 'x' }),
        string.strscpy_pad(alias_pad[0..], &[_]u8{ 'o', 'k', 0, 'x' }),
    );
    try std.testing.expectEqualSlices(u8, &direct_pad, &alias_pad);

    var direct_trim = [_]u8{ ' ', 'a', ' ', 'b', 0, 'x' };
    var alias_trim = [_]u8{ ' ', 'a', ' ', 'b', 0, 'x' };
    try std.testing.expectEqualStrings(string.trimSpaces(direct_trim[0..]), string.strstrip(alias_trim[0..]));

    var direct_remove = [_]u8{ 'a', ' ', 'b', ' ', 0, 'x' };
    var alias_remove = [_]u8{ 'a', ' ', 'b', ' ', 0, 'x' };
    try std.testing.expectEqualStrings(
        string.removeSpaces(direct_remove[0..]),
        string.remove_spaces(alias_remove[0..]),
    );

    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(
        string.sysfsMatchString(sysfs_haystack[0..], "auto"),
        string.sysfs_match_string(sysfs_haystack[0..], "auto"),
    );

    const match_haystack = [_][]const u8{ &[_]u8{ 'a', 0, 'x' }, "beta", "alpha" };
    try std.testing.expectEqual(
        string.matchString(match_haystack[0..], "a"),
        string.match_string(match_haystack[0..], "a"),
    );
}

test "phase1 helper ports A rbtree aliases keep duplicate iteration and cached leftmost aligned" {
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

    const key_cmp = struct {
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
    };
    var root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    const wanted = @as(i32, 10);
    var iter = rbtree.matchIterator(&wanted, &root.root, key_cmp);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.rb_first_cached(&root));
    rbtree.rb_erase_init_cached(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_first_cached(&root));

    var replacement = Entry{ .key = 10, .serial = 9 };
    rbtree.rb_replace_node_cached(&entries[0].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_first_cached(&root));
}
