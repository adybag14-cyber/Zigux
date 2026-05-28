const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap weighted xor ignores tail bits in weight while keeping aliases aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 6),
    };
    const rhs = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 8),
    };
    var direct = [_]bitmap.Word{ 0, 0 };
    var alias = [_]bitmap.Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 2), bitmap.weightedXor(&direct, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weighted_xor(&alias, &lhs, &rhs, nbits));

    const expected = [_]bitmap.Word{
        0,
        (@as(bitmap.Word, 1) << 0) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 6) | (@as(bitmap.Word, 1) << 8),
    };
    try std.testing.expectEqualSlices(bitmap.Word, &expected, &direct);
    try std.testing.expectEqualSlices(bitmap.Word, &expected, &alias);
    try std.testing.expect(bitmap.equal(&direct, &alias, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct, nbits));
    try std.testing.expect(bitmap.intersects(&direct, &rhs, nbits));
    try std.testing.expect(bitmap.subset(&direct, &lhs, nbits) == false);
}

test "phase1 helper ports A find_bit last and clump scans keep the final tail byte aligned" {
    const nbits = find_bit.bits_per_long + 13;
    const bitmap_words = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 8) | (@as(find_bit.Word, 1) << 12),
    };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 12), find_bit.findLastBit(&bitmap_words, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 12), find_bit.find_last_bit(&bitmap_words, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.findNextClump8(&clump, &bitmap_words, nbits, find_bit.bits_per_long + 9));
    try std.testing.expectEqual(@as(u8, 0b0001_0001), clump);

    clump = 0;
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.find_next_clump8(&clump, &bitmap_words, nbits, find_bit.bits_per_long + 8));
    try std.testing.expectEqual(@as(u8, 0b0001_0001), clump);

    clump = 0x5a;
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextClump8(&clump, &bitmap_words, nbits, find_bit.bits_per_long + 13));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
}

test "phase1 helper ports A string memparse and match helpers preserve suffix and c-string boundaries" {
    const parsed = string.memparse("-0x10Krest");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -16384))), parsed.value);
    try std.testing.expectEqualStrings("rest", parsed.rest);

    const unchanged = string.memparse("+?zig");
    try std.testing.expectEqual(@as(u64, 0), unchanged.value);
    try std.testing.expectEqualStrings("+?zig", unchanged.rest);

    const haystack = [_][]const u8{ "alpha", "beta", "gamma" };
    const beta_cstr = [_]u8{ 'b', 'e', 't', 'a', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(haystack[0..], &beta_cstr));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(haystack[0..], "beta"));

    const module_name = [_]u8{ 'l', 'a', 'n', 'e', '-', '0', '6', 0, '.', 'z', 'i', 'g' };
    try std.testing.expectEqual(@as(usize, 7), string.str_has_prefix(&module_name, "lane-06"));
    try std.testing.expect(string.strEndsWith(&module_name, "06"));
}

test "phase1 helper ports A rbtree duplicate iterators keep first-match and next-match ordering stable" {
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
        .{ .key = 12, .serial = 0 },
        .{ .key = 9, .serial = 1 },
        .{ .key = 12, .serial = 2 },
        .{ .key = 15, .serial = 3 },
        .{ .key = 12, .serial = 4 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = @as(i32, 12);
    const first_match = rbtree.findFirst(&duplicate, &root, cmp) orelse return error.TestUnexpectedResult;
    const first_entry: *const Entry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(@as(usize, 0), first_entry.serial);

    var iterator = rbtree.matchIterator(&duplicate, &root, cmp);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iterator.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);

    const second_match = rbtree.nextMatch(&duplicate, first_match, cmp) orelse return error.TestUnexpectedResult;
    const second_entry: *const Entry = @fieldParentPtr("node", second_match);
    try std.testing.expectEqual(@as(usize, 2), second_entry.serial);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.nextMatch(&duplicate, &entries[4].node, cmp));
}
