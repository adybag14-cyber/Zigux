const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = find_bit.Word;
const bits_per_long = find_bit.bits_per_long;

test "ports A OR token iterator replay keeps helper views aligned" {
    const nbits = bits_per_long + 12;
    const tail_a = bits_per_long + 2;
    const tail_b = bits_per_long + 7;
    const tail_c = bits_per_long + 9;

    const lhs = [_]Word{
        (@as(Word, 1) << 1) | (@as(Word, 1) << 3),
        (@as(Word, 1) << 2) | (@as(Word, 1) << 7),
    };
    const rhs = [_]Word{
        @as(Word, 1) << 3,
        (@as(Word, 1) << 2) | (@as(Word, 1) << 9),
    };

    var merged = [_]Word{ 0, 0 };
    var alias_merged = [_]Word{ 0, 0 };
    bitmap.orBits(&merged, &lhs, &rhs, nbits);
    bitmap.bitmap_or(&alias_merged, &lhs, &rhs, nbits);
    try std.testing.expectEqualSlices(Word, &merged, &alias_merged);
    try std.testing.expectEqual(@as(usize, 5), bitmap.weight(&merged, nbits));

    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&merged, nbits));
    try std.testing.expectEqual(@as(usize, 3), find_bit.findNextBit(&merged, nbits, 2));
    try std.testing.expectEqual(tail_a, find_bit.findNextBit(&merged, nbits, bits_per_long));
    try std.testing.expectEqual(tail_b, find_bit.findNextBit(&merged, nbits, tail_a + 1));
    try std.testing.expectEqual(tail_c, find_bit.findLastBit(&merged, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &merged, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_1010), clump);

    clump = 0;
    try std.testing.expectEqual(bits_per_long, find_bit.findNextClump8(&clump, &merged, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0b1000_0100), clump);

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&merged, nbits, &rendered);
    try std.testing.expectEqualStrings("1,3,66,71,73", rendered[0..rendered_len]);

    try std.testing.expectEqual(@as(usize, 1), string.strHasPrefix(rendered[0..rendered_len], "1"));
    try std.testing.expect(string.strEndsWith(rendered[0..rendered_len], "73"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(rendered[0..rendered_len], rendered_len, ','));
    try std.testing.expectEqual(@as(?usize, 1), string.memchrInv(rendered[0..2], '1'));

    const expected_renderings = [_][]const u8{ "0", "1,3,66,71,73", "missing" };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(expected_renderings[0..], rendered[0..rendered_len]));

    var rewritten: [64]u8 = @splat(0);
    @memcpy(rewritten[0..rendered_len], rendered[0..rendered_len]);
    try std.testing.expectEqual(rendered_len, string.replaceChar(rewritten[0..], ',', '|'));
    try std.testing.expectEqualStrings("1|3|66|71|73", rewritten[0..rendered_len]);

    const Entry = struct {
        key: usize,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs_node: *const rbtree.Node, rhs_node: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs_node);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs_node);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const usize = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 1, .serial = 0 },
        .{ .key = 3, .serial = 1 },
        .{ .key = tail_a, .serial = 2 },
        .{ .key = tail_b, .serial = 3 },
        .{ .key = tail_c, .serial = 4 },
        .{ .key = tail_a, .serial = 5 },
    };
    var replacement = Entry{ .key = tail_b, .serial = 6 };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var duplicate_key: usize = tail_a;
    var replacement_key: usize = tail_b;

    var duplicate_iter = rbtree.matchIterator(&duplicate_key, &root, cmp);
    var duplicate_serials: [2]usize = undefined;
    var duplicate_count: usize = 0;
    while (duplicate_iter.next()) |node| : (duplicate_count += 1) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        duplicate_serials[duplicate_count] = entry.serial;
    }
    try std.testing.expectEqual(@as(usize, 2), duplicate_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 2, 5 }, duplicate_serials[0..duplicate_count]);

    rbtree.replaceNode(&entries[3].node, &replacement.node, &root);
    const found_replacement = rbtree.find(&replacement_key, &root, cmp) orelse return error.TestUnexpectedResult;
    const found_entry: *const Entry = @fieldParentPtr("node", found_replacement);
    try std.testing.expectEqual(@as(usize, 6), found_entry.serial);

    rbtree.eraseInit(&entries[2].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[2].node));

    duplicate_iter = rbtree.matchIterator(&duplicate_key, &root, cmp);
    const remaining_duplicate = duplicate_iter.next() orelse return error.TestUnexpectedResult;
    const remaining_entry: *const Entry = @fieldParentPtr("node", remaining_duplicate);
    try std.testing.expectEqual(@as(usize, 5), remaining_entry.serial);
    try std.testing.expect(duplicate_iter.next() == null);
}
