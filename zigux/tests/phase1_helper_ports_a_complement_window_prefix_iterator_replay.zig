const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string_helpers = @import("string_helpers");
const rbtree = @import("rbtree");

test "lane06 replay keeps complement formatting inside the declared tail window" {
    const nbits = bitmap.bits_per_long + 5;
    const src = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        (bitmap.lastWordMask(nbits) &
            ~((@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3))) |
            (@as(bitmap.Word, 1) << 8) |
            (@as(bitmap.Word, 1) << 10),
    };
    var direct = [_]bitmap.Word{ 0, 0 };
    var alias_buffer: [64]u8 = undefined;
    var direct_buffer: [64]u8 = undefined;

    bitmap.complement(&direct, &src, nbits);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct[0]);
    try std.testing.expectEqual(
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3),
        direct[1],
    );

    const direct_len = bitmap.scnprintf(&direct, nbits, &direct_buffer);
    const alias_len = bitmap.bitmap_scnprintf(&direct, nbits, &alias_buffer);
    try std.testing.expectEqual(direct_len, alias_len);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d},{d}",
        .{ bitmap.bits_per_long + 1, bitmap.bits_per_long + 3 },
    );
    try std.testing.expectEqualStrings(expected_text, direct_buffer[0..direct_len]);
    try std.testing.expectEqualStrings(expected_text, alias_buffer[0..alias_len]);
}

test "lane06 replay keeps shared and zero tail windows aligned" {
    const nbits = find_bit.bits_per_long + 6;
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) &
            ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    const shared_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 9),
    };
    const shared_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << 4) |
            (@as(find_bit.Word, 1) << 10),
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 5),
    );

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findNextAndBit(&shared_lhs, &shared_rhs, nbits, find_bit.bits_per_long + 1),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextAndBit(&shared_lhs, &shared_rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextAndBit(&shared_lhs, &shared_rhs, nbits, find_bit.bits_per_long + 5),
    );
}

test "lane06 replay keeps prefix newline and dirty-byte boundaries stable" {
    try std.testing.expectEqual(
        @as(usize, 4),
        string_helpers.strHasPrefix(&[_]u8{ 'l', 'a', 'n', 'e', 0, 'x' }, "lane"),
    );
    try std.testing.expect(string_helpers.strstarts("lane-helper", "lane"));
    try std.testing.expect(string_helpers.strEndsWith(&[_]u8{ 'h', 'e', 'l', 'p', 'e', 'r', 0, 'x' }, "per"));
    try std.testing.expect(!string_helpers.strEndsWith("helper", "hers"));
    try std.testing.expect(string_helpers.sysfsStreq("lane\n", "lane"));

    const sysfs_values = [_][]const u8{ "off", "lane\n", "lane", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.sysfsMatchString(sysfs_values[0..], "lane"));

    const exact_values = [_][]const u8{
        &[_]u8{ 'l', 'a', 'n', 'e', 0, 'x' },
        "lane",
        "other",
    };
    try std.testing.expectEqual(@as(?usize, 0), string_helpers.matchString(exact_values[0..], "lane"));

    var backing = [_]u8{0} ** 32;
    backing[17] = 1;
    try std.testing.expectEqual(@as(?usize, 17), string_helpers.memchrInv(backing[0..], 0));
    try std.testing.expectEqual(@as(?usize, 17), string_helpers.memchr_inv(backing[0..], 0));
}

test "lane06 replay keeps cached duplicate iteration stable through leftmost handoff" {
    const Entry = struct {
        key: i32,
        serial: i32,
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
    var replacement = Entry{ .key = 15, .serial = 99 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    const promoted = rbtree.eraseCached(&entries[0].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[1].node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&entries[3].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    const key = @as(i32, 10);
    var iter = rbtree.matchIterator(&key, &root.root, cmp);
    var serials: [2]i32 = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 1, 2 }, serials[0..count]);
}
