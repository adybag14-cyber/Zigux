const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap state and allocation aliases keep zero fill and free semantics aligned" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 5;

    var direct = [_]Word{ 0xaa55, 0xaa55 };
    var alias = [_]Word{ 0xaa55, 0xaa55 };
    bitmap.zero(&direct, nbits);
    bitmap.bitmap_zero(&alias, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expect(bitmap.empty(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_empty(&alias, nbits));

    bitmap.fill(&direct, nbits);
    bitmap.bitmap_fill(&alias, nbits);
    try std.testing.expectEqualSlices(Word, &direct, &alias);
    try std.testing.expect(bitmap.full(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_full(&alias, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weight(&alias, nbits));

    var allocated: ?[]Word = try bitmap.bitmap_alloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &allocated);
    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(nbits)), allocated.?.len);

    var zeroed: ?[]Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }

    bitmap.bitmap_free(allocator, &allocated);
    bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expect(allocated == null);
    try std.testing.expect(zeroed == null);
}

test "find_bit or and zero scans keep boundary starts inclusive across tail windows" {
    const nbits = bits_per_long + 6;
    const boundary = bits_per_long;
    const or_lhs = [_]Word{
        @as(Word, 1) << @intCast(bits_per_long - 1),
        (@as(Word, 1) << 0) | (@as(Word, 1) << 4),
    };
    const or_rhs = [_]Word{
        0,
        (@as(Word, 1) << 2) | (@as(Word, 1) << 7),
    };
    const zero_map = [_]Word{
        ~@as(Word, 0),
        bitmap.lastWordMask(nbits) & ~((@as(Word, 1) << 0) | (@as(Word, 1) << 4)),
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextOrBit(&or_lhs, &or_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 2), find_bit.find_next_or_bit(&or_lhs, &or_rhs, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextOrBit(&or_lhs, &or_rhs, nbits, boundary + 3));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_or_bit(&or_lhs, &or_rhs, nbits, boundary + 5));

    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextZeroBit(&zero_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.find_next_zero_bit(&zero_map, nbits, boundary + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, boundary + 5));
}

test "string sysfs-aware matching aliases preserve newline and bounded lookup behavior" {
    const haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    const empty = [_][]const u8{};
    const nul_terminated = [_]u8{ 'a', 'u', 't', 'o', 0, 'x' };

    try std.testing.expect(string.sysfsStreq("mode\n", "mode"));
    try std.testing.expect(string.sysfs_streq("mode", "mode\n"));
    try std.testing.expect(!string.sysfsStreq("mode\nmore", "mode"));

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&haystack, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&haystack, "auto\n"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&haystack, &nul_terminated));
    try std.testing.expectEqual(@as(?usize, null), string.sysfs_match_string(&empty, "auto"));
}

test "rbtree erase-init cached aliases keep leftmost and detach state aligned through reseed" {
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

    const firstKey = struct {
        fn read(root: *const rbtree.RootCached) ?i32 {
            const node = rbtree.firstCached(root) orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", node);
            return entry.key;
        }
    }.read;

    var primary_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 12 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 12 },
    };
    var primary_reseed = Entry{ .key = 3 };
    var alias_reseed = Entry{ .key = 3 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, less);
    }

    try std.testing.expectEqual(@as(?i32, 5), firstKey(&primary_root));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    rbtree.eraseInitCached(&primary_entries[1].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[1].node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_entries[1].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[1].node));
    try std.testing.expectEqual(@as(?i32, 10), firstKey(&primary_root));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));

    rbtree.eraseInitCached(&primary_entries[0].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[0].node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_entries[0].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[0].node));
    try std.testing.expectEqual(@as(?i32, 12), firstKey(&primary_root));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));

    _ = rbtree.addCached(&primary_reseed.node, &primary_root, less);
    _ = rbtree.rb_add_cached(&alias_reseed.node, &alias_root, less);
    try std.testing.expectEqual(@as(?i32, 3), firstKey(&primary_root));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
}
