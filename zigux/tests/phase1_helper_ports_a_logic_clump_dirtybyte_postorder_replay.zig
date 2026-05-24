const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "lane06 replay keeps bitmap logical aliases aligned across masked tails" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{ 0b1110, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };
    const rhs = [_]bitmap.Word{ 0b1010, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 11) };
    const superset = [_]bitmap.Word{ lhs[0], lhs[1] | (@as(bitmap.Word, 1) << 4) };

    var direct_and = [_]bitmap.Word{ 0, 0 };
    var alias_and = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.andBits(&direct_and, &lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_and(&alias_and, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &direct_and, &alias_and);
    try std.testing.expectEqualSlices(bitmap.Word, &[_]bitmap.Word{ 0b1010, @as(bitmap.Word, 1) << 3 }, &direct_and);

    var direct_andnot = [_]bitmap.Word{ 0, 0 };
    var alias_andnot = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&direct_andnot, &lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_andnot(&alias_andnot, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &direct_andnot, &alias_andnot);
    try std.testing.expectEqualSlices(bitmap.Word, &[_]bitmap.Word{ 0b0100, @as(bitmap.Word, 1) << 1 }, &direct_andnot);

    try std.testing.expect(bitmap.intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.subset(&lhs, &superset, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&lhs, &superset, nbits));
    try std.testing.expect(bitmap.equal(&lhs, &lhs, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&lhs, &lhs, nbits));
}

test "lane06 replay keeps find_bit clump and boundary helpers alias-aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 8) };
    const shared_lhs = [_]find_bit.Word{ (@as(find_bit.Word, 1) << 7), (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 4) };
    const shared_rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 7) };
    const subtract_rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 2 };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findFirstClump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.find_next_clump8(&clump, &map, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&clump, &map, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0), clump);

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findFirstAndBit(&shared_lhs, &shared_rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit._find_next_and_bit(&shared_lhs, &shared_rhs, nbits, find_bit.bits_per_long + 3));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findFirstAndNotBit(&shared_lhs, &subtract_rhs, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_andnot_bit(&shared_lhs, &shared_rhs, nbits, find_bit.bits_per_long + 5));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findLastBit(&shared_rhs, nbits));
}

test "lane06 replay keeps string dirty-byte and newline-aware helpers aligned" {
    var direct = [_]u8{ 9, 9, 9, 9, 9 };
    var alias = [_]u8{ 9, 9, 9, 9, 9 };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(direct[0..], &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(alias[0..], &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &direct, &alias);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0 }, &direct);

    var long_buf = [_]u8{0} ** 24;
    long_buf[17] = 3;
    try std.testing.expectEqual(@as(?usize, 17), string.memchrInv(long_buf[0..], 0));
    try std.testing.expectEqual(@as(?usize, 17), string.memchr_inv(long_buf[0..], 0));

    const modes = [_][]const u8{ "off", "auto\n", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(modes[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(modes[0..], "auto"));

    const names = [_][]const u8{ &[_]u8{ 'a', 0, 'x' }, "beta", "gamma" };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(names[0..], "a"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(names[0..], "beta"));
}

test "lane06 replay keeps rbtree iterator and postorder helpers aligned" {
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 15, .serial = 3 },
        .{ .key = 10, .serial = 4 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = @as(i32, 10);
    var iter = rbtree.matchIterator(&duplicate, &root, keyCmp);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);

    var primary_count: usize = 0;
    var primary = rbtree.firstPostorder(&root);
    while (primary) |node| : (primary = rbtree.nextPostorder(node)) {
        primary_count += 1;
    }

    var alias_count: usize = 0;
    var alias = rbtree.rb_first_postorder(&root);
    while (alias) |node| : (alias = rbtree.rb_next_postorder(node)) {
        alias_count += 1;
    }

    try std.testing.expectEqual(@as(usize, entries.len), primary_count);
    try std.testing.expectEqual(primary_count, alias_count);
}
