const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string_helpers = @import("string_helpers");
const rbtree = @import("rbtree");

test "lane06 replay keeps subset and sparse rendering pinned to the declared tail window" {
    const nbits = bitmap.bits_per_long + 6;
    const subset = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 7),
        (@as(bitmap.Word, 1) << 0) |
            (@as(bitmap.Word, 1) << 4) |
            (@as(bitmap.Word, 1) << 9),
    };
    const superset = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) |
            (@as(bitmap.Word, 1) << 7) |
            (@as(bitmap.Word, 1) << 8),
        (@as(bitmap.Word, 1) << 0) |
            (@as(bitmap.Word, 1) << 4) |
            (@as(bitmap.Word, 1) << 5) |
            (@as(bitmap.Word, 1) << 9),
    };
    const disjoint = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 10),
    };
    var buffer: [64]u8 = undefined;
    var expected: [48]u8 = undefined;

    try std.testing.expect(bitmap.bitmap_subset(&subset, &superset, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&subset, &superset, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&subset, &disjoint, nbits));

    const rendered_len = bitmap.bitmap_scnprintf(&superset, nbits, &buffer);
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "1,7-8,{d},{d}-{d}",
        .{
            bitmap.bits_per_long,
            bitmap.bits_per_long + 4,
            bitmap.bits_per_long + 5,
        },
    );
    try std.testing.expectEqualStrings(expected_text, buffer[0..rendered_len]);
}

test "lane06 replay keeps last-bit, zero-bit, and clump scans aligned on a partial tail byte" {
    const nbits = find_bit.bits_per_long + 6;
    const sparse = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 5),
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 5) |
            (@as(find_bit.Word, 1) << 9),
    };
    const zeros = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << 3),
    };
    var clump: u8 = 0;

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.find_last_bit(&sparse, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.find_next_zero_bit(&zeros, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit._find_next_clump8(&clump, &sparse, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b0010_0010), clump);
}

test "lane06 replay keeps C-string comparisons, spans, and fallback indices in sync" {
    const with_nul = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x' };
    const modes = [_][]const u8{ "safe", "mode", "turbo" };
    var dirty = [_]u8{'z'} ** 24;

    dirty[dirty.len - 1] = '!';

    try std.testing.expect(string_helpers.streq(&with_nul, "mode"));
    try std.testing.expectEqual(@as(usize, 4), string_helpers.strHasPrefix(&with_nul, "mode"));
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.match_string(modes[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, dirty.len - 1), string_helpers.memchr_inv(dirty[0..], 'z'));
}

test "lane06 replay keeps cached leftmost state stable while duplicate iterators stay ordered" {
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

    var entries = [_]Entry{
        .{ .key = 5, .serial = 0 },
        .{ .key = 10, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 10, .serial = 3 },
        .{ .key = 20, .serial = 4 },
    };
    var replacement = Entry{ .key = 18, .serial = 5 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_first_cached(&root));

    rbtree.rb_replace_node_cached(&entries[4].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_first_cached(&root));

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
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 2, 3 }, serials[0..count]);

    const promoted = rbtree.rb_erase_cached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[1].node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first_cached(&root));
}
