const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string_helpers = @import("string_helpers");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap copy-and-weight helpers aligned across a partial tail" {
    const count = bitmap.bits_per_long + 5;
    const size = count + bitmap.bits_per_long;
    const src = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        (@as(bitmap.Word, 1) << 0) |
            (@as(bitmap.Word, 1) << 2) |
            (@as(bitmap.Word, 1) << 4) |
            (@as(bitmap.Word, 1) << 7),
    };

    var direct_copy = [_]bitmap.Word{ 0, 0 };
    var alias_copy = [_]bitmap.Word{ 0, 0 };
    bitmap.copyClearTail(&direct_copy, &src, count);
    bitmap.bitmap_copy_clear_tail(&alias_copy, &src, count);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_copy, &alias_copy);
    try std.testing.expectEqual(@as(bitmap.Word, 0b1_0101), direct_copy[1]);

    var direct_extended = [_]bitmap.Word{ 0xaa55, 0xaa55, 0xaa55 };
    var alias_extended = [_]bitmap.Word{ 0xaa55, 0xaa55, 0xaa55 };
    bitmap.copyAndExtend(&direct_extended, &src, count, size);
    bitmap.bitmap_copy_and_extend(&alias_extended, &src, count, size);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_extended, &alias_extended);
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct_extended[2]);

    var weighted_or_direct = [_]bitmap.Word{ 0, 0 };
    var weighted_or_alias = [_]bitmap.Word{ 0, 0 };
    const lhs = [_]bitmap.Word{ 0b0101_0000, 0b0000_0011 };
    const rhs = [_]bitmap.Word{ 0b0011_0000, 0b0000_0101 };
    const direct_or_weight = bitmap.weightedOr(&weighted_or_direct, &lhs, &rhs, count);
    const alias_or_weight = bitmap.bitmap_weighted_or(&weighted_or_alias, &lhs, &rhs, count);
    try std.testing.expectEqualSlices(bitmap.Word, &weighted_or_direct, &weighted_or_alias);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try std.testing.expectEqual(@as(usize, 6), direct_or_weight);

    var weighted_xor_direct = [_]bitmap.Word{ 0, 0 };
    var weighted_xor_alias = [_]bitmap.Word{ 0, 0 };
    const direct_xor_weight = bitmap.weightedXor(&weighted_xor_direct, &lhs, &rhs, count);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&weighted_xor_alias, &lhs, &rhs, count);
    try std.testing.expectEqualSlices(bitmap.Word, &weighted_xor_direct, &weighted_xor_alias);
    try std.testing.expectEqual(direct_xor_weight, alias_xor_weight);
    try std.testing.expectEqual(@as(usize, 4), direct_xor_weight);
}

test "lane06 replay keeps clump window helpers aligned across aligned byte boundaries" {
    const nbits = find_bit.bits_per_long * 2;
    const boundary = find_bit.bits_per_long - 8;
    const map = [_]find_bit.Word{
        @as(find_bit.Word, 0xa5) << @intCast(boundary),
        (@as(find_bit.Word, 0x3c) << 8) | (@as(find_bit.Word, 0x81) << 24),
    };

    var clump: u8 = 0;
    try std.testing.expectEqual(boundary, find_bit.findFirstClump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0xa5), clump);
    try std.testing.expectEqual(boundary, find_bit.find_first_clump8(&clump, &map, nbits));
    try std.testing.expectEqual(boundary, find_bit._find_first_clump8(&clump, &map, nbits));

    clump = 0;
    try std.testing.expectEqual(boundary, find_bit.findNextClump8(&clump, &map, nbits, boundary + 3));
    try std.testing.expectEqual(@as(u8, 0xa5), clump);
    try std.testing.expectEqual(find_bit.bits_per_long + 8, find_bit.find_next_clump8(&clump, &map, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x3c), clump);

    clump = 0;
    try std.testing.expectEqual(find_bit.bits_per_long + 24, find_bit._find_next_clump8(&clump, &map, nbits, find_bit.bits_per_long + 24));
    try std.testing.expectEqual(@as(u8, 0x81), clump);
}

test "lane06 replay keeps dirty-byte and prefix-suffix string helpers stable" {
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.memchrInv("ziggzg", 'z'));
    try std.testing.expectEqual(@as(?usize, null), string_helpers.memchrInv("zzzz", 'z'));

    try std.testing.expectEqual(@as(usize, 4), string_helpers.strHasPrefix("lane06", "lane"));
    try std.testing.expectEqual(@as(usize, 0), string_helpers.strHasPrefix("lane06", "Line"));
    try std.testing.expect(string_helpers.strstarts("lane06", "lane"));
    try std.testing.expect(!string_helpers.strstarts("lane06", "port"));

    try std.testing.expect(string_helpers.strEndsWith("helper.zig", ".zig"));
    try std.testing.expect(string_helpers.str_ends_with("helper.zig", ".zig"));
    try std.testing.expect(!string_helpers.strEndsWith("helper.zig", ".c"));

    const choices = [_][]const u8{ "alpha", "lane06\n", "omega" };
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.sysfsMatchString(&choices, "lane06"));
    try std.testing.expectEqual(@as(?usize, 1), string_helpers.sysfs_match_string(&choices, "lane06\n"));

    try std.testing.expectEqual(@as(?usize, 3), string_helpers.strnchr("lane06", 6, 'e'));
    try std.testing.expectEqual(@as(?usize, null), string_helpers.strnchr(&[_]u8{ 'l', 'a', 0, 'e' }, 4, 'e'));
}

test "lane06 replay keeps cached duplicate next-match iteration stable after a miss insert" {
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
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
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

    var leftmost = Entry{ .key = 4, .serial = 0 };
    var first_dup = Entry{ .key = 9, .serial = 1 };
    var second_dup = Entry{ .key = 9, .serial = 2 };
    var greater = Entry{ .key = 12, .serial = 3 };
    var miss = Entry{ .key = 10, .serial = 4 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.rb_add_cached(&leftmost.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&first_dup.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_add_cached(&second_dup.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&greater.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&miss.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.rb_first_cached(&root));

    const dup_key = @as(i32, 9);
    const first_match = rbtree.findFirst(&dup_key, &root.root, key_cmp) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 1), first_match_entry.serial);

    const next_match = rbtree.nextMatch(&dup_key, first_match, key_cmp) orelse return error.TestUnexpectedResult;
    const next_match_entry: *const Entry = @fieldParentPtr("node", next_match);
    try std.testing.expectEqual(@as(usize, 2), next_match_entry.serial);
    try std.testing.expect(rbtree.nextMatch(&dup_key, next_match, key_cmp) == null);

    var iter = rbtree.matchIterator(&dup_key, &root.root, key_cmp);
    const iter_first = iter.next() orelse return error.TestUnexpectedResult;
    const iter_first_entry: *const Entry = @fieldParentPtr("node", iter_first);
    try std.testing.expectEqual(@as(usize, 1), iter_first_entry.serial);
    const iter_second = iter.next() orelse return error.TestUnexpectedResult;
    const iter_second_entry: *const Entry = @fieldParentPtr("node", iter_second);
    try std.testing.expectEqual(@as(usize, 2), iter_second_entry.serial);
    try std.testing.expect(iter.next() == null);
}
