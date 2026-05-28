const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "phase1 helper ports A bitmap range clear and xor keep partial tails exact" {
    const nbits = find_bit.bits_per_long + 11;
    var lhs = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&lhs, find_bit.bits_per_long - 4, 9);

    var rhs = lhs;
    bitmap.bitmap_clear(&rhs, find_bit.bits_per_long + 1, 4);

    var diff = [_]bitmap.Word{ 0, 0 };
    try std.testing.expectEqual(@as(usize, 4), bitmap.bitmap_weighted_xor(&diff, &lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&rhs, &lhs, nbits));
    try std.testing.expect(!bitmap.bitmap_equal(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findFirstBit(&diff, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findLastBit(&diff, nbits));
}

test "phase1 helper ports A clump and zero scans stay byte-aligned at the tail" {
    const nbits = find_bit.bits_per_long + 16;
    const full_then_gap = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << 9),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 9), find_bit.findFirstZeroBit(&full_then_gap, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 9), find_bit.find_next_zero_bit(&full_then_gap, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&full_then_gap, nbits, find_bit.bits_per_long + 10));

    const clump_map = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 0b0010_0100) << 8,
    };
    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.find_first_clump8(&clump, &clump_map, nbits));
    try std.testing.expectEqual(@as(u8, 0b0010_0100), clump);
    try std.testing.expectEqual(@as(u8, 0b0010_0100), find_bit.getValue8(&clump_map, find_bit.bits_per_long + 8));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.findNextClump8(&clump, &clump_map, nbits, find_bit.bits_per_long + 9));
    try std.testing.expectEqual(@as(u8, 0b0010_0100), clump);
}

test "phase1 helper ports A sysfs and counted string helpers preserve C-string boundaries" {
    var compact = [_]u8{ ' ', 'z', ' ', 'i', ' ', 'g', 0, 'x' };
    const stripped = string.remove_spaces(&compact);
    try std.testing.expectEqualStrings("zig", stripped);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', 0 }, compact[0..4]);

    const nul_mode = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x' };
    try std.testing.expect(string.sysfsStreq("mode\n", &nul_mode));
    try std.testing.expect(string.sysfs_streq(&nul_mode, "mode"));

    const haystack = [_][]const u8{ "off", "mode\n", "mode", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "mode"));

    const counted = [_]u8{ 'a', '/', 'b', 0, '/', 'c' };
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&counted, counted.len, '/'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&counted, 1, '/'));
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr(&counted, counted.len, 0));
}

test "phase1 helper ports A match iteration and erase-init keep cached roots truthful" {
    const Entry = struct {
        const Self = @This();

        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),

        fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Self = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Self = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }

        fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Self = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    };

    var first_entry = Entry{ .key = 5, .serial = 0 };
    var dup_a = Entry{ .key = 7, .serial = 1 };
    var dup_b = Entry{ .key = 7, .serial = 2 };
    var tail = Entry{ .key = 9, .serial = 3 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.rb_add_cached(&first_entry.node, &root, Entry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&dup_a.node, &root, Entry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&dup_b.node, &root, Entry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&tail.node, &root, Entry.less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &first_entry.node), rbtree.rb_first_cached(&root));

    const wanted = @as(i32, 7);
    const first_match = rbtree.findFirst(&wanted, &root.root, Entry.cmpKey) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &dup_a.node), first_match);
    try std.testing.expectEqual(@as(?*rbtree.Node, &dup_b.node), rbtree.nextMatch(&wanted, first_match, Entry.cmpKey));

    var iter = rbtree.matchIterator(&wanted, &root.root, Entry.cmpKey);
    try std.testing.expectEqual(@as(?*rbtree.Node, &dup_a.node), iter.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, &dup_b.node), iter.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, null), iter.next());

    rbtree.rb_erase_init_cached(&first_entry.node, &root);
    try std.testing.expect(rbtree.emptyNode(&first_entry.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &dup_a.node), rbtree.rb_first_cached(&root));
}
