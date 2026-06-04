const std = @import("std");

const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const rbtree = @import("rbtree");
const string = @import("string");

const Word = bitmap.Word;

test "bitmap restart tail window feeds find-bit scans" {
    const nbits = bitmap.bits_per_long + 5;
    var words = [_]Word{ 0, ~@as(Word, 0) };
    bitmap.zero(&words, nbits);

    bitmap.setRange(&words, bitmap.bits_per_long - 2, 7);
    bitmap.clearRange(&words, bitmap.bits_per_long - 1, 4);

    try std.testing.expectEqual(bitmap.bits_per_long - 2, find_bit.findFirstBit(&words, nbits));
    try std.testing.expectEqual(bitmap.bits_per_long + 3, find_bit.findNextBit(&words, nbits, bitmap.bits_per_long - 1));
    try std.testing.expectEqual(bitmap.bits_per_long + 2, find_bit.findNextZeroBit(&words, nbits, bitmap.bits_per_long + 2));
    try std.testing.expectEqual(bitmap.bits_per_long + 4, find_bit.findLastBit(&words, nbits));

    var copied = [_]Word{ ~@as(Word, 0), ~@as(Word, 0) };
    bitmap.copyClearTail(&copied, &words, nbits);
    try std.testing.expect(bitmap.equal(&words, &copied, nbits));
    try std.testing.expectEqual(@as(Word, (1 << 3) | (1 << 4)), copied[1] & ~@as(Word, 0));

    var clump: u8 = 0xaa;
    try std.testing.expectEqual(bitmap.bits_per_long - 8, find_bit.findNextClump8(&clump, &copied, nbits, bitmap.bits_per_long - 2));
    try std.testing.expectEqual(@as(u8, 0x40), clump);
    try std.testing.expectEqual(bitmap.bits_per_long, find_bit.findNextClump8(&clump, &copied, nbits, bitmap.bits_per_long + 3));
    try std.testing.expectEqual(@as(u8, 0x18), clump);
}

test "string bounded copies and searches restart at C-string tails" {
    var dest = [_]u8{ 'x', 'x', 'x', 'x', 'x', 'x', 'x' };
    const source = [_]u8{ 'r', 'e', 's', 't', 'a', 'r', 't', 0, 'h', 'i', 'd', 'e' };

    try std.testing.expectEqual(@as(usize, 7), string.strlcpy(&dest, &source));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'r', 'e', 's', 't', 'a', 'r', 0 }, &dest);
    try std.testing.expectEqual(@as(?usize, 3), string.strnchr(&dest, dest.len, 't'));
    try std.testing.expectEqual(@as(?usize, null), string.strnchr(&source, source.len, 'h'));
    try std.testing.expectEqual(@as(?usize, 7), string.strnchr(&source, source.len, 0));

    var padded = [_]u8{ 'q', 'q', 'q', 'q', 'q', 'q' };
    try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, &[_]u8{ 'o', 'k', 0, 'x' }));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 0, 0, 0 }, &padded);
}

test "rbtree duplicate restart survives replacement and erase" {
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

    const cmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const Entry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 8, .serial = 0 },
        .{ .key = 4, .serial = 1 },
        .{ .key = 12, .serial = 2 },
        .{ .key = 8, .serial = 3 },
        .{ .key = 8, .serial = 4 },
    };
    var replacement = Entry{ .key = 8, .serial = 9 };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const wanted = @as(i32, 8);
    var iter = rbtree.matchIterator(&wanted, &root, cmp);
    var before: [3]usize = undefined;
    var before_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        before[before_count] = entry.serial;
        before_count += 1;
    }
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 3, 4 }, before[0..before_count]);

    rbtree.replaceNode(&entries[3].node, &replacement.node, &root);
    rbtree.erase(&replacement.node, &root);

    iter = rbtree.matchIterator(&wanted, &root, cmp);
    var after: [2]usize = undefined;
    var after_count: usize = 0;
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        after[after_count] = entry.serial;
        after_count += 1;
    }
    try std.testing.expectEqualSlices(usize, &[_]usize{ 0, 4 }, after[0..after_count]);
    try std.testing.expectEqual(@as(i32, 4), (@as(*const Entry, @fieldParentPtr("node", rbtree.first(&root).?))).key);
    try std.testing.expectEqual(@as(i32, 12), (@as(*const Entry, @fieldParentPtr("node", rbtree.last(&root).?))).key);
}
