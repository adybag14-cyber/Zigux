const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap allocation aliases feed tail-safe find-bit scans and formatting" {
    const allocator = std.testing.allocator;
    const nbits = bits_per_long + 7;
    var allocated: ?[]Word = try bitmap.bitmap_zalloc(allocator, nbits);
    defer bitmap.bitmap_free(allocator, &allocated);

    const map = allocated.?;
    bitmap.bitmap_set(map, 1, 2);
    bitmap.bitmap_set(map, bits_per_long - 1, 1);
    bitmap.bitmap_set(map, bits_per_long + 2, 3);
    bitmap.bitmap_set(map, nbits - 1, 1);

    var copied = [_]Word{ 0, ~@as(Word, 0) };
    bitmap.bitmap_copy_clear_tail(&copied, map, nbits);

    var mask = std.mem.zeroes([2]Word);
    bitmap.bitmap_set(&mask, 1, 1);
    bitmap.bitmap_set(&mask, bits_per_long + 2, 1);
    bitmap.bitmap_set(&mask, nbits - 1, 1);

    try std.testing.expectEqual(@as(usize, 7), bitmap.bitmap_weight(&copied, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.find_first_bit(&copied, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.find_first_and_bit(&copied, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 2), find_bit.find_next_andnot_bit(&copied, &mask, nbits, 2));
    try std.testing.expectEqual(bits_per_long + 2, find_bit.find_next_and_bit(&copied, &mask, nbits, bits_per_long));
    try std.testing.expectEqual(nbits - 1, find_bit.find_last_bit(&copied, nbits));

    var rendered: [64]u8 = undefined;
    const rendered_len = bitmap.bitmap_scnprintf(&copied, nbits, &rendered);

    var expected: [64]u8 = undefined;
    const expected_text = try std.fmt.bufPrint(
        &expected,
        "1-2,{d},{d}-{d},{d}",
        .{ bits_per_long - 1, bits_per_long + 2, bits_per_long + 4, nbits - 1 },
    );
    try std.testing.expectEqualStrings(expected_text, rendered[0..rendered_len]);
}

test "string aliases keep c-string padding and sysfs matching reusable" {
    var padded: [12]u8 = undefined;
    @memset(&padded, 0xaa);
    try std.testing.expectEqual(@as(isize, 5), string.strscpy_pad(&padded, "portA\x00ignored"));
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 'p', 'o', 'r', 't', 'A', 0, 0, 0, 0, 0, 0, 0 },
        &padded,
    );
    try std.testing.expectEqual(@as(?usize, null), string.memchr_inv(padded[5..], 0));

    var compact = [_]u8{ ' ', 'b', 'i', 't', 'm', 'a', 'p', ' ', 0, 'x' };
    const trimmed = string.strstrip(&compact);
    try std.testing.expectEqualStrings("bitmap", trimmed);
    try std.testing.expectEqual(@as(usize, 6), string.strreplace(trimmed, 'm', 'M'));
    try std.testing.expectEqualStrings("bitMap", trimmed);

    const choices = [_][]const u8{ "bitmap\n", "find_bit", "rbtree\x00old" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(&choices, "bitmap"));
    try std.testing.expectEqual(@as(?usize, 1), string.match_string(&choices, "find_bit"));
    try std.testing.expectEqual(@as(?usize, 2), string.match_string(&choices, "rbtree"));
}

test "rbtree duplicate iteration survives erase-init node reuse" {
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
            if (key.* < entry.key) return -1;
            if (key.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 12 },
        .{ .key = 7 },
        .{ .key = 7 },
        .{ .key = 20 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate_key: i32 = 7;
    var matches = rbtree.matchIterator(&duplicate_key, &root, cmp_key);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), matches.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), matches.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, null), matches.next());

    rbtree.eraseInit(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));

    matches = rbtree.matchIterator(&duplicate_key, &root, cmp_key);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), matches.next());
    try std.testing.expectEqual(@as(?*rbtree.Node, null), matches.next());

    entries[1].key = 5;
    rbtree.add(&entries[1].node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[2].node), rbtree.find(&duplicate_key, &root, cmp_key));
}
