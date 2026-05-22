const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 bitmap replay keeps copy-tail aliases and formatting boundaries aligned" {
    const count = bitmap.bits_per_long + 5;
    const size = bitmap.bits_per_long * 3;
    const nbits = bitmap.bits_per_long + 8;
    const src = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0), 0 };

    var direct_tail = [_]bitmap.Word{ 0, 0, 0 };
    var alias_tail = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.copyClearTail(&direct_tail, src[0..2], count);
    bitmap.bitmap_copy_clear_tail(&alias_tail, src[0..2], count);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_tail, &alias_tail);

    var direct_extend = [_]bitmap.Word{ 0xaa55, 0xaa55, 0xaa55 };
    var alias_extend = [_]bitmap.Word{ 0xaa55, 0xaa55, 0xaa55 };
    bitmap.copyAndExtend(&direct_extend, src[0..2], count, size);
    bitmap.bitmap_copy_and_extend(&alias_extend, src[0..2], count, size);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_extend, &alias_extend);

    var direct_map = [_]bitmap.Word{ 0, 0 };
    var alias_map = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&direct_map, bitmap.bits_per_long - 2, 5);
    bitmap.bitmap_set(&alias_map, bitmap.bits_per_long - 2, 5);
    bitmap.setRange(&direct_map, bitmap.bits_per_long + 6, 1);
    bitmap.bitmap_set(&alias_map, bitmap.bits_per_long + 6, 1);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&direct_map, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&alias_map, nbits, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);

    var terminator_only = [_]u8{0xaa};
    const terminator_only_len = bitmap.bitmap_scnprintf(&alias_map, nbits, terminator_only[0..1]);
    try std.testing.expectEqual(@as(usize, 0), terminator_only_len);
    try std.testing.expectEqual(@as(u8, 0), terminator_only[0]);
}

test "lane06 find_bit replay keeps clump aliases and byte windows aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const bitmap_words = [_]find_bit.Word{
        (@as(find_bit.Word, 0x42) << 8) | (@as(find_bit.Word, 0xa5) << 24),
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 6),
    };

    try std.testing.expectEqual(
        find_bit.getValue8(&bitmap_words, 8),
        @as(u8, 0x42),
    );
    try std.testing.expectEqual(
        find_bit.getValue8(&bitmap_words, 24),
        @as(u8, 0xa5),
    );

    var direct_clump: u8 = 0;
    var alias_clump: u8 = 0;
    const direct_first = find_bit.findFirstClump8(&direct_clump, &bitmap_words, nbits);
    const alias_first = find_bit.find_first_clump8(&alias_clump, &bitmap_words, nbits);
    try std.testing.expectEqual(direct_first, alias_first);
    try std.testing.expectEqual(direct_clump, alias_clump);
    try std.testing.expectEqual(@as(usize, 8), direct_first);
    try std.testing.expectEqual(@as(u8, 0x42), direct_clump);

    direct_clump = 0;
    alias_clump = 0;
    const direct_next = find_bit.findNextClump8(&direct_clump, &bitmap_words, nbits, find_bit.bits_per_long);
    const alias_next = find_bit._find_next_clump8(&alias_clump, &bitmap_words, nbits, find_bit.bits_per_long);
    try std.testing.expectEqual(direct_next, alias_next);
    try std.testing.expectEqual(direct_clump, alias_clump);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), direct_next);
    try std.testing.expectEqual(@as(u8, 0b0100_1000), direct_clump);

    const set_tail = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const and_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const and_rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextBit(&set_tail, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_bit(&set_tail, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_and_bit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long + 5));
}

test "lane06 string replay keeps prefix match and c-string search aliases aligned" {
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&[_]u8{ 'a', 'b', 'c', 0, 'x' }, "abc"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix("abcdef", "abc"));
    try std.testing.expect(string.strstarts("kernel", "ker"));

    try std.testing.expect(string.strEndsWith(&[_]u8{ 'd', 'e', 'f', 0, 'x' }, "def"));
    try std.testing.expect(string.str_ends_with("abcdef", "def"));

    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto"));
    const plain_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(plain_haystack[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(plain_haystack[0..], "a"));

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("abc", 1, 'b'));
    try std.testing.expect(string.streq(&[_]u8{ 'a', 0, 'z' }, &[_]u8{ 'a', 0, 'x' }));
    try std.testing.expectEqual(@as(?usize, 2), string.memchrInv(&[_]u8{ 'x', 'x', 'y' }, 'x'));
    try std.testing.expectEqual(
        string.memchrInv(&[_]u8{ 0, 0, 1 }, 0),
        string.memchr_inv(&[_]u8{ 0, 0, 1 }, 0),
    );
}

test "lane06 rbtree replay keeps cached aliases and duplicate iteration aligned" {
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

    const cmpNode = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const cmpKey = struct {
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
    var primary_replacement = Entry{ .key = 10, .serial = 4 };
    var alias_replacement = Entry{ .key = 10, .serial = 4 };

    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_entries[0].node), rbtree.addCached(&primary_entries[0].node, &primary_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entries[0].node), rbtree.rb_add_cached(&alias_entries[0].node, &alias_root, less));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_entries[1].node, &primary_root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_entries[1].node, &alias_root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_entries[2].node, &primary_root, cmpNode));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_entries[2].node, &alias_root, cmpNode));

    const primary_existing = rbtree.findAddCached(&primary_entries[3].node, &primary_root, cmpNode) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_entries[3].node, &alias_root, cmpNode) orelse return error.TestUnexpectedResult;
    const primary_existing_entry: *const Entry = @fieldParentPtr("node", primary_existing);
    const alias_existing_entry: *const Entry = @fieldParentPtr("node", alias_existing);
    try std.testing.expectEqual(primary_existing_entry.serial, alias_existing_entry.serial);
    try std.testing.expectEqual(@as(usize, 0), primary_existing_entry.serial);

    const duplicate_key = @as(i32, 10);
    var primary_iter = rbtree.matchIterator(&duplicate_key, &primary_root.root, cmpKey);
    var alias_iter = rbtree.matchIterator(&duplicate_key, &alias_root.root, cmpKey);
    var primary_serials: [1]usize = undefined;
    var alias_serials: [1]usize = undefined;
    var count: usize = 0;
    while (primary_iter.next()) |node| {
        const alias_node = alias_iter.next() orelse return error.TestUnexpectedResult;
        const primary_entry: *const Entry = @fieldParentPtr("node", node);
        const alias_entry: *const Entry = @fieldParentPtr("node", alias_node);
        primary_serials[count] = primary_entry.serial;
        alias_serials[count] = alias_entry.serial;
        count += 1;
    }
    try std.testing.expect(alias_iter.next() == null);
    try std.testing.expectEqual(@as(usize, 1), count);
    try std.testing.expectEqualSlices(usize, primary_serials[0..count], alias_serials[0..count]);

    const primary_promoted = rbtree.eraseCached(&primary_entries[1].node, &primary_root) orelse return error.TestUnexpectedResult;
    const alias_promoted = rbtree.rb_erase_cached(&alias_entries[1].node, &alias_root) orelse return error.TestUnexpectedResult;
    const primary_promoted_entry: *const Entry = @fieldParentPtr("node", primary_promoted);
    const alias_promoted_entry: *const Entry = @fieldParentPtr("node", alias_promoted);
    try std.testing.expectEqual(primary_promoted_entry.serial, alias_promoted_entry.serial);

    rbtree.replaceNodeCached(&primary_entries[0].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_entries[0].node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));

    rbtree.eraseInitCached(&primary_replacement.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_replacement.node, &alias_root);
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
}
