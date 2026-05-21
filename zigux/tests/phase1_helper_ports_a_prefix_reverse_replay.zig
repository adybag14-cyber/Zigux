const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A masked bitmap logical replay stays aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) };
    const rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9) };

    var weighted_or_dst = [_]bitmap.Word{ 0, 0 };
    const weighted_or = bitmap.weightedOr(&weighted_or_dst, &lhs, &rhs, nbits);
    try std.testing.expectEqual(
        @as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4)),
        weighted_or_dst[1] & bitmap.lastWordMask(nbits),
    );
    try std.testing.expectEqual(bitmap.weight(&weighted_or_dst, nbits), weighted_or);
    try std.testing.expectEqual(@as(usize, 2), weighted_or);

    var weighted_xor_dst = [_]bitmap.Word{ 0, 0 };
    const weighted_xor = bitmap.weightedXor(&weighted_xor_dst, &lhs, &rhs, nbits);
    try std.testing.expectEqual(
        @as(bitmap.Word, @as(bitmap.Word, 1) << 1),
        weighted_xor_dst[1] & bitmap.lastWordMask(nbits),
    );
    try std.testing.expectEqual(bitmap.weight(&weighted_xor_dst, nbits), weighted_xor);
    try std.testing.expectEqual(@as(usize, 1), weighted_xor);

    const replace_old = [_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 1 };
    const replace_new = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };
    const replace_mask = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };
    var replaced = [_]bitmap.Word{ 0, 0 };
    bitmap.replace(&replaced, &replace_old, &replace_new, &replace_mask, nbits);
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3)), replaced[1]);
}

test "phase1 helper ports A masked find-bit replay keeps partial tails reviewable" {
    const nbits = find_bit.bits_per_long + 6;
    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    const andnot_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };
    const andnot_rhs = [_]find_bit.Word{
        0,
        @as(find_bit.Word, 1) << 1,
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 1), find_bit.findFirstZeroBit(&zero_map, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findFirstAndNotBit(&andnot_lhs, &andnot_rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 4), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, find_bit.bits_per_long + 5));
}

test "phase1 helper ports A string prefix and suffix replay stops at C-string boundaries" {
    const source = [_]u8{ 'p', 'r', 'e', 'f', 'i', 'x', 0, 'x' };
    const embedded_prefix = [_]u8{ 'p', 'r', 'e', 0, 'y' };
    const embedded_suffix = [_]u8{ 'f', 'i', 'x', 0, 'y' };
    const past_nul_suffix = [_]u8{ 'z', 0, 'x' };
    const bounded = [_]u8{ 'a', 'b', 0, 'c', 'd' };

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&source, &embedded_prefix));
    try std.testing.expect(string.strstarts(&source, "prefix"));
    try std.testing.expect(string.strEndsWith(&source, &embedded_suffix));
    try std.testing.expect(!string.str_ends_with(&source, &past_nul_suffix));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&bounded, bounded.len, 'b'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&bounded, bounded.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, bounded.len, 'c'));
}

test "phase1 helper ports A rbtree reverse and duplicate replay stays ordered" {
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
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 15, .serial = 4 },
        .{ .key = 10, .serial = 5 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var reverse_order: [6]i32 = undefined;
    var reverse_count: usize = 0;
    var cursor = rbtree.last(&root);
    while (cursor) |node| : (cursor = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        reverse_order[reverse_count] = entry.key;
        reverse_count += 1;
    }
    try std.testing.expectEqual(@as(usize, 6), reverse_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 20, 15, 10, 10, 10, 5 }, reverse_order[0..reverse_count]);

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &root, cmp) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_entry.serial);

    var duplicate_serials: [3]usize = undefined;
    var duplicate_count: usize = 0;
    var duplicate_cursor = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", duplicate_cursor);
        duplicate_serials[duplicate_count] = entry.serial;
        duplicate_count += 1;
        duplicate_cursor = rbtree.nextMatch(&wanted, duplicate_cursor, cmp) orelse break;
    }

    try std.testing.expectEqual(@as(usize, 3), duplicate_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 5 }, duplicate_serials[0..duplicate_count]);
    try std.testing.expect(rbtree.nextMatch(&wanted, duplicate_cursor, cmp) == null);
}
