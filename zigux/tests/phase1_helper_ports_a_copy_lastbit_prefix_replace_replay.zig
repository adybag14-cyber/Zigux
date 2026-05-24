const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase 1 helper ports A replay keeps bitmap copy aliases aligned across tail clearing and extension" {
    const nbits = find_bit.bits_per_long + 5;
    const count = find_bit.bits_per_long + 3;
    const size = find_bit.bits_per_long * 3;
    const src = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        (~@as(bitmap.Word, 0)) ^ (@as(bitmap.Word, 1) << 2),
        0,
    };

    var direct_copy = [_]bitmap.Word{ 0xaa55, 0xbb66, 0xcc77 };
    var alias_copy = [_]bitmap.Word{ 0xaa55, 0xbb66, 0xcc77 };
    bitmap.copy(&direct_copy, src[0..2], nbits);
    bitmap.bitmap_copy(&alias_copy, src[0..2], nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_copy, &alias_copy);

    var direct_tail = [_]bitmap.Word{ 0, 0, 0 };
    var alias_tail = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.copyClearTail(&direct_tail, src[0..2], count);
    bitmap.bitmap_copy_clear_tail(&alias_tail, src[0..2], count);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_tail, &alias_tail);

    var direct_extend = [_]bitmap.Word{ 0x1357, 0x2468, 0x369c };
    var alias_extend = [_]bitmap.Word{ 0x1357, 0x2468, 0x369c };
    bitmap.copyAndExtend(&direct_extend, src[0..2], count, size);
    bitmap.bitmap_copy_and_extend(&alias_extend, src[0..2], count, size);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_extend, &alias_extend);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct_extend[2]);
}

test "phase 1 helper ports A replay keeps find_bit alias scans aligned across partial tails and last-bit windows" {
    const nbits = find_bit.bits_per_long + 5;
    const set_map = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 5) | (@as(find_bit.Word, 1) << 11),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };
    const zero_map = [_]find_bit.Word{
        ~(@as(find_bit.Word, 1) << 6),
        find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << 3),
    };
    const and_lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 5) | (@as(find_bit.Word, 1) << 12),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4),
    };
    const and_rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 12,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4),
    };

    try std.testing.expectEqual(find_bit.findFirstBit(&set_map, nbits), find_bit.find_first_bit(&set_map, nbits));
    try std.testing.expectEqual(find_bit.findNextBit(&set_map, nbits, 6), find_bit.find_next_bit(&set_map, nbits, 6));
    try std.testing.expectEqual(find_bit.findFirstZeroBit(&zero_map, nbits), find_bit.find_first_zero_bit(&zero_map, nbits));
    try std.testing.expectEqual(find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long), find_bit.find_next_zero_bit(&zero_map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(find_bit.findFirstAndBit(&and_lhs, &and_rhs, nbits), find_bit.find_first_and_bit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long), find_bit.find_next_and_bit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(find_bit.findFirstAndNotBit(&and_lhs, &and_rhs, nbits), find_bit.find_first_andnot_bit(&and_lhs, &and_rhs, nbits));
    try std.testing.expectEqual(find_bit.findNextAndNotBit(&and_lhs, &and_rhs, nbits, 6), find_bit.find_next_andnot_bit(&and_lhs, &and_rhs, nbits, 6));
    try std.testing.expectEqual(find_bit.findLastBit(&set_map, nbits), find_bit.find_last_bit(&set_map, nbits));
    try std.testing.expectEqual(find_bit.findLastBit(&set_map, nbits), find_bit._find_last_bit(&set_map, nbits));

    var clump_direct: u8 = 0;
    var clump_alias: u8 = 0;
    const clump_map = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 3 };
    try std.testing.expectEqual(find_bit.findFirstClump8(&clump_direct, &clump_map, nbits), find_bit.find_first_clump8(&clump_alias, &clump_map, nbits));
    try std.testing.expectEqual(clump_direct, clump_alias);
}

test "phase 1 helper ports A replay keeps string prefix and search aliases aligned on C-string boundaries" {
    const prefix_cstr = [_]u8{ 'k', 'e', 'r', 'n', 'e', 'l', 0, 'x' };
    const spaced = [_]u8{ ' ', '\t', 'l', 'e', 'a', 'd', 0 };
    const newline_cstr = [_]u8{ 'm', 'o', 'd', 'e', '\n', 0 };
    const match_haystack = [_][]const u8{ "alpha", "mode\n", "mode", "beta" };
    const cstr_haystack = [_][]const u8{ &[_]u8{ 'a', 0, 'x' }, "beta" };

    try std.testing.expectEqual(string.strHasPrefix(&prefix_cstr, "ker"), string.str_has_prefix(&prefix_cstr, "ker"));
    try std.testing.expectEqual(string.strstarts("kernel", "ker"), string.strHasPrefix("kernel", "ker") != 0);
    try std.testing.expectEqualSlices(u8, "lead\x00", string.skipSpaces(&spaced));
    try std.testing.expectEqual(string.sysfsStreq(&newline_cstr, "mode"), string.sysfs_streq(&newline_cstr, "mode"));
    try std.testing.expectEqual(string.sysfsMatchString(match_haystack[0..], "mode"), string.sysfs_match_string(match_haystack[0..], "mode"));
    try std.testing.expectEqual(string.matchString(cstr_haystack[0..], "a"), string.match_string(cstr_haystack[0..], "a"));
    try std.testing.expectEqual(string.memchrInv(&[_]u8{ 0, 0, 1 }, 0), string.memchr_inv(&[_]u8{ 0, 0, 1 }, 0));
    try std.testing.expectEqual(string.strnchr("alpha", 4, 'h'), @as(?usize, 3));
}

test "phase 1 helper ports A replay keeps plain rbtree replacement aliases aligned through ordered traversal" {
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

    const collect = struct {
        fn keys(root: *const rbtree.Root, out: []i32) usize {
            var count: usize = 0;
            var current = rbtree.first(root);
            while (current) |node| : (current = rbtree.next(node)) {
                const entry: *const Entry = @fieldParentPtr("node", node);
                out[count] = entry.key;
                count += 1;
            }
            return count;
        }
    }.keys;
    const readKey = struct {
        fn from(node: ?*rbtree.Node) ?i32 {
            const current = node orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", current);
            return entry.key;
        }
    }.from;

    var primary_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
    };
    var primary_replacement = Entry{ .key = 20 };
    var alias_replacement = Entry{ .key = 20 };
    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, less);
        rbtree.add(&alias_entry.node, &alias_root, less);
    }

    rbtree.replaceNode(&primary_entries[1].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node(&alias_entries[1].node, &alias_replacement.node, &alias_root);

    var primary_order: [4]i32 = undefined;
    var alias_order: [4]i32 = undefined;
    const primary_count = collect(&primary_root, &primary_order);
    const alias_count = collect(&alias_root, &alias_order);
    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, primary_order[0..primary_count], alias_order[0..alias_count]);
    try std.testing.expectEqual(readKey(rbtree.first(&primary_root)), readKey(rbtree.rb_first(&alias_root)));
    try std.testing.expectEqual(readKey(rbtree.last(&primary_root)), readKey(rbtree.rb_last(&alias_root)));

    const primary_last = rbtree.last(&primary_root) orelse return error.TestUnexpectedResult;
    const alias_last = rbtree.rb_last(&alias_root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(readKey(rbtree.prev(primary_last)), readKey(rbtree.rb_prev(alias_last)));
    try std.testing.expectEqual(readKey(rbtree.next(primary_last)), readKey(rbtree.rb_next(alias_last)));
}
