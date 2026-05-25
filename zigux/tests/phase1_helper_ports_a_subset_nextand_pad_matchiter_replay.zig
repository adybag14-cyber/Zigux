const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap subset checks masked to the declared tail window" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;

    const subset_lhs = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 8),
    };
    const subset_rhs = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | (@as(Word, 1) << 10),
    };
    const not_subset = [_]Word{
        0,
        (@as(Word, 1) << 1) | (@as(Word, 1) << 2),
    };

    try std.testing.expect(bitmap.subset(&subset_lhs, &subset_rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&subset_lhs, &subset_rhs, nbits));
    try std.testing.expect(!bitmap.subset(&subset_rhs, &subset_lhs, nbits));
    try std.testing.expect(!bitmap.bitmap_subset(&not_subset, &subset_lhs, nbits));
}

test "lane06 replay keeps next-and scans inside the declared tail window" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]Word{
        (@as(Word, 1) << 2) | (@as(Word, 1) << 6),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4) | (@as(Word, 1) << 7),
    };
    const rhs = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 6),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 4),
    };

    try std.testing.expectEqual(@as(usize, 6), find_bit.findNextAndBit(&lhs, &rhs, nbits, 3));
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findNextAndBit(&lhs, &rhs, nbits, 7),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5));
}

test "lane06 replay keeps string padding helpers aligned on embedded-nul sources" {
    var copied = [_]u8{ 9, 9, 9, 9, 9, 9 };
    var alias = [_]u8{ 7, 7, 7, 7, 7, 7 };
    try std.testing.expectEqual(
        @as(isize, 2),
        string.strscpyPad(copied[0..], &[_]u8{ 'o', 'k', 0, 'x', 'x' }),
    );
    try std.testing.expectEqual(
        @as(isize, 2),
        string.strscpy_pad(alias[0..], &[_]u8{ 'o', 'k', 0, 'x', 'x' }),
    );
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, copied[0..]);
    try std.testing.expectEqualSlices(u8, copied[0..], alias[0..]);
}

test "lane06 replay keeps duplicate match iteration ordered across public entry points" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
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
        .{ .key = 7, .serial = 0 },
        .{ .key = 7, .serial = 1 },
        .{ .key = 7, .serial = 2 },
        .{ .key = 9, .serial = 0 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = @as(i32, 7);

    var primary_iter = rbtree.matchIterator(&duplicate, &root, key_cmp);
    var primary_serials: [3]usize = undefined;
    var secondary_serials: [3]usize = undefined;
    var count: usize = 0;

    while (primary_iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        primary_serials[count] = entry.serial;
        count += 1;
    }

    var secondary_count: usize = 0;
    var current = rbtree.findFirst(&duplicate, &root, key_cmp);
    while (current) |node| : (current = rbtree.nextMatch(&duplicate, node, key_cmp)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        secondary_serials[secondary_count] = entry.serial;
        secondary_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqual(count, secondary_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 1, 2 }, primary_serials[0..count]);
    try std.testing.expectEqualSlices(usize, primary_serials[0..count], secondary_serials[0..secondary_count]);
}
