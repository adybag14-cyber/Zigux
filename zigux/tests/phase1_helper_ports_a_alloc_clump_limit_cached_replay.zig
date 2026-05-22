const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap alloc extend and logical replay" {
    const allocator = std.testing.allocator;
    const count = bitmap.bits_per_long + 3;
    const size = bitmap.bits_per_long * 2 + 5;

    var src = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&src, 1, 2);
    bitmap.setRange(&src, bitmap.bits_per_long + 1, 2);
    src[1] |= @as(bitmap.Word, 1) << 12;

    var direct = try bitmap.bitmap_zalloc(allocator, size);
    defer bitmap.bitmap_free(allocator, &direct);
    var alias: ?[]bitmap.Word = try bitmap.bitmap_alloc(allocator, size);
    defer bitmap.bitmap_free(allocator, &alias);
    bitmap.bitmap_zero(alias.?, size);
    bitmap.copyAndExtend(direct.?, &src, count, size);
    bitmap.bitmap_copy_and_extend(alias.?, &src, count, size);

    try std.testing.expectEqualSlices(bitmap.Word, direct.?, alias.?);
    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(size)), direct.?.len);
    try std.testing.expect(bitmap.subset(direct.?, alias.?, size));
    try std.testing.expectEqual(@as(usize, 4), bitmap.weight(direct.?, size));
    try std.testing.expect(bitmap.intersects(direct.?, &[_]bitmap.Word{ 0b10, @as(bitmap.Word, 1) << 2, 0 }, size));
}

test "phase1 helper ports A find_bit clump limit and alias replay" {
    const nbits = find_bit.bits_per_long + 12;
    const boundary = find_bit.bits_per_long;
    const words = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 7) | (@as(find_bit.Word, 1) << 14),
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 10),
    };
    const gate = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 14,
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 10),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.find_first_clump8(&clump, &words, nbits));
    try std.testing.expectEqual(@as(u8, 0b1000_0000), clump);
    try std.testing.expectEqual(@as(usize, 8), find_bit.find_next_clump8(&clump, &words, nbits, 8));
    try std.testing.expectEqual(@as(u8, 0b0100_0000), clump);
    try std.testing.expectEqual(@as(usize, boundary + 2), find_bit.find_next_and_bit(&words, &gate, nbits, 15));
    try std.testing.expectEqual(@as(usize, boundary + 2), find_bit._find_next_and_bit(&words, &gate, nbits, 15));

    var untouched: u8 = 0x6d;
    try std.testing.expectEqual(nbits, find_bit.findNextClump8(&untouched, &words, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x6d), untouched);
    try std.testing.expectEqual(@as(usize, boundary + 10), find_bit.find_last_bit(&words, nbits));
}

test "phase1 helper ports A string compare search and sysfs-limit replay" {
    try std.testing.expect(string.sysfsStreq("mode\n", "mode"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&[_][]const u8{ "off", "mode\n", "mode" }, "mode"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(&[_][]const u8{ "off", "mode\n", "mode" }, "mode"));

    try std.testing.expectEqual(@as(usize, 4), string.strHasPrefix("mode-select", "mode"));
    try std.testing.expect(string.strstarts("mode-select", "mode"));
    try std.testing.expect(string.strEndsWith("mode-select", "select"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(&[_][]const u8{ "mode", "select" }, "mode"));

    var bytes = [_]u8{'x'} ** 24;
    bytes[17] = 'y';
    try std.testing.expectEqual(@as(?usize, 17), string.memchr_inv(bytes[0..], 'x'));
}

test "phase1 helper ports A rbtree cached duplicate and detach replay" {
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

    const cmp = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    var first_entry = Entry{ .key = 10, .serial = 0 };
    var leftmost_entry = Entry{ .key = 5, .serial = 1 };
    var duplicate_entry = Entry{ .key = 10, .serial = 2 };
    var larger_entry = Entry{ .key = 15, .serial = 3 };
    var replacement = Entry{ .key = 15, .serial = 4 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.rb_add_cached(&first_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&leftmost_entry.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&larger_entry.node, &root, cmp));
    const duplicate = rbtree.rb_find_add_cached(&duplicate_entry.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &first_entry.node), duplicate);
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost_entry.node), rbtree.rb_first_cached(&root));

    rbtree.rb_replace_node_cached(&larger_entry.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(*rbtree.Node, &replacement.node), rbtree.rb_last(&root.root).?);
    rbtree.rb_erase_init_cached(&leftmost_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&leftmost_entry.node));
    try std.testing.expectEqual(rbtree.rb_first(&root.root), rbtree.rb_first_cached(&root));
}
