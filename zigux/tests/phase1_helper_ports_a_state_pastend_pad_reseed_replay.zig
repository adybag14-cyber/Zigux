const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap state aliases keep declared windows aligned" {
    const nbits = bitmap.bits_per_long + 5;

    try std.testing.expectEqual(bitmap.bitmap_size(0), bitmap.bitmap_size(0));
    try std.testing.expectEqual(bitmap.bitmap_size(nbits), bitmap.bitmap_size(nbits));

    var direct = [_]bitmap.Word{ 0xaa55, 0xaa55 };
    var alias = [_]bitmap.Word{ 0xaa55, 0xaa55 };
    bitmap.zero(&direct, nbits);
    bitmap.bitmap_zero(&alias, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expect(bitmap.empty(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_empty(&alias, nbits));

    bitmap.fill(&direct, nbits);
    bitmap.bitmap_fill(&alias, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expect(bitmap.full(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_full(&alias, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weight(&alias, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 5), bitmap.weight(&direct, nbits));

    const tail_noise = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 9) };
    try std.testing.expectEqual(@as(usize, 1), bitmap.weight(&tail_noise, nbits));
    try std.testing.expectEqual(@as(usize, 1), bitmap.bitmap_weight(&tail_noise, nbits));
}

test "phase1 helper ports A find_bit past-end scans leave caller state unchanged" {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9),
    };
    const rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3),
    };

    try std.testing.expectEqual(nbits, find_bit.findNextBit(&lhs, nbits, nbits));
    try std.testing.expectEqual(nbits, find_bit.find_next_bit(&lhs, nbits, nbits + 1));
    try std.testing.expectEqual(nbits, find_bit._find_next_bit(&lhs, nbits, nbits + 7));

    try std.testing.expectEqual(nbits, find_bit.findNextZeroBit(&lhs, nbits, nbits));
    try std.testing.expectEqual(nbits, find_bit.find_next_zero_bit(&lhs, nbits, nbits + 1));
    try std.testing.expectEqual(nbits, find_bit._find_next_zero_bit(&lhs, nbits, nbits + 7));

    try std.testing.expectEqual(nbits, find_bit.findNextAndBit(&lhs, &rhs, nbits, nbits));
    try std.testing.expectEqual(nbits, find_bit.find_next_and_bit(&lhs, &rhs, nbits, nbits + 1));
    try std.testing.expectEqual(nbits, find_bit._find_next_and_bit(&lhs, &rhs, nbits, nbits + 7));

    try std.testing.expectEqual(nbits, find_bit.findNextAndNotBit(&lhs, &rhs, nbits, nbits));
    try std.testing.expectEqual(nbits, find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, nbits + 1));
    try std.testing.expectEqual(nbits, find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, nbits + 7));

    var clump: u8 = 0x5a;
    try std.testing.expectEqual(nbits, find_bit.findNextClump8(&clump, &lhs, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
    try std.testing.expectEqual(nbits, find_bit.find_next_clump8(&clump, &lhs, nbits, nbits + 3));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
    try std.testing.expectEqual(nbits, find_bit._find_next_clump8(&clump, &lhs, nbits, nbits + 9));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "phase1 helper ports A string padding helpers keep C-string boundaries aligned" {
    var direct_pad = [_]u8{ 9, 9, 9, 9, 9 };
    var alias_pad = [_]u8{ 9, 9, 9, 9, 9 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(direct_pad[0..], "hi"));
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(alias_pad[0..], "hi"));
    try std.testing.expectEqualSlices(u8, &direct_pad, &alias_pad);

    try std.testing.expectEqualStrings("lead", string.skipSpaces(" \tlead"));
    try std.testing.expectEqualStrings("lead", string.skip_spaces(" \tlead"));

    var remove_buf = [_]u8{ 'a', ' ', 'b', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("ab", string.removeSpaces(remove_buf[0..]));

    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string.replaceChar(replace_buf[0..], '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '+', 'b', 0, '-' }, &replace_buf);

    var alias_replace_buf = [_]u8{ 'a', 'b', 'a', 0, 'a' };
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(alias_replace_buf[0..], 'a', 'z'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'b', 'z', 0, 'a' }, &alias_replace_buf);
}

test "phase1 helper ports A rbtree cached aliases keep leftmost reseed aligned" {
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

    const firstKey = struct {
        fn read(root: *const rbtree.RootCached) ?i32 {
            const node = rbtree.firstCached(root) orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", node);
            return entry.key;
        }
    }.read;

    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var primary_replacement = Entry{ .key = 10, .serial = 3 };
    var alias_replacement = Entry{ .key = 10, .serial = 3 };
    var primary_reseed = Entry{ .key = 6, .serial = 4 };
    var alias_reseed = Entry{ .key = 6, .serial = 4 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, less);
    }
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    rbtree.replaceNodeCached(&primary_entries[0].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_entries[0].node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    rbtree.eraseInitCached(&primary_entries[1].node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_entries[1].node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&primary_entries[1].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[1].node));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    _ = rbtree.addCached(&primary_reseed.node, &primary_root, less);
    _ = rbtree.rb_add_cached(&alias_reseed.node, &alias_root, less);
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.firstCached(&alias_root));
}
