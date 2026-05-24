const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const MatchEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn matchLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const MatchEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const MatchEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn matchKeyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const MatchEntry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "lane06 replay keeps bitmap allocation and state aliases aligned" {
    const allocator = std.testing.allocator;
    const nbits = bitmap.bits_per_long + 9;

    try std.testing.expectEqual(bitmap.sizeBytes(nbits), bitmap.bitmap_size(nbits));
    try std.testing.expectEqual(@as(usize, 0), bitmap.sizeBytes(0));

    var direct = try bitmap.alloc(allocator, nbits);
    defer bitmap.free(allocator, &direct);
    var alias = try bitmap.bitmap_alloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &alias);

    try std.testing.expect(direct != null);
    try std.testing.expect(alias != null);
    try std.testing.expectEqual(direct.?.len, alias.?.len);

    bitmap.zero(direct.?, nbits);
    bitmap.bitmap_fill(alias.?, nbits);
    try std.testing.expect(bitmap.empty(direct.?, nbits));
    try std.testing.expect(bitmap.bitmap_full(alias.?, nbits));
    try std.testing.expectEqual(@as(usize, nbits), bitmap.bitmap_weight(alias.?, nbits));

    bitmap.free(allocator, &direct);
    bitmap.bitmap_free(allocator, &alias);
    try std.testing.expect(direct == null);
    try std.testing.expect(alias == null);

    var direct_zero = try bitmap.zalloc(allocator, nbits);
    defer bitmap.free(allocator, &direct_zero);
    var alias_zero = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &alias_zero);

    try std.testing.expect(direct_zero != null);
    try std.testing.expect(alias_zero != null);
    for (direct_zero.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }
    for (alias_zero.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }

    var zero_direct = try bitmap.alloc(allocator, 0);
    defer bitmap.free(allocator, &zero_direct);
    var zero_alias = try bitmap.bitmap_alloc(allocator, 0);
    defer bitmap.bitmap_free(allocator, &zero_alias);
    try std.testing.expect(zero_direct == null);
    try std.testing.expect(zero_alias == null);
}

test "lane06 replay keeps clump and last-bit scans honest at the declared tail" {
    const nbits = find_bit.bits_per_long + 5;
    const map = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 8),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&clump, &map, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(u8, 0b0000_1010), clump);

    clump = 0xaa;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&clump, &map, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0xaa), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.find_last_bit(&map, nbits));

    const outside_only = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 8 };
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(&outside_only, nbits));
}

test "lane06 replay keeps string match helpers newline and C-string aware" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(sysfs_haystack[0..], "missing"));

    const cstring_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(cstring_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(cstring_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(cstring_haystack[0..], "beta"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(cstring_haystack[0..], "gamma"));
}

test "lane06 replay keeps duplicate-range match iteration ordered" {
    var entries = [_]MatchEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, matchLess);
    }

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &root, matchKeyCmp) orelse return error.TestUnexpectedResult;
    const first_entry: *const MatchEntry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_entry.serial);

    var via_next_match: [3]usize = undefined;
    var next_count: usize = 0;
    var cursor: ?*rbtree.Node = first_match;
    while (cursor) |node| {
        const entry: *const MatchEntry = @fieldParentPtr("node", node);
        via_next_match[next_count] = entry.serial;
        next_count += 1;
        cursor = rbtree.nextMatch(&wanted, node, matchKeyCmp);
    }

    var via_iter: [3]usize = undefined;
    var iter_count: usize = 0;
    var iter = rbtree.matchIterator(&wanted, &root, matchKeyCmp);
    while (iter.next()) |node| {
        const entry: *const MatchEntry = @fieldParentPtr("node", node);
        via_iter[iter_count] = entry.serial;
        iter_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), next_count);
    try std.testing.expectEqual(@as(usize, 3), iter_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, via_next_match[0..next_count]);
    try std.testing.expectEqualSlices(usize, via_next_match[0..next_count], via_iter[0..iter_count]);

    const missing = @as(i32, 17);
    var missing_iter = rbtree.matchIterator(&missing, &root, matchKeyCmp);
    try std.testing.expect(missing_iter.next() == null);
}
