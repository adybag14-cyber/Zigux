const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "phase1 helper ports A bitmap and/equal/subset helpers clamp partial tails" {
    const nbits = find_bit.bits_per_long + 6;
    const lhs = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 8),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    const rhs = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 8),
        (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };

    var both = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.bitmap_and(&both, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 8)), both[0]);
    try std.testing.expectEqual(@as(bitmap.Word, @as(bitmap.Word, 1) << 4), both[1]);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&both, nbits));

    const subset = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 8),
        (@as(bitmap.Word, 1) << 4),
    };
    try std.testing.expect(bitmap.bitmap_equal(&both, &subset, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&both, &lhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));

    var merged = [_]bitmap.Word{ 0, 0 };
    try std.testing.expectEqual(@as(usize, 4), bitmap.weightedOr(&merged, &lhs, &rhs, nbits));

    var rendered: [64]u8 = undefined;
    const len = bitmap.bitmap_scnprintf(&merged, nbits, &rendered);
    try std.testing.expectEqualStrings("2,8,65,68", rendered[0..len]);
}

test "phase1 helper ports A zero scans and clumps stop at the declared tail" {
    const nbits = find_bit.bits_per_long + 5;
    const zeros = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextZeroBit(&zeros, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.find_next_zero_bit(&zeros, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zeros, nbits, find_bit.bits_per_long + 5));

    const bits = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 7),
    };
    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &bits, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &bits, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findLastBit(&bits, nbits));
}

test "phase1 helper ports A sysfs and prefix helpers respect newline and embedded NUL boundaries" {
    try std.testing.expect(string.sysfsStreq("turbo\n", "turbo"));
    try std.testing.expect(string.sysfs_streq("turbo", "turbo\n"));
    try std.testing.expect(!string.sysfsStreq("turbo\nboost", "turbo"));

    const sysfs_haystack = [_][]const u8{ "off", "turbo\n", "auto" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "turbo"));

    const exact_haystack = [_][]const u8{
        &[_]u8{ 'p', 'r', 'e', 0, 'x' },
        "prefix",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(exact_haystack[0..], "pre"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(exact_haystack[0..], "prefix"));
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&[_]u8{ 'p', 'r', 'e', 0, 'x' }, "pre"));
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr(&[_]u8{ 'a', 'b', 'c', 0, 'd' }, 5, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 'b', 'c', 0, 'd' }, 3, 0));
}

test "phase1 helper ports A cached replacement keeps leftmost and neighbors stable" {
    const Entry = struct {
        const Self = @This();

        key: i32,
        tag: usize,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Self = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Self = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    };

    var left = Entry{ .key = 6, .tag = 0 };
    var root_entry = Entry{ .key = 10, .tag = 1 };
    var right = Entry{ .key = 14, .tag = 2 };
    var replacement = Entry{ .key = 6, .tag = 3 };
    var cached = rbtree.RootCached.init();

    _ = rbtree.addCached(&root_entry.node, &cached, Entry.less);
    _ = rbtree.addCached(&left.node, &cached, Entry.less);
    _ = rbtree.addCached(&right.node, &cached, Entry.less);

    try std.testing.expectEqual(@as(?*rbtree.Node, &left.node), rbtree.rb_first_cached(&cached));
    rbtree.replaceNodeCached(&left.node, &replacement.node, &cached);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_first_cached(&cached));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_prev(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.rb_next(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.rb_prev(&root_entry.node));

    const replacement_entry: *const Entry = @fieldParentPtr("node", rbtree.rb_first_cached(&cached).?);
    try std.testing.expectEqual(@as(i32, 6), replacement_entry.key);
    try std.testing.expectEqual(@as(usize, 3), replacement_entry.tag);
}
