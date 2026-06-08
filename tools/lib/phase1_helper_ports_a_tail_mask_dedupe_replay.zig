const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

test "tail mask dedupe replay spans bitmap find_bit string and rbtree" {
    const nbits = bitmap.bits_per_long + 13;
    const nwords = comptime bitmap.bitsToWords(nbits);

    var base = [_]bitmap.Word{0} ** nwords;
    bitmap.bitmap_set(&base, 1, 2);
    bitmap.bitmap_set(&base, bitmap.bits_per_long - 1, 2);
    bitmap.bitmap_set(&base, bitmap.bits_per_long + 4, 1);
    bitmap.bitmap_set(&base, bitmap.bits_per_long + 12, 1);

    var drop = [_]bitmap.Word{0} ** nwords;
    bitmap.bitmap_set(&drop, 2, 1);
    bitmap.bitmap_set(&drop, bitmap.bits_per_long, 1);

    var tail = [_]bitmap.Word{0} ** nwords;
    const has_tail = bitmap.bitmap_andnot(&tail, &base, &drop, nbits);
    try std.testing.expect(has_tail);
    try std.testing.expectEqual(@as(usize, 4), bitmap.bitmap_weight(&tail, nbits));
    try std.testing.expectEqual(@as(usize, 1), find_bit.findFirstBit(&tail, nbits));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long - 1), find_bit.findNextBit(&tail, nbits, 2));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 4), find_bit.findNextBit(&tail, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 12), find_bit.findLastBit(&tail, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, 0), find_bit.findFirstClump8(&clump, &tail, nbits));
    try std.testing.expectEqual(@as(u8, 0b0000_0010), clump);
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long - 8), find_bit.findNextClump8(&clump, &tail, nbits, bitmap.bits_per_long - 7));
    try std.testing.expectEqual(@as(u8, 0b1000_0000), clump);

    var rendered = [_]u8{0} ** 96;
    const rendered_len = bitmap.bitmap_scnprintf(&tail, nbits, &rendered);
    const rendered_slice = rendered[0..rendered_len];
    try std.testing.expect(string.strHasPrefix(rendered_slice, "1") != 0);
    try std.testing.expect(string.strEndsWith(rendered_slice, "76"));

    var padded = [_]u8{0xaa} ** 32;
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpyPad(&padded, rendered_slice));
    try std.testing.expectEqual(@as(u8, 0), padded[rendered_len]);
    try std.testing.expect(string.memchr_inv(padded[rendered_len + 1 ..], 0) == null);

    var spaced = [_]u8{ ' ', ' ', 'd', 'e', 'd', 'u', 'p', 'e', '-', '7', '6', '\n', 0, 0 };
    const trimmed = string.strim(&spaced);
    try std.testing.expectEqualSlices(u8, "dedupe-76", trimmed);
    try std.testing.expect(string.sysfs_streq("dedupe-76\n", trimmed));
    try std.testing.expectEqual(@as(?usize, 1), string.matchString(&[_][]const u8{ "tail", "dedupe-76", "mask" }, trimmed));

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

    const cmpKey = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = @intCast(find_bit.findFirstBit(&tail, nbits)), .serial = 0 },
        .{ .key = @intCast(find_bit.findNextBit(&tail, nbits, 2)), .serial = 1 },
        .{ .key = @intCast(find_bit.findNextBit(&tail, nbits, bitmap.bits_per_long)), .serial = 2 },
        .{ .key = @intCast(find_bit.findLastBit(&tail, nbits)), .serial = 3 },
        .{ .key = @intCast(find_bit.findLastBit(&tail, nbits)), .serial = 4 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const duplicate_key: i32 = @intCast(bitmap.bits_per_long + 12);
    var iter = rbtree.matchIterator(&duplicate_key, &root, cmpKey);
    var serials: [2]usize = undefined;
    var duplicate_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[duplicate_count] = entry.serial;
        duplicate_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 2), duplicate_count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 3, 4 }, serials[0..duplicate_count]);

    rbtree.erase(&entries[3].node, &root);
    rbtree.eraseInit(&entries[4].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[4].node));
    try std.testing.expect(rbtree.find(&duplicate_key, &root, cmpKey) == null);

    var order: [3]i32 = undefined;
    var count: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        order[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(
        i32,
        &[_]i32{ 1, @intCast(bitmap.bits_per_long - 1), @intCast(bitmap.bits_per_long + 4) },
        order[0..count],
    );
}
