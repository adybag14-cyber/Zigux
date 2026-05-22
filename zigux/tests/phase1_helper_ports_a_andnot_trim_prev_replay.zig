const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap andnot replace replay" {
    const nbits = bitmap.bits_per_long + 5;
    const in_range_tail = (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4);
    const out_of_range_tail = @as(bitmap.Word, 1) << 9;

    const lhs = [_]bitmap.Word{
        0b1110,
        in_range_tail | out_of_range_tail,
    };
    const rhs = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 10),
    };

    var direct_andnot = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    var alias_andnot = [_]bitmap.Word{ 0, 0 };
    try std.testing.expect(bitmap.andNotBits(&direct_andnot, &lhs, &rhs, nbits));
    try std.testing.expectEqual(true, bitmap.bitmap_andnot(&alias_andnot, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &direct_andnot, &alias_andnot);
    try std.testing.expectEqual(@as(bitmap.Word, 0b0100), direct_andnot[0]);
    try std.testing.expectEqual(@as(bitmap.Word, @as(bitmap.Word, 1) << 1), direct_andnot[1]);
    try std.testing.expectEqual(@as(usize, 2), bitmap.weight(&direct_andnot, nbits));

    const only_out_of_range = [_]bitmap.Word{
        0,
        out_of_range_tail,
    };
    var zeroed = [_]bitmap.Word{ 0x55aa, 0xaa55 };
    try std.testing.expect(!bitmap.andNotBits(&zeroed, &only_out_of_range, &[_]bitmap.Word{ 0, 0 }, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &[_]bitmap.Word{ 0, 0 }, &zeroed);

    const old = [_]bitmap.Word{
        0b0101,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4),
    };
    const new = [_]bitmap.Word{
        0b1010,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    const mask = [_]bitmap.Word{
        0b1111,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 9),
    };

    var direct_replace = [_]bitmap.Word{ 0, 0 };
    var alias_replace = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    bitmap.replace(&direct_replace, &old, &new, &mask, nbits);
    bitmap.bitmap_replace(&alias_replace, &old, &new, &mask, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_replace, &alias_replace);
    try std.testing.expectEqual(@as(bitmap.Word, 0b1010), direct_replace[0]);
    try std.testing.expectEqual(@as(bitmap.Word, (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 4)), direct_replace[1]);
    try std.testing.expect(bitmap.equal(&direct_replace, &alias_replace, nbits));
}

test "phase1 helper ports A find_bit shared-mask replay" {
    const nbits = find_bit.bits_per_long + 5;
    const boundary = find_bit.bits_per_long;
    const tail_visible = @as(find_bit.Word, 1) << 3;
    const tail_hidden = @as(find_bit.Word, 1) << 9;

    const lhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary - 1),
        tail_visible | tail_hidden,
    };
    const rhs = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary - 1),
        tail_visible,
    };
    const mask = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary - 1),
        tail_hidden,
    };

    try std.testing.expectEqual(@as(usize, boundary - 1), find_bit.findFirstAndBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 3), find_bit.findNextAndBit(&lhs, &rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 3), find_bit.find_next_and_bit(&lhs, &rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 3), find_bit.findFirstAndNotBit(&lhs, &mask, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &mask, nbits, boundary + 4));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_first_and_bit(&[_]find_bit.Word{ 0, tail_hidden }, &[_]find_bit.Word{ 0, tail_hidden }, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, boundary - 8), find_bit.findFirstClump8(&clump, &lhs, nbits));
    try std.testing.expectEqual(@as(u8, 0b1000_0000), clump);
    try std.testing.expectEqual(@as(usize, boundary), find_bit.findNextClump8(&clump, &lhs, nbits, boundary));
    try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);
    try std.testing.expectEqual(@as(usize, boundary + 3), find_bit.findLastBit(&lhs, nbits));
}

test "phase1 helper ports A string trim remove replace replay" {
    try std.testing.expectEqualStrings("zigux", string.skipSpaces(" \tzigux"));
    try std.testing.expectEqualStrings("zigux", string.skip_spaces("\nzigux"));

    var trim_buf = [_]u8{ ' ', '\t', 'z', 'i', 'g', ' ', 0, 'x' };
    const trimmed = string.trimSpaces(trim_buf[0..]);
    try std.testing.expectEqualStrings("zig", trimmed);
    try std.testing.expectEqualStrings("zig", string.strim(trim_buf[0..]));
    try std.testing.expectEqualStrings("zig", string.strstrip(trim_buf[0..]));

    var blank_buf = [_]u8{ ' ', '\t', 0, 'x' };
    const blank = string.trimSpaces(blank_buf[0..]);
    try std.testing.expectEqual(@as(usize, 0), blank.len);
    try std.testing.expectEqual(@as(u8, 0), blank_buf[0]);

    var remove_buf = [_]u8{ 'a', ' ', '\t', 'b', ' ', 0, 'x' };
    const removed = string.removeSpaces(remove_buf[0..]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '\t', 'b' }, removed);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '\t', 'b', 0, ' ', 0, 'x' }, &remove_buf);
    try std.testing.expectEqualSlices(u8, removed, string.remove_spaces(remove_buf[0..]));

    var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(@as(usize, 3), string.replaceChar(replace_buf[0..], '-', '+'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '+', 'b', 0, '-' }, &replace_buf);
    try std.testing.expectEqual(@as(usize, 3), string.strreplace(replace_buf[0..], '+', '='));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '=', 'b', 0, '-' }, &replace_buf);
}

test "phase1 helper ports A rbtree prev and cached erase replay" {
    const Entry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    var plain_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
        .{ .key = 12, .serial = 3 },
    };
    var plain_root = rbtree.Root.init();
    for (&plain_entries) |*entry| {
        rbtree.add(&entry.node, &plain_root, less);
    }

    const last = rbtree.last(&plain_root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &plain_entries[2].node), last);
    try std.testing.expectEqual(@as(?*rbtree.Node, &plain_entries[3].node), rbtree.prev(last));
    try std.testing.expectEqual(@as(?*rbtree.Node, &plain_entries[3].node), rbtree.rb_prev(last));
    try std.testing.expectEqual(@as(?*rbtree.Node, &plain_entries[0].node), rbtree.prev(&plain_entries[3].node));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.prev(&plain_entries[1].node));

    var cached_entries = [_]Entry{
        .{ .key = 10, .serial = 10 },
        .{ .key = 5, .serial = 11 },
        .{ .key = 15, .serial = 12 },
        .{ .key = 12, .serial = 13 },
    };
    var cached_root = rbtree.RootCached.init();
    for (&cached_entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &cached_root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[1].node), rbtree.firstCached(&cached_root));
    const promoted = rbtree.eraseCached(&cached_entries[1].node, &cached_root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &cached_entries[0].node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[0].node), rbtree.firstCached(&cached_root));
    try std.testing.expectEqual(rbtree.first(&cached_root.root), rbtree.firstCached(&cached_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_erase_cached(&cached_entries[2].node, &cached_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &cached_entries[0].node), rbtree.rb_first_cached(&cached_root));
    try std.testing.expectEqual(rbtree.first(&cached_root.root), rbtree.firstCached(&cached_root));
}
