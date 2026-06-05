const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "bitmap zero-width updates keep clump and tail scans stable" {
    const nbits = bits_per_long + 9;
    var map = [_]Word{ 0, 0 };

    bitmap.bitmap_zero(&map, 0);
    bitmap.bitmap_clear(&map, bits_per_long + 4, 0);
    try std.testing.expectEqual(@as(Word, 0), map[0]);
    try std.testing.expectEqual(@as(Word, 0), map[1]);

    bitmap.bitmap_set(&map, bits_per_long + 7, 1);
    map[1] |= @as(Word, 1) << 30;

    try std.testing.expectEqual(@as(usize, bits_per_long + 7), find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 7), find_bit.findLastBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 1), bitmap.bitmap_weight(&map, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bits_per_long), find_bit.findNextClump8(&clump, &map, nbits, bits_per_long + 5));
    try std.testing.expectEqual(@as(u8, 0b1000_0000), clump);

    bitmap.bitmap_clear(&map, bits_per_long + 7, 1);
    clump = 0x5a;
    try std.testing.expectEqual(nbits, find_bit.findNextClump8(&clump, &map, nbits, bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x5a), clump);
    try std.testing.expect(bitmap.bitmap_empty(&map, nbits));
}

test "string empty cleanup keeps C and sysfs boundaries distinct" {
    var blank = [_]u8{ ' ', '\t', '\n', 0, 'x' };
    const trimmed = string.strim(&blank);
    try std.testing.expectEqual(@as(usize, 0), trimmed.len);
    try std.testing.expectEqual(@as(u8, 0), blank[0]);

    var padded = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, "ok"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &padded);

    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(&[_]u8{ 0x5a, 0x5a, 0x5a, 0x5a }, 0x5a));
    try std.testing.expectEqual(@as(?usize, 2), string.memchrInv(&[_]u8{ 0x5a, 0x5a, 0x10, 0x5a }, 0x5a));

    const entries = [_][]const u8{ "ready\n", "ready\x00hidden", "other\n" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&entries, "ready"));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&entries, "ready"));
}

test "rbtree postorder aliases preserve empty and mutated traversal" {
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

    var root = rbtree.Root.init();
    try std.testing.expect(rbtree.rb_first_postorder(&root) == null);
    try std.testing.expect(rbtree.rb_next_postorder(null) == null);

    var entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 4 },
        .{ .key = 12 },
        .{ .key = 2 },
        .{ .key = 6 },
    };

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var postorder_keys: [5]i32 = undefined;
    var count: usize = 0;
    var cursor = rbtree.rb_first_postorder(&root);
    while (cursor) |node| : (cursor = rbtree.rb_next_postorder(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        postorder_keys[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 6, 4, 12, 8 }, postorder_keys[0..count]);

    rbtree.eraseInit(&entries[1].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[1].node));

    var forward_keys: [4]i32 = undefined;
    count = 0;
    cursor = rbtree.first(&root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        forward_keys[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqualSlices(i32, &[_]i32{ 2, 6, 8, 12 }, forward_keys[0..count]);
}
