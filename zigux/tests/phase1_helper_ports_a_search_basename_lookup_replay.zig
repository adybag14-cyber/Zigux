const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap logical aliases ignore spare storage outside the declared window" {
    const nbits = bitmap.bits_per_long;
    const lhs = [_]bitmap.Word{ 0b1011, @as(bitmap.Word, 1) << 6 };
    const rhs = [_]bitmap.Word{ 0b1011, @as(bitmap.Word, 1) << 12 };
    var buffer = [_]u8{0xaa} ** 16;

    try std.testing.expect(bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&lhs, &rhs, nbits));

    const len = bitmap.bitmap_scnprintf(&lhs, nbits, &buffer);
    try std.testing.expectEqualStrings("0-1,3", buffer[0..len]);
    try std.testing.expectEqual(@as(u8, 0), buffer[len]);
}

test "phase1 helper ports A find_bit shared and tail lookups stay clamped" {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 11) };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.find_first_and_bit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.find_next_and_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.find_last_bit(&lhs, nbits),
    );

    var clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.find_first_clump8(&clump, &lhs, nbits),
    );
    try std.testing.expectEqual(@as(u8, 0b0001_0010), clump);
}

test "phase1 helper ports A string copy and sysfs helpers honor C-string edges" {
    var padded = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    var spaced = [_]u8{ ' ', 'x', ' ', 'y', ' ', 0, 'z' };

    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0 }, &padded);
    try std.testing.expectEqualStrings("x y", string.trimSpaces(&spaced));
    try std.testing.expectEqual(@as(?usize, 2), string.memchrInv(&[_]u8{ 'q', 'q', 'r', 'q' }, 'q'));
    try std.testing.expect(string.streq(&[_]u8{ 'm', 'o', 'd', 'e', 0, 'x' }, "mode"));
    try std.testing.expect(string.sysfs_streq("mode\n", "mode"));
}

test "phase1 helper ports A rbtree plain-root lookup and replacement stay ordered" {
    const Entry = struct {
        key: i32,
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

    const cmpNode = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 20 },
        .{ .key = 15 },
    };
    var duplicate_probe = Entry{ .key = 15 };
    var inserted_probe = Entry{ .key = 12 };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const wanted = @as(i32, 15);
    const found = rbtree.find(&wanted, &root, cmp) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(i32, 15), found_entry.key);

    const duplicate = rbtree.findAdd(&duplicate_probe.node, &root, cmpNode) orelse return error.TestUnexpectedResult;
    const duplicate_entry: *const Entry = @fieldParentPtr("node", duplicate);
    try std.testing.expectEqual(@as(i32, 15), duplicate_entry.key);

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAdd(&inserted_probe.node, &root, cmpNode));
    const found_inserted = rbtree.find(&inserted_probe.key, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &inserted_probe.node), found_inserted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.rb_last(&root));

    rbtree.eraseInit(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expect(rbtree.find(&entries[1].key, &root, cmp) == null);

    var reverse_order: [4]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.rb_last(&root);
    while (current) |node| : (current = rbtree.rb_prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        reverse_order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 20, 15, 12, 10 }, reverse_order[0..count]);
}
