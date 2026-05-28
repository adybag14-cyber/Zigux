const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap complement keeps partial tail noise masked" {
    const nbits = bitmap.bits_per_long + 5;
    const src = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 7) | (@as(bitmap.Word, 1) << 10),
    };
    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };

    bitmap.complement(&direct, &src, nbits);
    bitmap.bitmap_complement(&alias, &src, nbits);

    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expectEqual(~@as(bitmap.Word, 0b1010), direct[0]);
    try std.testing.expectEqual((~src[1]) & bitmap.lastWordMask(nbits), direct[1]);
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 2), bitmap.weight(&direct, nbits));
}

test "phase1 helper ports A tail scans keep shared and unique in-range bits visible" {
    const nbits = find_bit.bits_per_long + 6;
    const shared_bit = @as(find_bit.Word, 1) << 4;
    const unique_bit = @as(find_bit.Word, 1) << 2;
    const out_of_range_noise = @as(find_bit.Word, 1) << 9;
    const lhs = [_]find_bit.Word{ 0, shared_bit | unique_bit | out_of_range_noise };
    const rhs = [_]find_bit.Word{ 0, shared_bit | out_of_range_noise };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findFirstAndBit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 2),
        find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findLastBit(&rhs, nbits),
    );

    var clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.findFirstClump8(&clump, &lhs, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0b0001_0100), clump);
}

test "phase1 helper ports A string catalog helpers preserve first matches and early dirty bytes" {
    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));

    const exact_haystack = [_][]const u8{
        &[_]u8{ 'a', 0, 'x' },
        "beta",
        "alpha",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(exact_haystack[0..], "a"));

    var dirty = [_]u8{0} ** 24;
    dirty[17] = 5;
    try std.testing.expectEqual(@as(?usize, 17), string.memchrInv(dirty[0..], 0));
}

test "phase1 helper ports A duplicate iterators keep match traversal ordered" {
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
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = @as(i32, 10);
    const first_match = rbtree.findFirst(&duplicate, &root, cmp) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_entry.serial);

    var via_next_match: [3]usize = undefined;
    var count: usize = 0;
    var cursor = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", cursor);
        via_next_match[count] = entry.serial;
        count += 1;
        cursor = rbtree.nextMatch(&duplicate, cursor, cmp) orelse break;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, via_next_match[0..count]);

    var iter = rbtree.matchIterator(&duplicate, &root, cmp);
    var via_iter: [3]usize = undefined;
    var iter_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        via_iter[iter_count] = entry.serial;
        iter_count += 1;
    }

    try std.testing.expectEqual(count, iter_count);
    try std.testing.expectEqualSlices(usize, via_next_match[0..count], via_iter[0..iter_count]);
}
