const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

fn expectWordSlicesEqual(expected: []const bitmap.Word, actual: []const bitmap.Word) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |lhs, rhs| {
        try std.testing.expectEqual(lhs, rhs);
    }
}

fn cmpEntryKeys(comptime Entry: type, lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

test "phase1 helper ports A bitmap logical aliases clamp declared tails" {
    const nbits = bitmap.bits_per_long + 5;

    const or_lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 8) };
    const or_rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };
    var direct_or = [_]bitmap.Word{ 0, 0 };
    var alias_or = [_]bitmap.Word{ 0, 0 };

    const direct_or_weight = bitmap.weightedOr(&direct_or, &or_lhs, &or_rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &or_lhs, &or_rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_or_weight);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try expectWordSlicesEqual(&direct_or, &alias_or);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_or, nbits));

    const xor_lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8) };
    const xor_rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9) };
    var direct_xor = [_]bitmap.Word{ 0, 0 };
    var alias_xor = [_]bitmap.Word{ 0, 0 };

    const direct_xor_weight = bitmap.weightedXor(&direct_xor, &xor_lhs, &xor_rhs, nbits);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&alias_xor, &xor_lhs, &xor_rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_xor_weight);
    try std.testing.expectEqual(direct_xor_weight, alias_xor_weight);
    try expectWordSlicesEqual(&direct_xor, &alias_xor);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_xor, nbits));

    const src = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 7) | (@as(bitmap.Word, 1) << 10),
    };
    var direct_complement = [_]bitmap.Word{ 0, 0 };
    var alias_complement = [_]bitmap.Word{ 0, 0 };
    bitmap.complement(&direct_complement, &src, nbits);
    bitmap.bitmap_complement(&alias_complement, &src, nbits);
    try expectWordSlicesEqual(&direct_complement, &alias_complement);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct_complement[1]);
}

