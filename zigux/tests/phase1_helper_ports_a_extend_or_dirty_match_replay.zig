const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

const Entry = struct {
    key: i32,
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
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

test "phase1 helper ports replay keeps extended unions and dirty-byte scans aligned" {
    const count = find_bit.bits_per_long + 5;
    const size = find_bit.bits_per_long * 3;
    const src = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
        0x0123_4567_89ab_cdef,
    };

    var extended = [_]bitmap.Word{ 0, 0, 0, 0x55aa_55aa_55aa_55aa };
    bitmap.copyAndExtend(extended[0..3], src[0..2], count, size);
    try std.testing.expectEqual(~@as(bitmap.Word, 0), extended[0]);
    try std.testing.expectEqual(find_bit.lastWordMask(count), extended[1]);
    try std.testing.expectEqual(@as(bitmap.Word, 0), extended[2]);
    try std.testing.expectEqual(@as(bitmap.Word, 0x55aa_55aa_55aa_55aa), extended[3]);

    var extra = [_]bitmap.Word{ 0, 0, 0 };
    extra[1] = @as(bitmap.Word, 1) << 7;

    var union_bits = [_]bitmap.Word{ 0, 0, 0 };
    try std.testing.expectEqual(count + 1, bitmap.weightedOr(union_bits[0..], extended[0..3], extra[0..], size));
    try std.testing.expectEqual(@as(usize, count + 2), find_bit.findNextOrBit(extended[0..3], extra[0..], size, count));
    try std.testing.expectEqual(@as(usize, count + 2), find_bit.find_next_or_bit(extended[0..3], extra[0..], size, count));

    var log = [_]u8{'.'} ** 16;
    const dirty_idx = find_bit.findNextOrBit(extended[0..3], extra[0..], size, count) - count;
    log[dirty_idx] = 'X';
    try std.testing.expectEqual(@as(?usize, 2), string.memchrInv(log[0..], '.'));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv("........", '.'));
}

test "phase1 helper ports replay keeps duplicate matches and compact labels stable" {
    var entries = [_]Entry{
        .{ .key = 8, .serial = 0 },
        .{ .key = 3, .serial = 1 },
        .{ .key = 8, .serial = 2 },
        .{ .key = 12, .serial = 3 },
        .{ .key = 8, .serial = 4 },
    };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(*rbtree.Node, &entries[1].node), rbtree.firstCached(&root).?);

    const duplicate = @as(i32, 8);
    var iter = rbtree.matchIterator(&duplicate, &root.root, cmpKey);
    var serials: [3]usize = undefined;
    var count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        serials[count] = entry.serial;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 2, 4 }, serials[0..count]);

    const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &root) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), promoted_leftmost);
    try std.testing.expectEqual(@as(*rbtree.Node, &entries[0].node), rbtree.firstCached(&root).?);

    var label = [_]u8{ '8', ' ', '8', ' ', '8', 0, 0 };
    const compact = string.removeSpaces(&label);
    try std.testing.expectEqualStrings("888", compact);
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv(compact, '8'));
}
