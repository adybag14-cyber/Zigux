const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const expectEqual = std.testing.expectEqual;
const expectEqualSlices = std.testing.expectEqualSlices;
const expectEqualStrings = std.testing.expectEqualStrings;

test "lane06 replay keeps weighted bitmap masks aligned across a partial tail" {
    const nbits = bitmap.bits_per_long + 6;
    const lhs = [_]bitmap.Word{
        @as(bitmap.Word, 0b1011_0001),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    const rhs = [_]bitmap.Word{
        @as(bitmap.Word, 0b0110_0011),
        (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 5) | (@as(bitmap.Word, 1) << 9),
    };
    const old = [_]bitmap.Word{
        @as(bitmap.Word, 0b1111_0000),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 5),
    };
    const new = [_]bitmap.Word{
        @as(bitmap.Word, 0b0000_1111),
        (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    const mask = [_]bitmap.Word{
        @as(bitmap.Word, 0b0011_1100),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };

    var weighted_or_dst = [_]bitmap.Word{ 0, 0 };
    var weighted_xor_dst = [_]bitmap.Word{ 0, 0 };
    var andnot_dst = [_]bitmap.Word{ 0, 0 };
    var replaced = [_]bitmap.Word{ 0, 0 };
    var alias_replaced = [_]bitmap.Word{ 0, 0 };

    try expectEqual(@as(usize, 9), bitmap.weightedOr(&weighted_or_dst, &lhs, &rhs, nbits));
    try expectEqualSlices(bitmap.Word, &[_]bitmap.Word{
        @as(bitmap.Word, 0b1111_0011),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 5) | (@as(bitmap.Word, 1) << 9),
    }, &weighted_or_dst);

    try expectEqual(@as(usize, 6), bitmap.bitmap_weighted_xor(&weighted_xor_dst, &lhs, &rhs, nbits));
    try expectEqualSlices(bitmap.Word, &[_]bitmap.Word{
        @as(bitmap.Word, 0b1101_0010),
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 5),
    }, &weighted_xor_dst);

    try std.testing.expect(bitmap.bitmap_andnot(&andnot_dst, &lhs, &rhs, nbits));
    try expectEqualSlices(bitmap.Word, &[_]bitmap.Word{
        @as(bitmap.Word, 0b1001_0000),
        @as(bitmap.Word, 1) << 1,
    }, &andnot_dst);

    bitmap.replace(&replaced, &old, &new, &mask, nbits);
    bitmap.__bitmap_replace(&alias_replaced, &old, &new, &mask, nbits);
    try expectEqualSlices(bitmap.Word, &replaced, &alias_replaced);
    try expectEqualSlices(bitmap.Word, &[_]bitmap.Word{
        @as(bitmap.Word, 0b1100_1100),
        (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 5),
    }, &replaced);
}

test "lane06 replay keeps andnot scans reachable across partial tail windows" {
    const nbits = find_bit.bits_per_long + 6;
    const lhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 7,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };
    const rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 5,
        (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };
    var clump: u8 = 0xaa;

    try expectEqual(@as(usize, 7), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try expectEqual(@as(usize, 7), find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, 0));
    try expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, 8));
    try expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit._find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long));
    try expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 2));

    try expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &lhs, nbits));
    try expectEqual(@as(u8, 0b1000_0000), clump);
    try expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextClump8(&clump, &lhs, nbits, find_bit.bits_per_long + 2));
    try expectEqual(@as(u8, 0b0001_0010), clump);
}

test "lane06 replay keeps string parse and bounded-search edges stable" {
    const parsed_negative_hex = string.memparse("-0x10Ktail");
    try expectEqual(@as(u64, @bitCast(@as(i64, -0x4_000))), parsed_negative_hex.value);
    try expectEqualStrings("tail", parsed_negative_hex.rest);

    const saturated_positive = string.memparse("+0x8000000000000000Mrest");
    try expectEqual(@as(u64, std.math.maxInt(i64)), saturated_positive.value);
    try expectEqualStrings("rest", saturated_positive.rest);

    var padded = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x' };
    try expectEqual(@as(isize, 2), string.strscpy_pad(&padded, "ok"));
    try expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &padded);

    const cstr = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x', 'y' };
    try expectEqual(@as(?usize, 2), string.strnchr(&cstr, cstr.len, 'd'));
    try expectEqual(@as(?usize, 4), string.strnchr(&cstr, cstr.len, 0));
    try expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, 'x'));

    const sysfs_modes = [_][]const u8{
        "auto\n",
        "manual",
        "manual\n",
    };
    try expectEqual(@as(?usize, 1), string.sysfs_match_string(&sysfs_modes, "manual"));
    try expectEqual(@as(?usize, 0), string.sysfsMatchString(&sysfs_modes, "auto"));
}

test "lane06 replay keeps cached rbtree leftmost reseed stable after singleton reset" {
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

    var singleton = Entry{ .key = 7, .serial = 0 };
    var leftmost = Entry{ .key = 3, .serial = 1 };
    var root_entry = Entry{ .key = 9, .serial = 2 };
    var larger = Entry{ .key = 14, .serial = 3 };
    var duplicate = Entry{ .key = 3, .serial = 4 };
    var replacement = Entry{ .key = 3, .serial = 5 };
    var root = rbtree.RootCached.init();

    try expectEqual(@as(?*rbtree.Node, &singleton.node), rbtree.addCached(&singleton.node, &root, less));
    try expectEqual(@as(?*rbtree.Node, &singleton.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&singleton.node, &root);
    try std.testing.expect(rbtree.emptyNode(&singleton.node));
    try std.testing.expect(rbtree.firstCached(&root) == null);
    try std.testing.expect(root.root.node == null);

    try expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.rb_add_cached(&leftmost.node, &root, less));
    try expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&root_entry.node, &root, cmp));
    try expectEqual(@as(?*rbtree.Node, null), rbtree.addCached(&larger.node, &root, less));
    try expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));
    try expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.first(&root.root));

    const duplicate_hit = rbtree.findAddCached(&duplicate.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try expectEqual(@as(*rbtree.Node, &leftmost.node), duplicate_hit);
    try expectEqual(@as(?*rbtree.Node, &leftmost.node), rbtree.firstCached(&root));

    rbtree.rb_replace_node_cached(&leftmost.node, &replacement.node, &root);
    try expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.first(&root.root));

    try std.testing.expect(rbtree.rb_erase_cached(&larger.node, &root) == null);
    try expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
}
