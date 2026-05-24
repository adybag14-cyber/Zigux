const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap weighted helpers clamp partial-tail predicates" {
    const nbits = bitmap.bits_per_long + 5;
    const or_lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 8) };
    const or_rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 9) };
    var or_dst = [_]bitmap.Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weighted_or(&or_dst, &or_lhs, &or_rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&or_dst, nbits));
    try std.testing.expect(!bitmap.bitmap_empty(&or_dst, nbits));
    try std.testing.expect(!bitmap.bitmap_full(&or_dst, nbits));
    try std.testing.expect(bitmap.bitmap_subset(
        &[_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) },
        &or_dst,
        nbits,
    ));

    const xor_lhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 1) | (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 8) };
    const xor_rhs = [_]bitmap.Word{ 0, (@as(bitmap.Word, 1) << 3) | (@as(bitmap.Word, 1) << 4) | (@as(bitmap.Word, 1) << 9) };
    var xor_dst = [_]bitmap.Word{ 0, 0 };

    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weighted_xor(&xor_dst, &xor_lhs, &xor_rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&xor_dst, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&xor_dst, &[_]bitmap.Word{ 0, @as(bitmap.Word, 1) << 1 }, nbits));
}

test "phase1 helper ports A find_bit byte reads keep aligned word boundaries explicit" {
    const last_aligned_byte = find_bit.bits_per_long - 8;
    const byte_words = [_]find_bit.Word{
        (@as(find_bit.Word, 0x42) << 8) | (@as(find_bit.Word, 0xa5) << @intCast(last_aligned_byte)),
        @as(find_bit.Word, 0x11) << 8,
    };

    try std.testing.expectEqual(@as(u8, 0x42), find_bit.getValue8(&byte_words, 8));
    try std.testing.expectEqual(@as(u8, 0xa5), find_bit.getValue8(&byte_words, last_aligned_byte));
    try std.testing.expectEqual(@as(u8, 0x11), find_bit.getValue8(&byte_words, find_bit.bits_per_long + 8));

    const nbits = find_bit.bits_per_long * 2;
    const scan_words = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(last_aligned_byte),
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 8),
    };
    try std.testing.expectEqual(@as(usize, last_aligned_byte), find_bit.findFirstBit(&scan_words, nbits));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long), find_bit.findNextBit(&scan_words, nbits, last_aligned_byte + 1));
    try std.testing.expectEqual(@as(usize, find_bit.bits_per_long + 8), find_bit.findNextBit(&scan_words, nbits, find_bit.bits_per_long + 1));
}

test "phase1 helper ports A string prefix and match helpers honor C-string edges" {
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&[_]u8{ 'a', 'b', 'c', 0, 'x' }, "abc"));
    try std.testing.expect(string.strEndsWith("kernel", "nel"));
    try std.testing.expect(!string.strEndsWith("kernel", "nex"));
    try std.testing.expectEqual(@as(?usize, 1), string.strnchr("abc", 2, 'b'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&[_]u8{ 'a', 0, 'b' }, 3, 'b'));
    try std.testing.expect(string.sysfsStreq("mode\n", "mode"));

    const sysfs_haystack = [_][]const u8{ "off", "auto\n", "on" };
    try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(sysfs_haystack[0..], "auto"));

    const cstring_haystack = [_][]const u8{ &[_]u8{ 'a', 0, 'x' }, "beta", "alpha" };
    try std.testing.expectEqual(@as(?usize, 0), string.matchString(cstring_haystack[0..], "a"));
}

test "phase1 helper ports A cached rbtree helpers preserve singleton teardown and non-leftmost replacement" {
    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var singleton = Entry{ .key = 7 };
    var singleton_root = rbtree.RootCached.init();

    _ = rbtree.addCached(&singleton.node, &singleton_root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &singleton.node), rbtree.firstCached(&singleton_root));
    try std.testing.expect(rbtree.eraseCached(&singleton.node, &singleton_root) == null);
    try std.testing.expect(rbtree.firstCached(&singleton_root) == null);
    try std.testing.expect(singleton_root.root.node == null);

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 20 },
    };
    var replacement = Entry{ .key = 20 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    rbtree.replaceNodeCached(&entries[2].node, &replacement.node, &root);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));
    try std.testing.expectEqual(rbtree.first(&root.root), rbtree.firstCached(&root));
}
