const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "phase1 helper ports a tail copy and clump masking stay aligned" {
    const count = bitmap.bits_per_long + 5;
    const size = bitmap.bits_per_long * 3;
    const sentinel = @as(bitmap.Word, 0xaa55_aa55_aa55_aa55);
    const src = [_]bitmap.Word{ 0, ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    var dst = [_]bitmap.Word{ sentinel, sentinel, sentinel, sentinel };

    bitmap.copyAndExtend(dst[0..3], src[0..2], count, size);
    try std.testing.expectEqual(@as(bitmap.Word, 0), dst[0]);
    try std.testing.expectEqual(bitmap.lastWordMask(count), dst[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), dst[2]);
    try std.testing.expectEqual(sentinel, dst[3]);

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), find_bit.findFirstClump8(&clump, dst[0..2], count));
    try std.testing.expectEqual(@as(u8, 0b0001_1111), clump);
}

test "phase1 helper ports a andnot tail scans ignore masked-out tail noise" {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 7) };
    const rhs = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 7 };

    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.findFirstAndNotBit(&lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 2), find_bit.find_next_andnot_bit(&lhs, &rhs, nbits, find_bit.bits_per_long + 1));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextAndNotBit(&lhs, &rhs, nbits, find_bit.bits_per_long + 3));

    const exhausted = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 7 };
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findFirstAndNotBit(&exhausted, &rhs, nbits));
}

test "phase1 helper ports a sysfs and exact string lookups keep their own boundaries" {
    const haystack = [_][]const u8{ "off", "auto\n", "auto", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 1), string.sysfs_match_string(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 2), string.matchString(haystack[0..], "auto"));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(haystack[0..], "auto"));

    const cstr = [_]u8{ 'm', 'o', 'd', 'e', 0, 'x' };
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&cstr, cstr.len, 'x'));
    try std.testing.expectEqual(@as(?usize, 4), string.strnchr(&cstr, cstr.len, 0));
}

test "phase1 helper ports a cached leftmost promotion stays stable across duplicate misses" {
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

    var root_entry = Entry{ .key = 10, .serial = 0 };
    var left_entry = Entry{ .key = 5, .serial = 1 };
    var right_entry = Entry{ .key = 15, .serial = 2 };
    var duplicate_probe = Entry{ .key = 10, .serial = 99 };
    var root = rbtree.RootCached.init();

    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.addCached(&root_entry.node, &root, less));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&left_entry.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, null), rbtree.findAddCached(&right_entry.node, &root, cmp));
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_entry.node), rbtree.firstCached(&root));

    const duplicate = rbtree.findAddCached(&duplicate_probe.node, &root, cmp) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), duplicate);
    try std.testing.expectEqual(@as(?*rbtree.Node, &left_entry.node), rbtree.firstCached(&root));

    const promoted = rbtree.eraseCached(&left_entry.node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &root_entry.node), promoted);
    try std.testing.expectEqual(@as(?*rbtree.Node, &root_entry.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
