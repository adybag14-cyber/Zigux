const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap state and replace aliases keep tail-masked results aligned" {
    const nbits = bitmap.bits_per_long + 5;

    try std.testing.expectEqual(
        bitmap.bitsToWords(nbits) * @sizeOf(bitmap.Word),
        bitmap.bitmap_size(nbits),
    );

    var direct = [_]bitmap.Word{ 0x55aa, 0x55aa };
    var alias = [_]bitmap.Word{ 0x55aa, 0x55aa };
    bitmap.zero(&direct, nbits);
    bitmap.bitmap_zero(&alias, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expect(bitmap.empty(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_empty(&alias, nbits));

    bitmap.fill(&direct, nbits);
    bitmap.bitmap_fill(&alias, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &direct, &alias);
    try std.testing.expect(bitmap.full(&direct, nbits));
    try std.testing.expect(bitmap.bitmap_full(&alias, nbits));
    try std.testing.expectEqual(bitmap.weight(&direct, nbits), bitmap.bitmap_weight(&alias, nbits));

    const old = [_]bitmap.Word{
        0b1111_0000,
        (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 4),
    };
    const new = [_]bitmap.Word{
        0b0000_1111,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 7),
    };
    const mask = [_]bitmap.Word{
        0b0011_1100,
        (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 7),
    };
    var replaced = [_]bitmap.Word{ 0, 0 };
    var alias_replaced = [_]bitmap.Word{ 0, 0 };
    bitmap.replace(&replaced, &old, &new, &mask, nbits);
    bitmap.bitmap_replace(&alias_replaced, &old, &new, &mask, nbits);
    try std.testing.expectEqualSlices(bitmap.Word, &replaced, &alias_replaced);
    try std.testing.expectEqual(@as(bitmap.Word, 0b1100_1100), replaced[0]);
    try std.testing.expectEqual(
        @as(bitmap.Word, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 2) | (@as(bitmap.Word, 1) << 4)),
        replaced[1],
    );
}

test "phase1 helper ports A find_bit zero and next-scan aliases keep partial windows aligned" {
    const nbits = find_bit.bits_per_long + 6;
    const boundary = find_bit.bits_per_long;

    const zero_map = [_]find_bit.Word{
        ~@as(find_bit.Word, 0),
        find_bit.lastWordMask(nbits) & ~((@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4)),
    };
    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.findFirstZeroBit(&zero_map, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.find_first_zero_bit(&zero_map, nbits));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextZeroBit(&zero_map, nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.find_next_zero_bit(&zero_map, nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextZeroBit(&zero_map, nbits, boundary + 5));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.find_next_zero_bit(&zero_map, nbits, nbits + 3));

    const set_map = [_]find_bit.Word{
        @as(find_bit.Word, 1) << 5,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4),
    };
    const and_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 8),
    };
    const and_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 8),
    };
    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.findNextBit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 1), find_bit.find_next_bit(&set_map, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextBit(&set_map, nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.find_next_bit(&set_map, nbits, boundary + 2));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&set_map, nbits, boundary + 5));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, boundary + 4), find_bit.find_next_and_bit(&and_lhs, &and_rhs, nbits, boundary));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndBit(&and_lhs, &and_rhs, nbits, boundary + 5));
}

