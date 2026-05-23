const std = @import("std");
const bitmap = @import("bitmap_helpers");
const find_bit = @import("find_bit_helpers");
const string = @import("string_helpers");
const rbtree = @import("rbtree_helpers");

test "phase1 helper ports A bitmap tail-logic replay keeps masked aliases aligned" {
    const nbits = bitmap.bits_per_long + 5;
    const lhs = [_]bitmap.Word{
        0b10110,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
    };
    const rhs = [_]bitmap.Word{
        0b00110,
        (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 10),
    };

    var direct_complement = [_]bitmap.Word{ 0, 0 };
    var alias_complement = [_]bitmap.Word{ 0, 0 };
    bitmap.complement(&direct_complement, &lhs, nbits);
    bitmap.bitmap_complement(&alias_complement, &lhs, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_complement, &alias_complement);
    try std.testing.expectEqual((~lhs[1]) & bitmap.lastWordMask(nbits), direct_complement[1]);

    var direct_and = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    var alias_and = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    try std.testing.expectEqual(bitmap.andBits(&direct_and, &lhs, &rhs, nbits), bitmap.bitmap_and(&alias_and, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &direct_and, &alias_and);
    try std.testing.expectEqual(@as(bitmap.Word, 0b00110), direct_and[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 1) << 4, direct_and[1]);

    var direct_andnot = [_]bitmap.Word{ 0, 0 };
    var alias_andnot = [_]bitmap.Word{ 0, 0 };
    try std.testing.expectEqual(bitmap.andNotBits(&direct_andnot, &lhs, &rhs, nbits), bitmap.bitmap_andnot(&alias_andnot, &lhs, &rhs, nbits));
    try std.testing.expectEqualSlices(bitmap.Word, &direct_andnot, &alias_andnot);
    try std.testing.expectEqual(@as(bitmap.Word, 0b10000), direct_andnot[0]);
    try std.testing.expectEqual(@as(bitmap.Word, 1) << 1, direct_andnot[1]);

    const outside_only = [_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 9 };
    try std.testing.expect(bitmap.equal(&outside_only, &[_]bitmap.Word{ 0, 0 }, nbits));
    try std.testing.expect(bitmap.bitmap_equal(&outside_only, &[_]bitmap.Word{ 0, 0 }, nbits));
    try std.testing.expect(!bitmap.intersects(&outside_only, &outside_only, nbits));
    try std.testing.expect(!bitmap.bitmap_intersects(&outside_only, &outside_only, nbits));
    try std.testing.expect(bitmap.subset(&outside_only, &[_]bitmap.Word{ 0, 0 }, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&outside_only, &[_]bitmap.Word{ 0, 0 }, nbits));
}

test "phase1 helper ports A find-bit replay keeps last-bit and boundary scans aligned" {
    const tail_bits: usize = 5;
    const boundary = find_bit.bits_per_long + tail_bits - 1;
    const nbits = boundary + 1;
    const set_map = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(find_bit.bits_per_long - 1),
        (@as(find_bit.Word, 1) << 1) |
            (@as(find_bit.Word, 1) << @intCast(tail_bits - 1)) |
            (@as(find_bit.Word, 1) << @intCast(tail_bits + 2)),
    };
    const zero_map = [_]find_bit.Word{
        ~(@as(find_bit.Word, 1) << @intCast(find_bit.bits_per_long - 1)),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << @intCast(tail_bits - 1))),
    };
    const and_lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << @intCast(tail_bits - 1)) };
    const and_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << @intCast(tail_bits - 1)) | (@as(find_bit.Word, 1) << @intCast(tail_bits + 2)),
    };

    try std.testing.expectEqual(boundary, find_bit.findLastBit(&set_map, nbits));
    try std.testing.expectEqual(boundary, find_bit.find_next_bit(&set_map, nbits, boundary));
    try std.testing.expectEqual(nbits, find_bit.find_next_bit(&set_map, nbits, boundary + 1));

    try std.testing.expectEqual(find_bit.bits_per_long - 1, find_bit.findNextZeroBit(&zero_map, nbits, find_bit.bits_per_long - 1));
    try std.testing.expectEqual(boundary, find_bit.find_next_zero_bit(&zero_map, nbits, boundary));
    try std.testing.expectEqual(nbits, find_bit.find_next_zero_bit(&zero_map, nbits, boundary + 1));

    try std.testing.expectEqual(boundary, find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, find_bit.bits_per_long));
    try std.testing.expectEqual(boundary, find_bit._find_next_and_bit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(nbits, find_bit._find_next_and_bit(&and_lhs, &and_rhs, nbits, boundary + 1));
}

