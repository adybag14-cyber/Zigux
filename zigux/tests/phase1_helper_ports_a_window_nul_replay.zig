const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 window-nul bitmap helpers keep formatted caller windows aligned" {
    const Word = bitmap.Word;
    const start = bitmap.bits_per_long - 1;
    const nbits = bitmap.bits_per_long + 8;
    var direct = [_]Word{ 0, 0 };
    var alias = [_]Word{ 0, 0 };

    bitmap.setRange(&direct, start, 4);
    bitmap.bitmap_set(&alias, start, 4);
    bitmap.clearRange(&direct, start + 2, 1);
    bitmap.bitmap_clear(&alias, start + 2, 1);
    try std.testing.expectEqualSlices(Word, &direct, &alias);

    var direct_buffer: [64]u8 = undefined;
    var alias_buffer: [64]u8 = undefined;
    const direct_len = bitmap.scnprintf(&direct, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&alias, nbits, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);
    try std.testing.expectEqualStrings(direct_buffer[0..direct_len], alias_buffer[0..alias_len]);

    var direct_terminator = [_]u8{0xaa};
    var alias_terminator = [_]u8{0xbb};
    try std.testing.expectEqual(@as(usize, 0), bitmap.scnprintf(&direct, nbits, direct_terminator[0..1]));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_scnprintf(&alias, nbits, alias_terminator[0..1]));
    try std.testing.expectEqual(@as(u8, 0), direct_terminator[0]);
    try std.testing.expectEqual(@as(u8, 0), alias_terminator[0]);

    var direct_zero_backing = [_]u8{0xcc};
    var alias_zero_backing = [_]u8{0xdd};
    try std.testing.expectEqual(@as(usize, 0), bitmap.scnprintf(&direct, nbits, direct_zero_backing[0..0]));
    try std.testing.expectEqual(@as(usize, 0), bitmap.bitmap_scnprintf(&alias, nbits, alias_zero_backing[0..0]));
    try std.testing.expectEqual(@as(u8, 0xcc), direct_zero_backing[0]);
    try std.testing.expectEqual(@as(u8, 0xdd), alias_zero_backing[0]);
}

test "lane06 window-nul find-bit helpers keep byte windows and tail clumps aligned" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 8;
    const map = [_]Word{
        @as(Word, 0xa5) << @intCast(find_bit.bits_per_long - 8),
        (@as(Word, 0x54) << 0),
    };

    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&map, find_bit.bits_per_long - 8));
    try std.testing.expectEqual(@as(u8, 0x54), find_bit.getValue8(&map, find_bit.bits_per_long));

    var direct_clump: u8 = 0;
    var alias_clump: u8 = 0;
    var underscore_clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long - 8), find_bit.findFirstClump8(&direct_clump, &map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long - 8), find_bit.find_first_clump8(&alias_clump, &map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long - 8), find_bit._find_first_clump8(&underscore_clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0xa5), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);
    try std.testing.expectEqual(direct_clump, underscore_clump);

    direct_clump = 0;
    alias_clump = 0;
    underscore_clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&direct_clump, &map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&alias_clump, &map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit._find_next_clump8(&underscore_clump, &map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x54), direct_clump);
    try std.testing.expectEqual(direct_clump, alias_clump);
    try std.testing.expectEqual(direct_clump, underscore_clump);

    direct_clump = 0x5a;
    alias_clump = 0x6b;
    underscore_clump = 0x7c;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&direct_clump, &map, nbits, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_clump8(&alias_clump, &map, nbits, nbits + 8));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&underscore_clump, &map, nbits, nbits + 16));
    try std.testing.expectEqual(@as(u8, 0x5a), direct_clump);
    try std.testing.expectEqual(@as(u8, 0x6b), alias_clump);
    try std.testing.expectEqual(@as(u8, 0x7c), underscore_clump);
}

test "lane06 window-nul string helpers keep bounded matches inside the first terminator" {
    const bounded = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    const match_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };

    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&bounded, 5, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, 5, 'c'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&bounded, 5, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, 2, 0));
    try std.testing.expectEqual(@as(usize, 2), string.strHasPrefix(&bounded, "ab"));
    try std.testing.expect(string.strstarts("abcdef", "abc"));
    try std.testing.expect(string.strEndsWith(&[_]u8{ 'a', 'b', 'c', 0, 'd' }, "bc"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(string.sysfsMatchString(sysfs_haystack[0..], "auto"), string.sysfs_match_string(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(match_haystack[0..], "a"));
    try std.testing.expectEqual(string.matchString(match_haystack[0..], "a"), string.match_string(match_haystack[0..], "a"));
}

test "lane06 window-nul rbtree cached aliases keep singleton teardown and reseed aligned" {
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

    const keyOf = struct {
        fn read(node: ?*rbtree.Node) ?i32 {
            const current = node orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", current);
            return entry.key;
        }
    }.read;

    var direct_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();
    var direct_first = Entry{ .key = 10 };
    var alias_first = Entry{ .key = 10 };
    var direct_left = Entry{ .key = 5 };
    var alias_left = Entry{ .key = 5 };
    var direct_reseed = Entry{ .key = 7 };
    var alias_reseed = Entry{ .key = 7 };

    try std.testing.expectEqual(@as(?*rbtree.Node, &direct_first.node), rbtree.addCached(&direct_first.node, &direct_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_first.node), rbtree.rb_add_cached(&alias_first.node, &alias_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &direct_left.node), rbtree.addCached(&direct_left.node, &direct_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_left.node), rbtree.rb_add_cached(&alias_left.node, &alias_root, less));
    try std.testing.expectEqual(keyOf(rbtree.firstCached(&direct_root)), keyOf(rbtree.rb_first_cached(&alias_root)));

    rbtree.eraseInitCached(&direct_left.node, &direct_root);
    rbtree.rb_erase_init_cached(&alias_left.node, &alias_root);
    try std.testing.expect(rbtree.emptyNode(&direct_left.node));
    try std.testing.expect(rbtree.emptyNode(&alias_left.node));
    try std.testing.expectEqual(keyOf(rbtree.firstCached(&direct_root)), keyOf(rbtree.rb_first_cached(&alias_root)));
    try std.testing.expectEqual(@as(i32, 10), keyOf(rbtree.firstCached(&direct_root)).?);

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.eraseCached(&direct_first.node, &direct_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_erase_cached(&alias_first.node, &alias_root));
    try std.testing.expectEqual(@as(?i32, null), keyOf(rbtree.firstCached(&direct_root)));
    try std.testing.expectEqual(@as(?i32, null), keyOf(rbtree.rb_first_cached(&alias_root)));
    try std.testing.expect(direct_root.root.node == null);
    try std.testing.expect(alias_root.root.node == null);

    try std.testing.expectEqual(@as(?*rbtree.Node, &direct_reseed.node), rbtree.addCached(&direct_reseed.node, &direct_root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_reseed.node), rbtree.rb_add_cached(&alias_reseed.node, &alias_root, less));
    try std.testing.expectEqual(keyOf(rbtree.firstCached(&direct_root)), keyOf(rbtree.rb_first_cached(&alias_root)));

    var detached = rbtree.Node.init();
    rbtree.clearNode(&detached);
    try std.testing.expect(rbtree.emptyNode(&detached));
    try std.testing.expect(rbtree.rb_next(&detached) == null);
    try std.testing.expect(rbtree.rb_prev(&detached) == null);
}