test "phase1 helper ports A string prefix suffix trim and replace helpers keep C-string boundaries aligned" {
    var direct = [_]u8{ 'a', '-', 'b', 0, '-' };
    var alias = [_]u8{ 'a', '-', 'b', 0, '-' };
    try std.testing.expectEqual(
        string.replaceChar(direct[0..], '-', '+'),
        string.strreplace(alias[0..], '-', '+'),
    );
    try std.testing.expectEqualSlices(u8, &direct, &alias);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', '+', 'b', 0, '-' }, direct[0..]);

    try std.testing.expectEqualStrings("lead", string.skipSpaces("  \tlead"));
    try std.testing.expectEqualStrings("lead", string.skip_spaces("  \tlead"));
    try std.testing.expect(string.streq(&[_]u8{ 'a', 0, 'z' }, &[_]u8{ 'a', 0, 'x' }));
    try std.testing.expect(!string.strEq("abc", "abd"));

    var trim_buf = [_]u8{ ' ', 'o', 'k', ' ', 0, 'x' };
    try std.testing.expectEqualStrings("ok", string.trimSpaces(trim_buf[0..]));
    try std.testing.expectEqualStrings("ok", string.strim(trim_buf[0..]));
    try std.testing.expectEqualStrings("ok", string.strstrip(trim_buf[0..]));

    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix("kernel", "ker"));
    try std.testing.expectEqual(@as(usize, 3), string.str_has_prefix("kernel", "ker"));
    try std.testing.expect(string.strstarts("kernel", "ker"));
    try std.testing.expect(string.strEndsWith("kernel", "nel"));
    try std.testing.expect(string.str_ends_with("kernel", "nel"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));

    var dirty = [_]u8{'a'} ** 24;
    dirty[@sizeOf(usize)] = 'b';
    try std.testing.expectEqual(@as(?usize, @sizeOf(usize)), string.memchrInv(dirty[0..], 'a'));
    try std.testing.expectEqual(string.memchrInv(dirty[0..], 'a'), string.memchr_inv(dirty[0..], 'a'));
}

test "phase1 helper ports A rbtree cached find-add and replace aliases keep first pointers aligned" {
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
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const nodeId = struct {
        fn read(node: ?*rbtree.Node) ?struct { i32, usize } {
            const current = node orelse return null;
            const entry: *const Entry = @fieldParentPtr("node", current);
            return .{ entry.key, entry.serial };
        }
    }.read;

    var primary_first = Entry{ .key = 10, .serial = 0 };
    var alias_first = Entry{ .key = 10, .serial = 0 };
    var primary_leftmost = Entry{ .key = 5, .serial = 1 };
    var alias_leftmost = Entry{ .key = 5, .serial = 1 };
    var primary_right = Entry{ .key = 15, .serial = 2 };
    var alias_right = Entry{ .key = 15, .serial = 2 };
    var primary_duplicate = Entry{ .key = 10, .serial = 3 };
    var alias_duplicate = Entry{ .key = 10, .serial = 3 };
    var primary_replacement = Entry{ .key = 5, .serial = 4 };
    var alias_replacement = Entry{ .key = 5, .serial = 4 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(
        nodeId(rbtree.addCached(&primary_first.node, &primary_root, less)),
        nodeId(rbtree.rb_add_cached(&alias_first.node, &alias_root, less)),
    );
    try std.testing.expectEqual(
        nodeId(rbtree.firstCached(&primary_root)),
        nodeId(rbtree.rb_first_cached(&alias_root)),
    );

    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_leftmost.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_leftmost.node, &alias_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&primary_right.node, &primary_root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.rb_find_add_cached(&alias_right.node, &alias_root, cmp));
    try std.testing.expectEqual(
        nodeId(rbtree.firstCached(&primary_root)),
        nodeId(rbtree.rb_first_cached(&alias_root)),
    );

    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_root, cmp) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(nodeId(primary_existing), nodeId(alias_existing));
    try std.testing.expectEqual(
        nodeId(rbtree.firstCached(&primary_root)),
        nodeId(rbtree.rb_first_cached(&alias_root)),
    );

    rbtree.replaceNodeCached(&primary_leftmost.node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_leftmost.node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(
        nodeId(rbtree.firstCached(&primary_root)),
        nodeId(rbtree.rb_first_cached(&alias_root)),
    );
    try std.testing.expectEqual(
        @as(?struct { i32, usize }, .{ 5, 4 }),
        nodeId(rbtree.firstCached(&primary_root)),
    );
    try std.testing.expectEqual(
        nodeId(rbtree.first(&primary_root.root)),
        nodeId(rbtree.rb_first_cached(&alias_root)),
    );
}
