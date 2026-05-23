const std = @import("std");
const bitmap = @import("bitmap_helpers");
const find_bit = @import("find_bit_helpers");
const string = @import("string_helpers");
const rbtree = @import("rbtree_helpers");

test "phase1 helper ports A bitmap copy-and-extend replay keeps masked tails aligned" {
    const count = bitmap.bits_per_long + 5;
    const size = bitmap.bits_per_long * 3;
    const src = [_]bitmap.Word{
        0b101101,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9),
        ~@as(bitmap.Word, 0),
    };

    var direct_cleared = [_]bitmap.Word{ 0, 0, 0 };
    var alias_cleared = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.copyClearTail(&direct_cleared, src[0..2], count);
    bitmap.bitmap_copy_clear_tail(&alias_cleared, src[0..2], count);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_cleared, &alias_cleared);
    try std.testing.expectEqual(@as(bitmap.Word, 0b101101), direct_cleared[0]);
    try std.testing.expectEqual(
        @as(bitmap.Word, (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 4)),
        direct_cleared[1],
    );

    var direct_extended = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
    };
    var alias_extended = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
    };
    bitmap.copyAndExtend(&direct_extended, src[0..2], count, size);
    bitmap.bitmap_copy_and_extend(&alias_extended, src[0..2], count, size);
    try std.testing.expectEqualSlices(bitmap.Word, &direct_extended, &alias_extended);
    try std.testing.expectEqual(@as(bitmap.Word, 0b101101), direct_extended[0]);
    try std.testing.expectEqual(
        @as(bitmap.Word, (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 4)),
        direct_extended[1],
    );
    try std.testing.expectEqual(@as(bitmap.Word, 0), direct_extended[2]);
}

test "phase1 helper ports A find-bit clump replay rescans byte windows across words" {
    const nbits = find_bit.bits_per_long + 8;
    const words = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 5),
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 6),
    };

    var direct_clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&direct_clump, &words, nbits));
    try std.testing.expectEqual(@as(u8, 0b0010_0100), direct_clump);

    var same_byte_clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findNextClump8(&same_byte_clump, &words, nbits, 3));
    try std.testing.expectEqual(direct_clump, same_byte_clump);

    var tail_clump: u8 = 0;
    try std.testing.expectEqual(
        @as(usize, find_bit.bits_per_long),
        find_bit.find_next_clump8(&tail_clump, &words, nbits, 8),
    );
    try std.testing.expectEqual(@as(u8, 0b0101_0010), tail_clump);

    var untouched: u8 = 0x7c;
    try std.testing.expectEqual(@as(usize, nbits), find_bit._find_next_clump8(&untouched, &words, nbits, nbits));
    try std.testing.expectEqual(@as(u8, 0x7c), untouched);
}

test "phase1 helper ports A string replay keeps sysfs and NUL-bounded searches aligned" {
    const newline_beta = "beta\n";
    const embedded_beta = [_]u8{ 'b', 'e', 't', 'a', 0, 'x' };
    const haystack = [_][]const u8{
        "alpha",
        newline_beta,
        &embedded_beta,
        "gamma",
    };

    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "beta"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "beta\n"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "beta"));
    try std.testing.expectEqual(@as(?usize, null), string.sysfsMatchString(haystack[0..1], "beta"));

    const nul_bounded = [_]u8{ 'a', 'b', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&embedded_beta, embedded_beta.len, 'x'));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&nul_bounded, 3, 0));
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr("beta", 4, 'a'));
}

test "phase1 helper ports A cached rbtree replay keeps duplicate leftmost ownership stable" {
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

    var first_duplicate = Entry{ .key = 5, .serial = 0 };
    var second_duplicate = Entry{ .key = 5, .serial = 1 };
    var larger = Entry{ .key = 9, .serial = 2 };
    var smaller = Entry{ .key = 3, .serial = 3 };
    var root = rbtree.RootCached.init();

    _ = rbtree.addCached(&first_duplicate.node, &root, less);
    _ = rbtree.addCached(&second_duplicate.node, &root, less);
    _ = rbtree.addCached(&larger.node, &root, less);

    try std.testing.expectEqual(@as(?*rbtree.Node, &first_duplicate.node), rbtree.firstCached(&root));

    rbtree.eraseInitCached(&first_duplicate.node, &root);
    try std.testing.expect(rbtree.emptyNode(&first_duplicate.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &second_duplicate.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));

    const wanted = @as(i32, 5);
    var iter = rbtree.matchIterator(&wanted, &root.root, cmp);
    const only_match = iter.next() orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &second_duplicate.node), only_match);
    try std.testing.expect(iter.next() == null);

    try std.testing.expectEqual(@as(?*rbtree.Node, &smaller.node), rbtree.rb_add_cached(&smaller.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, &smaller.node), rbtree.rb_first_cached(&root));
    try std.testing.expectEqual(rbtree.rb_first(&root.root), rbtree.rb_first_cached(&root));
}
