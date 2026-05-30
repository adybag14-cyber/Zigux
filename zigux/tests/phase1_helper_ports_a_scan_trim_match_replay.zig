const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;
const bits_per_long = bitmap.bits_per_long;

test "phase 1 ports A bitmap predicates feed bounded find scans" {
    const nbits = bits_per_long + 9;
    var lhs = [_]Word{ 0, 0 };
    var rhs = [_]Word{ 0, 0 };
    var dst = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };

    bitmap.setRange(&lhs, 3, 4);
    bitmap.setRange(&lhs, bits_per_long + 4, 1);
    bitmap.setRange(&rhs, 5, 2);
    bitmap.setRange(&rhs, bits_per_long + 4, 1);
    rhs[1] |= @as(Word, 1) << 12;

    try std.testing.expectEqual(@as(usize, 3), find_bit.findFirstBit(&lhs, nbits));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findNextBit(&lhs, nbits, bits_per_long));
    try std.testing.expectEqual(@as(usize, bits_per_long + 4), find_bit.findLastBit(&lhs, nbits));

    try std.testing.expect(bitmap.bitmap_and(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 3), bitmap.bitmap_weight(&dst, nbits));
    try std.testing.expectEqual(@as(usize, 5), find_bit.findFirstBit(&dst, nbits));
    try std.testing.expectEqual(@as(usize, nbits), find_bit.findNextBit(&dst, nbits, nbits));

    try std.testing.expect(bitmap.bitmap_andnot(&dst, &lhs, &rhs, nbits));
    try std.testing.expectEqual(@as(usize, 2), bitmap.bitmap_weight(&dst, nbits));
    try std.testing.expect(bitmap.bitmap_subset(&dst, &lhs, nbits));
    try std.testing.expect(bitmap.bitmap_intersects(&lhs, &rhs, nbits));
}

test "phase 1 ports A string trimming keeps match helpers inside C strings" {
    var padded = [_]u8{ ' ', '\t', 'd', 'e', 'v', 'i', 'c', 'e', '\n', 0, 'x' };
    const trimmed = string.strim(&padded);

    try std.testing.expectEqualStrings("device", trimmed);
    try std.testing.expect(string.streq(trimmed, "device"));
    try std.testing.expect(!string.streq(&padded, "device"));
    try std.testing.expectEqual(@as(?usize, 0), string.match_string(&[_][]const u8{ "device", "driver" }, trimmed));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(&[_][]const u8{"driver"}, trimmed));

    const sysfs_names = [_][]const u8{ "device", "driver" };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfs_match_string(&sysfs_names, "device\n"));
    try std.testing.expectEqual(@as(?usize, null), string.match_string(&sysfs_names, "device\n"));
    try std.testing.expectEqual(@as(?usize, 2), string.memchr_inv(&[_]u8{ 0, 0, 1, 0 }, 0));
}

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn lessNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) return lhs_entry.key < rhs_entry.key;
    return lhs_entry.serial < rhs_entry.serial;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "phase 1 ports A rbtree duplicate-key matches stay ordered" {
    var entries = [_]Entry{
        .{ .key = 8, .serial = 0 },
        .{ .key = 3, .serial = 1 },
        .{ .key = 8, .serial = 2 },
        .{ .key = 12, .serial = 3 },
        .{ .key = 8, .serial = 4 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, lessNode);
    }

    var duplicate = Entry{ .key = 8, .serial = 99 };
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.findAdd(&duplicate.node, &root, cmpNode));

    const key: i32 = 8;
    var iter = rbtree.matchIterator(&key, &root, cmpKey);
    const expected_serials = [_]usize{ 0, 2, 4 };
    var actual_serials: [expected_serials.len]usize = undefined;
    var count: usize = 0;

    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        actual_serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(expected_serials.len, count);
    try std.testing.expectEqualSlices(usize, &expected_serials, actual_serials[0..count]);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.rb_first(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[3].node), rbtree.rb_last(&root));
}
