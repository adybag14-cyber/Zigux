const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap andnot tails keep only in-range unique bits" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 7) };
    const rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 6) };
    var dst = [_]bitmap.Word{ 0, 0 };
    var alias_dst = [_]bitmap.Word{ 0, 0 };

    try std.testing.expect(bitmap.andNotBits(&dst, &lhs, &rhs, nbits));
    try std.testing.expect(bitmap.bitmap_andnot(&alias_dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(bitmap.Word, @as(bitmap.Word, 1) << 1), dst[1]);
    try std.testing.expectEqualSlices(bitmap.Word, &dst, &alias_dst);
    try std.testing.expect(bitmap.subset(&dst, &lhs, nbits));
    try std.testing.expect(!bitmap.intersects(&dst, &rhs, nbits));
}

test "phase1 helper ports A find_bit keeps the last aligned clump and bit visible" {
    const clump_offset = find_bit.bits_per_long + 8;
    const nbits = clump_offset + 8;
    const map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 8) | (@as(find_bit.Word, 1) << 10) | (@as(find_bit.Word, 1) << 15) };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 15), find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 15), find_bit.find_last_bit(&map, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, clump_offset), find_bit.find_first_clump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0b1000_0101), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&clump, &map, nbits, clump_offset + 8));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "phase1 helper ports A string prefix suffix basename and dirty-byte helpers stay c-string aware" {
    const module_name = [_]u8{ 'z', 'i', 'g', 'u', 'x', '.', 'z', 'i', 'g', 0, 'x' };
    const all_clean = [_]u8{ 'z', 'z', 'z', 'z', 'z', 'z', 'z', 'z' };
    const first_dirty = [_]u8{ 'z', 'z', 'z', 'z', 'z', 'y', 'z', 'z' };
    var spaced = [_]u8{ ' ', 'z', 'i', 'g', ' ', 'u', 'x', ' ', 0, 'x' };
    var replaced = [_]u8{ 'z', 'i', 'g', '-', 'u', 'x', 0, 'x' };

    try std.testing.expectEqual(@as(usize, 5), string.strHasPrefix(&module_name, "zigux"));
    try std.testing.expect(string.strstarts(&module_name, "zig"));
    try std.testing.expect(string.strEndsWith(&module_name, ".zig"));
    try std.testing.expectEqualStrings("zigux", string.removeSpaces(&spaced));
    try std.testing.expectEqual(@as(usize, 6), string.replaceChar(&replaced, '-', '_'));
    try std.testing.expectEqualStrings("zig_ux", replaced[0..6]);
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(&all_clean, 'z'));
    try std.testing.expectEqual(@as(?usize, 5), string.memchrInv(&first_dirty, 'z'));
}

test "phase1 helper ports A cached rbtree replacement keeps duplicate iteration anchored at the leftmost node" {
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

    var first_entry = Entry{ .key = 4, .serial = 0 };
    var second_entry = Entry{ .key = 4, .serial = 1 };
    var third_entry = Entry{ .key = 7, .serial = 2 };
    var replacement = Entry{ .key = 4, .serial = 99 };
    var root = rbtree.RootCached.init();
    const needle: i32 = 4;

    _ = rbtree.addCached(&first_entry.node, &root, less);
    _ = rbtree.addCached(&second_entry.node, &root, less);
    _ = rbtree.addCached(&third_entry.node, &root, less);

    var serials: [2]usize = undefined;
    var count: usize = 0;
    var iter = rbtree.matchIterator(&needle, &root.root, cmp_key);
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 1 }, serials[0..count]);

    rbtree.replaceNodeCached(&first_entry.node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.findFirst(&needle, &root.root, cmp_key));
    try std.testing.expectEqual(@as(?*rbtree.Node, &second_entry.node), rbtree.nextMatch(&needle, &replacement.node, cmp_key));

    rbtree.eraseInitCached(&replacement.node, &root);
    try std.testing.expect(rbtree.emptyNode(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &second_entry.node), rbtree.firstCached(&root));
}
