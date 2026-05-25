const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap scnprintf aliases aligned across word boundaries and truncation" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 8;
    var map = [_]Word{ 0, 0 };
    bitmap.setRange(&map, bitmap.bits_per_long - 2, 5);
    bitmap.bitmap_set(&map, bitmap.bits_per_long + 6, 1);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&map, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&map, nbits, &alias_buffer);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d}-{d},{d}",
        .{
            bitmap.bits_per_long - 2,
            bitmap.bits_per_long + 2,
            bitmap.bits_per_long + 6,
        },
    );

    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(expected_text, direct_buffer[0..direct_len]);
    try std.testing.expectEqualStrings(expected_text, alias_buffer[0..alias_len]);

    var trunc_direct = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    var trunc_alias = [_]u8{ 0xbb, 0xbb, 0xbb, 0xbb };
    const trunc_direct_len = bitmap.scnprintf(&map, nbits, &trunc_direct);
    const trunc_alias_len = bitmap.bitmap_scnprintf(&map, nbits, &trunc_alias);

    try std.testing.expectEqual(trunc_direct_len, trunc_alias_len);
    try std.testing.expectEqualStrings(trunc_direct[0..trunc_direct_len], trunc_alias[0..trunc_alias_len]);
    try std.testing.expectEqual(@as(u8, 0), trunc_direct[trunc_direct_len]);
    try std.testing.expectEqual(@as(u8, 0), trunc_alias[trunc_alias_len]);
}

test "lane06 replay keeps clump aliases aligned to word-byte boundaries across words" {
    const Word = find_bit.Word;
    const last_aligned_byte = find_bit.bits_per_long - 8;
    const nbits = find_bit.bits_per_long * 2;
    const map = [_]Word{
        @as(Word, 0xa5) << @intCast(last_aligned_byte),
        @as(Word, 0x11),
    };

    var first_clump: u8 = 0;
    var alias_clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, last_aligned_byte),
        find_bit.findFirstClump8(&first_clump, &map, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, last_aligned_byte),
        find_bit.find_first_clump8(&alias_clump, &map, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0xa5), first_clump);
    try std.testing.expectEqual(first_clump, alias_clump);

    first_clump = 0;
    alias_clump = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findNextClump8(&first_clump, &map, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.find_next_clump8(&alias_clump, &map, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(@as(u8, 0x11), first_clump);
    try std.testing.expectEqual(first_clump, alias_clump);
}

test "lane06 replay keeps string match helpers and C-string replacements aligned" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_haystack[0..], "auto"));

    const exact_haystack = [_][]const u8{
        "alpha",
        &[_]u8{ 'b', 'e', 't', 'a', 0, 'x' },
        "gamma",
    };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(exact_haystack[0..], "beta"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(exact_haystack[0..], "beta"));

    var replace_buf = [_]u8{ 'm', 'o', 'd', 'e', '-', 'x', 0, '-' };
    try std.testing.expectEqual(@as(usize, 6), string.strreplace(&replace_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'm', 'o', 'd', 'e', '_', 'x', 0, '-' }, &replace_buf);
    try std.testing.expect(string.strstarts("mode-check", "mode"));
    try std.testing.expect(string.strEndsWith(&[_]u8{ 'm', 'o', 'd', 'e', 0, 'x' }, "de"));
    try std.testing.expect(string.str_ends_with("mode-check", "check"));
}

test "lane06 replay keeps cached detach helpers aligned as leftmost nodes are removed" {
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

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.rb_erase_init_cached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    rbtree.rb_erase_init_cached(&entries[2].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);
}
