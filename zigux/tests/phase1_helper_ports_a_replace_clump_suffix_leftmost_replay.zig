const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const string = @import("string");
const rbtree = @import("rbtree");

test "phase1 helper ports A bitmap replace clamps masked tail windows" {
    const nbits = bitmap.bits_per_long + 5;

    const old = [_]bitmap.Word{
        0b1010_0101,
        0b0001_0010,
    };
    const new = [_]bitmap.Word{
        0b0101_1010,
        0b1110_1101,
    };
    const mask = [_]bitmap.Word{
        0b1111_0000,
        0b1111_1111,
    };
    var dst = [_]bitmap.Word{ 0, 0 };

    bitmap.replace(&dst, &old, &new, &mask, nbits);

    try std.testing.expectEqual(
        @as(bitmap.Word, (old[0] & ~mask[0]) | (new[0] & mask[0])),
        dst[0],
    );
    try std.testing.expectEqual(
        @as(bitmap.Word, ((old[1] & ~mask[1]) | (new[1] & mask[1])) & bitmap.lastWordMask(nbits)),
        dst[1],
    );
    try std.testing.expect(bitmap.equal(&dst, &[_]bitmap.Word{ 0b0101_0101, 0b01101 }, nbits));
}

test "phase1 helper ports A clump scans keep aligned bytes readable across a word edge" {
    const edge_offset = find_bit.bits_per_long - 8;
    const nbits = find_bit.bits_per_long + 8;
    const map = [_]find_bit.Word{
        @as(find_bit.Word, 0xA5) << @intCast(edge_offset),
        0x3C,
    };

    try std.testing.expectEqual(@as(u8, 0xA5), find_bit.getValue8(&map, edge_offset));
    try std.testing.expectEqual(@as(u8, 0x3C), find_bit.getValue8(&map, find_bit.bits_per_long));

    var clump: u8 = 0;
    try std.testing.expectEqual(edge_offset, find_bit.findFirstClump8(&clump, &map, nbits));
    try std.testing.expectEqual(@as(u8, 0xA5), clump);
    try std.testing.expectEqual(find_bit.bits_per_long, find_bit.findNextClump8(&clump, &map, nbits, edge_offset + 8));
    try std.testing.expectEqual(@as(u8, 0x3C), clump);
}

test "phase1 helper ports A string suffix and counted search stop at the C-string boundary" {
    const suffixed = [_]u8{ 't', 'a', 'i', 'l', 0, 'x', 'x' };
    try std.testing.expect(string.strEndsWith(&suffixed, "ail"));
    try std.testing.expect(!string.strEndsWith(&suffixed, "ailx"));
    try std.testing.expectEqual(@as(?usize, 2), string.strnchr(&suffixed, suffixed.len, 'i'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&suffixed, suffixed.len, 'x'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr("suffix", 2, 'f'));
}

test "phase1 helper ports A cached replacement retargets the leftmost pointer when replacing the first node" {
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

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 20 },
    };
    var replacement = Entry{ .key = 5 };
    var root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &root, less);
    }

    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[1].node), rbtree.firstCached(&root));

    rbtree.replaceNodeCached(&entries[1].node, &replacement.node, &root);

    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.firstCached(&root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.first(&root.root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &entries[0].node), rbtree.next(&replacement.node));
    try std.testing.expectEqual(@as(?*rbtree.Node, &replacement.node), rbtree.prev(&entries[0].node));
}
