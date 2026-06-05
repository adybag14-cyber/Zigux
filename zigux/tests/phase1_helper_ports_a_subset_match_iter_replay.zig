const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Word = bitmap.Word;

const Entry = struct {
    key: usize,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "bitmap subset and find-bit paired scans drive duplicate rbtree match iteration" {
    const nbits = bitmap.bits_per_long + 17;
    var base = [_]Word{ 0, 0 };
    var mask = [_]Word{ 0, 0 };
    var union_map = [_]Word{ 0, 0 };

    bitmap.setRange(&base, 3, 4);
    bitmap.setRange(&base, bitmap.bits_per_long + 4, 3);
    bitmap.setRange(&mask, 3, 4);
    bitmap.setRange(&mask, bitmap.bits_per_long + 4, 3);
    bitmap.setRange(&mask, bitmap.bits_per_long + 12, 1);

    try std.testing.expect(bitmap.subset(&base, &mask, nbits));
    try std.testing.expect(!bitmap.subset(&mask, &base, nbits));
    try std.testing.expect(bitmap.intersects(&base, &mask, nbits));
    try std.testing.expect(!bitmap.equal(&base, &mask, nbits));
    try std.testing.expect(bitmap.andBits(&union_map, &base, &mask, nbits));
    try std.testing.expectEqual(@as(usize, 7), bitmap.weight(&union_map, nbits));

    const first_shared = find_bit.findNextAndBit(&base, &mask, nbits, 0);
    const second_shared = find_bit.findNextAndBit(&base, &mask, nbits, first_shared + 1);
    const tail_gap = find_bit.findNextAndNotBit(&mask, &base, nbits, bitmap.bits_per_long + 8);
    const missing_shared = find_bit.findNextAndBit(&base, &mask, nbits, nbits);

    try std.testing.expectEqual(@as(usize, 3), first_shared);
    try std.testing.expectEqual(@as(usize, 4), second_shared);
    try std.testing.expectEqual(bitmap.bits_per_long + 12, tail_gap);
    try std.testing.expectEqual(nbits, missing_shared);

    var rendered: [48]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&mask, nbits, &rendered);
    try std.testing.expectEqualStrings("3-6,68-70,76", rendered[0..rendered_len]);

    var copied = [_]u8{0xaa} ** 32;
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpyPad(&copied, rendered[0..rendered_len]));
    try std.testing.expectEqual(@as(u8, 0), copied[rendered_len]);
    try std.testing.expectEqual(@as(u8, 0), copied[rendered_len + 1]);

    const labels = [_][]const u8{
        "3-6,68-70,76\n",
        "3-6",
        "76",
    };
    try std.testing.expectEqual(@as(?usize, 0), string.sysfsMatchString(&labels, copied[0..rendered_len]));
    try std.testing.expectEqual(@as(?usize, 2), string.matchString(&labels, "76"));

    var entries = [_]Entry{
        .{ .key = first_shared, .serial = 0 },
        .{ .key = tail_gap, .serial = 1 },
        .{ .key = bitmap.bits_per_long + 4, .serial = 2 },
        .{ .key = tail_gap, .serial = 3 },
        .{ .key = second_shared, .serial = 4 },
        .{ .key = tail_gap, .serial = 5 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var iter = rbtree.matchIterator(&tail_gap, &root, cmpKey);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 1, 3, 5 }, serials[0..count]);

    const missing = @as(usize, 99);
    var missing_iter = rbtree.matchIterator(&missing, &root, cmpKey);
    try std.testing.expect(missing_iter.next() == null);
}
