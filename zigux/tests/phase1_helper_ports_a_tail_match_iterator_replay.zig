const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "bitmap complement and weighted aliases clamp partial tails consistently" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;
    const out_of_range = (@as(Word, 1) << 7) | (@as(Word, 1) << 11);
    const src = [_]Word{
        0b1010,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | out_of_range,
    };

    var direct_complement = [_]Word{ 0, 0 };
    var alias_complement = [_]Word{ 0, 0 };
    bitmap.complement(&direct_complement, &src, nbits);
    bitmap.bitmap_complement(&alias_complement, &src, nbits);
    try std.testing.expectEqualSlices(Word, &direct_complement, &alias_complement);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct_complement[1]);

    const lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 8) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    var direct_or = [_]Word{ 0, 0 };
    var alias_or = [_]Word{ 0, 0 };
    const direct_or_weight = bitmap.weightedOr(&direct_or, &lhs, &rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_or_weight);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try std.testing.expectEqualSlices(Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_or, nbits));

    const xor_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 8) };
    const xor_rhs = [_]Word{ 0, (@as(Word, 1) << 4) | (@as(Word, 1) << 2) | (@as(Word, 1) << 9) };
    var direct_xor = [_]Word{ 0, 0 };
    var alias_xor = [_]Word{ 0, 0 };
    const direct_xor_weight = bitmap.weightedXor(&direct_xor, &xor_lhs, &xor_rhs, nbits);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&alias_xor, &xor_lhs, &xor_rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_xor_weight);
    try std.testing.expectEqual(direct_xor_weight, alias_xor_weight);
    try std.testing.expectEqualSlices(Word, &direct_xor, &alias_xor);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_xor, nbits));
}

test "find-bit tail windows keep zero shared and clump scans aligned" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 6;
    const zero_map = [_]Word{
        ~@as(Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(Word, 1) << 1) | (@as(Word, 1) << 4)),
    };
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 5));

    const shared_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    const shared_rhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 10) };
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextAndBit(&shared_lhs, &shared_rhs, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_next_and_bit(&shared_lhs, &shared_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&shared_lhs, &shared_rhs, nbits, find_bit.bits_per_long + 5));

    const clump_nbits = find_bit.bits_per_long + 8;
    const clump_words = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 7),
    };
    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &clump_words, clump_nbits));
    try std.testing.expectEqual(@as(u8, 0b1001_0010), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, clump_nbits), find_bit._find_next_clump8(&clump, &clump_words, clump_nbits, clump_nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "string match and search helpers stop at c-string boundaries" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto"));

    const match_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(match_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(match_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(match_haystack[0..], "gamma"));

    const cstr = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expect(string.strstarts("prefix-value", "prefix"));
    try std.testing.expect(string.strEndsWith("prefix-value", "value"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&cstr, cstr.len, 'b'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&cstr, cstr.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, 'c'));
}

test "cached rbtree duplicate iteration and leftmost tracking stay aligned" {
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

    var root = rbtree.Root.init();
    var root_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    for (&root_entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate_key = @as(i32, 10);
    var iter = rbtree.matchIterator(&duplicate_key, &root, cmp_key);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);

    var cached = rbtree.RootCached.init();
    var cache_entries = [_]Entry{
        .{ .key = 10, .serial = 10 },
        .{ .key = 5, .serial = 11 },
        .{ .key = 15, .serial = 12 },
    };
    var duplicate_probe = Entry{ .key = 10, .serial = 13 };
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&cache_entries[0].node, &cached, cmp_node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&cache_entries[1].node, &cached, cmp_node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&cache_entries[2].node, &cached, cmp_node));
    const duplicate = rbtree.findAddCached(&duplicate_probe.node, &cached, cmp_node) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &cache_entries[0].node), duplicate);
    try std.testing.expectEqual(rbtree.first(&cached.root), rbtree.firstCached(&cached));

    const first_leftmost = rbtree.firstCached(&cached) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &cache_entries[1].node), first_leftmost);

    rbtree.eraseInitCached(&cache_entries[1].node, &cached);
    try std.testing.expect(rbtree.emptyNode(&cache_entries[1].node));
    try std.testing.expectEqual(rbtree.first(&cached.root), rbtree.firstCached(&cached));

    var replacement = Entry{ .key = 15, .serial = 9 };
    rbtree.replaceNodeCached(&cache_entries[2].node, &replacement.node, &cached);
    try std.testing.expectEqual(rbtree.first(&cached.root), rbtree.firstCached(&cached));
}
