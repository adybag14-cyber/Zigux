const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string_helpers = @import("string_helpers");
const rbtree = @import("rbtree");

test "lane06 replay keeps partial fills copy-clear subsets and zero extension aligned" {
    const nbits = bitmap.bits_per_long + 6;
    const size = bitmap.bits_per_long * 3;

    var filled = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.fill(&filled, nbits);

    try std.testing.expectEqual(~@as(bitmap.Word, 0), filled[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(nbits), filled[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), filled[2]);

    var cleared_tail = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.copyClearTail(cleared_tail[0..2], filled[0..2], nbits);
    try std.testing.expect(bitmap.subset(cleared_tail[0..2], filled[0..2], nbits));
    try std.testing.expectEqualSlices(bitmap.Word, filled[0..2], cleared_tail[0..2]);

    var extended = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
    };
    bitmap.copyAndExtend(&extended, filled[0..2], nbits, size);

    try std.testing.expect(bitmap.subset(cleared_tail[0..2], extended[0..2], nbits));
    try std.testing.expectEqual(filled[0], extended[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(nbits), extended[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), extended[2]);
}

test "lane06 replay keeps last-bit and tail clump windows in sync" {
    const nbits = find_bit.bits_per_long + 6;
    const bitmap_words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 5) |
            (@as(find_bit.Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.findLastBit(&bitmap_words, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &bitmap_words, nbits));
    try std.testing.expectEqual(@as(u8, 0b0010_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&clump, &bitmap_words, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(u8, 0b0010_0010), clump);

    clump = 0x7c;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &bitmap_words, nbits, find_bit.bits_per_long + 6));
    try std.testing.expectEqual(@as(u8, 0x7c), clump);
}

test "lane06 replay keeps padded strings and newline-aware sysfs matches stable" {
    var padded = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 4), string_helpers.strscpyPad(&padded, "lane"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'l', 'a', 'n', 'e', 0, 0 }, &padded);

    const sysfs_values = [_][]const u8{ "off", "lane\n", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.sysfsMatchString(sysfs_values[0..], "lane"));
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.sysfs_match_string(sysfs_values[0..], "lane"));

    const exact_values = [_][]const u8{ "left", "lane", "right" };
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.matchString(exact_values[0..], "lane"));
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.match_string(exact_values[0..], "lane"));
}

test "lane06 replay keeps cached duplicate handoff stable through erase-init and replacement" {
    const Entry = struct {
        key: i32,
        serial: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    const cmp = struct {
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
        .{ .key = 15, .serial = 3 },
    };
    var replacement = Entry{ .key = 10, .serial = 99 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    const key = @as(i32, 10);
    var before_iter = rbtree.matchIterator(&key, &root.root, cmp);
    var before_serials: [2]i32 = undefined;
    var before_count: usize = 0;
    while (before_iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        before_serials[before_count] = entry.serial;
        before_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), before_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 2 }, before_serials[0..before_count]);

    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));

    var after_iter = rbtree.matchIterator(&key, &root.root, cmp);
    var after_serials: [2]i32 = undefined;
    var after_count: usize = 0;
    while (after_iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        after_serials[after_count] = entry.serial;
        after_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 2), after_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 99, 2 }, after_serials[0..after_count]);
}
