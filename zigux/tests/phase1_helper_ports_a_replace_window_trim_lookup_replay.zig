const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string_helpers = @import("string_helpers");
const rbtree = @import("rbtree");

test "lane06 replay keeps bitmap replace tails and predicates aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const old = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4),
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 9),
    };
    const new = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 4),
        (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 11),
    };
    const mask = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 1),
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) | (@as(bitmap.Word, 1) << 11),
    };
    const expected = [_]bitmap.Word{
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 4),
        @as(bitmap.Word, 1) << 3,
    };

    var replaced = [_]bitmap.Word{ 0, 0 };
    bitmap.bitmap_replace(&replaced, &old, &new, &mask, nbits);

    try std.testing.expect(bitmap.bitmap_equal(&replaced, &expected, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&expected, &replaced, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&replaced, &expected, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&replaced, nbits));
    try std.testing.expect(!bitmap.bitmap_full(&replaced, nbits));

    var rendered: [64]u8 = undefined;
    const len = bitmap.bitmap_scnprintf(&replaced, nbits, &rendered);

    var expected_text_buf: [32]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected_text_buf,
        "0,4,{d}",
        .{bitmap.bits_per_long + 3},
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..len]);
}

test "lane06 replay keeps find-bit masked windows and zero scans aligned" {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 7) | (@as(find_bit.Word, 1) << (find_bit.bits_per_long - 1)),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };
    const rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << (find_bit.bits_per_long - 1),
        (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9),
    };
    const mostly_full = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };

    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long - 1),
        find_bit.findFirstAndBit(&lhs, &rhs, nbits),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextAndBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 5),
    );

    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstZeroBit(&lhs, nbits));
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 1),
        find_bit.findNextZeroBit(&mostly_full, nbits, find_bit.bits_per_long),
    );
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long + 4),
        find_bit.findNextZeroBit(&mostly_full, nbits, find_bit.bits_per_long + 2),
    );
    try std.testing.expectEqual(
        @as(usize, nbits),
        find_bit.findNextZeroBit(&mostly_full, nbits, find_bit.bits_per_long + 5),
    );
}

test "lane06 replay keeps string cleanup, booleans, and dirty-byte scans aligned" {
    var bool_buf = [_]u8{ ' ', '\t', 'o', 'n', ' ', 0, 'x' };
    const trimmed = string_helpers.trimSpaces(&bool_buf);
    try std.testing.expectEqualStrings("on", trimmed);
    try std.testing.expect(try string_helpers.strtobool(trimmed));

    var remove_buf = [_]u8{ 'z', 'i', ' ', 'g', ' ', 'u', 'x', 0, 'x' };
    try std.testing.expectEqualStrings("zigux", string_helpers.removeSpaces(&remove_buf));

    var replace_buf = [_]u8{ 'z', 'i', 'g', '-', 'u', 'x', 0, '-' };
    try std.testing.expectEqual(@as(usize, 6), string_helpers.strreplace(&replace_buf, '-', '_'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 'g', '_', 'u', 'x', 0, '-' }, &replace_buf);

    const dirty_bytes = [_]u8{ 0, 0, 0x20, 0, 0x7f };
    try std.testing.expectEqual(@as(?usize, 2), string_helpers.memchrInv(&dirty_bytes, 0));
    try std.testing.expectEqual(@as(?usize, null), string_helpers.memchrInv(&[_]u8{ 0, 0, 0, 0 }, 0));
}

test "lane06 replay keeps cached duplicate lookup and iteration aligned" {
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

    const cmp_node = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
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

    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 10, .serial = 3 },
        .{ .key = 12, .serial = 4 },
    };
    var duplicate_candidate = Entry{ .key = 10, .serial = 9 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    const duplicate = rbtree.findAddCached(&duplicate_candidate.node, &root, cmp_node) orelse return error.TestUnexpectedResult;
    const duplicate_entry: *const Entry = @fieldParentPtr("node", duplicate);
    try std.testing.expectEqual(@as(usize, 0), duplicate_entry.serial);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.firstCached(&root));

    const wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&wanted, &root.root, cmp_key) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_match_entry.serial);

    var iter = rbtree.matchIterator(&wanted, &root.root, cmp_key);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 3 }, serials[0..count]);

    const missing = @as(i32, 11);
    try std.testing.expect(rbtree.find(&missing, &root.root, cmp_key) == null);
}
