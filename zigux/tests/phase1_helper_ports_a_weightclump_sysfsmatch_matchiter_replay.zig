const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap tail weights and range formatting aligned" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 8) };
    const rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    var dst = [_]Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 3), bitmap.weightedOr(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.weight(&dst, nbits));
    var andnot_dst = [_]Word{ 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&andnot_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 1), bitmap.weight(&andnot_dst, nbits));

    var fmt_map = [_]Word{ 0, 0 };
    bitmap.setRange(&fmt_map, bitmap.bits_per_long + 1, 1);
    bitmap.setRange(&fmt_map, bitmap.bits_per_long + 3, 2);

    var buffer: [64]u8 = undefined;
    const len = bitmap.scnprintf(&fmt_map, nbits, &buffer);

    var expected: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "{d},{d}-{d}",
        .{ bitmap.bits_per_long + 1, bitmap.bits_per_long + 3, bitmap.bits_per_long + 4 },
    );
    try std.testing.expectEqualStrings(expected_text, buffer[0..len]);
}

test "lane06 replay keeps find_bit clumps and andnot scans aligned at boundaries" {
    const Word = find_bit.Word;
    const nbits = find_bit.bits_per_long + 5;
    const andnot_lhs = [_]Word{
        @as(Word, 1) << @intCast(find_bit.bits_per_long - 1),
        (@as(Word, 1) << 1) | (@as(Word, 1) << 8),
    };
    const andnot_rhs = [_]Word{
        0,
        @as(Word, 1) << 9,
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 5),
    );

    const clump_map = [_]Word{ 0, @as(Word, 1) << 3 };
    var clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findFirstClump8(&clump, &clump_map, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);
}

test "lane06 replay keeps string sysfs and bounded search helpers aligned" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    const exact_haystack = [_][]const u8{ "off", "auto", "on" };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(exact_haystack[0..], "auto"));
    try std.testing.expect(string.sysfsStreq("auto\n", "auto"));
    try std.testing.expect(string.streq(&[_]u8{ 'a', 'u', 't', 'o', 0, 'x' }, "auto"));
}

test "lane06 replay keeps rbtree duplicate iterators in insertion order" {
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
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = @as(i32, 10);
    var iter = rbtree.matchIterator(&duplicate, &root, cmp);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);
}