test "phase1 helper ports A find_bit aliases keep tail windows and clumps masked" {
    const nbits = find_bit.bits_per_long + 5;
    const tail_map = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 3 };
    const full_tail_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    const and_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9) };
    const and_rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9) };

    try std.testing.expectEqual(find_bit.findFirstBit(&tail_map, nbits), find_bit.find_first_bit(&tail_map, nbits));
    try std.testing.expectEqual(find_bit.findFirstAndBit(&and_lhs, &and_rhs, nbits), find_bit.find_first_and_bit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(find_bit.findNextZeroBit(&full_tail_map, nbits, find_bit.bits_per_long + 2), find_bit.find_next_zero_bit(&full_tail_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(find_bit.findLastBit(&tail_map, nbits), find_bit.find_last_bit(&tail_map, nbits));

    var direct_clump: u8 = 0;
    var alias_clump: u8 = 0;
    var underscore_clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&direct_clump, &tail_map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_first_clump8(&alias_clump, &tail_map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit._find_first_clump8(&underscore_clump, &tail_map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);
    try std.testing.expectEqual(direct_clump, underscore_clump);
}

test "phase1 helper ports A string suffix and terminator helpers honor C-string boundaries" {
    const suffix_cstr = [_]u8{ 'a', 'b', 'c', 0, 'd' };
    try std.testing.expect(string.strEndsWith("abcdef", "def"));
    try std.testing.expect(string.str_ends_with("abcdef", "def"));
    try std.testing.expect(string.strEndsWith(&suffix_cstr, "abc"));
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix("abcdef", "abc"));
    try std.testing.expect(string.strstarts("abcdef", "abc"));

    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(string.sysfsMatchString(sysfs_haystack[0..], "auto"), string.sysfs_match_string(sysfs_haystack[0..], "auto"));

    const match_haystack = [_][]const u8{ &[_]u8{ 'a', 0, 'x' }, "beta", "alpha" };
    try std.testing.expectEqual(string.matchString(match_haystack[0..], "a"), string.match_string(match_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(match_haystack[0..], "gamma"));

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 1, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));

    var zero_scan = [_]u8{0} ** 32;
    zero_scan[19] = 1;
    try std.testing.expectEqual(string.memchrInv(zero_scan[0..], 0), string.memchr_inv(zero_scan[0..], 0));
    try std.testing.expectEqual(@as(?usize, 19), string.memchrInv(zero_scan[0..], 0));
}

test "phase1 helper ports A rbtree ordered aliases preserve traversal and cached leftmost state" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    const cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            return cmpEntryKeys(Entry, lhs, rhs);
        }
    }.compare;

    var direct_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 20 },
        .{ .key = 15 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 20 },
        .{ .key = 15 },
    };
    var direct_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    for (&direct_entries, &alias_entries) |*direct_entry, *alias_entry| {
        rbtree.add(&direct_entry.node, &direct_root, less);
        rbtree.add(&alias_entry.node, &alias_root, less);
    }

    var direct_forward: [4]i32 = undefined;
    var alias_forward: [4]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&direct_root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        direct_forward[count] = entry.key;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 4), count);

    count = 0;
    current = rbtree.rb_first(&alias_root);
    while (current) |node| : (current = rbtree.rb_next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_forward[count] = entry.key;
        count += 1;
    }
    try std.testing.expectEqualSlices(i32, &direct_forward, &alias_forward);

    var direct_reverse: [4]i32 = undefined;
    var alias_reverse: [4]i32 = undefined;
    count = 0;
    current = rbtree.last(&direct_root);
    while (current) |node| : (current = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        direct_reverse[count] = entry.key;
        count += 1;
    }
    count = 0;
    current = rbtree.rb_last(&alias_root);
    while (current) |node| : (current = rbtree.rb_prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        alias_reverse[count] = entry.key;
        count += 1;
    }
    try std.testing.expectEqualSlices(i32, &direct_reverse, &alias_reverse);

    var direct_replacement = Entry{ .key = 20 };
    var alias_replacement = Entry{ .key = 20 };
    rbtree.replaceNode(&direct_entries[2].node, &direct_replacement.node, &direct_root);
    rbtree.rb_replace_node(&alias_entries[2].node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &direct_replacement.node), rbtree.last(&direct_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_replacement.node), rbtree.rb_last(&alias_root));

    var direct_cached = rbtree.RootCached.init();
    var alias_cached = rbtree.RootCached.init();
    var direct_cached_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 20 },
    };
    var alias_cached_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 20 },
    };
    for (&direct_cached_entries, &alias_cached_entries) |*direct_entry, *alias_entry| {
        _ = rbtree.addCached(&direct_entry.node, &direct_cached, less);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_cached, less);
    }

    var direct_cached_duplicate = Entry{ .key = 10 };
    var alias_cached_duplicate = Entry{ .key = 10 };
    const direct_existing = rbtree.findAddCached(&direct_cached_duplicate.node, &direct_cached, cmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_cached_duplicate.node, &alias_cached, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(
        (@as(*const Entry, @fieldParentPtr("node", direct_existing))).key,
        (@as(*const Entry, @fieldParentPtr("node", alias_existing))).key,
    );

    const direct_leftmost = rbtree.firstCached(&direct_cached) orelse return error.TestUnexpectedResult;
    const alias_leftmost = rbtree.rb_first_cached(&alias_cached) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(i32, 5), (@as(*const Entry, @fieldParentPtr("node", direct_leftmost))).key);
    try std.testing.expectEqual(@as(i32, 5), (@as(*const Entry, @fieldParentPtr("node", alias_leftmost))).key);

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.eraseCached(&direct_cached_entries[2].node, &direct_cached));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_erase_cached(&alias_cached_entries[2].node, &alias_cached));
    try std.testing.expectEqual(
        (@as(*const Entry, @fieldParentPtr("node", rbtree.firstCached(&direct_cached).?))).key,
        (@as(*const Entry, @fieldParentPtr("node", rbtree.rb_first_cached(&alias_cached).?))).key,
    );
}
