const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

const Entry = struct {
    key: i32,
    serial: u8,
    node: rbtree.Node = rbtree.Node.init(),
};

fn entryLess(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key == rhs_entry.key) {
        return lhs_entry.serial < rhs_entry.serial;
    }
    return lhs_entry.key < rhs_entry.key;
}

fn cmpKey(key_ptr: *const anyopaque, node: *const rbtree.Node) i32 {
    const key: *const i32 = @ptrCast(@alignCast(key_ptr));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (key.* < entry.key) return -1;
    if (key.* > entry.key) return 1;
    return 0;
}

fn expectSerialsForKey(root: *const rbtree.Root, key: i32, expected: []const u8) !void {
    var actual: [8]u8 = undefined;
    var count: usize = 0;
    var iter = rbtree.matchIterator(&key, root, cmpKey);
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        actual[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(expected.len, count);
    try std.testing.expectEqualSlices(u8, expected, actual[0..count]);
}

test "phase1 ports A tail bitmap scans and string labels agree" {
    const nbits = bits_per_long + 9;
    var map: [2]Word = @splat(0);
    var rendered: [48]u8 = undefined;

    bitmap.bitmap_set(map[0..], bits_per_long - 3, 6);
    bitmap.bitmap_set(map[0..], bits_per_long + 7, 4);
    bitmap.bitmap_clear(map[0..], bits_per_long + 9, 8);

    try std.testing.expectEqual(bits_per_long - 3, find_bit.findFirstBit(map[0..], nbits));
    try std.testing.expectEqual(bits_per_long + 3, find_bit.findNextZeroBit(map[0..], nbits, bits_per_long - 3));
    try std.testing.expectEqual(bits_per_long + 7, find_bit.findNextBit(map[0..], nbits, bits_per_long + 3));
    try std.testing.expectEqual(nbits, find_bit.findNextBit(map[0..], nbits, bits_per_long + 9));
    try std.testing.expectEqual(@as(usize, 8), bitmap.bitmap_weight(map[0..], nbits));

    const written = bitmap.scnprintf(map[0..], nbits, rendered[0..]);
    try std.testing.expectEqualStrings("61-66,71-72", rendered[0..written]);

    const labels = [_][]const u8{
        "61-66,71-72\n",
        "61-66,71-73\n",
        "bitmap-tail",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(labels[0..], rendered[0..written]));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(labels[0..], rendered[0..written]));
    try std.testing.expectEqual(@as(?usize, 5), string.strnchr(rendered[0..written], written, ','));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(rendered[0..written], 2, ','));
}

test "phase1 ports A bitmap predicates select duplicate rbtree key runs" {
    var selector: [1]Word = @splat(0);
    bitmap.bitmap_set(selector[0..], 2, 1);
    bitmap.bitmap_set(selector[0..], 5, 1);
    bitmap.bitmap_set(selector[0..], 8, 1);

    var entries = [_]Entry{
        .{ .key = 7, .serial = 4 },
        .{ .key = 3, .serial = 0 },
        .{ .key = 7, .serial = 2 },
        .{ .key = 7, .serial = 5 },
        .{ .key = 11, .serial = 8 },
    };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, entryLess);
    }

    const selected_key: i32 = if (bitmap.bitmap_empty(selector[0..], 9)) 3 else 7;
    const first_set = find_bit.findFirstBit(selector[0..], 9);
    const last_set = find_bit.findLastBit(selector[0..], 9);

    try std.testing.expectEqual(@as(usize, 2), first_set);
    try std.testing.expectEqual(@as(usize, 8), last_set);
    try expectSerialsForKey(&root, selected_key, &.{ 2, 4, 5 });

    const absent_key: i32 = @intCast(last_set + 5);
    try expectSerialsForKey(&root, absent_key, &.{});
}
