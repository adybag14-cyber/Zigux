const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "helper ports A bitmap gaps feed find-bit scans and formatting" {
    const nbits = bits_per_long + 13;
    var map = [_]Word{ 0, 0 };

    bitmap.fill(&map, nbits);
    bitmap.clearRange(&map, 2, 3);
    bitmap.clearRange(&map, bits_per_long + 1, 2);
    bitmap.clearRange(&map, bits_per_long + 11, 2);

    try std.testing.expect(!bitmap.full(&map, nbits));
    try std.testing.expect(!bitmap.empty(&map, nbits));
    try std.testing.expectEqual(nbits - 7, bitmap.weight(&map, nbits));

    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.findFirstZeroBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findNextBit(&map, nbits, 2));
    try std.testing.expectEqual(@as(usize, bits_per_long + 1), find_bit.findNextZeroBit(&map, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 10), find_bit.findLastBit(&map, nbits));

    var formatted = [_]u8{0xaa} ** 64;
    const written = bitmap.scnprintf(&map, nbits, &formatted);
    var expected_storage: [64]u8 = undefined;
    const expected = try std.fmt.bufPrint(
        &expected_storage,
        "0-1,5-{d},{d}-{d}",
        .{ bits_per_long, bits_per_long + 3, bits_per_long + 10 },
    );

    try std.testing.expectEqual(expected.len, written);
    try std.testing.expectEqualSlices(u8, expected, formatted[0..written]);
    try std.testing.expectEqual(@as(u8, 0), formatted[written]);
}

test "helper ports A string padding preserves sysfs token matching" {
    var padded = [_]u8{0xcc} ** 12;
    try std.testing.expectEqual(@as(isize, 6), string.strscpy_pad(&padded, "target"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 't', 'a', 'r', 'g', 'e', 't', 0, 0, 0, 0, 0, 0 }, &padded);

    const haystack = [_][]const u8{
        "target\n",
        "fallback",
        "target-extra",
    };

    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(&haystack, padded[0..]));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(&haystack, padded[0..]));
    try std.testing.expectEqual(@as(usize, 6), string.str_has_prefix(padded[0..], "target"));
}

test "helper ports A rbtree reverse traversal survives cached erase-init" {
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

    const cmp_key = struct {
        fn compare(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
            const key: *const i32 = @ptrCast(@alignCast(key_ptr));
            const entry: *const Entry = @fieldParentPtr("node", node);
            return if (key.* < entry.key) -1 else if (key.* > entry.key) 1 else 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 40 },
        .{ .key = 20 },
        .{ .key = 60 },
        .{ .key = 10 },
        .{ .key = 30 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(&entries[3].node, rbtree.firstCached(&root).?);
    rbtree.eraseInitCached(&entries[3].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[3].node));
    try std.testing.expectEqual(&entries[1].node, rbtree.firstCached(&root).?);

    var reverse_order: [4]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.last(&root.root);
    while (current) |node| : (current = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        reverse_order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 4), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 60, 40, 30, 20 }, reverse_order[0..count]);

    const needle: i32 = 30;
    try std.testing.expectEqual(&entries[4].node, rbtree.findFirst(&needle, &root.root, cmp_key).?);
}
