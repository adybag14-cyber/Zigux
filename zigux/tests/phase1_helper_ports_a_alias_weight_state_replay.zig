const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap weighted aliases and allocation state replay" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 8) };
    const rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };
    var direct_or = [_]bitmap.Word{ 0, 0 };
    var alias_or = [_]bitmap.Word{ 0, 0 };

    const direct_or_weight = bitmap.weightedOr(&direct_or, &lhs, &rhs, nbits);
    const alias_or_weight = bitmap.bitmap_weighted_or(&alias_or, &lhs, &rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_or_weight);
    try std.testing.expectEqual(direct_or_weight, alias_or_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_or, &alias_or);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_or, nbits));

    const xor_lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8) };
    const xor_rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9) };
    var direct_xor = [_]bitmap.Word{ 0, 0 };
    var alias_xor = [_]bitmap.Word{ 0, 0 };

    const direct_xor_weight = bitmap.weightedXor(&direct_xor, &xor_lhs, &xor_rhs, nbits);
    const alias_xor_weight = bitmap.bitmap_weighted_xor(&alias_xor, &xor_lhs, &xor_rhs, nbits);
    try std.testing.expectEqual(@as(usize, 2), direct_xor_weight);
    try std.testing.expectEqual(direct_xor_weight, alias_xor_weight);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_xor, &alias_xor);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_xor, nbits));

    const allocator = std.testing.allocator;
    var zeroed: ?[]bitmap.Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expectEqual(@as(usize, bitmap.bitsToWords(nbits)), zeroed.?.len);
    for (zeroed.?) |word| {
        try std.testing.expectEqual(@as(bitmap.Word, 0), word);
    }

    bitmap.bitmap_free(allocator, &zeroed);
    try std.testing.expect(zeroed == null);
}

test "phase1 helper ports A find_bit inclusive boundaries and tail-byte replay" {
    const tail_bits: usize = 5;
    const boundary = find_bit.bits_per_long + tail_bits - 1;
    const nbits = boundary + 1;
    const tail_word = (@as(find_bit.Word, 1) << @intCast(tail_bits - 1)) | (@as(find_bit.Word, 1) << @intCast(tail_bits + 2));
    const set_map = [_]find_bit.Word{ 0, tail_word };
    const andnot_rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << @intCast(tail_bits + 2) };
    const zero_map = [_]find_bit.Word{ ~@as(find_bit.Word, 0), find_bit.lastWordMask(nbits) & ~(@as(find_bit.Word, 1) << @intCast(tail_bits - 1)) };
    const byte_map = [_]find_bit.Word{
        @as(find_bit.Word, 0xa5) << @intCast(find_bit.bits_per_long - 8),
        @as(find_bit.Word, 0x11),
    };

    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_next_bit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_next_andnot_bit(&set_map, &andnot_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_next_zero_bit(&zero_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary), find_bit.find_last_bit(&set_map, nbits));

    const last_aligned_byte = find_bit.bits_per_long - 8;
    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&byte_map, last_aligned_byte));
    try std.testing.expectEqual(@as(u8, 0x11), find_bit.getValue8(&byte_map, find_bit.bits_per_long));
}

test "phase1 helper ports A string parse copy and replacement replay" {
    const parsed = string.memparse("-16 trailing");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -16))), parsed.value);
    try std.testing.expectEqualStrings(" trailing", parsed.rest);

    var padded = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 2), string.strscpy_pad(&padded, &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0 }, &padded);

    var single = [_]u8{7};
    try std.testing.expectEqual(@as(isize, -7), string.strscpy(single[0..], "x"));
    try std.testing.expectEqual(@as(u8, 0), single[0]);

    var spaces = [_]u8{ ' ', 'a', ' ', 'b', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("ab", string.remove_spaces(&spaces));

    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(&replace_buf, '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '+', 'b', 0, '-' }, &replace_buf);
}

test "phase1 helper ports A rbtree cached singleton and alias replay" {
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

    var singleton = Entry{ .key = 7, .serial = 0 };
    var root = rbtree.RootCached.init();
    _ = rbtree.rb_add_cached(&singleton.node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &singleton.node), rbtree.rb_first_cached(&root));
    try std.testing.expect(rbtree.rb_erase_cached(&singleton.node, &root) == null);
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), root.root.node);

    var entries = [_]Entry{
        .{ .key = 10, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 10, .serial = 3 },
        .{ .key = 10, .serial = 4 },
    };
    for (&entries) |*entry| {
        _ = rbtree.rb_add_cached(&entry.node, &root, less);
    }

    const wanted = @as(i32, 10);
    var iter = rbtree.matchIterator(&wanted, &root.root, key_cmp);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }
    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 3, 4 }, serials[0..count]);

    rbtree.rb_erase_init_cached(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(rbtree.rb_first(&root.root), rbtree.rb_first_cached(&root));
}