test "phase1 helper ports A string replay keeps NUL-bounded copies and matches aligned" {
    const embedded = [_]u8{ 'b', 'e', 't', 'a', 0, 'x' };
    const haystack = [_][]const u8{
        "alpha",
        &embedded,
        "beta",
        "gamma",
    };

    var direct = [_]u8{ 9, 9, 9, 9, 9, 9 };
    var alias = [_]u8{ 9, 9, 9, 9, 9, 9 };
    try std.testing.expectEqual(@as(isize, 4), string.strscpyPad(direct[0..], &embedded));
    try std.testing.expectEqual(@as(isize, 4), string.strscpy_pad(alias[0..], &embedded));
    try std.testing.expectEqualSlices(u8, &direct, &alias);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'b', 'e', 't', 'a', 0, 0 }, &direct);

    try std.testing.expect(string.strEq(&embedded, "beta"));
    try std.testing.expect(string.streq(&embedded, "beta"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(haystack[0..], "beta"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(haystack[0..], "beta"));

    var dirty = [_]u8{0} ** 24;
    dirty[15] = 1;
    try std.testing.expectEqual(@as(?usize, 15), string.memchrInv(dirty[0..], 0));
    try std.testing.expectEqual(@as(?usize, 15), string.memchr_inv(dirty[0..], 0));

    var replace_buf = [_]u8{ 'a', 0, 'b', 'a' };
    try std.testing.expectEqual(@as(usize, 1), string.replaceChar(replace_buf[0..], 'a', 'z'));
    try std.testing.expectEqual(@as(usize, 1), string.strreplace(replace_buf[0..], 'z', 'q'));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'q', 0, 'b', 'a' }, &replace_buf);
}

test "phase1 helper ports A cached rbtree replay keeps non-leftmost replacement ownership stable" {
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

    const firstKey = struct {
        fn read(root: *const rbtree.RootCached) ?i32 {
            const node = rbtree.firstCached(root) orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", node);
            return entry.key;
        }
    }.read;

    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 20, .serial = 2 },
    };
    var primary_replacement = Entry{ .key = 20, .serial = 3 };
    var alias_replacement = Entry{ .key = 20, .serial = 3 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        _ = rbtree.addCached(&primary_entry.node, &primary_root, less);
        _ = rbtree.rb_add_cached(&alias_entry.node, &alias_root, less);
    }

    try std.testing.expectEqual(@as(?i32, 5), firstKey(&primary_root));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    rbtree.replaceNodeCached(&primary_entries[2].node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_entries[2].node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(@as(?i32, 5), firstKey(&primary_root));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.rb_first(&alias_root.root), rbtree.rb_first_cached(&alias_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.eraseCached(&primary_replacement.node, &primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_erase_cached(&alias_replacement.node, &alias_root));
    try std.testing.expectEqual(@as(?i32, 5), firstKey(&primary_root));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    var primary_singleton = Entry{ .key = 7, .serial = 0 };
    var alias_singleton = Entry{ .key = 7, .serial = 0 };
    var primary_singleton_root = rbtree.RootCached.init();
    var alias_singleton_root = rbtree.RootCached.init();

    _ = rbtree.addCached(&primary_singleton.node, &primary_singleton_root, less);
    _ = rbtree.rb_add_cached(&alias_singleton.node, &alias_singleton_root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_singleton.node), rbtree.firstCached(&primary_singleton_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_singleton.node), rbtree.rb_first_cached(&alias_singleton_root));

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.eraseCached(&primary_singleton.node, &primary_singleton_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_erase_cached(&alias_singleton.node, &alias_singleton_root));
    try std.testing.expect(rbtree.firstCached(&primary_singleton_root) == null);
    try std.testing.expect(rbtree.rb_first_cached(&alias_singleton_root) == null);
    try std.testing.expect(primary_singleton_root.root.node == null);
    try std.testing.expect(alias_singleton_root.root.node == null);
}
