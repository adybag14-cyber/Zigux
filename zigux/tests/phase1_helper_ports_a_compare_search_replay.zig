const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A compare/search replay keeps bitmap find_bit and string windows aligned" {
    const nbits = bitmap.bits_per_long + 6;

    const bitmap_lhs = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 9),
    };
    const bitmap_rhs = [_]bitmap.Word{
        0b1000,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 11),
    };
    var complement_direct = [_]bitmap.Word{ 0, 0 };
    var complement_alias = [_]bitmap.Word{ 0, 0 };

    bitmap.complement(&complement_direct, &bitmap_lhs, nbits);
    bitmap.bitmap_complement(&complement_alias, &bitmap_lhs, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &complement_direct, &complement_alias);
    try std.testing.expect(bitmap.intersects(&bitmap_lhs, &bitmap_rhs, nbits));
    try std.testing.expect(bitmap.subset(&bitmap_rhs, &bitmap_lhs, nbits));
    try std.testing.expect(!bitmap.equal(&bitmap_lhs, &bitmap_rhs, nbits));

    const set_map = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(find_bit.bits_per_long - 2),
        (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << 1) & ~(@as(find_bit.Word, 1) << 4),
    };
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long - 2),
        find_bit.findNextBit(&set_map, nbits, find_bit.bits_per_long - 3),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextBit(&set_map, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 5),
    );

    const embedded_nul = [_]u8{ 'a', 'b', 'c', 0, 't', 'a', 'i', 'l' };
    const haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expect(string.strEq(&embedded_nul, "abc"));
    try std.testing.expect(string.streq("alpha", "alpha"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 3), string.matchString(&[_][]const u8{ "red", "blue", "green", "gold" }, "gold"));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&embedded_nul, 7, 'c'));
}

test "phase1 helper ports A compare/search replay keeps ordered rbtree lookups and replacement stable" {
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
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 12 },
    };
    var replacement = Entry{ .key = 12 };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const wanted = @as(i32, 12);
    const found = rbtree.find(&wanted, &root, key_cmp) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(@as(i32, 12), found_entry.key);
    const missing = @as(i32, 11);
    try std.testing.expect(rbtree.find(&missing, &root, key_cmp) == null);

    const first = rbtree.first(&root) orelse return error.TestUnexpectedResult;
    const next = rbtree.next(first) orelse return error.TestUnexpectedResult;
    const last = rbtree.last(&root) orelse return error.TestUnexpectedResult;
    const prev = rbtree.prev(last) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(@as(i32, 5), (@as(*const Entry, @fieldParentPtr("node", first))).key);
    try std.testing.expectEqual(@as(i32, 10), (@as(*const Entry, @fieldParentPtr("node", next))).key);
    try std.testing.expectEqual(@as(i32, 15), (@as(*const Entry, @fieldParentPtr("node", last))).key);
    try std.testing.expectEqual(@as(i32, 12), (@as(*const Entry, @fieldParentPtr("node", prev))).key);
    try std.testing.expectEqual(first, rbtree.rb_first(&root));
    try std.testing.expectEqual(last, rbtree.rb_last(&root));
    try std.testing.expectEqual(next, rbtree.rb_next(first));
    try std.testing.expectEqual(prev, rbtree.rb_prev(last));

    rbtree.replaceNode(&entries[3].node, &replacement.node, &root);
    const replaced = rbtree.find(&wanted, &root, key_cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &replacement.node), replaced);

    rbtree.eraseInit(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var cursor = rbtree.first(&root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 10, 12, 15 }, order[0..count]);
}
