const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap weighted helpers clamp tail noise and reset freed optionals" {
    const nbits = bits_per_long + 5;
    const or_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 8) };
    const or_rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 9) };
    var direct_or = [_]Word{ 0, 0 };
    var alias_or = [_]Word{ 0, 0 };

    const direct_or_weight = bitmap.weightedOr(&direct_or, &or_lhs, &or_rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &or_lhs, &or_rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_or_weight);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try std.testing.expectEqualSlices(Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_or, nbits));

    const xor_lhs = [_]Word{ 0, (@as(Word, 1) << 1) | (@as(Word, 1) << 3) | (@as(Word, 1) << 8) };
    const xor_rhs = [_]Word{ 0, (@as(Word, 1) << 3) | (@as(Word, 1) << 4) | (@as(Word, 1) << 9) };
    var direct_xor = [_]Word{ 0, 0 };
    var alias_xor = [_]Word{ 0, 0 };

    const direct_xor_weight = bitmap.weightedXor(&direct_xor, &xor_lhs, &xor_rhs, nbits);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&alias_xor, &xor_lhs, &xor_rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_xor_weight);
    try std.testing.expectEqual(direct_xor_weight, alias_xor_weight);
    try std.testing.expectEqualSlices(Word, &direct_xor, &alias_xor);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_xor, nbits));

    const allocator = std.testing.allocator;
    var zeroed: ?[]Word = try bitmap.bitmap_zalloc(allocator, nbits);
    try std.testing.expect(zeroed != null);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(Word, 0), word);
    }
    bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expect(zeroed == null);
}

test "find_bit last and andnot helpers keep inclusive tail boundaries stable" {
    const nbits = bits_per_long + 6;
    const map = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 9) };
    const mask = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 9) };

    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findFirstAndNotBit(map[0..], mask[0..], nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit._find_first_andnot_bit(map[0..], mask[0..], nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextAndNotBit(map[0..], mask[0..], nbits, bits_per_long + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(map[0..], mask[0..], nbits, bits_per_long + 5));

    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findLastBit(map[0..], nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.find_last_bit(map[0..], nbits));

    var cleared = map;
    cleared[1] &= ~(@as(find_bit.Word, 1) << 4);
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findLastBit(cleared[0..], nbits));
    cleared[1] &= ~(@as(find_bit.Word, 1) << 1);
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findLastBit(cleared[0..], nbits));
}

test "string memparse and bounded terminator helpers stay aligned on saturated input" {
    const saturated = string.memparse("18446744073709551615Ktail");
    try std.testing.expectEqual(std.math.maxInt(u64), saturated.value);
    try std.testing.expectEqualStrings("tail", saturated.rest);

    const signed = string.memparse("-17 tail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -17))), signed.value);
    try std.testing.expectEqualStrings(" tail", signed.rest);

    const bounded = [_]u8{ 'a', 'b', 0, 'c', 'd' };
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&bounded, bounded.len, 'b'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&bounded, bounded.len, 0));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, bounded.len, 'd'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&bounded, 2, 0));
}

test "rbtree duplicate iteration and cached replacement keep leftmost state stable" {
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

    const key_cmp = struct {
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
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate = @as(i32, 10);
    var iter = rbtree.matchIterator(&duplicate, &root, key_cmp);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);

    var cached_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
    };
    var replacement = Entry{ .key = 20, .serial = 3 };
    var cached_root = rbtree.RootCached.init();
    for (&cached_entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &cached_root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[1].node), rbtree.rb_first_cached(&cached_root));
    rbtree.rb_replace_node_cached(&cached_entries[2].node, &replacement.node, &cached_root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[1].node), rbtree.rb_first_cached(&cached_root));

    rbtree.rb_erase_init_cached(&cached_entries[1].node, &cached_root);
    try std.testing.expect(rbtree.emptyNode(&cached_entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[0].node), rbtree.rb_first_cached(&cached_root));
}
