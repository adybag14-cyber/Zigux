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

fn entryOf(node: *const rbtree.Node) *const Entry {
    return @fieldParentPtr("node", node);
}

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry = entryOf(lhs);
    const rhs_entry = entryOf(rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry = entryOf(node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "phase1 helper ports A mask-dirty-postorder replay keeps masked bitmap replacements tail-clamped" {
    const nbits = bitmap.bits_per_long + 6;
    const old = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 8),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 11),
    };
    const new = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 5) | (@as(bitmap.Word, 1) << 8),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 5) | (@as(bitmap.Word, 1) << 13),
    };
    const mask = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 5),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 5) | (@as(bitmap.Word, 1) << 12),
    };

    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };
    bitmap.replace(direct[0..], old[0..], new[0..], mask[0..], nbits);
    bitmap.bitmap_replace(alias[0..], old[0..], new[0..], mask[0..], nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);

    const expected = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 5) | (@as(bitmap.Word, 1) << 8),
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 5),
    };
    try std.testing.expectEqualSlices(bitmap.Word, &expected, &direct);

    const noisy_equal = [_]bitmap.Word{
        expected[0],
        expected[1] | (@as(bitmap.Word, 1) << 11),
    };
    try std.testing.expect(bitmap.equal(direct[0..], noisy_equal[0..], nbits));
    try std.testing.expect(bitmap.bitmap_equal(direct[0..], noisy_equal[0..], nbits));

    const probe = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 5) | (@as(bitmap.Word, 1) << 14),
    };
    try std.testing.expect(bitmap.intersects(direct[0..], probe[0..], nbits));
    try std.testing.expect(bitmap.bitmap_intersects(direct[0..], probe[0..], nbits));
    try std.testing.expect(bitmap.subset(probe[0..], direct[0..], nbits));
    try std.testing.expect(bitmap.bitmap_subset(probe[0..], direct[0..], nbits));
}

test "phase1 helper ports A mask-dirty-postorder replay keeps zero and shared find-bit windows aligned" {
    const nbits = find_bit.bits_per_long + 10;
    const map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        (@as(find_bit.Word, 1) << 0) |
            (@as(find_bit.Word, 1) << 3) |
            (@as(find_bit.Word, 1) << 8) |
            (@as(find_bit.Word, 1) << 17),
    };
    const peer = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) |
            (@as(find_bit.Word, 1) << 8) |
            (@as(find_bit.Word, 1) << 19),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findFirstZeroBit(map[0..], nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.find_first_zero_bit(map[0..], nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextZeroBit(map[0..], nbits, find_bit.bits_per_long + 4));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(map[0..], nbits, nbits));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 3), find_bit.findFirstAndBit(map[0..], peer[0..], nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.findNextAndBit(map[0..], peer[0..], nbits, find_bit.bits_per_long + 4));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(map[0..], peer[0..], nbits, find_bit.bits_per_long + 9));

    try std.testing.expectEqual(@as(u8, 0b0000_1001), find_bit.getValue8(map[0..], find_bit.bits_per_long));
}

test "phase1 helper ports A mask-dirty-postorder replay keeps dirty-byte scans distinct from sysfs matching" {
    var dirty = [_]u8{0} ** 32;
    dirty[23] = 7;
    try std.testing.expectEqual(@as(?usize, 23), string.memchrInv(dirty[0..], 0));
    try std.testing.expectEqual(@as(?usize, 23), string.memchr_inv(dirty[0..], 0));

    const sysfs_choices = [_][]const u8{ "mode\n", "model", "mode", "safe" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(sysfs_choices[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(sysfs_choices[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 2), string.matchString(sysfs_choices[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(sysfs_choices[0..], "mode"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_choices[0..], "model"));
}

test "phase1 helper ports A mask-dirty-postorder replay keeps duplicate-first and reverse postorder traversal stable" {
    var duplicate_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 12, .serial = 3 },
        .{ .key = 15, .serial = 4 },
    };
    var duplicate_root = rbtree.Root.init();
    for (&duplicate_entries) |*entry| {
        rbtree.add(&entry.node, &duplicate_root, entryLess);
    }

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &duplicate_root, keyCmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), entryOf(first_match).serial);

    var reverse_serials: [5]usize = undefined;
    var reverse_count: usize = 0;
    var current = rbtree.rb_last(&duplicate_root);
    while (current) |node| : (current = rbtree.rb_prev(node)) {
        reverse_serials[reverse_count] = entryOf(node).serial;
        reverse_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 5), reverse_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 4, 3, 2, 0, 1 }, reverse_serials[0..reverse_count]);

    var postorder_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
        .{ .key = 12, .serial = 3 },
    };
    var postorder_root = rbtree.Root.init();
    for (&postorder_entries) |*entry| {
        rbtree.add(&entry.node, &postorder_root, entryLess);
    }

    var postorder_keys: [4]i32 = undefined;
    var postorder_count: usize = 0;
    var post = rbtree.rb_first_postorder(&postorder_root);
    while (post) |node| : (post = rbtree.rb_next_postorder(node)) {
        postorder_keys[postorder_count] = entryOf(node).key;
        postorder_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 4), postorder_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 5, 12, 15, 10 }, postorder_keys[0..postorder_count]);
}
