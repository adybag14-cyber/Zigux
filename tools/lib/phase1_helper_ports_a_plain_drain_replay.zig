const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A plain drain replay" {
    const Word = bitmap.Word;
    const nbits = bitmap.bits_per_long + 13;

    var seed = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };
    var drain = [_]Word{ 0, 0 };

    bitmap.bitmap_zero(&seed, nbits);
    seed[0] = (@as(Word, 1) << 3) | (@as(Word, 1) << 9);
    seed[1] = (@as(Word, 1) << 2) | (@as(Word, 1) << 8) | (@as(Word, 1) << 12);
    bitmap.copyClearTail(&drain, &seed, nbits);

    bitmap.bitmap_fill(&mask, nbits);
    mask[0] = (@as(Word, 1) << 3) | (@as(Word, 1) << 9);
    mask[1] = (@as(Word, 1) << 2);

    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(&seed, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&mask, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 8), find_bit.find_first_andnot_bit(&seed, &mask, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 8), find_bit.find_next_bit(&seed, nbits, bitmap.bits_per_long + 3));

    var combined = [_]Word{ 0, 0 };
    bitmap.bitmap_or(&combined, &seed, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 5), bitmap.bitmap_weight(&combined, nbits));
    bitmap.bitmap_xor(&combined, &combined, &mask, nbits);
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&combined, nbits));

    var text_buf: [32]u8 = undefined;
    @memset(&text_buf, 0);
    try std.testing.expectEqual(@as(usize, 15), string.strlcpy(&text_buf, "  zigux\tdrain  "));
    try std.testing.expectEqualStrings("zigux\tdrain", string.strim(&text_buf));

    var label: [24]u8 = undefined;
    @memset(&label, 0);
    try std.testing.expectEqual(@as(usize, 12), string.strlcpy(&label, "lane6-rbtree"));
    var padded: [16]u8 = undefined;
    @memset(&padded, 0xaa);
    try std.testing.expectEqual(@as(isize, 12), string.strscpyPad(&padded, label[0..]));
    try std.testing.expect(string.streq(padded[0..], "lane6-rbtree"));
    try std.testing.expectEqual(@as(u8, 0), padded[12]);

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

    const readKey = struct {
        fn read(node: *const rbtree.Node) i32 {
            const entry: *const Entry = @fieldParentPtr("node", node);
            return entry.key;
        }
    }.read;

    var entries = [_]Entry{
        .{ .key = 30 },
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 40 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    rbtree.erase(&entries[0].node, &root);
    rbtree.eraseInit(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));
    try std.testing.expectEqual(@as(i32, 20), readKey(rbtree.first(&root).?));
    try std.testing.expectEqual(@as(i32, 40), readKey(rbtree.last(&root).?));

    var drained: [2]i32 = undefined;
    var count: usize = 0;
    var cursor = rbtree.first(&root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        drained[count] = readKey(node);
        count += 1;
    }
    try std.testing.expectEqualSlices(i32, &[_]i32{ 20, 40 }, drained[0..count]);
}
