const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap helpers keep zeroed allocation and formatted tails aligned" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 6;

    var direct = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &direct);
    var alias = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &alias);

    try std.testing.expectEqual(direct.?.len, alias.?.len);
    for (alias.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }

    bitmap.setRange(direct.?, bits_per_long - 2, 4);
    bitmap.bitmap_set(alias.?, bits_per_long - 2, 4);
    bitmap.setRange(direct.?, bits_per_long + 4, 2);
    bitmap.bitmap_set(alias.?, bits_per_long + 4, 2);

    try std.testing.expectEqualSlices(Word, direct.?, alias.?);
    try std.testing.expectEqual(bitmap.weight(direct.?, nbits), bitmap.bitmap_weight(alias.?, nbits));

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(direct.?, nbits, direct_buffer[0..]);
    const alias_len = bitmap.bitmap_scnprintf(alias.?, nbits, alias_buffer[0..]);

    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);

    var short_buffer = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    const short_len = bitmap.bitmap_scnprintf(alias.?, nbits, short_buffer[0..]);
    try std.testing.expectEqual(@as(usize, 4), short_len);
    try std.testing.expectEqualSlices(u8, alias_buffer[0..short_len], short_buffer[0..short_len]);
    try std.testing.expectEqual(@as(u8, 0), short_buffer[short_len]);
}

test "find_bit helpers keep last and inclusive tail scans aligned" {
    const nbits = bits_per_long + 6;
    const boundary = bits_per_long + 5;
    const bitmap_words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 5) |
            (@as(find_bit.Word, 1) << 9),
    };
    const zero_words = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) &
            ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 5)),
    };
    const and_rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 5) };
    const andnot_rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 1 };

    try std.testing.expectEqual(boundary, find_bit.findLastBit(bitmap_words[0..], nbits));
    try std.testing.expectEqual(boundary, find_bit.find_last_bit(bitmap_words[0..], nbits));

    try std.testing.expectEqual(boundary, find_bit.findNextBit(bitmap_words[0..], nbits, boundary));
    try std.testing.expectEqual(nbits, find_bit.find_next_bit(bitmap_words[0..], nbits, boundary + 1));

    try std.testing.expectEqual(boundary, find_bit.findNextZeroBit(zero_words[0..], nbits, bits_per_long + 2));
    try std.testing.expectEqual(nbits, find_bit.find_next_zero_bit(zero_words[0..], nbits, boundary + 1));

    try std.testing.expectEqual(bits_per_long + 1, find_bit.findFirstAndBit(bitmap_words[0..], and_rhs[0..], nbits));
    try std.testing.expectEqual(boundary, find_bit.find_next_and_bit(bitmap_words[0..], and_rhs[0..], nbits, bits_per_long + 2));

    try std.testing.expectEqual(boundary, find_bit.findFirstAndNotBit(bitmap_words[0..], andnot_rhs[0..], nbits));
    try std.testing.expectEqual(boundary, find_bit.find_next_andnot_bit(bitmap_words[0..], andnot_rhs[0..], nbits, boundary));
    try std.testing.expectEqual(nbits, find_bit.find_next_andnot_bit(bitmap_words[0..], andnot_rhs[0..], nbits, boundary + 1));
}

test "string sysfs count and delimiter helpers stop at visible boundaries" {
    const sysfs_haystack = [_][]const u8{ "mode\n", "manual", "mode" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(sysfs_haystack[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(sysfs_haystack[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(sysfs_haystack[1..2], "mode"));

    const bounded = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    const match_haystack = [_][]const u8{
        &[_]u8{ 'm', 'o', 'd', 'e', 0, 'x' },
        "manual",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(match_haystack[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(match_haystack[0..], "manual"));
    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix("mode-switch", "mode"));
    try std.testing.expect(string.strEndsWith("mode-switch", "switch"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&bounded, bounded.len, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, bounded.len, 'c'));
}

test "rbtree duplicate iterators and cached find-add helpers stay aligned" {
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

    const key_cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    const node_cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
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
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = @as(i32, 10);
    var iter = rbtree.matchIterator(&duplicate, &root, key_cmp);
    var iterator_serials: [3]usize = undefined;
    var next_match_serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        iterator_serials[count] = entry.serial;
        count += 1;
    }

    const first_match = rbtree.findFirst(&duplicate, &root, key_cmp) orelse return error.TestUnexpectedResult;
    var alias_count: usize = 0;
    var current: ?*rbtree.Node = first_match;
    while (current) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        next_match_serials[alias_count] = entry.serial;
        alias_count += 1;
        current = rbtree.nextMatch(&duplicate, node, key_cmp);
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqual(count, alias_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, iterator_serials[0..count]);
    try std.testing.expectEqualSlices(usize, iterator_serials[0..count], next_match_serials[0..alias_count]);

    var primary_cached = rbtree.RootCached.init();
    var alias_cached = rbtree.RootCached.init();
    var primary_root_entry = Entry{ .key = 10, .serial = 10 };
    var primary_leftmost = Entry{ .key = 5, .serial = 11 };
    var primary_larger = Entry{ .key = 15, .serial = 12 };
    var primary_duplicate = Entry{ .key = 10, .serial = 13 };
    var alias_root_entry = Entry{ .key = 10, .serial = 10 };
    var alias_leftmost = Entry{ .key = 5, .serial = 11 };
    var alias_larger = Entry{ .key = 15, .serial = 12 };
    var alias_duplicate = Entry{ .key = 10, .serial = 13 };

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_root_entry.node, &primary_cached, node_cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_root_entry.node, &alias_cached, node_cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_leftmost.node, &primary_cached, node_cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_leftmost.node, &alias_cached, node_cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_larger.node, &primary_cached, node_cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_larger.node, &alias_cached, node_cmp));

    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_cached, node_cmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_cached, node_cmp) orelse return error.TestUnexpectedResult;
    const primary_existing_entry: *const Entry = @fieldParentPtr("node", primary_existing);
    const alias_existing_entry: *const Entry = @fieldParentPtr("node", alias_existing);

    try std.testing.expectEqual(@as(i32, 10), primary_existing_entry.key);
    try std.testing.expectEqual(primary_existing_entry.key, alias_existing_entry.key);
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_leftmost.node), rbtree.firstCached(&primary_cached));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_leftmost.node), rbtree.rb_first_cached(&alias_cached));
    try std.testing.expectEqual(rbtree.first(&primary_cached.root), rbtree.firstCached(&primary_cached));
    try std.testing.expectEqual(rbtree.first(&alias_cached.root), rbtree.rb_first_cached(&alias_cached));
}
