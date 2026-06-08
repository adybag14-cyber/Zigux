const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Entry = struct {
    node: rbtree.Node = .{},
    key: usize,
    serial: usize,
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key or (lhs_entry.key == rhs_entry.key and lhs_entry.serial < rhs_entry.serial);
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const usize = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) {
        return -1;
    }
    if (wanted.* > entry.key) {
        return 1;
    }
    return 0;
}

fn expectEntry(node: ?*rbtree.Node, key: usize, serial: usize) !void {
    const found = node orelse return error.TestUnexpectedResult;
    const entry: *const Entry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(key, entry.key);
    try std.testing.expectEqual(serial, entry.serial);
}

test "phase1 helper ports A pad cached replay" {
    const nbits = bitmap.bits_per_long + 10;
    var map = [_]bitmap.Word{0} ** 2;
    bitmap.setRange(&map, 4, 3);
    bitmap.setRange(&map, 17, 1);
    bitmap.setRange(&map, bitmap.bits_per_long + 1, 2);

    try std.testing.expectEqual(@as(usize, 6), bitmap.weight(&map, nbits));
    try std.testing.expectEqual(@as(usize, 4), find_bit.findFirstBit(&map, nbits));
    try std.testing.expectEqual(@as(usize, 7), find_bit.findNextZeroBit(&map, nbits, 4));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 1), find_bit.findNextBit(&map, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long + 2), find_bit.findLastBit(&map, nbits));

    var clump: u8 = 0;
    try std.testing.expectEqual(@as(usize, bitmap.bits_per_long), find_bit.findNextClump8(&clump, &map, nbits, bitmap.bits_per_long));
    try std.testing.expectEqual(@as(u8, 0x06), clump);

    var rendered = [_]u8{0} ** 32;
    const rendered_len = bitmap.scnprintf(&map, nbits, &rendered);
    try std.testing.expectEqualStrings("4-6,17,65-66", rendered[0..rendered_len]);

    var padded = [_]u8{0xaa} ** 24;
    try std.testing.expectEqual(@as(isize, @intCast(rendered_len)), string.strscpyPad(&padded, rendered[0..rendered_len]));
    try std.testing.expectEqualStrings("4-6,17,65-66", padded[0..rendered_len]);
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(padded[rendered_len + 1 ..], 0));
    try std.testing.expectEqual(@as(usize, 3), string.strHasPrefix(&padded, "4-6"));
    try std.testing.expect(string.strEndsWith(&padded, "65-66"));
    try std.testing.expect(string.sysfsStreq("4-6,17,65-66\n", &padded));

    var root = rbtree.RootCached.init();
    var entries = [_]Entry{
        .{ .key = find_bit.findFirstBit(&map, nbits), .serial = 0 },
        .{ .key = find_bit.findNextZeroBit(&map, nbits, 4), .serial = 1 },
        .{ .key = find_bit.findNextBit(&map, nbits, bitmap.bits_per_long), .serial = 2 },
        .{ .key = find_bit.findLastBit(&map, nbits), .serial = 3 },
    };

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try expectEntry(rbtree.firstCached(&root), 4, 0);
    try expectEntry(rbtree.find(&entries[2].key, &root.root, cmpKey), bitmap.bits_per_long + 1, 2);

    rbtree.eraseInitCached(&entries[0].node, &root);
    try std.testing.expect(rbtree.emptyNode(&entries[0].node));
    try expectEntry(rbtree.firstCached(&root), 7, 1);

    const replacement = rbtree.addCached(&entries[0].node, &root, less);
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), replacement);
    try expectEntry(rbtree.firstCached(&root), 4, 0);
}
