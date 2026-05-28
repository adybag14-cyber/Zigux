const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap copyAndExtend keeps tail clearing and overlap helpers aligned" {
    const count = bitmap.bits_per_long + 5;
    const size = bitmap.bits_per_long * 3;
    const src = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 7),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 8),
        ~@as(bitmap.Word, 0),
    };
    const expected = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 7),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4),
        0,
    };
    const overlap = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 4),
        0,
    };

    var direct = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    var alias = [_]bitmap.Word{ 0, 1, 2 };
    bitmap.copyAndExtend(&direct, src[0..2], count, size);
    bitmap.bitmap_copy_and_extend(&alias, src[0..2], count, size);

    try std.testing.expectEqualSlices(bitmap.Word, &expected, &direct);
    try std.testing.expectEqualSlices(bitmap.Word, &expected, &alias);
    try std.testing.expect(bitmap.equal(&direct, &alias, size));
    try std.testing.expect(bitmap.subset(&overlap, &direct, size));
    try std.testing.expect(bitmap.intersects(&direct, &overlap, size));
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct[1] & ~bitmap.lastWordMask(count));
}

test "phase1 helper ports A find_bit clump and last scans keep the aligned byte visible" {
    const nbits = find_bit.bits_per_long + 8;
    const bitmap_words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 5),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &bitmap_words, nbits));
    try std.testing.expectEqual(@as(u8, 0b0010_0001), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&clump, &bitmap_words, nbits, find_bit.bits_per_long + 4));
    try std.testing.expectEqual(@as(u8, 0b0010_0001), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.findLastBit(&bitmap_words, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 5), find_bit.find_last_bit(&bitmap_words, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&bitmap_words, nbits, nbits));
}

test "phase1 helper ports A string padding and catalog helpers keep matches and zero tails stable" {
    var padded = [_]u8{ 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, 0x11, 0x22 };
    const source = [_]u8{ 'z', 'i', 'g', 0, 'x', 'x' };
    const sysfs_modes = [_][]const u8{ "manual\n", "auto", "auto\n" };
    const catalog = [_][]const u8{
        &[_]u8{ 'z', 'i', 'g', 0, 'x' },
        "zigux",
        "tools",
    };

    try std.testing.expectEqual(@as(isize, 3), string.strscpyPad(&padded, &source));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 0, 0, 0, 0, 0 }, &padded);
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(padded[3..], 0));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_modes[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(sysfs_modes[0..], "auto\n"));
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(catalog[0..], "zig"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(catalog[0..], "zigux"));
}

test "phase1 helper ports A cached duplicates keep iterator order and promoted leftmost stable" {
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

    const cmp_key = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var leftmost = Entry{ .key = 3, .serial = 0 };
    var first_duplicate = Entry{ .key = 7, .serial = 1 };
    var second_duplicate = Entry{ .key = 7, .serial = 2 };
    var right = Entry{ .key = 9, .serial = 3 };
    var root = rbtree.RootCached.init();
    const needle: i32 = 7;

    _ = rbtree.addCached(&first_duplicate.node, &root, less);
    _ = rbtree.addCached(&leftmost.node, &root, less);
    _ = rbtree.addCached(&second_duplicate.node, &root, less);
    _ = rbtree.addCached(&right.node, &root, less);

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    var iter = rbtree.matchIterator(&needle, &root.root, cmp_key);
    const first_match = iter.next() orelse return error.TestUnexpectedResult;
    const second_match = iter.next() orelse return error.TestUnexpectedResult;
    try std.testing.expect(iter.next() == null);
    try std.testing.expectEqual(@as(*rbtree.Node, &first_duplicate.node), first_match);
    try std.testing.expectEqual(@as(*rbtree.Node, &second_duplicate.node), second_match);

    const promoted = rbtree.eraseCached(&leftmost.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &first_duplicate.node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_duplicate.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
