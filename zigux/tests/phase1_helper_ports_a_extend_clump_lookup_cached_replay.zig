const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "phase1 helper ports A replay keeps bitmap extend tail masks and extension words stable" {
    const count = bitmap.bits_per_long + 5;
    const size = bitmap.bits_per_long * 3;
    const src = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0), 0x0123_4567_89ab_cdef };
    const expected = [_]bitmap.Word{ ~@as(bitmap.Word, 0), bitmap.lastWordMask(count), 0 };
    var dst = [_]bitmap.Word{ 0x55aa, 0x55aa, 0x55aa };

    bitmap.copyAndExtend(dst[0..3], src[0..2], count, size);

    try std.testing.expectEqualSlices(bitmap.Word, &expected, &dst);
    try std.testing.expect(bitmap.equal(&dst, &expected, size));
    try std.testing.expect(bitmap.subset(&dst, &expected, size));
    try std.testing.expect(bitmap.intersects(&dst, &expected, count));
    try std.testing.expectEqual(@as(usize, count), bitmap.weight(&dst, size));
}

test "phase1 helper ports A replay keeps find_bit tail clumps and last-bit ownership aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const bitmap_words = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) };

    var clump: u8 = 0xaa;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &bitmap_words, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findLastBit(&bitmap_words, nbits));

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &bitmap_words, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "phase1 helper ports A replay keeps string sysfs and moving-dirty ownership explicit" {
    const values = [_][]const u8{ "off", "auto\n", "auto", "on" };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&values, "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&values, "auto"));
    try std.testing.expectEqual(@as(?usize, null), string.matchString(&[_][]const u8{ "alpha", "beta" }, "gamma"));

    var moving_dirty = [_]u8{'a'} ** 32;
    moving_dirty[21] = 'b';
    try std.testing.expectEqual(@as(?usize, 21), string.memchrInv(&moving_dirty, 'a'));
    moving_dirty[7] = 'c';
    try std.testing.expectEqual(@as(?usize, 7), string.memchrInv(&moving_dirty, 'a'));
}

test "phase1 helper ports A replay keeps rbtree cached leftmost and duplicate iteration aligned after erase" {
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

    const cmp_key = struct {
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
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 15, .serial = 3 },
        .{ .key = 10, .serial = 4 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &root.root, cmp_key) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_match_entry.serial);

    var next_serials: [3]usize = undefined;
    var next_count: usize = 0;
    var cursor = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", cursor);
        next_serials[next_count] = entry.serial;
        next_count += 1;
        cursor = rbtree.nextMatch(&wanted, cursor, cmp_key) orelse break;
    }
    try std.testing.expectEqual(@as(usize, 3), next_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, next_serials[0..next_count]);

    const promoted = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    var iter = rbtree.matchIterator(&wanted, &root.root, cmp_key);
    var iter_serials: [3]usize = undefined;
    var iter_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        iter_serials[iter_count] = entry.serial;
        iter_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), iter_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, iter_serials[0..iter_count]);
}
