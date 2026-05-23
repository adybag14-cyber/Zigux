const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const SearchEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn searchLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const SearchEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const SearchEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn searchCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const SearchEntry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "lane06 replay keeps bitmap mask-driven helpers tail-clamped and alias-aligned" {
    const nbits = bitmap.bits_per_long + 6;
    const lhs = [_]bitmap.Word{
        0b11110000,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 5) | (@as(bitmap.Word, 1) << 9),
    };
    const rhs = [_]bitmap.Word{
        0b10110000,
        (@as(bitmap.Word, 1) << 5) | (@as(bitmap.Word, 1) << 8),
    };

    var primary_and = [_]bitmap.Word{ 0, 0 };
    var alias_and = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.andBits(&primary_and, &lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_and(&alias_and, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &primary_and, &alias_and);
    try std.testing.expectEqual(@as(bitmap.Word, 0b10110000), primary_and[0]);
    try std.testing.expectEqual(@as(bitmap.Word, @as(bitmap.Word, 1) << 5), primary_and[1]);

    var primary_andnot = [_]bitmap.Word{ 0, 0 };
    var alias_andnot = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&primary_andnot, &lhs, &rhs, nbits));
    try std.testing.expect(bitmap.__bitmap_andnot(&alias_andnot, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &primary_andnot, &alias_andnot);
    try std.testing.expectEqual(@as(bitmap.Word, 0b01000000), primary_andnot[0]);
    try std.testing.expectEqual(@as(bitmap.Word, @as(bitmap.Word, 1) << 1), primary_andnot[1]);

    const old = [_]bitmap.Word{ 0b00001111, @as(bitmap.Word, 1) << 1 };
    const new = [_]bitmap.Word{ 0b11110000, (@as(bitmap.Word, 1) << 5) | (@as(bitmap.Word, 1) << 8) };
    const mask = [_]bitmap.Word{ 0b11110000, (@as(bitmap.Word, 1) << 5) | (@as(bitmap.Word, 1) << 8) };
    var primary_replace = [_]bitmap.Word{ 0, 0 };
    var alias_replace = [_]bitmap.Word{ 0, 0 };
    bitmap.replace(&primary_replace, &old, &new, &mask, nbits);
    bitmap.bitmap_replace(&alias_replace, &old, &new, &mask, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &primary_replace, &alias_replace);
    try std.testing.expectEqual(@as(bitmap.Word, 0b11111111), primary_replace[0]);
    try std.testing.expectEqual(
        @as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 5)),
        primary_replace[1],
    );
}

test "lane06 replay keeps find_bit clump scans and tail-bounded last-bit queries aligned" {
    const nbits = find_bit.bits_per_long + 6;
    const map = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 10,
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 8), find_bit.findFirstClump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b00000100), clump);
    try std.testing.expectEqual(@as(usize, 8), find_bit.find_first_clump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(usize, 8), find_bit._find_next_clump8(&clump, &map, nbits, 9));
    try std.testing.expectEqual(@as(u8, 0b00000100), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&clump, &map, nbits, 11));
    try std.testing.expectEqual(@as(u8, 0b00010001), clump);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&clump, &map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b00010001), find_bit.getValue8(&map, find_bit.bits_per_long));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_last_bit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 10), find_bit.findLastBit(&map, find_bit.bits_per_long));
}

test "lane06 replay keeps string space-aware helpers and sysfs comparisons C-string aware" {
    try std.testing.expectEqualStrings("zigux", string.skipSpaces(" \t\nzigux"));
    try std.testing.expectEqualStrings("trim", string.skip_spaces("trim"));

    var trimmed = [_]u8{ ' ', '\t', 'o', 'k', ' ', '\n', 0, 'x' };
    try std.testing.expectEqualStrings("ok", string.trimSpaces(&trimmed));

    var stripped = [_]u8{ ' ', '\n', '\t', 0, 'x' };
    try std.testing.expectEqual(@as(usize, 0), string.strstrip(&stripped).len);
    try std.testing.expectEqual(@as(u8, 0), stripped[0]);

    var no_spaces = [_]u8{ ' ', 'a', ' ', 'b', ' ', ' ', 'c', 0, 'z' };
    try std.testing.expectEqualStrings("abc", string.removeSpaces(&no_spaces));

    var alias_no_spaces = [_]u8{ ' ', 'd', ' ', 'e', 0, 'q' };
    try std.testing.expectEqualStrings("de", string.remove_spaces(&alias_no_spaces));

    try std.testing.expect(string.sysfsStreq("auto\n", "auto"));
    try std.testing.expect(string.sysfs_streq("auto", "auto\n"));
    try std.testing.expect(!string.sysfsStreq("autoX", "auto"));
}

test "lane06 replay keeps rbtree duplicate match iteration ordered and bounded" {
    var root = rbtree.Root.init();
    var entries = [_]SearchEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 20, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, searchLess);
    }

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &root, searchCmp) orelse return error.TestUnexpectedResult;
    const first_entry: *const SearchEntry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_entry.serial);

    var next_match_serials: [3]usize = undefined;
    var next_match_count: usize = 0;
    var cursor = first_match;
    while (true) {
        const entry: *const SearchEntry = @fieldParentPtr("node", cursor);
        next_match_serials[next_match_count] = entry.serial;
        next_match_count += 1;
        cursor = rbtree.nextMatch(&wanted, cursor, searchCmp) orelse break;
    }
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, next_match_serials[0..next_match_count]);
    try std.testing.expect(rbtree.nextMatch(&wanted, cursor, searchCmp) == null);

    var iter = rbtree.matchIterator(&wanted, &root, searchCmp);
    var iter_serials: [3]usize = undefined;
    var iter_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const SearchEntry = @fieldParentPtr("node", node);
        iter_serials[iter_count] = entry.serial;
        iter_count += 1;
    }
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, iter_serials[0..iter_count]);

    const missing = @as(i32, 99);
    try std.testing.expect(rbtree.findFirst(&missing, &root, searchCmp) == null);
    var missing_iter = rbtree.matchIterator(&missing, &root, searchCmp);
    try std.testing.expect(missing_iter.next() == null);
}